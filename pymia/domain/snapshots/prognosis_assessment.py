"""PrognosisAssessment — Snapshot inmutable de pronóstico organizacional."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.prognosis_risk_level import PrognosisRiskLevel
from pymia.domain.types.prognosis_trajectory import PrognosisTrajectory


@dataclass(frozen=True)
class PrognosisAssessment:
    """Evaluación pronóstica de trayectoria y riesgo organizacional."""

    id: UUID
    diagnostic_report_id: UUID
    pathology_ids: List[UUID]
    trajectory: PrognosisTrajectory
    risk_level: PrognosisRiskLevel
    summary: str
    projected_outcome: str
    recommended_monitoring: List[str]
    key_risks: List[str] = field(default_factory=list)
    intervention_plan_id: Optional[UUID] = None
    point_of_no_return: Optional[datetime] = None
    point_of_no_return_description: Optional[str] = None
    intervention_window_days: Optional[int] = None
    organization_id: Optional[UUID] = None
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessor: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.diagnostic_report_id:
            raise ValueError("diagnostic_report_id es obligatorio")
        self._validate_uuid_list(self.pathology_ids, "pathology_ids", allow_empty=False)
        if not isinstance(self.trajectory, PrognosisTrajectory):
            raise ValueError("trajectory debe ser PrognosisTrajectory")
        if not isinstance(self.risk_level, PrognosisRiskLevel):
            raise ValueError("risk_level debe ser PrognosisRiskLevel")
        if not self.summary or len(self.summary.strip()) < 10:
            raise ValueError("summary debe tener mínimo 10 caracteres")
        if not self.projected_outcome or len(self.projected_outcome.strip()) < 10:
            raise ValueError("projected_outcome debe tener mínimo 10 caracteres")
        self._validate_text_list(self.recommended_monitoring, "recommended_monitoring", allow_empty=False)
        self._validate_text_list(self.key_risks, "key_risks", allow_empty=True)
        if self.risk_level in (PrognosisRiskLevel.ALTO, PrognosisRiskLevel.CRITICO) and not self.key_risks:
            raise ValueError("risk_level alto/critico requiere key_risks no vacío")
        self._require_timezone_aware(self.assessed_at, "assessed_at")
        if self.point_of_no_return is not None:
            self._require_timezone_aware(self.point_of_no_return, "point_of_no_return")
            if self.point_of_no_return <= self.assessed_at:
                raise ValueError("point_of_no_return debe ser posterior a assessed_at")
            if not self.point_of_no_return_description or not self.point_of_no_return_description.strip():
                raise ValueError("point_of_no_return requiere descripción")
        if self.point_of_no_return_description is not None and not self.point_of_no_return_description.strip():
            raise ValueError("point_of_no_return_description no puede estar vacío")
        if self.point_of_no_return_description and self.point_of_no_return is None:
            raise ValueError("point_of_no_return_description requiere point_of_no_return")
        if self.intervention_window_days is not None and self.intervention_window_days <= 0:
            raise ValueError("intervention_window_days debe ser > 0")
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

    def is_high_risk(self) -> bool:
        return self.risk_level in (PrognosisRiskLevel.ALTO, PrognosisRiskLevel.CRITICO)

    def has_intervention_plan(self) -> bool:
        return self.intervention_plan_id is not None

    def has_point_of_no_return(self) -> bool:
        return self.point_of_no_return is not None

    def pathology_count(self) -> int:
        return len(self.pathology_ids)

    def monitoring_count(self) -> int:
        return len(self.recommended_monitoring)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "diagnostic_report_id": str(self.diagnostic_report_id),
            "pathology_ids": [str(pid) for pid in self.pathology_ids],
            "trajectory": self.trajectory.value,
            "risk_level": self.risk_level.value,
            "summary": self.summary,
            "projected_outcome": self.projected_outcome,
            "recommended_monitoring": list(self.recommended_monitoring),
            "key_risks": list(self.key_risks),
            "intervention_plan_id": str(self.intervention_plan_id) if self.intervention_plan_id else None,
            "point_of_no_return": self.point_of_no_return.isoformat() if self.point_of_no_return else None,
            "point_of_no_return_description": self.point_of_no_return_description,
            "intervention_window_days": self.intervention_window_days,
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "assessed_at": self.assessed_at.isoformat(),
            "assessor": self.assessor,
            "notes": self.notes,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrognosisAssessment":
        return cls(
            id=UUID(data["id"]),
            diagnostic_report_id=UUID(data["diagnostic_report_id"]),
            pathology_ids=[UUID(pid) for pid in data.get("pathology_ids", [])],
            trajectory=PrognosisTrajectory(data["trajectory"]),
            risk_level=PrognosisRiskLevel(data["risk_level"]),
            summary=data["summary"],
            projected_outcome=data["projected_outcome"],
            recommended_monitoring=list(data.get("recommended_monitoring", [])),
            key_risks=list(data.get("key_risks", [])),
            intervention_plan_id=UUID(data["intervention_plan_id"]) if data.get("intervention_plan_id") else None,
            point_of_no_return=datetime.fromisoformat(data["point_of_no_return"]) if data.get("point_of_no_return") else None,
            point_of_no_return_description=data.get("point_of_no_return_description"),
            intervention_window_days=data.get("intervention_window_days"),
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            assessed_at=datetime.fromisoformat(data["assessed_at"]),
            assessor=data.get("assessor"),
            notes=data.get("notes"),
            metadata=data.get("metadata"),
        )
