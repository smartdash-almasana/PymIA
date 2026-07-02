from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    Service1ColumnConfirmationOwnerPromptBatchV1,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_v1 import (
    ALLOWED_OWNER_RESPONSES,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_PROMPT_BATCH_DISPLAY_MODEL_V1"
SERVICE_NAME = "SERVICE_1"

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
class Service1OwnerPromptDisplayQuestionV1:
    file_name: str
    sheet_name: str
    column_name: str
    prompt_text: str
    allowed_owner_responses: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_owner_responses"] = list(self.allowed_owner_responses)
        return data


@dataclass(frozen=True)
class Service1OwnerPromptBatchDisplayModelV1:
    schema_version: str
    service_name: str
    file_name: str
    total_questions: int
    has_questions: bool
    questions: tuple[Service1OwnerPromptDisplayQuestionV1, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "service_name": self.service_name,
            "file_name": self.file_name,
            "total_questions": self.total_questions,
            "has_questions": self.has_questions,
            "questions": [question.to_dict() for question in self.questions],
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_owner_prompt_batch_display_model_v1(
    *,
    owner_prompt_batch: Service1ColumnConfirmationOwnerPromptBatchV1,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerPromptBatchDisplayModelV1:
    if not isinstance(owner_prompt_batch, Service1ColumnConfirmationOwnerPromptBatchV1):
        raise ValueError("owner_prompt_batch must be a Service1ColumnConfirmationOwnerPromptBatchV1")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    questions = tuple(
        _build_display_question(
            file_name=owner_prompt_batch.file_name,
            prompt_bridge=prompt_bridge,
        )
        for prompt_bridge in owner_prompt_batch.prompts
    )
    display_metadata = dict(metadata or owner_prompt_batch.metadata)

    return Service1OwnerPromptBatchDisplayModelV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        file_name=owner_prompt_batch.file_name,
        total_questions=len(questions),
        has_questions=bool(questions),
        questions=questions,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=display_metadata,
    )


def _build_display_question(
    *,
    file_name: str,
    prompt_bridge: Any,
) -> Service1OwnerPromptDisplayQuestionV1:
    owner_prompt = prompt_bridge.owner_prompt
    _assert_owner_text_is_safe(owner_prompt.prompt_text)
    _assert_allowed_responses_are_safe(owner_prompt.allowed_owner_responses)

    return Service1OwnerPromptDisplayQuestionV1(
        file_name=file_name,
        sheet_name=owner_prompt.sheet_name,
        column_name=owner_prompt.column_name,
        prompt_text=owner_prompt.prompt_text,
        allowed_owner_responses=tuple(owner_prompt.allowed_owner_responses),
    )


def _assert_owner_text_is_safe(prompt_text: str) -> None:
    lowered = prompt_text.lower()
    leaked = [term for term in _FORBIDDEN_INTERNAL_TERMS if term in lowered]
    if leaked:
        raise ValueError(f"display model cannot expose internal semantic terms: {leaked}")


def _assert_allowed_responses_are_safe(allowed_owner_responses: tuple[str, ...]) -> None:
    if tuple(allowed_owner_responses) != ALLOWED_OWNER_RESPONSES:
        raise ValueError("allowed_owner_responses must be exactly SÍ, NO, TU_RESPUESTA")


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "Service1OwnerPromptBatchDisplayModelV1",
    "Service1OwnerPromptDisplayQuestionV1",
    "build_service_1_owner_prompt_batch_display_model_v1",
]
