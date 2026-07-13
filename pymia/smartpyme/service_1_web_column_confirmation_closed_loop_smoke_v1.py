from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.contracts.column_confirmation_v1 import OwnerColumnConfirmationOutcome
from pymia.smartpyme.service_1_owner_column_confirmation_answer_intake_v1 import (
    Service1OwnerColumnConfirmationAnswerIntakeResultV1,
    build_service_1_owner_column_confirmation_answer_intake_v1,
)
from pymia.smartpyme.service_1_owner_prompt_batch_display_model_v1 import (
    Service1OwnerPromptBatchDisplayModelV1,
    build_service_1_owner_prompt_batch_display_model_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_extraction_to_adapter_chain_v1 import (
    Service1XlsxStructureExtractionToAdapterChainResultV1,
    build_service_1_xlsx_structure_extraction_to_adapter_chain_v1,
)

SCHEMA_VERSION = "SERVICE_1_WEB_COLUMN_CONFIRMATION_CLOSED_LOOP_SMOKE_V1"
SERVICE_NAME = "SERVICE_1"
STATUS_AWAITING_OWNER = "AWAITING_OWNER"
STATUS_OWNER_RESPONSES_CAPTURED = "OWNER_RESPONSES_CAPTURED"
STATUS_NEEDS_OWNER_FOLLOWUP = "NEEDS_OWNER_FOLLOWUP"
STATUS_BLOCKED_NO_COLUMNS = "BLOCKED_NO_COLUMNS"
STATUS_BLOCKED_INVALID_OWNER_ANSWER = "BLOCKED_INVALID_OWNER_ANSWER"

_FORBIDDEN_INTERNAL_TERMS = (
    "venta_total",
    "precio_venta",
    "costo_unitario",
    "costo_total",
    "computed_variables",
    "margen_bruto",
    "margen_bruto_pct",
    "owner_rectified_function",
    "suggested_semantic_role",
)


@dataclass(frozen=True)
class Service1OwnerColumnConfirmationInputV1:
    sheet_name: str
    column_name: str
    owner_response: str
    owner_free_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnConfirmationClosedLoopSummaryV1:
    total_questions: int
    total_answers: int
    accepted_unknown_count: int
    rejected_count: int
    needs_normalization_count: int
    conflicting_count: int
    insufficient_count: int
    pending_answer_count: int
    ready_for_semantic_normalization: bool
    ready_for_matrix_application: bool
    ready_for_evidence_profile: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1WebColumnConfirmationClosedLoopSmokeResultV1:
    schema_version: str
    service_name: str
    status: str
    file_name: str
    extraction_chain_result: Service1XlsxStructureExtractionToAdapterChainResultV1
    display_model: Service1OwnerPromptBatchDisplayModelV1
    answer_results: tuple[Service1OwnerColumnConfirmationAnswerIntakeResultV1, ...]
    summary: Service1ColumnConfirmationClosedLoopSummaryV1
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    evidence_profile_generated: bool
    matrix_application_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "status": self.status,
            "file_name": self.file_name,
            "extraction_chain_summary": {
                "schema_version": self.extraction_chain_result.schema_version,
                "service_name": self.extraction_chain_result.service_name,
                "status": self.extraction_chain_result.status,
                "extracted_file_name": self.extraction_chain_result.extracted_file_name,
                "runtime_authorized": self.extraction_chain_result.runtime_authorized,
                "tool_execution_authorized": self.extraction_chain_result.tool_execution_authorized,
                "delivery_authorized": self.extraction_chain_result.delivery_authorized,
                "diagnosis_generated": self.extraction_chain_result.diagnosis_generated,
            },
            "display_model": self.display_model.to_dict(),
            "answer_results": [answer_result.to_dict() for answer_result in self.answer_results],
            "summary": self.summary.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "evidence_profile_generated": self.evidence_profile_generated,
            "matrix_application_authorized": self.matrix_application_authorized,
            "metadata": dict(self.metadata),
        }


def build_service_1_web_column_confirmation_closed_loop_smoke_v1(
    *,
    extracted_structure: dict[str, Any],
    owner_answers: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1WebColumnConfirmationClosedLoopSmokeResultV1:
    if not isinstance(extracted_structure, dict):
        raise ValueError("extracted_structure must be a dict")
    if owner_answers is not None and not isinstance(owner_answers, (list, tuple)):
        raise ValueError("owner_answers must be a list, tuple, or None")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    smoke_metadata = dict(metadata or {})
    extraction_chain_result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=extracted_structure,
        metadata=smoke_metadata,
    )
    display_model = build_service_1_owner_prompt_batch_display_model_v1(
        owner_prompt_batch=extraction_chain_result.column_confirmation_result.owner_prompt_batch,
        metadata=smoke_metadata,
    )
    _assert_display_is_safe(display_model)

    answer_results = tuple(
        _capture_owner_answer(
            display_model=display_model,
            raw_owner_answer=raw_owner_answer,
            metadata=smoke_metadata,
        )
        for raw_owner_answer in tuple(owner_answers or ())
    )
    summary = _summarize_closed_loop(
        display_model=display_model,
        answer_results=answer_results,
    )
    status = _resolve_status(
        display_model=display_model,
        summary=summary,
    )

    return Service1WebColumnConfirmationClosedLoopSmokeResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        file_name=display_model.file_name,
        extraction_chain_result=extraction_chain_result,
        display_model=display_model,
        answer_results=answer_results,
        summary=summary,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        evidence_profile_generated=False,
        matrix_application_authorized=False,
        metadata=smoke_metadata,
    )


def _capture_owner_answer(
    *,
    display_model: Service1OwnerPromptBatchDisplayModelV1,
    raw_owner_answer: dict[str, Any],
    metadata: dict[str, Any],
) -> Service1OwnerColumnConfirmationAnswerIntakeResultV1:
    if not isinstance(raw_owner_answer, dict):
        raise ValueError("each owner answer must be a dict")
    return build_service_1_owner_column_confirmation_answer_intake_v1(
        display_model=display_model,
        sheet_name=_required_text(raw_owner_answer.get("sheet_name"), field_name="sheet_name"),
        column_name=_required_text(raw_owner_answer.get("column_name"), field_name="column_name"),
        owner_response=_required_text(raw_owner_answer.get("owner_response"), field_name="owner_response"),
        owner_free_text=_optional_text(raw_owner_answer.get("owner_free_text")),
        metadata=metadata,
    )


def _summarize_closed_loop(
    *,
    display_model: Service1OwnerPromptBatchDisplayModelV1,
    answer_results: tuple[Service1OwnerColumnConfirmationAnswerIntakeResultV1, ...],
) -> Service1ColumnConfirmationClosedLoopSummaryV1:
    outcomes = [answer_result.answer.outcome for answer_result in answer_results]
    answered_keys = {(answer_result.sheet_name, answer_result.column_name) for answer_result in answer_results}
    expected_keys = {(question.sheet_name, question.column_name) for question in display_model.questions}
    pending_answer_count = len(expected_keys - answered_keys)
    needs_normalization_count = sum(
        1 for answer_result in answer_results
        if answer_result.answer.outcome == OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER
        and answer_result.answer.owner_answer_text.startswith("TU_RESPUESTA:")
    )

    return Service1ColumnConfirmationClosedLoopSummaryV1(
        total_questions=display_model.total_questions,
        total_answers=len(answer_results),
        accepted_unknown_count=outcomes.count(OwnerColumnConfirmationOutcome.OWNER_UNKNOWN),
        rejected_count=outcomes.count(OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING),
        needs_normalization_count=needs_normalization_count,
        conflicting_count=outcomes.count(OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER),
        insufficient_count=outcomes.count(OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER),
        pending_answer_count=pending_answer_count,
        ready_for_semantic_normalization=needs_normalization_count > 0,
        ready_for_matrix_application=False,
        ready_for_evidence_profile=False,
    )


def _resolve_status(
    *,
    display_model: Service1OwnerPromptBatchDisplayModelV1,
    summary: Service1ColumnConfirmationClosedLoopSummaryV1,
) -> str:
    if display_model.total_questions == 0:
        return STATUS_BLOCKED_NO_COLUMNS
    if summary.conflicting_count > 0:
        return STATUS_BLOCKED_INVALID_OWNER_ANSWER
    if summary.pending_answer_count > 0:
        return STATUS_AWAITING_OWNER
    if summary.needs_normalization_count > 0 or summary.rejected_count > 0:
        return STATUS_NEEDS_OWNER_FOLLOWUP
    return STATUS_OWNER_RESPONSES_CAPTURED


def _assert_display_is_safe(display_model: Service1OwnerPromptBatchDisplayModelV1) -> None:
    rendered = str(display_model.to_dict()).lower()
    leaked = [term for term in _FORBIDDEN_INTERNAL_TERMS if term in rendered]
    if leaked:
        raise ValueError(f"closed loop smoke cannot expose internal semantic terms: {leaked}")


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("owner_free_text must be a string or None")
    stripped = value.strip()
    return stripped or None


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_AWAITING_OWNER",
    "STATUS_OWNER_RESPONSES_CAPTURED",
    "STATUS_NEEDS_OWNER_FOLLOWUP",
    "STATUS_BLOCKED_NO_COLUMNS",
    "STATUS_BLOCKED_INVALID_OWNER_ANSWER",
    "Service1OwnerColumnConfirmationInputV1",
    "Service1ColumnConfirmationClosedLoopSummaryV1",
    "Service1WebColumnConfirmationClosedLoopSmokeResultV1",
    "build_service_1_web_column_confirmation_closed_loop_smoke_v1",
]
