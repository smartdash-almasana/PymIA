from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


OwnerAnswerEvaluationVerdict = Literal[
    "accepted_as_declared",
    "verified",
    "needs_clarification",
    "rejected",
]


class OwnerAnswerEvaluation(BaseModel):
    """Evaluación epistemológica estructurada de una respuesta del dueño."""

    evaluation_id: str = Field(..., description="Identificador estable de la evaluación.")
    source_answer_id: str = Field(..., description="Identificador de la respuesta origen.")
    linked_question_id: str = Field(..., description="Identificador de la pregunta asociada.")
    verdict: OwnerAnswerEvaluationVerdict = Field(
        ...,
        description="Veredicto contractual de la evaluación.",
    )
    mapped_key: str | None = Field(
        default=None,
        description="Clave normalizada asociada, si corresponde.",
    )
    normalized_value: Any | None = Field(
        default=None,
        description="Valor normalizado opcional sin promoción automática a evidencia.",
    )
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "evaluation_id",
        "source_answer_id",
        "linked_question_id",
    )
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text

    @field_validator("mapped_key")
    @classmethod
    def _normalize_mapped_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("validation_errors", "warnings", "notes")
    @classmethod
    def _normalize_string_lists(cls, value: list[str]) -> list[str]:
        return [str(item).strip() for item in value if str(item).strip()]


class OwnerAnswerEvaluationBundle(BaseModel):
    """Bundle mínimo de evaluaciones estructuradas de respuestas del dueño."""

    bundle_id: str = Field(..., description="Identificador estable del bundle de evaluaciones.")
    source_answers_bundle_id: str = Field(
        ...,
        description="Identificador del OwnerAnswersBundle evaluado.",
    )
    evaluated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de evaluación del bundle.",
    )
    evaluations: list[OwnerAnswerEvaluation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("bundle_id", "source_answers_bundle_id")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text
