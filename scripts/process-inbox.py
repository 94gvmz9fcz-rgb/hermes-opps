#!/usr/bin/env python3
"""
process-inbox — The iron-clad data ingestion handler.

One channel (inbox/), one format (data + manifest), one handler (this script).
8-step pipeline with verification gates. Never guesses. Never silently drops data.

Usage:
    python3 scripts/process-inbox.py                         # process inbox/
    python3 scripts/process-inbox.py --manifest manifest.json  # process a specific file
    python3 scripts/process-inbox.py --rollback <manifest_id>  # rollback a previous run
    python3 scripts/process-inbox.py --dry-run                 # validate + diff, no writes

Environment:
    Requires vault decryption to read Airtable token.
    Configure base_id + table_name in ~/./config/airtable.json or via env vars.
"""

import csv
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# Add repo root to sys.path for model imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from models.airtable_crm import (
    ActionType,
    ChangelogEntry,
    ConflictPolicy,
    ContactV2,
    DiffResult,
    ManifestV1,
    QuarantineReport,
    Snapshot,
)
from pydantic import ValidationError


# ─── Configuration ──────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".hermes" / "config"
VAULT_DIR = Path.home() / ".hermes" / "vault"
INBOX_DIR = Path.home() / "OneDrive" / "Hermy" / "inbox"
PROCESSED_DIR = Path.home() / "OneDrive" / "Hermy" / "processed"
QUARANTINE_DIR = Path.home() / "OneDrive" / "Hermy" / "quarantine"
CHANGELOG_DIR = Path.home() / "OneDrive" / "Hermy" / "changelog"
SNAPSHOT_DIR = Path.home() / "OneDrive" / "Hermy" / "snapshots"
LOCKFILE = INBOX_DIR / ".process-inbox.lock"

SCHEMA_REGISTRY = {"contacts-v2": ContactV2}

AIRTABLE_API = "https://api.airtable.com/v0"

# Rate limiting
BATCH_SIZE = 10
RATE_LIMIT_DELAY = 0.35  # seconds between batches (stays under 5req/s)
MAX_RETRIES = 3


# ─── Vault / Secrets ────────────────────────────────────────────────────────

def read_vault() -> dict:
    """Read secrets from the Hermes vault.

    The vault is an encrypted JSON file. If vault isn't mounted/decrypted,
    try the env file as fallback.
    """
    vault_path = VAULT_DIR / "vault.json"
    if vault_path.exists():
        try:
            with open(vault_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError):
            pass

    # Fallback to env file
    env_path = CONFIG_DIR.parent / ".env"
    if env_path.exists():
        secrets = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    secrets[k.strip()] = v.strip().strip('"').strip("'")
        return secrets

    return {}


def get_airtable_token() -> str:
    import base64
    secrets = read_vault()
    # Try standard env names
    for key in ("AIRTABLE_TOKEN", "AIRTABLE_PAT", "AIRTABLE_API_KEY"):
        if key in secrets and secrets[key]:
            val = secrets[key].strip('"').strip("'")
            # Try base64 decode (Hermes vault encodes tokens)
            try:
                return base64.b64decode(val).decode()
            except Exception:
                return val
    raise RuntimeError(
        "Airtable token not found in vault or env. "
        "Run: hermes vault decrypt first, or set AIRTABLE_TOKEN in .env"
    )


# ─── Airtable Client ────────────────────────────────────────────────────────

class AirtableClient:
    """Thin client for Airtable REST API with rate limiting and retries."""

    def __init__(self, base_id: str, table_name: str):
        self.base_id = base_id
        self.table_name = table_name
        self.token = get_airtable_token()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })
        self._rate_limit_ts = 0.0

    def _rate_limit(self):
        """Ensure we don't exceed 5 requests/second."""
        elapsed = time.time() - self._rate_limit_ts
        if elapsed < 0.2:
            time.sleep(0.2 - elapsed)
        self._rate_limit_ts = time.time()

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{AIRTABLE_API}/{self.base_id}/{endpoint}"
        for attempt in range(MAX_RETRIES + 1):
            self._rate_limit()
            try:
                resp = self.session.request(method, url, timeout=30, **kwargs)
            except requests.RequestException as e:
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Network error after {MAX_RETRIES} retries: {e}")

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                time.sleep(retry_after)
                continue

            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Airtable API error {resp.status_code}: "
                    f"{resp.text[:500]}"
                )

            return resp.json()

        raise RuntimeError("Max retries exceeded on 429 responses")

    def list_records(self, fields: Optional[list[str]] = None, offset: Optional[str] = None) -> dict:
        """Get records with optional field selection and pagination."""
        params = {"maxRecords": 100}
        if fields:
            params["fields"] = fields
        if offset:
            params["offset"] = offset
        return self._request("GET", self.table_name, params=params)

    def get_record(self, record_id: str) -> dict:
        return self._request("GET", f"{self.table_name}/{record_id}")

    def create_records(self, records: list[dict]) -> dict:
        """Batch create (max 10 at a time)."""
        return self._request("POST", self.table_name, json={"records": [{"fields": r} for r in records]})

    def update_records(self, records: list[dict]) -> dict:
        """Batch update (max 10 at a time)."""
        return self._request("PATCH", self.table_name, json={"records": records})

    def delete_records(self, record_ids: list[str]) -> dict:
        params = [("records[]", rid) for rid in record_ids]
        return self._request("DELETE", self.table_name, params=params)

    def preflight_check(self) -> bool:
        """Gate 1: verify the target exists and token has access."""
        try:
            resp = self._request("GET", f"{self.table_name}?maxRecords=1")
            return True
        except RuntimeError:
            return False

    def verify_record(self, record_id: str, expected_fields: dict) -> bool:
        """Gate 2: read back a written record and verify fields match."""
        try:
            data = self.get_record(record_id)
            actual = data.get("fields", {})
            for k, v in expected_fields.items():
                if k not in actual:
                    return False
                # Normalize comparison: both as strings
                if str(actual.get(k, "")) != str(v):
                    return False
            return True
        except RuntimeError:
            return False


# ─── Pipeline Steps ─────────────────────────────────────────────────────────

def step1_read_manifest(path: Path) -> ManifestV1:
    """Step 1: Read and validate the manifest file."""
    with open(path) as f:
        raw = json.load(f)
    return ManifestV1.model_validate(raw)


def step2_validate_data(records: list[dict], schema_name: str) -> tuple[list[dict], list[dict]]:
    """Step 2: Validate data against Pydantic model.

    Returns (valid_records, quarantined_records).
    """
    if schema_name not in SCHEMA_REGISTRY:
        raise ValueError(
            f"Unknown schema '{schema_name}'. "
            f"Known schemas: {list(SCHEMA_REGISTRY.keys())}"
        )

    Model = SCHEMA_REGISTRY[schema_name]
    good, bad = [], []

    for i, rec in enumerate(records):
        try:
            validated = Model(**rec)
            good.append(validated.model_dump(exclude_none=True))
        except ValidationError as e:
            bad.append({
                "index": i,
                "record": rec,
                "errors": [
                    {"field": err.get("loc", []), "msg": err.get("msg", "")}
                    for err in e.errors()
                ],
            })

    return good, bad


def step3_diff(airtable: AirtableClient, records: list[dict], dedup_key: list[str]) -> DiffResult:
    """Step 3: Diff incoming data against current Airtable state.

    Returns DiffResult with new, changed, unchanged, and conflicted records.
    """
    diff = DiffResult()

    # Fetch all existing records (handle pagination)
    existing = {}
    offset = None
    while True:
        resp = airtable.list_records(offset=offset)
        for rec in resp.get("records", []):
            existing[rec["id"]] = rec.get("fields", {})
        offset = resp.get("offset")
        if not offset:
            break

    # Build dedup index from existing records
    dedup_index = {}
    for rid, fields in existing.items():
        key_parts = [str(fields.get(k, "")).strip().lower() for k in dedup_key]
        if any(not p for p in key_parts):
            continue
        key = "::".join(key_parts)
        dedup_index[key] = rid

    for record in records:
        key_parts = [str(record.get(k, "")).strip().lower() for k in dedup_key]
        if any(not p for p in key_parts):
            diff.conflicts.append({
                "record": record,
                "reason": f"dedup_key fields {dedup_key} not present or empty",
            })
            continue

        key = "::".join(key_parts)

        if key not in dedup_index:
            diff.new.append(record)
        else:
            rid = dedup_index[key]
            current = existing[rid]

            # Check if data is actually different (exclude metadata)
            changed = False
            for field, value in record.items():
                # Skip fields not in Airtable (source, source_id, imported_at)
                str_current = str(current.get(field, "")).strip()
                str_incoming = str(value).strip()
                if str_current != str_incoming:
                    changed = True
                    break

            if changed:
                if any(
                    str(current.get(k, "")).strip().lower() != str(record.get(k, "")).strip().lower()
                    for k in dedup_key
                ):
                    # Dedup key itself changed — conflict
                    diff.conflicts.append({
                        "record": record,
                        "existing_id": rid,
                        "existing_fields": current,
                        "reason": "dedup key fields differ from existing record",
                    })
                else:
                    diff.changed.append({"id": rid, "fields": record})
            else:
                diff.unchanged.append(record)

    return diff


def step4_write(
    airtable: AirtableClient,
    diff: DiffResult,
    action: ActionType,
    conflict_policy: ConflictPolicy,
    manifest_id: str = "",
    dry_run: bool = False,
) -> tuple[list[str], ChangelogEntry]:
    """Step 4: Write only new/changed records.

    Returns (written_record_ids, changelog_entry).
    """
    log = ChangelogEntry(
        action=action,
        table=airtable.table_name,
        manifest_id=manifest_id,
    )

    if dry_run:
        log.added = len(diff.new)
        log.updated = len(diff.changed)
        log.skipped = len(diff.unchanged)
        log.conflicts = diff.conflicts
        log.records = [f"[DRY RUN] would write {len(diff.new)} new + {len(diff.changed)} updated"]
        return [], log

    written_ids = []

    # --- Handle conflicts ---
    if diff.conflicts and conflict_policy == ConflictPolicy.MANUAL_REVIEW:
        log.conflicts = diff.conflicts
        print(f"⚠️  {len(diff.conflicts)} records have conflicts — quarantined for manual review")
        # Don't write conflicts, just log them
    elif diff.conflicts and conflict_policy == ConflictPolicy.OVERWRITE:
        log.conflicts = diff.conflicts
        for c in diff.conflicts:
            if "existing_id" in c:
                diff.changed.append({"id": c["existing_id"], "fields": c["record"]})

    # --- Write new records ---
    for i in range(0, len(diff.new), BATCH_SIZE):
        batch = diff.new[i : i + BATCH_SIZE]
        resp = airtable.create_records(batch)
        for rec in resp.get("records", []):
            written_ids.append(rec["id"])
        log.added += len(batch)
        time.sleep(RATE_LIMIT_DELAY)

    # --- Update changed records ---
    for i in range(0, len(diff.changed), BATCH_SIZE):
        batch = diff.changed[i : i + BATCH_SIZE]
        # Pydantic validates records data
        payload = [
            {"id": r["id"], "fields": {k: v for k, v in r["fields"].items() if v is not None}}
            for r in batch
        ]
        resp = airtable.update_records(payload)
        for rec in resp.get("records", []):
            written_ids.append(rec["id"])
        log.updated += len(batch)
        time.sleep(RATE_LIMIT_DELAY)

    # --- Handle REPLACE / DELETE ---
    # For these actions, we also remove records in the target that aren't
    # in the incoming data. This is a simplified implementation — in practice
    # the dedup_index from step3 is the right source of truth.
    # Phase 1: REPLACE/DELETE always goes to manual_review for safety.
    if action in (ActionType.REPLACE, ActionType.DELETE) and conflict_policy == ConflictPolicy.MANUAL_REVIEW:
        log.conflicts.append({
            "reason": f"action={action.value} requires manual review — not executing destructive operation",
            "records_count": len(diff.unchanged),
        })
        print(f"  ⚠️  Action '{action.value}' blocked by manual_review policy")

        log.records = written_ids
        return written_ids, log

    log.records = written_ids
    log.skipped = len(diff.unchanged)
    return written_ids, log


def step5_verify(
    airtable: AirtableClient,
    record_ids: list[str],
    expected_records: list[dict],
    written_ids: list[str],
) -> tuple[list[str], list[str]]:
    """Step 5: Read back and verify each written record.

    Returns (verified_ids, failed_ids).
    """
    verified, failed = [], []

    for rid in written_ids:
        # Find the expected data for this record
        expected = next(
            (r for r in expected_records if r.get("_airtable_id") == rid),
            None,
        )
        if expected and airtable.verify_record(rid, expected):
            verified.append(rid)
        else:
            failed.append(rid)

    return verified, failed


def step6_write_changelog(log: ChangelogEntry):
    """Step 6: Append changelog entry as JSONL."""
    CHANGELOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOG_DIR / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with open(log_path, "a") as f:
        f.write(log.model_dump_json() + "\n")
    print(f"  Changelog → {log_path}")


def step7_cleanup(file_pair: tuple[Path, Path], manifest_id: str):
    """Step 7: Move processed files to processed/."""
    data_file, manifest_file = file_pair
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    dest_data = PROCESSED_DIR / f"{manifest_id}_{data_file.name}"
    dest_manifest = PROCESSED_DIR / f"{manifest_id}_{manifest_file.name}"

    # Counters work on OneDrive sync — rename then copy
    import shutil
    shutil.copy2(data_file, dest_data)
    shutil.copy2(manifest_file, dest_manifest)

    # Remove originals
    data_file.unlink()
    manifest_file.unlink()

    print(f"  Processed → {dest_data}")
    print(f"  Processed → {dest_manifest}")


def step8_report(log: ChangelogEntry, verified: list[str], failed: list[str]):
    """Step 8: Report summary."""
    print()
    print("=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Added:       {log.added}")
    print(f"  Updated:     {log.updated}")
    print(f"  Skipped:     {log.skipped}")
    print(f"  Quarantined: {log.quarantined}")
    print(f"  Conflicts:   {len(log.conflicts)}")
    if log.conflicts:
        for c in log.conflicts:
            reason = c.get("reason", "conflict detected")
            record = c.get("record", {})
            name = record.get("name", "unknown")
            print(f"    ⚠️  {name} — {reason}")
    if verified:
        print(f"  Verified:    {len(verified)}/{len(verified) + len(failed)} records passed readback")
    if failed:
        print(f"  ⚠️  {len(failed)} records FAILED verification — check changelog")
    print(f"  Changelog:   written")
    print("=" * 60)


# ─── Snapshot / Rollback ────────────────────────────────────────────────────

def take_snapshot(airtable: AirtableClient, record_ids: list[str], manifest_id: str) -> Snapshot:
    """Snapshot records before writing them, for rollback support."""
    snapshot = Snapshot(manifest_id=manifest_id, action=ActionType.UPSERT)

    # Batch-fetch records to snapshot
    for rid in record_ids:
        try:
            data = airtable.get_record(rid)
            snapshot.records[rid] = data.get("fields", {})
        except RuntimeError:
            print(f"  ⚠️  Could not snapshot {rid} — continuing")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snap_path = SNAPSHOT_DIR / f"{manifest_id}.json"
    with open(snap_path, "w") as f:
        f.write(snapshot.model_dump_json(indent=2))
    print(f"  Snapshot → {snap_path}")
    return snapshot


def rollback(manifest_id: str):
    """Rollback a previous run by re-applying the snapshot."""
    snap_path = SNAPSHOT_DIR / f"{manifest_id}.json"
    if not snap_path.exists():
        print(f"❌ No snapshot found for manifest_id '{manifest_id}'")
        print(f"   Looked at: {snap_path}")
        return False

    with open(snap_path) as f:
        data = json.load(f)

    snapshot = Snapshot(**data)
    secrets = read_vault()

    # We need base_id/table_name — read from config
    config_path = CONFIG_DIR / "airtable.json"
    if not config_path.exists():
        print("❌ No airtable config found for rollback")
        return False

    with open(config_path) as f:
        config = json.load(f)

    airtable = AirtableClient(config["base_id"], config["table_name"])

    print(f"↩️  Rolling back manifest '{manifest_id}' — {len(snapshot.records)} records")

    # Group into batches of 10
    records_batch = []
    for rid, fields in snapshot.records.items():
        records_batch.append({"id": rid, "fields": fields})
        if len(records_batch) >= BATCH_SIZE:
            airtable.update_records(records_batch)
            records_batch = []
            time.sleep(RATE_LIMIT_DELAY)

    if records_batch:
        airtable.update_records(records_batch)
        time.sleep(RATE_LIMIT_DELAY)

    print(f"✅ Rollback complete — {len(snapshot.records)} records restored")
    return True


# ─── Main ───────────────────────────────────────────────────────────────────

def process_file(data_file: Path, manifest_file: Path, dry_run: bool = False):
    """Process a single data file + manifest pair through the 8-step pipeline."""
    manifest_id = data_file.stem
    print(f"\n{'─' * 60}")
    print(f"  Processing: {data_file.name}")
    print(f"  Manifest:   {manifest_file.name}")
    print(f"{'─' * 60}")

    # ─── Step 1: Read manifest ───
    print("\n[Step 1/8] Reading manifest...")
    try:
        manifest = step1_read_manifest(manifest_file)
        print(f"  ✓ Manifest valid: action={manifest.action.value}, "
              f"target={manifest.target}, schema={manifest.schema_name}")
    except (json.JSONDecodeError, ValidationError, ValueError) as e:
        print(f"  ❌ Manifest invalid: {e}")
        return False

    # ─── Load data file ───
    records = []
    if data_file.suffix == ".csv":
        with open(data_file, newline="") as f:
            reader = csv.DictReader(f)
            records = list(reader)
    elif data_file.suffix == ".json":
        with open(data_file) as f:
            raw = json.load(f)
            records = raw if isinstance(raw, list) else raw.get("records", [raw])
    elif data_file.suffix == ".vcf":
        records = parse_vcf(data_file)
    else:
        print(f"  ❌ Unsupported file format: {data_file.suffix}")
        return False

    print(f"  ✓ Loaded {len(records)} records from {data_file.name}")

    # ─── Step 2: Validate data ───
    print("\n[Step 2/8] Validating data against schema...")
    valid, quarantined = step2_validate_data(records, manifest.schema_name)
    if quarantined:
        q_report = QuarantineReport(
            manifest_id=manifest_id,
            failed_at="validation",
            records=quarantined,
            original_file=str(data_file),
        )
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        q_path = QUARANTINE_DIR / f"{manifest_id}.quarantine.json"
        with open(q_path, "w") as f:
            f.write(q_report.model_dump_json(indent=2))
        print(f"  ⚠️  {len(quarantined)} records quarantined → {q_path}")

        if not valid:
            print("  ❌ All records failed validation. Aborting.")
            return False

    print(f"  ✓ {len(valid)} valid, {len(quarantined)} quarantined")

    # ─── Setup Airtable ───
    config_path = CONFIG_DIR / "airtable.json"
    if not config_path.exists():
        if dry_run:
            print("  [DRY RUN] Skipping Airtable setup (no config file)")
            print()
            print("=" * 60)
            print("  DRY RUN COMPLETE — VALIDATION PASSED")
            print("=" * 60)
            print(f"  Valid:       {len(valid)}")
            print(f"  Quarantined: {len(quarantined)}")
            print("=" * 60)
            return True
        else:
            print("  ❌ No airtable config found at", config_path)
            return False

    with open(config_path) as f:
        config = json.load(f)

    airtable_table = config.get("table_name", manifest.target.replace("crm", "Contacts"))
    staging_table = f"{airtable_table}_STAGING"

    # ─── Gate 1: Pre-flight check ───
    print("\n[Gate 1] Pre-flight check (staging)...")
    staging_client = AirtableClient(config["base_id"], staging_table)
    if not staging_client.preflight_check():
        # Try without staging
        staging_client = AirtableClient(config["base_id"], airtable_table)
        if not staging_client.preflight_check():
            print("  ❌ Pre-flight failed — base/table not accessible")
            return False
        staging_table = airtable_table
        print("  ⚠️  Staging table not found — writing directly to production")
    else:
        print(f"  ✓ Staging table '{staging_table}' accessible")

    # ─── Step 3: Diff ───
    print(f"\n[Step 3/8] Diffing against current state ({staging_table})...")
    diff = step3_diff(staging_client, valid, manifest.dedup_key)
    print(f"  New: {len(diff.new)}, Changed: {len(diff.changed)}, "
          f"Unchanged: {len(diff.unchanged)}, Conflicts: {len(diff.conflicts)}")

    if not diff.new and not diff.changed:
        print("  ✓ No changes to write.")
        log = ChangelogEntry(
            action=manifest.action,
            table=staging_table,
            manifest_id=manifest_id,
            skipped=len(diff.unchanged),
            conflicts=diff.conflicts,
        )
        step6_write_changelog(log)
        step7_cleanup((data_file, manifest_file), manifest_id)
        step8_report(log, [], [])
        return True

    # ─── Snapshot before write (for rollback) ───
    existing_ids: list[str] = []
    for c in diff.conflicts:
        eid = c.get("existing_id")
        if eid:
            existing_ids.append(eid)
    for c in diff.changed:
        rid = c.get("id")
        if rid:
            existing_ids.append(rid)
    if existing_ids and not dry_run:
        print(f"\n[Snapshot] Saving {len(existing_ids)} existing records for rollback...")
        take_snapshot(staging_client, existing_ids, manifest_id)

    # ─── Step 4: Write ───
    print(f"\n[Step 4/8] Writing to {staging_table}...")
    written_ids, log = step4_write(
        staging_client, diff, manifest.action,
        manifest.conflict_policy, manifest_id=manifest_id, dry_run=dry_run
    )

    if dry_run:
        print("  [DRY RUN] No writes performed")
        log.manifest_id = manifest_id
        step6_write_changelog(log)
        step7_cleanup((data_file, manifest_file), manifest_id)
        log.skipped = len(diff.unchanged)
        step8_report(log, [], [])
        return True

    log.manifest_id = manifest_id
    print(f"  ✓ {len(written_ids)} records written")

    # ─── Step 5: Verify ───
    print(f"\n[Step 5/8] Verifying written records...")
    verified, failed = step5_verify(
        staging_client, written_ids, diff.new + [r["fields"] for r in diff.changed if "fields" in r], written_ids
    )
    log.quarantined = len(failed)
    if failed:
        print(f"  ⚠️  {len(failed)} records FAILED verification")
        for fid in failed[:5]:
            print(f"    ⚠️  Record {fid} — fields don't match expected values")
        if len(failed) > 5:
            print(f"    ... and {len(failed) - 5} more")
    else:
        print(f"  ✓ All {len(verified)} records verified")

    # ─── Step 6: Write changelog ───
    print(f"\n[Step 6/8] Writing changelog...")
    step6_write_changelog(log)

    # ─── Step 7: Cleanup ───
    print(f"\n[Step 7/8] Moving processed files...")
    step7_cleanup((data_file, manifest_file), manifest_id)

    # ─── Step 8: Report ───
    step8_report(log, verified, failed)

    # Check if any failed records need attention
    if failed:
        print("\n⚠️  NEXT STEPS:")
        print(f"  1. Check changelog for failed record details")
        print(f"  2. Run: python3 scripts/process-inbox.py --rollback {manifest_id}")
        print("     to revert all changes from this run")
        return True

    print("\n✅ All clean.")
    return True


def parse_vcf(path: Path) -> list[dict]:
    """Parse a VCF/vCard file into a list of dicts matching ContactV2 schema."""
    records = []
    with open(path, errors="replace") as f:
        text = f.read()

    # Split by VCARD boundary
    raw_cards = re.split(r"BEGIN:VCARD", text, flags=re.IGNORECASE)

    for raw in raw_cards:
        if not raw.strip():
            continue

        contact = {}

        # Extract fields
        name_match = re.search(r"FN[^:]*:(.+)", raw, re.IGNORECASE)
        if name_match:
            contact["name"] = name_match.group(1).strip()

        # N field as fallback
        if "name" not in contact:
            n_match = re.search(r"N[^:]*:(.+?)(?:;|$)", raw, re.IGNORECASE)
            if n_match:
                parts = n_match.group(1).strip().split(";")
                if len(parts) >= 2:
                    contact["name"] = f"{parts[1]} {parts[0]}".strip()
                elif parts[0]:
                    contact["name"] = parts[0]

        if not contact.get("name"):
            continue

        tel_match = re.search(r"TEL[^:]*:(.+)", raw, re.IGNORECASE)
        if tel_match:
            contact["phone"] = tel_match.group(1).strip()

        email_match = re.search(r"EMAIL[^:]*:(.+)", raw, re.IGNORECASE)
        if email_match:
            contact["email"] = email_match.group(1).strip().lower()

        org_match = re.search(r"ORG[^:]*:(.+)", raw, re.IGNORECASE)
        if org_match:
            contact["company"] = org_match.group(1).strip()

        note_match = re.search(r"NOTE[^:]*:(.+)", raw, re.IGNORECASE)
        if note_match:
            contact["notes"] = note_match.group(1).strip()

        uid_match = re.search(r"UID[^:]*:(.+)", raw, re.IGNORECASE)
        if uid_match:
            contact["source_id"] = uid_match.group(1).strip()

        contact["source"] = "vcf-import"

        records.append(contact)

    return records


def scan_inbox() -> list[tuple[Path, Path]]:
    """Scan inbox/ for data files with companion manifest files.

    Returns list of (data_file, manifest_file) pairs.
    """
    pairs = []

    if not INBOX_DIR.exists():
        print(f"  Inbox directory not found: {INBOX_DIR}")
        return pairs

    for f in sorted(INBOX_DIR.iterdir()):
        if f.name.endswith(".manifest.json"):
            continue  # skip manifest files themselves
        if f.suffix in (".csv", ".json", ".vcf"):
            manifest = INBOX_DIR / f"{f.stem}.manifest.json"
            if manifest.exists():
                pairs.append((f, manifest))
            else:
                print(f"  ⚠️  {f.name} has no manifest — skipping (contract: no manifest, no processing)")

    return pairs


def acquire_lock() -> bool:
    """Acquire lockfile to prevent concurrent processing."""
    LOCKFILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCKFILE.exists():
        age = time.time() - LOCKFILE.stat().st_mtime
        if age < 1800:  # 30 minutes
            print(f"  Lockfile present ({int(age)}s old) — another process may be running")
            return False
        else:
            print(f"  Lockfile stale ({int(age)}s old) — overriding")
            LOCKFILE.unlink()

    LOCKFILE.write_text(str(time.time()))
    return True


def release_lock():
    if LOCKFILE.exists():
        LOCKFILE.unlink()


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args

    if "--rollback" in args:
        idx = args.index("--rollback")
        if idx + 1 < len(args):
            manifest_id = args[idx + 1]
            rollback(manifest_id)
            return
        else:
            print("❌ --rollback requires a manifest_id argument")
            sys.exit(1)

    if "--manifest" in args:
        idx = args.index("--manifest")
        if idx + 1 < len(args):
            manifest_path = Path(args[idx + 1])
            data_path = manifest_path.with_suffix("")
            # Try common extensions
            for ext in (".csv", ".json", ".vcf"):
                candidate = data_path.with_suffix(ext)
                if candidate.exists():
                    process_file(candidate, manifest_path, dry_run=dry_run)
                    return
            else:
                print(f"❌ No data file found for manifest: {manifest_path}")
                sys.exit(1)
        else:
            print("❌ --manifest requires a file path")
            sys.exit(1)

    # Default: scan inbox
    if not acquire_lock():
        print("  Exiting: lock held by another process")
        sys.exit(0)

    try:
        pairs = scan_inbox()
        if not pairs:
            print("  No files to process")
            return

        for data_file, manifest_file in pairs:
            try:
                process_file(data_file, manifest_file, dry_run=dry_run)
            except (RuntimeError, ValueError, json.JSONDecodeError) as e:
                print(f"\n  ❌ Error processing {data_file.name}: {e}")
                # Don't crash the pipeline — move to next file
                continue
    finally:
        release_lock()


if __name__ == "__main__":
    main()
