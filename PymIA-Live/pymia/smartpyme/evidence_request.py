from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


EVIDENCE_REQUEST_STATUS_OPEN = "OPEN"
EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD = "WAITING_UPLOAD"
EVIDENCE_REQUEST_STATUS_FULFILLED = "FULFILLED"
EVIDENCE_REQUEST_STATUS_CANCELLED = "CANCELLED"
EVIDENCE_REQUEST_STATUS_BLOCKED = "BLOCKED"

ALLOWED_EVIDENCE_REQUEST_STATUSES = (
    EVIDENCE_REQUEST_STATUS_OPEN,
    EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD,
    EVIDENCE_REQUEST_STATUS_FULFILLED,
    EVIDENCE_REQUEST_STATUS_CANCELLED,
    EVIDENCE_REQUEST_STATUS_BLOCKED,
)


@dataclass(frozen=True)
class EvidenceRequestRecord:
    request_id: str
    tenant_id: str
    intake_id: str
    anamnesis_id: str
    investigation_id: str
    owner_answer_id: str | None
    requested_evidence: list[str]
    request_reason: str
    status: str
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _optional_text(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string or None")
    normalized = value.strip()
    return normalized or None


def _required_string_list(value: list[str], *, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a non-empty list of strings")
    copied: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} items must be strings")
        normalized = item.strip()
        if normalized:
            copied.append(normalized)
    if not copied:
        raise ValueError(f"{field_name} must be a non-empty list of strings")
    return copied


def create_evidence_request_record(
    *,
    tenant_id: str,
    intake_id: str,
    anamnesis_id: str,
    investigation_id: str,
    requested_evidence: list[str],
    request_reason: str,
    owner_answer_id: str | None = None,
    status: str = EVIDENCE_REQUEST_STATUS_OPEN,
    metadata: dict[str, Any] | None = None,
) -> EvidenceRequestRecord:
    if status not in ALLOWED_EVIDENCE_REQUEST_STATUSES:
        raise ValueError(f"status {status!r} not in allowed: {ALLOWED_EVIDENCE_REQUEST_STATUSES}")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    return EvidenceRequestRecord(
        request_id=f"evidence_request_{uuid.uuid4().hex}",
        tenant_id=_required_text(tenant_id, field_name="tenant_id"),
        intake_id=_required_text(intake_id, field_name="intake_id"),
        anamnesis_id=_required_text(anamnesis_id, field_name="anamnesis_id"),
        investigation_id=_required_text(investigation_id, field_name="investigation_id"),
        owner_answer_id=_optional_text(owner_answer_id, field_name="owner_answer_id"),
        requested_evidence=_required_string_list(requested_evidence, field_name="requested_evidence"),
        request_reason=_required_text(request_reason, field_name="request_reason"),
        status=status,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "EvidenceRequestRecord",
    "create_evidence_request_record",
    "EVIDENCE_REQUEST_STATUS_OPEN",
    "EVIDENCE_REQUEST_STATUS_WAITING_UPLOAD",
    "EVIDENCE_REQUEST_STATUS_FULFILLED",
    "EVIDENCE_REQUEST_STATUS_CANCELLED",
    "EVIDENCE_REQUEST_STATUS_BLOCKED",
    "ALLOWED_EVIDENCE_REQUEST_STATUSES",
]
