from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.smartpyme.service_1_question_bundle_v1 import (
    ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
    SERVICE_NAME,
    SOURCE_COLUMN_CONFIRMATION,
)
from pymia.smartpyme.service_1_reentry_projection_v1 import Service1ProjectedQuestionV1

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_REENTRY_CANDIDATE_V1"

STATUS_READY_FOR_CLASSIFIER = "READY_FOR_CLASSIFIER"
STATUS_BLOCKED = "BLOCKED"

BLOCK_QUESTION_SOURCE_UNSUPPORTED = "QUESTION_SOURCE_UNSUPPORTED"
BLOCK_ANSWER_TYPE_UNSUPPORTED = "ANSWER_TYPE_UNSUPPORTED"
BLOCK_QUESTION_NOT_ANSWERED = "QUESTION_NOT_ANSWERED"
BLOCK_RAW_OWNER_ANSWER_MISSING = "RAW_OWNER_ANSWER_MISSING"
BLOCK_TARGET_REF_INVALID = "TARGET_REF_INVALID"
BLOCK_ROLE_MISSING = "ROLE_MISSING"
BLOCK_OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED = "OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED"

OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED = "DECLARED_NOT_VALIDATED"

PROJECTION_STATUS_ANSWERED = "ANSWERED"


@dataclass(frozen=True)
class ColumnConfirmationTargetRefV1:
    file_name: str
    sheet_name: str
    column_name: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnConfirmationReentryCandidateV1:
    schema_version: str
    service_name: str
    status: str
    blocked_reason: str | None
    question_ref: str
    question_source: str
    target_ref: str | None
    parsed_target_ref: ColumnConfirmationTargetRefV1 | None
    answer_type: str
    raw_owner_answer: str | None
    proposed_role: str | None
    owner_answer_validation_status: str | None
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["parsed_target_ref"] = (
            self.parsed_target_ref.to_dict() if self.parsed_target_ref else None
        )
        return data


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _optional_text(value: str | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value).strip()
    return value.strip()


def _normalize_role(
    *,
    proposed_role: str | None,
    suggested_semantic_role: str | None,
) -> str:
    return _optional_text(proposed_role) or _optional_text(suggested_semantic_role)


def _parse_target_ref(target_ref: str) -> ColumnConfirmationTargetRefV1:
    target_ref = _required_text(target_ref, field_name="target_ref")

    file_prefix = "file:"
    sheet_marker = ":sheet:"
    column_marker = ":column:"

    if not target_ref.startswith(file_prefix):
        raise ValueError("target_ref must start with file:")
    if sheet_marker not in target_ref or column_marker not in target_ref:
        raise ValueError("target_ref must contain :sheet: and :column: segments")

    file_start = len(file_prefix)
    sheet_start = target_ref.index(sheet_marker)
    column_start = target_ref.index(column_marker, sheet_start + len(sheet_marker))

    file_name = target_ref[file_start:sheet_start].strip()
    sheet_name = target_ref[sheet_start + len(sheet_marker):column_start].strip()
    column_name = target_ref[column_start + len(column_marker):].strip()

    if not file_name or not sheet_name or not column_name:
        raise ValueError("target_ref file_name, sheet_name, and column_name are required")

    return ColumnConfirmationTargetRefV1(
        file_name=file_name,
        sheet_name=sheet_name,
        column_name=column_name,
    )


def _base_packet(
    *,
    projected_question: Service1ProjectedQuestionV1,
    target_ref: str | None,
    parsed_target_ref: ColumnConfirmationTargetRefV1 | None,
    raw_owner_answer: str | None,
    proposed_role: str | None,
    blocked_reason: str | None,
    status: str,
    owner_answer_validation_status: str | None,
    metadata: dict[str, Any] | None,
) -> Service1ColumnConfirmationReentryCandidateV1:
    return Service1ColumnConfirmationReentryCandidateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        blocked_reason=blocked_reason,
        question_ref=projected_question.question_ref,
        question_source=projected_question.source,
        target_ref=target_ref,
        parsed_target_ref=parsed_target_ref,
        answer_type=projected_question.answer_type,
        raw_owner_answer=raw_owner_answer,
        proposed_role=proposed_role,
        owner_answer_validation_status=owner_answer_validation_status,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_column_confirmation_reentry_candidate_v1(
    *,
    projected_question: Service1ProjectedQuestionV1,
    proposed_role: str | None = None,
    suggested_semantic_role: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationReentryCandidateV1:
    if not isinstance(projected_question, Service1ProjectedQuestionV1):
        raise ValueError("projected_question must be Service1ProjectedQuestionV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    role = _normalize_role(
        proposed_role=proposed_role,
        suggested_semantic_role=suggested_semantic_role,
    )
    raw_owner_answer = _optional_text(projected_question.latest_raw_owner_answer) or None
    target_ref = _optional_text(projected_question.target_ref) or None
    validation_status = projected_question.owner_answer_validation_status

    blocked_reason: str | None = None
    parsed_target_ref: ColumnConfirmationTargetRefV1 | None = None

    if projected_question.source != SOURCE_COLUMN_CONFIRMATION:
        blocked_reason = BLOCK_QUESTION_SOURCE_UNSUPPORTED
    elif projected_question.answer_type != ANSWER_TYPE_CONFIRM_COLUMN_ROLE:
        blocked_reason = BLOCK_ANSWER_TYPE_UNSUPPORTED
    elif projected_question.projection_status != PROJECTION_STATUS_ANSWERED:
        blocked_reason = BLOCK_QUESTION_NOT_ANSWERED
    elif raw_owner_answer is None:
        blocked_reason = BLOCK_RAW_OWNER_ANSWER_MISSING
    elif validation_status != OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED:
        blocked_reason = BLOCK_OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED
    elif not role:
        blocked_reason = BLOCK_ROLE_MISSING
    else:
        try:
            parsed_target_ref = _parse_target_ref(projected_question.target_ref)
        except ValueError:
            blocked_reason = BLOCK_TARGET_REF_INVALID

    if blocked_reason is not None:
        return _base_packet(
            projected_question=projected_question,
            target_ref=target_ref,
            parsed_target_ref=None,
            raw_owner_answer=raw_owner_answer,
            proposed_role=role or None,
            blocked_reason=blocked_reason,
            status=STATUS_BLOCKED,
            owner_answer_validation_status=validation_status,
            metadata=metadata,
        )

    return _base_packet(
        projected_question=projected_question,
        target_ref=target_ref,
        parsed_target_ref=parsed_target_ref,
        raw_owner_answer=raw_owner_answer,
        proposed_role=role,
        blocked_reason=None,
        status=STATUS_READY_FOR_CLASSIFIER,
        owner_answer_validation_status=validation_status,
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY_FOR_CLASSIFIER",
    "STATUS_BLOCKED",
    "BLOCK_QUESTION_SOURCE_UNSUPPORTED",
    "BLOCK_ANSWER_TYPE_UNSUPPORTED",
    "BLOCK_QUESTION_NOT_ANSWERED",
    "BLOCK_RAW_OWNER_ANSWER_MISSING",
    "BLOCK_TARGET_REF_INVALID",
    "BLOCK_ROLE_MISSING",
    "BLOCK_OWNER_ANSWER_VALIDATION_STATUS_UNSUPPORTED",
    "OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED",
    "ColumnConfirmationTargetRefV1",
    "Service1ColumnConfirmationReentryCandidateV1",
    "build_service_1_column_confirmation_reentry_candidate_v1",
]
