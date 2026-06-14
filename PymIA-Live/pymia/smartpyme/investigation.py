from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from typing import Any


INVESTIGATION_STATUS_OPEN = "OPEN"
INVESTIGATION_STATUS_WAITING_EVIDENCE = "WAITING_EVIDENCE"
INVESTIGATION_STATUS_READY_FOR_CONTRAST = "READY_FOR_CONTRAST"
INVESTIGATION_STATUS_REPORTED = "REPORTED"
INVESTIGATION_STATUS_CLOSED = "CLOSED"
INVESTIGATION_STATUS_BLOCKED = "BLOCKED"

ALLOWED_INVESTIGATION_STATUSES = (
    INVESTIGATION_STATUS_OPEN,
    INVESTIGATION_STATUS_WAITING_EVIDENCE,
    INVESTIGATION_STATUS_READY_FOR_CONTRAST,
    INVESTIGATION_STATUS_REPORTED,
    INVESTIGATION_STATUS_CLOSED,
    INVESTIGATION_STATUS_BLOCKED,
)


@dataclass(frozen=True)
class InvestigationRecord:
    investigation_id: str
    tenant_id: str
    intake_id: str
    anamnesis_id: str
    owner_prompt: str
    investigation_axis: str
    declared_question: str
    status: str
    evidence_required: list[str] = field(default_factory=list)
    pathology_candidates: list[str] = field(default_factory=list)
    formula_candidates: list[str] = field(default_factory=list)
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _copy_string_list(value: list[str] | None, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list or None")
    copied: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} items must be strings")
        normalized = item.strip()
        if normalized:
            copied.append(normalized)
    return copied


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def create_investigation_record(
    *,
    tenant_id: str,
    intake_id: str,
    anamnesis_id: str,
    owner_prompt: str,
    investigation_axis: str = "desconocido",
    declared_question: str = "",
    status: str = INVESTIGATION_STATUS_OPEN,
    evidence_required: list[str] | None = None,
    pathology_candidates: list[str] | None = None,
    formula_candidates: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> InvestigationRecord:
    if status not in ALLOWED_INVESTIGATION_STATUSES:
        raise ValueError(f"status {status!r} not in allowed: {ALLOWED_INVESTIGATION_STATUSES}")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    normalized_owner_prompt = _required_text(owner_prompt, field_name="owner_prompt")
    normalized_declared_question = declared_question.strip() if isinstance(declared_question, str) and declared_question.strip() else normalized_owner_prompt

    return InvestigationRecord(
        investigation_id=f"investigation_{uuid.uuid4().hex}",
        tenant_id=_required_text(tenant_id, field_name="tenant_id"),
        intake_id=_required_text(intake_id, field_name="intake_id"),
        anamnesis_id=_required_text(anamnesis_id, field_name="anamnesis_id"),
        owner_prompt=normalized_owner_prompt,
        investigation_axis=_required_text(investigation_axis, field_name="investigation_axis"),
        declared_question=normalized_declared_question,
        status=status,
        evidence_required=_copy_string_list(evidence_required, field_name="evidence_required"),
        pathology_candidates=_copy_string_list(pathology_candidates, field_name="pathology_candidates"),
        formula_candidates=_copy_string_list(formula_candidates, field_name="formula_candidates"),
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def derive_investigation_status_from_evidence_request(
    investigation: InvestigationRecord,
    evidence_request: dict[str, Any],
) -> InvestigationRecord:
    if not isinstance(investigation, InvestigationRecord):
        raise ValueError("investigation must be an InvestigationRecord")
    if not isinstance(evidence_request, dict):
        raise ValueError("evidence_request must be a dict")
    if evidence_request.get("tenant_id") != investigation.tenant_id:
        raise ValueError("evidence_request tenant_id does not match investigation")
    if evidence_request.get("intake_id") != investigation.intake_id:
        raise ValueError("evidence_request intake_id does not match investigation")
    if evidence_request.get("investigation_id") != investigation.investigation_id:
        raise ValueError("evidence_request investigation_id does not match investigation")

    request_status = evidence_request.get("status")
    if request_status == "FULFILLED":
        next_status = INVESTIGATION_STATUS_READY_FOR_CONTRAST
    elif request_status in {"OPEN", "WAITING_UPLOAD"}:
        next_status = INVESTIGATION_STATUS_WAITING_EVIDENCE
    elif request_status in {"CANCELLED", "BLOCKED"}:
        next_status = INVESTIGATION_STATUS_BLOCKED
    else:
        raise ValueError("evidence_request status is not supported")

    metadata = dict(investigation.metadata)
    metadata["evidence_request_id"] = evidence_request.get("request_id")
    metadata["evidence_request_status"] = request_status
    return replace(investigation, status=next_status, metadata=metadata)


__all__ = [
    "InvestigationRecord",
    "create_investigation_record",
    "derive_investigation_status_from_evidence_request",
    "INVESTIGATION_STATUS_OPEN",
    "INVESTIGATION_STATUS_WAITING_EVIDENCE",
    "INVESTIGATION_STATUS_READY_FOR_CONTRAST",
    "INVESTIGATION_STATUS_REPORTED",
    "INVESTIGATION_STATUS_CLOSED",
    "INVESTIGATION_STATUS_BLOCKED",
    "ALLOWED_INVESTIGATION_STATUSES",
]
