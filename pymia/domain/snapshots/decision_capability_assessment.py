"""DecisionCapabilityAssessment — Snapshot de capacidad decisional agregada."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.decision_capability_rating import DecisionCapabilityRating


@dataclass(frozen=True)
class DecisionCapabilityAssessment:
    """Evaluación inmutable de capacidad decisional organizacional."""

    id: UUID
    organization_id: UUID
    decision_record_ids: List[UUID]
    learning_cycle_ids: List[UUID]
    rating: DecisionCapabilityRating
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    recommended_improvements: List[str]
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessor: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.organization_id:
            raise ValueError("organization_id es obligatorio")
        self._validate_uuid_list(self.decision_record_ids, "decision_record_ids", allow_empty=False)
        self._validate_uuid_list(self.learning_cycle_ids, "learning_cycle_ids", allow_empty=True)
        if not isinstance(self.rating, DecisionCapabilityRating):
            raise ValueError("rating debe ser DecisionCapabilityRating")
        if not self.summary or len(self.summary.strip()) < 10:
            raise ValueError("summary debe tener mínimo 10 caracteres")
        self._validate_text_list(self.strengths, "strengths", allow_empty=True)
        self._validate_text_list(self.weaknesses, "weaknesses", allow_empty=True)
        self._validate_text_list(self.recommended_improvements, "recommended_improvements", allow_empty=False)
        if self.rating in (DecisionCapabilityRating.BAJA, DecisionCapabilityRating.CRITICA) and not self.weaknesses:
            raise ValueError("rating baja/critica requiere weaknesses no vacío")
        self._require_timezone_aware(self.assessed_at, "assessed_at")
        if self.assessor is not None and not self.assessor.strip():
            raise ValueError("assessor no puede estar vacío")

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    @staticmethod
    def _validate_uuid_list(values: List[UUID], field_name: str, allow_empty: bool) -> None:
        if not allow_empty and not values:
            raise ValueError(f"{field_name} no puede estar vacío")
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} no puede contener duplicados")
        if any(not isinstance(value, UUID) for value in values):
            raise ValueError(f"{field_name} debe contener UUIDs")

    @staticmethod
    def _validate_text_list(values: List[str], field_name: str, allow_empty: bool) -> None:
        if not allow_empty and not values:
            raise ValueError(f"{field_name} no puede estar vacío")
        if any(not value or not value.strip() for value in values):
            raise ValueError(f"{field_name} no puede contener strings vacíos")
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} no puede contener duplicados")

    def is_low_capability(self) -> bool:
        return self.rating in (DecisionCapabilityRating.BAJA, DecisionCapabilityRating.CRITICA)

    def decision_count(self) -> int:
        return len(self.decision_record_ids)

    def learning_cycle_count(self) -> int:
        return len(self.learning_cycle_ids)

    def has_learning_evidence(self) -> bool:
        return bool(self.learning_cycle_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "decision_record_ids": [str(value) for value in self.decision_record_ids],
            "learning_cycle_ids": [str(value) for value in self.learning_cycle_ids],
            "rating": self.rating.value,
            "summary": self.summary,
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "recommended_improvements": list(self.recommended_improvements),
            "assessed_at": self.assessed_at.isoformat(),
            "assessor": self.assessor,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionCapabilityAssessment":
        return cls(
            id=UUID(data["id"]),
            organization_id=UUID(data["organization_id"]),
            decision_record_ids=[UUID(value) for value in data.get("decision_record_ids", [])],
            learning_cycle_ids=[UUID(value) for value in data.get("learning_cycle_ids", [])],
            rating=DecisionCapabilityRating(data["rating"]),
            summary=data["summary"],
            strengths=list(data.get("strengths", [])),
            weaknesses=list(data.get("weaknesses", [])),
            recommended_improvements=list(data.get("recommended_improvements", [])),
            assessed_at=datetime.fromisoformat(data["assessed_at"]),
            assessor=data.get("assessor"),
            metadata=data.get("metadata"),
        )
