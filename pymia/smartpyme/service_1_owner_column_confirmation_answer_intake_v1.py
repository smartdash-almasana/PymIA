from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_v1 import (
    OWNER_RESPONSE_NO,
    OWNER_RESPONSE_SI,
    OWNER_RESPONSE_TU_RESPUESTA,
)
from pymia.smartpyme.service_1_owner_prompt_batch_display_model_v1 import (
    Service1OwnerPromptBatchDisplayModelV1,
    Service1OwnerPromptDisplayQuestionV1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_COLUMN_CONFIRMATION_ANSWER_INTAKE_V1"
SERVICE_NAME = "SERVICE_1"
STATUS_ANSWER_CAPTURED = "ANSWER_CAPTURED"
STATUS_ANSWER_REJECTED = "ANSWER_REJECTED"
UNKNOWN_PROPOSED_ROLE = "unknown"

_FORBIDDEN_INTERNAL_TERMS = (
    "venta_total",
    "precio_venta",
    "costo_unitario",
    "costo_total",
    "computed_variables",
    "margen_bruto",
    "margen_bruto_pct",
    "owner_rectified_function",
)


@dataclass(frozen=True)
class Service1OwnerColumnConfirmationAnswerIntakeResultV1:
    schema_version: str
    service_name: str
    status: str
    file_name: str
    sheet_name: str
    column_name: str
    answer: OwnerColumnConfirmationAnswer
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    evidence_profile_generated: bool
    owner_rectification_created: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["answer"] = self.answer.model_dump()
        return data


def build_service_1_owner_column_confirmation_answer_intake_v1(
    *,
    display_model: Service1OwnerPromptBatchDisplayModelV1,
    sheet_name: str,
    column_name: str,
    owner_response: str,
    owner_free_text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerColumnConfirmationAnswerIntakeResultV1:
    """Capture one owner column-confirmation response without semantic rectification.

    This boundary intentionally does not interpret business meaning from free text.
    It only converts the owner-facing response surface into a classified
    OwnerColumnConfirmationAnswer. Later layers may normalize a free-text correction,
    but this function must not create operational evidence or unlock execution.
    """

    if not isinstance(display_model, Service1OwnerPromptBatchDisplayModelV1):
        raise ValueError("display_model must be a Service1OwnerPromptBatchDisplayModelV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    sheet_name = _required_text(sheet_name, field_name="sheet_name")
    column_name = _required_text(column_name, field_name="column_name")
    normalized_response = _normalize_owner_response(owner_response)
    free_text = _optional_text(owner_free_text)
    question = _find_question(
        display_model=display_model,
        sheet_name=sheet_name,
        column_name=column_name,
    )
    _assert_question_is_safe(question)

    outcome, confirmed_role, reason = _classify_owner_response(
        normalized_response=normalized_response,
        free_text=free_text,
    )
    status = STATUS_ANSWER_CAPTURED
    if outcome in {
        OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
        OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER,
    }:
        status = STATUS_ANSWER_REJECTED

    answer_text = _render_owner_answer_text(
        normalized_response=normalized_response,
        free_text=free_text,
    )
    answer = OwnerColumnConfirmationAnswer(
        sheet_name=question.sheet_name,
        column_name=question.column_name,
        owner_answer_text=answer_text,
        proposed_role=UNKNOWN_PROPOSED_ROLE,
        confirmed_role=confirmed_role,
        outcome=outcome,
        unblocks_variable_names=[],
        reason=reason,
    )

    return Service1OwnerColumnConfirmationAnswerIntakeResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        file_name=display_model.file_name,
        sheet_name=question.sheet_name,
        column_name=question.column_name,
        answer=answer,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        evidence_profile_generated=False,
        owner_rectification_created=False,
        metadata=dict(metadata or {}),
    )


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("owner_free_text must be a string or None")
    normalized = value.strip()
    return normalized or None


def _normalize_owner_response(owner_response: str) -> str:
    response = _required_text(owner_response, field_name="owner_response").strip().upper()
    if response in {"SI", "SÍ"}:
        return OWNER_RESPONSE_SI
    if response == OWNER_RESPONSE_NO:
        return OWNER_RESPONSE_NO
    if response in {"TU_RESPUESTA", "TU RESPUESTA"}:
        return OWNER_RESPONSE_TU_RESPUESTA
    raise ValueError("owner_response must be SÍ, NO, or TU_RESPUESTA")


def _find_question(
    *,
    display_model: Service1OwnerPromptBatchDisplayModelV1,
    sheet_name: str,
    column_name: str,
) -> Service1OwnerPromptDisplayQuestionV1:
    for question in display_model.questions:
        if question.sheet_name == sheet_name and question.column_name == column_name:
            return question
    raise ValueError(f"display question not found: {sheet_name}.{column_name}")


def _assert_question_is_safe(question: Service1OwnerPromptDisplayQuestionV1) -> None:
    rendered = " ".join(
        [
            question.file_name,
            question.sheet_name,
            question.column_name,
            question.prompt_text,
            " ".join(question.allowed_owner_responses),
        ]
    ).lower()
    leaked = [term for term in _FORBIDDEN_INTERNAL_TERMS if term in rendered]
    if leaked:
        raise ValueError(f"answer intake cannot consume unsafe owner-facing question: {leaked}")


def _classify_owner_response(
    *,
    normalized_response: str,
    free_text: str | None,
) -> tuple[OwnerColumnConfirmationOutcome, str | None, str]:
    if normalized_response == OWNER_RESPONSE_SI:
        if free_text:
            return (
                OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER,
                None,
                "Owner answered SÍ but also supplied free-text correction; no semantic truth was created.",
            )
        return (
            OwnerColumnConfirmationOutcome.OWNER_UNKNOWN,
            None,
            "Owner accepted the displayed interpretation, but the display model does not carry an operational semantic role.",
        )

    if normalized_response == OWNER_RESPONSE_NO:
        if free_text:
            return (
                OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER,
                None,
                "Owner answered NO but also supplied free text; correction must be submitted as TU_RESPUESTA.",
            )
        return (
            OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
            None,
            "Owner rejected the displayed interpretation; no computation was unlocked.",
        )

    if normalized_response == OWNER_RESPONSE_TU_RESPUESTA:
        if not free_text:
            return (
                OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
                None,
                "Owner selected TU_RESPUESTA but did not provide a correction.",
            )
        return (
            OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
            None,
            "Owner provided a free-text correction; semantic normalization is required before operational use.",
        )

    return (
        OwnerColumnConfirmationOutcome.CONFLICTING_ANSWER,
        None,
        "Unsupported owner response.",
    )


def _render_owner_answer_text(*, normalized_response: str, free_text: str | None) -> str:
    if free_text:
        return f"{normalized_response}: {free_text}"
    return normalized_response


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_ANSWER_CAPTURED",
    "STATUS_ANSWER_REJECTED",
    "UNKNOWN_PROPOSED_ROLE",
    "Service1OwnerColumnConfirmationAnswerIntakeResultV1",
    "build_service_1_owner_column_confirmation_answer_intake_v1",
]
