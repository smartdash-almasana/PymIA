from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


OwnerNextActionType = Literal[
    "ask_clarification",
    "reject_answer",
    "keep_as_declared",
]


class OwnerNextAction(BaseModel):
    """Acción mínima siguiente derivada de un bundle de evaluación owner-facing."""

    action_id: str = Field(..., description="Identificador estable de la acción.")
    action_type: OwnerNextActionType = Field(
        ...,
        description="Tipo contractual de siguiente acción.",
    )
    target_questions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("action_id")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("action_id must be non-empty")
        return text

    @field_validator("target_questions")
    @classmethod
    def _normalize_target_questions(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                normalized.append(text)
        return normalized


class OwnerNextActionBundle(BaseModel):
    """Bundle mínimo de siguiente acción para el dueño."""

    bundle_id: str = Field(..., description="Identificador estable del bundle de acciones.")
    source_evaluation_bundle_id: str = Field(
        ...,
        description="Identificador del OwnerAnswerEvaluationBundle origen.",
    )
    actions: list[OwnerNextAction] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de creación.",
    )

    @field_validator("bundle_id", "source_evaluation_bundle_id")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text
