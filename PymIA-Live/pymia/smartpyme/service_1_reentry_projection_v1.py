from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.smartpyme.service_1_case_reentry_read_model_v1 import (
    Service1CaseReentryReadModelV1,
    Service1ReentryAnswerViewV1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    SERVICE_NAME,
    Service1QuestionBundleV1,
    Service1QuestionV1,
)

SCHEMA_VERSION = "SERVICE_1_REENTRY_PROJECTION_V1"

PROJECTION_STATUS_NO_QUESTIONS = "NO_QUESTIONS"
PROJECTION_STATUS_NO_ANSWERS = "NO_ANSWERS"
PROJECTION_STATUS_PARTIAL = "PARTIAL"
PROJECTION_STATUS_COMPLETE = "COMPLETE"
PROJECTION_STATUS_BLOCKED = "BLOCKED"

PROJECTION_BLOCK_CASE_MISMATCH = "CASE_MISMATCH"


@dataclass(frozen=True)
class Service1ProjectedQuestionV1:
    question_ref: str
    source: str
    text: str
    target_ref: str
    answer_type: str
    required: bool
    original_status: str
    projection_status: str
    latest_answer_id: str | None
    latest_raw_owner_answer: str | None
    owner_answer_validation_status: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ReentryProjectionV1:
    schema_version: str
    service_name: str
    status: str
    blocked_reason: str | None
    case_id: str
    tenant_id: str
    intake_id: str
    source_run_id: str
    read_model_status: str
    total_questions: int
    answered_count: int
    pending_count: int
    answered_question_refs: tuple[str, ...]
    pending_question_refs: tuple[str, ...]
    selected_next_pending_question_ref: str | None
    answered_questions: tuple[Service1ProjectedQuestionV1, ...]
    pending_questions: tuple[Service1ProjectedQuestionV1, ...]
    runtime_authorized: bool
    human_review_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["answered_question_refs"] = list(self.answered_question_refs)
        data["pending_question_refs"] = list(self.pending_question_refs)
        data["answered_questions"] = [question.to_dict() for question in self.answered_questions]
        data["pending_questions"] = [question.to_dict() for question in self.pending_questions]
        return data


def _latest_answers_by_question_ref(
    answers: tuple[Service1ReentryAnswerViewV1, ...]
) -> dict[str, Service1ReentryAnswerViewV1]:
    latest: dict[str, Service1ReentryAnswerViewV1] = {}
    for answer in answers:
        latest[answer.question_ref] = answer
    return latest


def _project_question(
    question: Service1QuestionV1,
    latest_answer: Service1ReentryAnswerViewV1 | None,
) -> Service1ProjectedQuestionV1:
    is_answered = latest_answer is not None
    return Service1ProjectedQuestionV1(
        question_ref=question.question_ref,
        source=question.source,
        text=question.text,
        target_ref=question.target_ref,
        answer_type=question.answer_type,
        required=question.required,
        original_status=question.status,
        projection_status="ANSWERED" if is_answered else "PENDING",
        latest_answer_id=latest_answer.answer_id if latest_answer else None,
        latest_raw_owner_answer=latest_answer.raw_owner_answer if latest_answer else None,
        owner_answer_validation_status=(
            latest_answer.owner_answer_validation_status if latest_answer else None
        ),
        metadata=dict(question.metadata),
    )


def _status_for_counts(total_questions: int, answered_count: int) -> str:
    if total_questions == 0:
        return PROJECTION_STATUS_NO_QUESTIONS
    if answered_count == 0:
        return PROJECTION_STATUS_NO_ANSWERS
    if answered_count == total_questions:
        return PROJECTION_STATUS_COMPLETE
    return PROJECTION_STATUS_PARTIAL


def _blocked_projection(
    *,
    question_bundle: Service1QuestionBundleV1,
    read_model: Service1CaseReentryReadModelV1,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1ReentryProjectionV1:
    return Service1ReentryProjectionV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=PROJECTION_STATUS_BLOCKED,
        blocked_reason=blocked_reason,
        case_id=question_bundle.case_id,
        tenant_id=question_bundle.tenant_id,
        intake_id=question_bundle.intake_id,
        source_run_id=question_bundle.run_id,
        read_model_status=read_model.status,
        total_questions=len(question_bundle.questions),
        answered_count=0,
        pending_count=len(question_bundle.questions),
        answered_question_refs=(),
        pending_question_refs=tuple(question.question_ref for question in question_bundle.questions),
        selected_next_pending_question_ref=question_bundle.selected_next_question_ref,
        answered_questions=(),
        pending_questions=tuple(
            _project_question(question, None) for question in question_bundle.questions
        ),
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata=dict(metadata or {}),
    )


def project_service_1_reentry_v1(
    *,
    question_bundle: Service1QuestionBundleV1,
    read_model: Service1CaseReentryReadModelV1,
    metadata: dict[str, Any] | None = None,
) -> Service1ReentryProjectionV1:
    """Project answered and pending Servicio 1 questions.

    This function is pure. It does not write storage, re-run pipelines,
    recalculate evidence, apply column confirmation, or generate new questions.
    """

    if not isinstance(question_bundle, Service1QuestionBundleV1):
        raise ValueError("question_bundle must be Service1QuestionBundleV1")
    if not isinstance(read_model, Service1CaseReentryReadModelV1):
        raise ValueError("read_model must be Service1CaseReentryReadModelV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    if question_bundle.tenant_id != read_model.tenant_id or question_bundle.intake_id != read_model.intake_id:
        return _blocked_projection(
            question_bundle=question_bundle,
            read_model=read_model,
            blocked_reason=PROJECTION_BLOCK_CASE_MISMATCH,
            metadata=metadata,
        )

    latest_answer_by_ref = _latest_answers_by_question_ref(read_model.answers)
    answered_questions: list[Service1ProjectedQuestionV1] = []
    pending_questions: list[Service1ProjectedQuestionV1] = []

    for question in question_bundle.questions:
        projected = _project_question(question, latest_answer_by_ref.get(question.question_ref))
        if projected.projection_status == "ANSWERED":
            answered_questions.append(projected)
        else:
            pending_questions.append(projected)

    answered_question_refs = tuple(question.question_ref for question in answered_questions)
    pending_question_refs = tuple(question.question_ref for question in pending_questions)
    selected_next_pending_question_ref = pending_question_refs[0] if pending_question_refs else None

    status = _status_for_counts(
        total_questions=len(question_bundle.questions),
        answered_count=len(answered_questions),
    )

    return Service1ReentryProjectionV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        blocked_reason=None,
        case_id=question_bundle.case_id,
        tenant_id=question_bundle.tenant_id,
        intake_id=question_bundle.intake_id,
        source_run_id=question_bundle.run_id,
        read_model_status=read_model.status,
        total_questions=len(question_bundle.questions),
        answered_count=len(answered_questions),
        pending_count=len(pending_questions),
        answered_question_refs=answered_question_refs,
        pending_question_refs=pending_question_refs,
        selected_next_pending_question_ref=selected_next_pending_question_ref,
        answered_questions=tuple(answered_questions),
        pending_questions=tuple(pending_questions),
        runtime_authorized=False,
        human_review_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "PROJECTION_STATUS_NO_QUESTIONS",
    "PROJECTION_STATUS_NO_ANSWERS",
    "PROJECTION_STATUS_PARTIAL",
    "PROJECTION_STATUS_COMPLETE",
    "PROJECTION_STATUS_BLOCKED",
    "PROJECTION_BLOCK_CASE_MISMATCH",
    "Service1ProjectedQuestionV1",
    "Service1ReentryProjectionV1",
    "project_service_1_reentry_v1",
]
