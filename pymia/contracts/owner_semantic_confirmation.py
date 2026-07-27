from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


OwnerSemanticConfirmationStatus = Literal[
    "PENDING_OWNER_CONFIRMATION",
    "CONFIRMED_BY_OWNER",
    "REJECTED_BY_OWNER",
    "CORRECTED_BY_OWNER",
]

OwnerSemanticConfirmationTargetType = Literal[
    "SEMANTIC_INTERPRETATION",
    "EVIDENCE_REQUEST_AXIS",
    "PATHOLOGY_AXIS",
    "FORMULA_AXIS",
]


class OwnerSemanticConfirmationGate(BaseModel):
    """Gate soberano de confirmación semántica del dueño.

    PymIA/Hermes puede proponer un sentido operativo. El dueño debe confirmarlo,
    corregirlo o rechazarlo antes de usarlo como eje confirmado.
    """

    gate_id: str = Field(..., description="Identificador estable del gate.")
    target_type: OwnerSemanticConfirmationTargetType = Field(
        default="SEMANTIC_INTERPRETATION",
        description="Tipo de eje semántico sometido a confirmación.",
    )
    proposed_interpretation: str = Field(
        ...,
        description="Interpretación tentativa presentada al dueño.",
    )
    confirmation_question: str = Field(
        ...,
        description="Pregunta explícita de autorización/corrección al dueño.",
    )
    status: OwnerSemanticConfirmationStatus = Field(
        default="PENDING_OWNER_CONFIRMATION",
        description="Estado soberano de confirmación por parte del dueño.",
    )
    owner_response_text: str | None = Field(
        default=None,
        description="Respuesta explícita del dueño al gate, si existe.",
    )
    corrected_interpretation: str | None = Field(
        default=None,
        description="Interpretación corregida por el dueño, si aplica.",
    )
    related_missing_keys: list[str] = Field(default_factory=list)
    related_pathology_candidates: list[str] = Field(default_factory=list)
    related_formula_candidates: list[str] = Field(default_factory=list)
    source_ref: str = Field(..., description="Referencia trazable al artefacto fuente.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("gate_id", "proposed_interpretation", "confirmation_question", "source_ref")
    @classmethod
    def _must_be_non_empty(cls, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            raise ValueError("field must be non-empty")
        return text

    @field_validator("owner_response_text", "corrected_interpretation")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @field_validator("related_missing_keys", "related_pathology_candidates", "related_formula_candidates")
    @classmethod
    def _normalize_string_list(cls, values: list[str]) -> list[str]:
        return [str(value).strip() for value in values if str(value).strip()]

    @model_validator(mode="after")
    def _validate_owner_confirmation_state(self) -> "OwnerSemanticConfirmationGate":
        if self.status == "PENDING_OWNER_CONFIRMATION":
            if self.owner_response_text is not None or self.corrected_interpretation is not None:
                raise ValueError("pending gate cannot include owner response or correction")
        elif self.status in {"CONFIRMED_BY_OWNER", "REJECTED_BY_OWNER"}:
            if self.owner_response_text is None:
                raise ValueError("confirmed or rejected gate requires owner_response_text")
            if self.corrected_interpretation is not None:
                raise ValueError("confirmed or rejected gate cannot include corrected_interpretation")
        elif self.status == "CORRECTED_BY_OWNER":
            if self.owner_response_text is None or self.corrected_interpretation is None:
                raise ValueError("corrected gate requires owner_response_text and corrected_interpretation")
        return self

    @property
    def is_owner_confirmed(self) -> bool:
        return self.status == "CONFIRMED_BY_OWNER"

    @property
    def is_terminal(self) -> bool:
        return self.status in {"CONFIRMED_BY_OWNER", "REJECTED_BY_OWNER", "CORRECTED_BY_OWNER"}

    def to_owner_question_metadata(self) -> dict[str, Any]:
        """Project a pending semantic confirmation gate into OwnerQuestion metadata.

        This metadata asks for explicit owner confirmation. It does not carry a
        terminal confirmation status and must not be treated as structural evidence.
        """
        return {
            "expects_semantic_confirmation": True,
            "semantic_confirmation_gate_id": self.gate_id,
            "semantic_confirmation_target_type": self.target_type,
            "proposed_interpretation": self.proposed_interpretation,
            "related_missing_keys": list(self.related_missing_keys),
            "related_pathology_candidates": list(self.related_pathology_candidates),
            "related_formula_candidates": list(self.related_formula_candidates),
            "semantic_confirmation_source_ref": self.source_ref,
        }

    def to_owner_answer_metadata(self) -> dict[str, Any]:
        """Project a terminal semantic confirmation gate into OwnerAnswer metadata.

        The bridge reentry consumes this explicit status. Free text alone is not
        interpreted as confirmation.
        """
        if not self.is_terminal:
            raise ValueError("terminal semantic confirmation gate is required")

        metadata: dict[str, Any] = {
            "semantic_confirmation_status": self.status,
            "semantic_confirmation_gate_id": self.gate_id,
            "semantic_confirmation_target_type": self.target_type,
            "proposed_interpretation": self.proposed_interpretation,
            "owner_response_text": self.owner_response_text,
            "related_missing_keys": list(self.related_missing_keys),
            "related_pathology_candidates": list(self.related_pathology_candidates),
            "related_formula_candidates": list(self.related_formula_candidates),
            "semantic_confirmation_source_ref": self.source_ref,
        }
        if self.corrected_interpretation is not None:
            metadata["corrected_interpretation"] = self.corrected_interpretation
        return metadata
