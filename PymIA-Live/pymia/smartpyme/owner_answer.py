from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


ANSWER_KIND_PENDING_QUESTION = "ANSWER_TO_PENDING_QUESTION"
ANSWER_KIND_CLARIFICATION = "CLARIFICATION"
ANSWER_KIND_CORRECTION = "CORRECTION"
ANSWER_KIND_INSUFFICIENT = "INSUFFICIENT"

ALLOWED_ANSWER_KINDS = (
    ANSWER_KIND_PENDING_QUESTION,
    ANSWER_KIND_CLARIFICATION,
    ANSWER_KIND_CORRECTION,
    ANSWER_KIND_INSUFFICIENT,
)


@dataclass(frozen=True)
class OwnerAnswerRecord:
    answer_id: str
    tenant_id: str
    intake_id: str
    anamnesis_id: str
    investigation_id: str
    question_ref: str
    raw_owner_answer: str
    answer_kind: str
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


def create_owner_answer_record(
    *,
    tenant_id: str,
    intake_id: str,
    anamnesis_id: str,
    investigation_id: str,
    question_ref: str,
    raw_owner_answer: str,
    answer_kind: str = ANSWER_KIND_PENDING_QUESTION,
    metadata: dict[str, Any] | None = None,
) -> OwnerAnswerRecord:
    if answer_kind not in ALLOWED_ANSWER_KINDS:
        raise ValueError(f"answer_kind {answer_kind!r} not in allowed: {ALLOWED_ANSWER_KINDS}")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    return OwnerAnswerRecord(
        answer_id=f"answer_{uuid.uuid4().hex}",
        tenant_id=_required_text(tenant_id, field_name="tenant_id"),
        intake_id=_required_text(intake_id, field_name="intake_id"),
        anamnesis_id=_required_text(anamnesis_id, field_name="anamnesis_id"),
        investigation_id=_required_text(investigation_id, field_name="investigation_id"),
        question_ref=_required_text(question_ref, field_name="question_ref"),
        raw_owner_answer=_required_text(raw_owner_answer, field_name="raw_owner_answer"),
        answer_kind=answer_kind,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "OwnerAnswerRecord",
    "create_owner_answer_record",
    "ANSWER_KIND_PENDING_QUESTION",
    "ANSWER_KIND_CLARIFICATION",
    "ANSWER_KIND_CORRECTION",
    "ANSWER_KIND_INSUFFICIENT",
    "ALLOWED_ANSWER_KINDS",
]
