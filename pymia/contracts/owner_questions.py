from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


OwnerQuestionReason = Literal[
    "missing_evidence",
    "next_question",
    "blocked_message",
]

OwnerQuestionAnswerType = Literal[
    "text",
    "number",
    "date",
    "boolean",
    "document",
    "period",
    "unknown",
]

OwnerQuestionMissingInputType = Literal[
    "STRUCTURAL_INPUT",
    "OWNER_SEMANTIC_CLARIFICATION",
    "MIXED",
]


class OwnerQuestion(BaseModel):
    """Pregunta explícita al dueño PyME derivada de artefactos ya trazados.

    Este contrato representa estructura. No diagnostica ni decide heurísticamente.
    """

    question_id: str = Field(..., description="Identificador estable de la pregunta.")
    question_text: str = Field(..., description="Texto explícito a responder por el dueño.")
    reason: OwnerQuestionReason = Field(
        ...,
        description="Motivo contractual de la pregunta según el artefacto fuente.",
    )
    missing_key: str | None = Field(
        default=None,
        description="Clave faltante asociada, si existe.",
    )
    missing_input_type: OwnerQuestionMissingInputType | None = Field(
        default=None,
        description="Clasificación contractual del faltante asociado, si existe.",
    )
    source_ref: str = Field(..., description="Referencia trazable al artefacto fuente.")
    expected_answer_type: OwnerQuestionAnswerType = Field(default="unknown")
    required: bool = Field(
        default=True,
        description="Indica si la respuesta es obligatoria para destrabar el caso.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("question_id", "question_text", "source_ref")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text

    @field_validator("missing_key")
    @classmethod
    def _normalize_missing_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None


class OwnerQuestionsBundle(BaseModel):
    """Bundle mínimo de preguntas explícitas al dueño."""

    bundle_id: str = Field(..., description="Identificador estable del bundle de preguntas.")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de creación del bundle.",
    )
    questions: list[OwnerQuestion] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("bundle_id")
    @classmethod
    def _bundle_id_must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("bundle_id must be non-empty")
        return text
