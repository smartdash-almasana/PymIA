from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


OwnerResolvedNextActionType = Literal[
    "ask_clarification",
    "reject_answer",
    "keep_as_declared",
]


class OwnerResolvedNextAction(BaseModel):
    """Acción owner-facing con preguntas objetivo ya resueltas a texto."""

    action_id: str = Field(..., description="Identificador estable de la acción resuelta.")
    action_type: OwnerResolvedNextActionType = Field(
        ...,
        description="Tipo contractual de acción resuelta.",
    )
    resolved_questions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("action_id")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("action_id must be non-empty")
        return text

    @field_validator("resolved_questions")
    @classmethod
    def _normalize_resolved_questions(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if not text:
                raise ValueError("resolved_questions must not contain empty text")
            normalized.append(text)
        return normalized


class OwnerResolvedNextActionBundle(BaseModel):
    """Bundle mínimo de acciones owner-facing con preguntas resueltas a texto."""

    bundle_id: str = Field(..., description="Identificador estable del bundle resuelto.")
    source_action_bundle_id: str = Field(
        ...,
        description="Identificador del OwnerNextActionBundle origen.",
    )
    source_questions_bundle_id: str = Field(
        ...,
        description="Identificador del OwnerQuestionsBundle usado para resolver textos.",
    )
    resolved_actions: list[OwnerResolvedNextAction] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp ISO UTC de creación.",
    )

    @field_validator(
        "bundle_id",
        "source_action_bundle_id",
        "source_questions_bundle_id",
    )
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text
