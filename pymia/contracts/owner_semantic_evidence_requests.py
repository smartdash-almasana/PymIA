from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


OwnerSemanticMissingInputType = Literal["STRUCTURAL_INPUT"]


class OwnerSemanticEvidenceRequest(BaseModel):
    """Pedido semántico de evidencia estructural al dueño PyME.

    La narrativa del dueño puede refinar el pedido, pero no destraba evidencia dura.
    """

    request_id: str = Field(..., description="Identificador estable del pedido semántico.")
    missing_key: str = Field(..., description="Clave técnica faltante preservada.")
    missing_input_type: OwnerSemanticMissingInputType = Field(
        default="STRUCTURAL_INPUT",
        description="Tipo contractual del faltante estructural.",
    )
    owner_answer_text: str = Field(..., description="Respuesta narrativa original del dueño.")
    semantic_signal: str | None = Field(
        default=None,
        description="Señal semántica interpretada, si existe.",
    )
    interpreted_meaning: str | None = Field(
        default=None,
        description="Interpretación operativa de la narrativa del dueño.",
    )
    refined_request_text: str = Field(
        ...,
        description="Pedido owner-facing accionable de evidencia estructural.",
    )
    required_fields: list[str] = Field(
        default_factory=list,
        description="Campos, columnas o datos requeridos para avanzar.",
    )
    accepted_formats: list[str] = Field(
        default_factory=list,
        description="Formatos aceptados para aportar la evidencia.",
    )
    does_resolve_structural_input: bool = Field(
        default=False,
        description="Debe permanecer false: la narrativa no resuelve evidencia estructural.",
    )
    confidence: float | None = Field(
        default=None,
        description="Confianza de la interpretación semántica, entre 0 y 1.",
    )
    source_ref: str = Field(..., description="Referencia trazable al owner answer fuente.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "request_id",
        "missing_key",
        "owner_answer_text",
        "refined_request_text",
        "source_ref",
    )
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text

    @field_validator("semantic_signal", "interpreted_meaning")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("required_fields", "accepted_formats")
    @classmethod
    def _list_must_have_non_empty_items(cls, values: list[str]) -> list[str]:
        normalized = [str(value).strip() for value in values if str(value).strip()]
        if not normalized:
            raise ValueError("list must contain at least one non-empty item")
        return normalized

    @field_validator("confidence")
    @classmethod
    def _confidence_must_be_probability(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value < 0 or value > 1:
            raise ValueError("confidence must be between 0 and 1")
        return value

    @model_validator(mode="after")
    def _narrative_must_not_resolve_structural_input(self) -> "OwnerSemanticEvidenceRequest":
        if self.does_resolve_structural_input:
            raise ValueError("owner narrative cannot resolve structural input")
        return self
