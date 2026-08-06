"""Service 1 — Column Understanding Owner Question Adapter V1.

Pure owner-facing projection of Service1ColumnUnderstandingV1, consumed by
the canonical semantic bridge. No frontend I/O, orchestration, tool execution
or runtime authorization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final

from pymia.smartpyme.service_1_column_understanding_engine_contract_v1 import (
    Service1ColumnUnderstandingV1,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import (
    build_service_1_owner_options_for_understanding_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_COLUMN_UNDERSTANDING_OWNER_QUESTION_ADAPTER_V1"
STATUS_QUESTION_READY: Final[str] = "OWNER_QUESTION_READY"
STATUS_NO_QUESTION_REQUIRED: Final[str] = "NO_OWNER_QUESTION_REQUIRED"


@dataclass(frozen=True)
class Service1OwnerQuestionOptionViewV1:
    option_id: str
    label: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnOwnerQuestionViewV1:
    schema_version: str
    status: str
    column_name: str
    sheet_name: str
    question_required: bool
    title: str
    context: str
    question: str | None
    options: tuple[Service1OwnerQuestionOptionViewV1, ...]
    risk_note: str | None
    confidence_note: str
    source_confidence: float
    source_normalized_header: str
    runtime_authorized: bool = False
    frontend_wiring_authorized: bool = False
    delivery_authorized: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_service_1_column_owner_question_view_v1(
    understanding: Service1ColumnUnderstandingV1,
    *,
    require_explicit_owner_confirmation: bool = False,
) -> Service1ColumnOwnerQuestionViewV1:
    if not isinstance(understanding, Service1ColumnUnderstandingV1):
        raise ValueError("understanding must be a Service1ColumnUnderstandingV1")

    sample_text = _format_samples(understanding.sample_values)
    context = (
        f"En la hoja '{understanding.sheet_name}', la columna "
        f"'{understanding.column_name}' tiene ejemplos como {sample_text}."
    )
    confidence_note = _confidence_note(understanding.confidence)

    question_required = bool(
        understanding.owner_question_needed or require_explicit_owner_confirmation
    )

    if not question_required:
        primary_label = _primary_label(understanding)
        return Service1ColumnOwnerQuestionViewV1(
            schema_version=SCHEMA_VERSION,
            status=STATUS_NO_QUESTION_REQUIRED,
            column_name=understanding.column_name,
            sheet_name=understanding.sheet_name,
            question_required=False,
            title=f"Columna comprendida: {understanding.column_name}",
            context=context,
            question=None,
            options=(),
            risk_note=None,
            confidence_note=f"PymIA la interpreta como {primary_label}. {confidence_note}",
            source_confidence=understanding.confidence,
            source_normalized_header=understanding.normalized_header,
            runtime_authorized=False,
            frontend_wiring_authorized=False,
            delivery_authorized=False,
            metadata={"projection_only": True, "source_question_needed": False},
        )

    if understanding.owner_question_needed and not understanding.owner_question_text:
        raise ValueError("owner_question_text is required when owner_question_needed is True")

    source_options = understanding.allowed_owner_answers
    if not source_options and require_explicit_owner_confirmation:
        source_options = build_service_1_first_contact_owner_options_v1(understanding)
    if not source_options:
        raise ValueError("owner answer options are required when confirmation is required")

    options = tuple(
        Service1OwnerQuestionOptionViewV1(
            option_id=option.option_id,
            label=option.label,
            description=option.description,
        )
        for option in source_options
    )
    question = "¿Qué representa esta columna en tu negocio?"
    return Service1ColumnOwnerQuestionViewV1(
        schema_version=SCHEMA_VERSION,
        status=STATUS_QUESTION_READY,
        column_name=understanding.column_name,
        sheet_name=understanding.sheet_name,
        question_required=True,
        title=f"Necesito confirmar qué significa: {understanding.column_name}",
        context=context,
        question=question,
        options=options,
        risk_note=f"Por qué importa: {understanding.risk_if_wrong}",
        confidence_note=confidence_note,
        source_confidence=understanding.confidence,
        source_normalized_header=understanding.normalized_header,
        runtime_authorized=False,
        frontend_wiring_authorized=False,
        delivery_authorized=False,
        metadata={
            "projection_only": True,
            "source_question_needed": bool(understanding.owner_question_needed),
            "explicit_owner_confirmation_required": bool(
                require_explicit_owner_confirmation
            ),
            "option_count": len(options),
        },
    )


def build_service_1_column_owner_question_views_v1(
    understandings: tuple[Service1ColumnUnderstandingV1, ...] | list[Service1ColumnUnderstandingV1],
    *,
    require_explicit_owner_confirmation: bool = False,
) -> tuple[Service1ColumnOwnerQuestionViewV1, ...]:
    if not isinstance(understandings, (tuple, list)):
        raise ValueError("understandings must be a tuple or list")
    return tuple(
        build_service_1_column_owner_question_view_v1(
            item,
            require_explicit_owner_confirmation=require_explicit_owner_confirmation,
        )
        for item in understandings
    )


def build_service_1_first_contact_owner_options_v1(
    understanding: Service1ColumnUnderstandingV1,
):
    return build_service_1_owner_options_for_understanding_v1(understanding)


def _format_samples(values: tuple[Any, ...]) -> str:
    if not values:
        return "sin valores de muestra"
    rendered = []
    for value in values[:3]:
        rendered.append(repr(value) if not isinstance(value, str) else f"'{value}'")
    return ", ".join(rendered)


def _confidence_note(confidence: float) -> str:
    if confidence >= 0.8:
        return "La señal es fuerte, pero la confirmación evita usar una interpretación incorrecta."
    if confidence >= 0.6:
        return "La señal es razonable, aunque todavía hay alternativas posibles."
    return "La señal es débil; PymIA no debe asumir el significado sin tu respuesta."


def _primary_label(understanding: Service1ColumnUnderstandingV1) -> str:
    if understanding.allowed_owner_answers:
        return understanding.allowed_owner_answers[0].label
    if understanding.primary_hypothesis is not None:
        return understanding.primary_hypothesis.semantic_role.replace("_", " ")
    return "una columna todavía no clasificada"


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_QUESTION_READY",
    "STATUS_NO_QUESTION_REQUIRED",
    "Service1OwnerQuestionOptionViewV1",
    "Service1ColumnOwnerQuestionViewV1",
    "build_service_1_first_contact_owner_options_v1",
    "build_service_1_column_owner_question_view_v1",
    "build_service_1_column_owner_question_views_v1",
]
