from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


OwnerAnswerType = Literal[
    "text",
    "number",
    "date",
    "boolean",
    "document",
    "period",
    "unknown",
]

OwnerAnswerCaptureStatus = Literal[
    "provided",
    "declined",
    "unclear",
]


class OwnerAnswer(BaseModel):
    """Respuesta explícita del dueño PyME a una pregunta ya emitida."""

    answer_id: str = Field(..., description="Identificador estable de la respuesta.")
    question_id: str = Field(..., description="Identificador de la pregunta origen.")
    question_text: str = Field(..., description="Texto de la pregunta respondida.")
    answer_text: str | None = Field(
        default=None,
        description="Texto libre capturado de la respuesta, si existe.",
    )
    structured_answer: dict[str, Any] = Field(
        default_factory=dict,
        description="Payload estructurado mínimo de respuesta, si aplica.",
    )
    answer_type: OwnerAnswerType = Field(default="unknown")
    capture_status: OwnerAnswerCaptureStatus = Field(default="provided")
    source_ref: str = Field(..., description="Referencia trazable al origen de captura.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("answer_id", "question_id", "question_text", "source_ref")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text

    @field_validator("answer_text")
    @classmethod
    def _normalize_answer_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @model_validator(mode="after")
    def _validate_provided_has_content(self) -> "OwnerAnswer":
        if self.capture_status == "provided":
            has_text = self.answer_text is not None
            has_structured = bool(self.structured_answer)
            if not has_text and not has_structured:
                raise ValueError("provided answer must include answer_text or structured_answer")
        return self


class OwnerAnswersBundle(BaseModel):
    """Bundle mínimo de respuestas explícitas del dueño."""

    bundle_id: str = Field(..., description="Identificador estable del bundle de respuestas.")
    captured_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de captura del bundle.",
    )
    answers: list[OwnerAnswer] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("bundle_id")
    @classmethod
    def _bundle_id_must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("bundle_id must be non-empty")
        return text
