"""FIO contracts for transparency and ownership in document inference."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class FichaInformativaOpacidad(BaseModel):
    """Transparency record for ambiguity and unresolved ownership questions."""

    owner: str = Field(min_length=1)
    specific_owner_question: str = Field(min_length=1)
    opacity_reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_specific_owner_question(self) -> "FichaInformativaOpacidad":
        """Ensure the owner question is specific enough for escalation."""
        if len(self.specific_owner_question.strip()) < 10:
            raise ValueError("specific_owner_question must be explicit and actionable.")
        return self
