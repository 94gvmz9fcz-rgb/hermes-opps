"""
Pydantic models for the JStew data pipeline.

Every data file that enters the system must validate against one of these models
before it touches Airtable or any other external system.

Usage:
    from models.airtable_crm import ContactV2
    c = ContactV2(name="Josh Stewart", phone="+14155551234")
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# ─── Phone Validation ───────────────────────────────────────────────────────

PHONE_RE = re.compile(r"^\+?\d{7,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ─── Contact (CRM) ──────────────────────────────────────────────────────────

class ContactV2(BaseModel):
    """Canonical contact record for the Jermy CRM.

    Every contact that enters the system must validate against this model.
    Fields that are set to None will be skipped during writes (not overwritten).
    """

    name: str = Field(..., min_length=1, description="Contact full name (required)")
    phone: Optional[str] = Field(None, description="Phone number with optional + prefix")
    email: Optional[str] = Field(None, description="Email address")
    company: Optional[str] = Field(None, description="Company or organization")
    notes: Optional[str] = Field(None, description="Free-text notes")
    source: Optional[str] = Field(
        None, description="Origin of this record (e.g. 'biz-card-scan', 'vcf-import')"
    )
    source_id: Optional[str] = Field(
        None, description="External ID from the source system (e.g. vcard UID)"
    )
    imported_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when this record entered the pipeline",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            cleaned = v.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace(".", "")
            if not PHONE_RE.match(cleaned):
                raise ValueError(
                    f"Invalid phone format: '{v}'. Expected 7-15 digits, optionally starting with +"
                )
            return cleaned
        return None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            if not EMAIL_RE.match(v.strip()):
                raise ValueError(f"Invalid email format: '{v}'")
            return v.strip().lower()
        return None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("name cannot be empty or whitespace-only")
        return stripped

    @model_validator(mode="after")
    def check_minimum_data(self) -> "ContactV2":
        """At least name is required. Everything else is optional but validated if present."""
        return self


# ─── Dedup / Conflict Resolution ────────────────────────────────────────────

class ConflictPolicy(str, Enum):
    """What to do when the dedup key matches an existing record with different data."""
    MANUAL_REVIEW = "manual_review"   # Phase 1 default — JStew decides
    SKIP = "skip"                     # Keep existing, don't write
    OVERWRITE = "overwrite"           # Replace with incoming data


class ActionType(str, Enum):
    UPSERT = "upsert"
    REPLACE = "replace"
    DELETE = "delete"


# ─── Manifest ───────────────────────────────────────────────────────────────

class ManifestV1(BaseModel):
    """Parsed manifest.json sidecar file.

    Every file in inbox/ must have a companion manifest.json.
    """

    version: str = Field(..., pattern=r"^\d+\.\d+$")
    source: str = Field(..., min_length=1)
    collected_at: str = Field(
        ..., description="ISO 8601 UTC timestamp of when data was collected"
    )
    action: ActionType
    target: str = Field(..., min_length=1)
    schema_name: str = Field(..., min_length=1, alias="schema")
    dedup_key: list[str] = Field(
        default_factory=lambda: ["name"],
        description="Fields to use for dedup detection. Composite keys supported.",
    )
    conflict_policy: ConflictPolicy = ConflictPolicy.MANUAL_REVIEW
    error_policy: dict = Field(
        default_factory=lambda: {"max_retries": 3, "quarantine_threshold": 5}
    )

    @field_validator("collected_at")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(
                f"Invalid timestamp format: '{v}'. Expected ISO 8601 (e.g. 2026-06-23T14:30:00Z)"
            )
        return v


# ─── Changelog ──────────────────────────────────────────────────────────────

class ChangelogEntry(BaseModel):
    """One entry in the append-only changelog (JSONL)."""

    ts: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    action: ActionType
    table: str
    manifest_id: str = Field(..., min_length=1)
    added: int = 0
    updated: int = 0
    skipped: int = 0
    quarantined: int = 0
    records: list[str] = Field(default_factory=list)
    conflicts: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# ─── Quarantine Report ──────────────────────────────────────────────────────

class QuarantineReport(BaseModel):
    """Written to OneDrive/Hermy/quarantine/ when records fail validation."""

    manifest_id: str
    failed_at: str = Field(..., description="pipeline step: validation|write|verify")
    records: list[dict] = Field(
        ..., description="list of {index, record, errors}"
    )
    original_file: str


# ─── Diff Result ────────────────────────────────────────────────────────────

class DiffResult(BaseModel):
    """Result of comparing incoming data against current Airtable state."""

    new: list[dict] = Field(default_factory=list)
    changed: list[dict] = Field(default_factory=list)
    unchanged: list[dict] = Field(default_factory=list)
    conflicts: list[dict] = Field(
        default_factory=list,
        description="Records where dedup key matches but data differs — needs resolution",
    )


# ─── Staging Replica ────────────────────────────────────────────────────────

class StagingReplica(BaseModel):
    """Tracks a batch of records landed in the staging table."""

    manifest_id: str
    table: str
    record_ids: list[str]
    written_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    verified: bool = False
    promoted: bool = False


# ─── Snapshot (for rollback) ────────────────────────────────────────────────

class Snapshot(BaseModel):
    """Before/after snapshot for rollback support."""

    manifest_id: str
    action: ActionType
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    records: dict[str, dict] = Field(
        default_factory=dict,
        description="Map of Airtable record ID -> pre-write field values",
    )
