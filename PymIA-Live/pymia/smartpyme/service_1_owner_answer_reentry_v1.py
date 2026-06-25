from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.smartpyme.owner_answer import (
    ANSWER_KIND_PENDING_QUESTION,
    OwnerAnswerRecord,
    create_owner_answer_record,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    QUESTION_STATUS_PENDING,
    SCHEMA_VERSION as QUESTION_BUNDLE_SCHEMA_VERSION,
    SERVICE_NAME,
    Service1QuestionBundleV1,
    Service1QuestionV1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_ANSWER_REENTRY_V1"

REENTRY_STATUS_ACCEPTED = "ACCEPTED_FOR_REENTRY"
REENTRY_STATUS_BLOCKED = "BLOCKED"

REENTRY_BLOCK_QUESTION_NOT_FOUND = "QUESTION_REF_NOT_FOUND"
REENTRY_BLOCK_QUESTION_NOT_PENDING = "QUESTION_NOT_PENDING"
REENTRY_BLOCK_BUNDLE_SCHEMA_UNSUPPORTED = "QUESTION_BUNDLE_SCHEMA_UNSUPPORTED"


@dataclass(frozen=True)
class Service1OwnerAnswerReentryV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    source_run_id: str
    question_ref: str
    owner_answer_record: OwnerAnswerRecord | None
    selected_question: Service1QuestionV1 | None
    blocked_reason: str | None
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["owner_answer_record"] = (
            self.owner_answer_record.to_dict() if self.owner_answer_record is not None else None
        )
        data["selected_question"] = (
            self.selected_question.to_dict() if self.selected_question is not None else None
        )
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _bundle_to_object(bundle: Service1QuestionBundleV1 | dict[str, Any]) -> Service1QuestionBundleV1:
    if isinstance(bundle, Service1QuestionBundleV1):
        return bundle
    if not isinstance(bundle, dict):
        raise ValueError("question_bundle must be a Service1QuestionBundleV1 or dict")

    if bundle.get("schema_version") != QUESTION_BUNDLE_SCHEMA_VERSION:
        raise ValueError(REENTRY_BLOCK_BUNDLE_SCHEMA_UNSUPPORTED)

    questions = tuple(
        Service1QuestionV1(
            question_ref=_required_text(item.get("question_ref", ""), field_name="question_ref"),
            source=_required_text(item.get("source", ""), field_name="source"),
            text=_required_text(item.get("text", ""), field_name="text"),
            target_ref=str(item.get("target_ref") or ""),
            answer_type=_required_text(item.get("answer_type", ""), field_name="answer_type"),
            required=bool(item.get("required", True)),
            status=_required_text(item.get("status", ""), field_name="status"),
            metadata=dict(item.get("metadata") or {}),
        )
        for item in bundle.get("questions", [])
    )

    return Service1QuestionBundleV1(
        schema_version=_required_text(bundle.get("schema_version", ""), field_name="schema_version"),
        service_name=_required_text(bundle.get("service_name", ""), field_name="service_name"),
        case_id=_required_text(bundle.get("case_id", ""), field_name="case_id"),
        tenant_id=_required_text(bundle.get("tenant_id", ""), field_name="tenant_id"),
        intake_id=_required_text(bundle.get("intake_id", ""), field_name="intake_id"),
        run_id=_required_text(bundle.get("run_id", ""), field_name="run_id"),
        questions=questions,
        selected_next_question_ref=bundle.get("selected_next_question_ref"),
        runtime_authorized=bool(bundle.get("runtime_authorized", False)),
        human_review_required=bool(bundle.get("human_review_required", True)),
        created_at=_required_text(bundle.get("created_at", ""), field_name="created_at"),
        metadata=dict(bundle.get("metadata") or {}),
    )


def _find_question(bundle: Service1QuestionBundleV1, question_ref: str) -> Service1QuestionV1 | None:
    for question in bundle.questions:
        if question.question_ref == question_ref:
            return question
    return None


def _blocked_packet(
    *,
    bundle: Service1QuestionBundleV1,
    question_ref: str,
    selected_question: Service1QuestionV1 | None,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1OwnerAnswerReentryV1:
    return Service1OwnerAnswerReentryV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=REENTRY_STATUS_BLOCKED,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        source_run_id=bundle.run_id,
        question_ref=question_ref,
        owner_answer_record=None,
        selected_question=selected_question,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def bind_owner_answer_for_service_1_reentry_v1(
    *,
    question_bundle: Service1QuestionBundleV1 | dict[str, Any],
    question_ref: str,
    raw_owner_answer: str,
    anamnesis_id: str,
    investigation_id: str,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerAnswerReentryV1:
    """Validate a pending Servicio 1 question and bind an owner answer to it.

    This function deliberately stops before reexecution/recalculation. It creates
    a reentry packet that future slices can consume without treating owner text as
    validated evidence or as authorization for runtime delivery.
    """

    bundle = _bundle_to_object(question_bundle)
    question_ref = _required_text(question_ref, field_name="question_ref")
    raw_owner_answer = _required_text(raw_owner_answer, field_name="raw_owner_answer")

    selected_question = _find_question(bundle, question_ref)
    if selected_question is None:
        return _blocked_packet(
            bundle=bundle,
            question_ref=question_ref,
            selected_question=None,
            blocked_reason=REENTRY_BLOCK_QUESTION_NOT_FOUND,
            metadata=metadata,
        )

    if selected_question.status != QUESTION_STATUS_PENDING:
        return _blocked_packet(
            bundle=bundle,
            question_ref=question_ref,
            selected_question=selected_question,
            blocked_reason=REENTRY_BLOCK_QUESTION_NOT_PENDING,
            metadata=metadata,
        )

    answer_metadata = {
        "service_1_reentry_schema_version": SCHEMA_VERSION,
        "case_id": bundle.case_id,
        "source_run_id": bundle.run_id,
        "question_source": selected_question.source,
        "question_target_ref": selected_question.target_ref,
        "question_answer_type": selected_question.answer_type,
        "question_text": selected_question.text,
        "owner_answer_validation_status": "DECLARED_NOT_VALIDATED",
        "reexecution_authorized": False,
        "recalculation_authorized": False,
    }
    answer_metadata.update(dict(metadata or {}))

    owner_answer_record = create_owner_answer_record(
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        anamnesis_id=_required_text(anamnesis_id, field_name="anamnesis_id"),
        investigation_id=_required_text(investigation_id, field_name="investigation_id"),
        question_ref=question_ref,
        raw_owner_answer=raw_owner_answer,
        answer_kind=ANSWER_KIND_PENDING_QUESTION,
        metadata=answer_metadata,
    )

    return Service1OwnerAnswerReentryV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=REENTRY_STATUS_ACCEPTED,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        source_run_id=bundle.run_id,
        question_ref=question_ref,
        owner_answer_record=owner_answer_record,
        selected_question=selected_question,
        blocked_reason=None,
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "REENTRY_STATUS_ACCEPTED",
    "REENTRY_STATUS_BLOCKED",
    "REENTRY_BLOCK_QUESTION_NOT_FOUND",
    "REENTRY_BLOCK_QUESTION_NOT_PENDING",
    "REENTRY_BLOCK_BUNDLE_SCHEMA_UNSUPPORTED",
    "Service1OwnerAnswerReentryV1",
    "bind_owner_answer_for_service_1_reentry_v1",
]
