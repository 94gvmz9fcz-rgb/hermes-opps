# Data Pipeline Contract

## The Iron-Clad Rule

> **One channel. One format. One handler.**

There is exactly one way data enters the JStew system:
- **Channel:** `OneDrive/Hermy/inbox/`
- **Format:** Data file + `manifest.json` sidecar
- **Handler:** `process-inbox` (single entry point)

If the manifest is missing, the handler pauses and asks — it never guesses.

---

## Manifest Format (v1.0)

Every data file in `inbox/` **must** have a companion manifest.json with the same basename:

```
inbox/biz-cards-june-23.csv
inbox/biz-cards-june-23.manifest.json
```

### Schema

```json
{
  "version": "1.0",
  "source": "meetup-scanner-v2",
  "collected_at": "2026-06-23T14:30:00Z",
  "action": "upsert",
  "target": "crm",
  "schema": "contacts-v2",
  "dedup_key": ["name"],
  "conflict_policy": "manual_review",
  "error_policy": {
    "max_retries": 3,
    "quarantine_threshold": 5
  }
}
```

### Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| `version` | ✅ | `"1.0"` | Manifest schema version. Pinned for future-proofing. |
| `source` | ✅ | free string | What system/person generated this data. Enables traceability. |
| `collected_at` | ✅ | ISO 8601 UTC | When the data was collected (not when it was dropped in inbox). |
| `action` | ✅ | `"upsert"`, `"replace"`, `"delete"` | What to do with matching records. |
| `target` | ✅ | `"crm"`, `"contacts"`, `"notes"` | Which external system this targets. |
| `schema_name` | ✅ | `"contacts-v2"` | Which Pydantic model to validate against. |
| `dedup_key` | ✅ | `["name"]` or `["name","email"]` | Fields used to detect existing records. Composite keys supported. |
| `conflict_policy` | ✅ | `"manual_review"`, `"skip"`, `"overwrite"` | What to do when the dedup key matches an existing record with *different* data. Phase 1: always `manual_review`. |
| `error_policy` | ❌ | object with `max_retries` and `quarantine_threshold` | Retry behavior and how many failures before a file goes to quarantine instead of crashing. |

### Supported Data File Formats

| Format | Extension | Parser |
|--------|-----------|--------|
| CSV | `.csv` | `csv.DictReader` |
| JSON array | `.json` | `json.load()` |
| VCF/vCard | `.vcf` | `vobject` or manual regex |

---

## The 8-Step Pipeline

Every inbound file goes through this exact sequence. No skipping, no shortcutting.

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Read manifest → know target, schema, dedup, action │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Validate data against Pydantic schema → fail fast   │
├─────────────────────────────────────────────────────────────┤
│  Step 3: GET current state from target → diff against what   │
│            already exists                                    │
├─────────────────────────────────────────────────────────────┤
│  Step 4: Write only new/changed records (skip identical)     │
├─────────────────────────────────────────────────────────────┤
│  Step 5: Read back each written record → verify fields match │
├─────────────────────────────────────────────────────────────┤
│  Step 6: Write changelog entry (manifest_id, action, diff)   │
├─────────────────────────────────────────────────────────────┤
│  Step 7: Move processed files → OneDrive/Hermy/processed/    │
├─────────────────────────────────────────────────────────────┤
│  Step 8: Report — "Added 12, updated 3, quarantined 1"      │
└─────────────────────────────────────────────────────────────┘
```

### Gate 1: Pre-Flight
Before writing a single byte:
- Verify the target (Airtable base, table) exists and the token has permission
- Verify the manifest is parseable and the schema name maps to a known Pydantic model
- If either fails → **STOP**. Report the issue. Do not proceed.

### Gate 2: Post-Write Verification
After every write:
- GET the written record by ID
- Compare every field against what was sent
- If any field differs → **FLAG**. Write a changelog warning. Do not suppress.

---

## Schema Enforcement

Data must validate against the declared Pydantic model before touching Airtable.

```python
from models.airtable_crm import ContactV2

def validate(records: list[dict], schema_name: str) -> tuple[list[dict], list[dict]]:
    """Returns (valid_records, quarantined_records)."""
    models = {"contacts-v2": ContactV2}
    Model = models[schema_name]  # fails fast if unknown
    good, bad = [], []
    for i, rec in enumerate(records):
        try:
            validated = Model(**rec)
            good.append(validated.model_dump())
        except ValidationError as e:
            bad.append({"index": i, "record": rec, "errors": e.errors()})
    return good, bad
```

On validation failure, records are **quarantined** — not silently dropped. The quarantine file goes to `OneDrive/Hermy/quarantine/<basename>.quarantine.json`.

---

## Error Quarantine

Records that fail any step of the pipeline go to `OneDrive/Hermy/quarantine/`:

```json
{
  "manifest_id": "biz-cards-june-23",
  "failed_at": "validation",
  "records": [
    {"index": 4, "record": {"name": "", "phone": "abc"}, "errors": ["name: field required", "phone: invalid format"]}
  ],
  "original_file": "inbox/biz-cards-june-23.csv"
}
```

The handler reports "N records quarantined" in its summary. JStew reviews quarantine files and either fixes the data or overrides the schema.

---

## Changelog

Every write operation produces a changelog entry. Written as JSONL (newline-delimited JSON) to `OneDrive/Hermy/changelog/` and/or an Airtable log table.

```json
{"ts": "2026-06-23T15:00:00Z", "action": "upsert", "table": "Contacts", "manifest_id": "biz-cards-june-23", "added": 12, "updated": 3, "quarantined": 1, "records": ["recA1b2c3", "recD4e5f6"]}
```

### Why JSONL
- Append-only — no risk of corrupting existing entries
- Easy to tail, grep, or load into a spreadsheet
- Survives network failures (last entry may be truncated, not corrupted)

---

## Rollback Strategy

If a write corrupts data, rollback works like this:

1. **Before any write**, snapshot affected records:
   ```python
   snapshot = airtable.get_records(record_ids)
   # Store in OneDrive/Hermy/snapshots/<manifest_id>.json
   ```

2. **To rollback**, re-apply the snapshot:
   ```bash
   process-inbox.py --rollback <manifest_id>
   ```
   This reads the snapshot, writes the original values back, and logs the rollback in the changelog.

3. **For destructive actions** (replace, delete), the handler prompts JStew for confirmation first.

---

## Staging Environment

All writes go through a staging table first:

| Table | Purpose |
|-------|---------|
| `Contacts_STAGING` | Write target for process-inbox |
| `Contacts` | Production table, promoted from staging |

### Promotion Protocol
1. Handler writes to `_STAGING` table
2. Read back and verify records in staging
3. Diff staging against production
4. **If all checks pass →** copy staging records to production
5. **If any check fails →** quarantine the batch, alert JStew

This is implemented as a two-step write: staging first, then promotion. If promotion fails, staging still has the data — nothing is lost.

---

## Rate Limiting

Airtable's free tier limits:
- 5 requests per second per base
- 100,000 records per base

**Handler behavior:**
- Batch writes: 10 records per API call (Airtable batch limit)
- 0.3s delay between batches (stays well under the 5req/s limit)
- Exponential backoff on 429 responses: 1s → 2s → 4s → 8s → report failure
- All rate limiting is logged so JStew can see it happening

---

## File Locking

Concurrent inbox processing is prevented via lockfile:

```
OneDrive/Hermy/inbox/.process-inbox.lock
```

If the lockfile exists and is less than 30 minutes old, the handler exits without processing. If older than 30 minutes, it's treated as stale and processing proceeds.

---

## Summary: The Contract

> **No manifest → No processing.**
> **No validation → No write.**
> **No verification → No report.**
> **No changelog → It didn't happen.**
