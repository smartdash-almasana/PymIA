from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    OwnerColumnConfirmationAnswer,
)
from pymia.smartpyme.service_1_owner_column_confirmation_answer_intake_v1 import (
    Service1OwnerColumnConfirmationAnswerIntakeResultV1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_ANSWERS_TO_COLUMN_CONFIRMATION_MATRIX_APPLICATION_V1"
SERVICE_NAME = "SERVICE_1"
STATUS_MATRIX_UPDATED = "MATRIX_UPDATED"
STATUS_MATRIX_BLOCKED = "MATRIX_BLOCKED"
STATUS_MATRIX_PENDING = "MATRIX_PENDING"
STATUS_NO_ANSWERS = "NO_ANSWERS"


@dataclass(frozen=True)
class Service1AppliedOwnerAnswerV1:
    sheet_name: str
    column_name: str
    outcome: str
    confirmation_status_after: str
    owner_confirmed_role_after: str | None
    owner_rectified_function_after: str | None
    semantic_rectification_status_after: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnConfirmationMatrixApplicationSummaryV1:
    total_entries: int
    total_answers: int
    applied_answers_count: int
    confirmed_count: int
    blocked_count: int
    pending_count: int
    ignored_count: int
    owner_rectified_functions_count: int
    matrix_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1:
    schema_version: str
    service_name: str
    status: str
    source_file_name: str
    updated_matrix: ColumnConfirmationMatrix
    applied_answers: tuple[Service1AppliedOwnerAnswerV1, ...]
    summary: Service1ColumnConfirmationMatrixApplicationSummaryV1
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    evidence_profile_generated: bool
    candidate_tools_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "status": self.status,
            "source_file_name": self.source_file_name,
            "updated_matrix": self.updated_matrix.model_dump(),
            "applied_answers": [applied.to_dict() for applied in self.applied_answers],
            "summary": self.summary.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "evidence_profile_generated": self.evidence_profile_generated,
            "candidate_tools_generated": self.candidate_tools_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_owner_answers_to_column_confirmation_matrix_application_v1(
    *,
    matrix: ColumnConfirmationMatrix,
    owner_answers: tuple[
        OwnerColumnConfirmationAnswer | Service1OwnerColumnConfirmationAnswerIntakeResultV1,
        ...,
    ] | list[OwnerColumnConfirmationAnswer | Service1OwnerColumnConfirmationAnswerIntakeResultV1],
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1:
    """Apply already-classified owner answers to a copied ColumnConfirmationMatrix.

    This bridge intentionally delegates semantic mutation to
    ColumnConfirmationMatrix.apply_owner_answer(...). It does not classify free text,
    create evidence profiles, create candidate tools, execute tools, authorize
    runtime, or deliver outputs.
    """
    if not isinstance(matrix, ColumnConfirmationMatrix):
        raise ValueError("matrix must be a ColumnConfirmationMatrix")
    if not isinstance(owner_answers, (list, tuple)):
        raise ValueError("owner_answers must be a list or tuple")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    updated_matrix = matrix.model_copy(deep=True)
    normalized_answers = tuple(_extract_answer(answer) for answer in owner_answers)
    applied_answers: list[Service1AppliedOwnerAnswerV1] = []

    for answer in normalized_answers:
        entry_after = updated_matrix.apply_owner_answer(answer)
        applied_answers.append(_applied_from_entry(answer=answer, entry_after=entry_after))

    summary = _summarize_matrix(updated_matrix=updated_matrix, total_answers=len(normalized_answers))
    return Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=_resolve_status(summary=summary),
        source_file_name=updated_matrix.file_name,
        updated_matrix=updated_matrix,
        applied_answers=tuple(applied_answers),
        summary=summary,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        evidence_profile_generated=False,
        candidate_tools_generated=False,
        metadata=dict(metadata or {}),
    )


def _extract_answer(
    answer_or_intake: OwnerColumnConfirmationAnswer | Service1OwnerColumnConfirmationAnswerIntakeResultV1,
) -> OwnerColumnConfirmationAnswer:
    if isinstance(answer_or_intake, OwnerColumnConfirmationAnswer):
        return _normalize_ui_answer_token_for_matrix_contract(answer_or_intake)
    if isinstance(answer_or_intake, Service1OwnerColumnConfirmationAnswerIntakeResultV1):
        return _normalize_ui_answer_token_for_matrix_contract(answer_or_intake.answer)
    raise ValueError("owner_answers must contain OwnerColumnConfirmationAnswer or intake result items")


def _normalize_ui_answer_token_for_matrix_contract(
    answer: OwnerColumnConfirmationAnswer,
) -> OwnerColumnConfirmationAnswer:
    if not answer.owner_answer_text.strip().upper().startswith("TU_RESPUESTA"):
        return answer
    return answer.model_copy(
        update={"owner_answer_text": answer.owner_answer_text.replace("TU_RESPUESTA", "tu respuesta", 1)}
    )


def _applied_from_entry(
    *,
    answer: OwnerColumnConfirmationAnswer,
    entry_after: ColumnConfirmationEntry,
) -> Service1AppliedOwnerAnswerV1:
    return Service1AppliedOwnerAnswerV1(
        sheet_name=answer.sheet_name,
        column_name=answer.column_name,
        outcome=answer.outcome.value,
        confirmation_status_after=entry_after.confirmation_status.value,
        owner_confirmed_role_after=entry_after.owner_confirmed_role,
        owner_rectified_function_after=entry_after.owner_rectified_function,
        semantic_rectification_status_after=entry_after.semantic_rectification_status.value,
    )


def _summarize_matrix(
    *,
    updated_matrix: ColumnConfirmationMatrix,
    total_answers: int,
) -> Service1ColumnConfirmationMatrixApplicationSummaryV1:
    confirmed_count = len(updated_matrix.confirmed_entries())
    blocked_count = len(updated_matrix.blocked_entries())
    pending_count = len(updated_matrix.pending_entries())
    ignored_count = len(updated_matrix.ignored_entries())
    owner_rectified_functions_count = sum(
        1
        for entry in updated_matrix.entries
        if isinstance(entry.owner_rectified_function, str) and bool(entry.owner_rectified_function.strip())
    )
    return Service1ColumnConfirmationMatrixApplicationSummaryV1(
        total_entries=len(updated_matrix.entries),
        total_answers=total_answers,
        applied_answers_count=total_answers,
        confirmed_count=confirmed_count,
        blocked_count=blocked_count,
        pending_count=pending_count,
        ignored_count=ignored_count,
        owner_rectified_functions_count=owner_rectified_functions_count,
        matrix_status=updated_matrix.status(),
    )


def _resolve_status(*, summary: Service1ColumnConfirmationMatrixApplicationSummaryV1) -> str:
    if summary.total_answers == 0:
        return STATUS_NO_ANSWERS
    if summary.blocked_count > 0:
        return STATUS_MATRIX_BLOCKED
    if summary.pending_count > 0:
        return STATUS_MATRIX_PENDING
    return STATUS_MATRIX_UPDATED


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_MATRIX_UPDATED",
    "STATUS_MATRIX_BLOCKED",
    "STATUS_MATRIX_PENDING",
    "STATUS_NO_ANSWERS",
    "Service1AppliedOwnerAnswerV1",
    "Service1ColumnConfirmationMatrixApplicationSummaryV1",
    "Service1OwnerAnswersToColumnConfirmationMatrixApplicationResultV1",
    "build_service_1_owner_answers_to_column_confirmation_matrix_application_v1",
]
