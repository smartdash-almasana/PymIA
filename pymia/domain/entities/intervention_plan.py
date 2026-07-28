"""InterventionPlan — Entidad de plan terapéutico organizacional."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.intervention_priority import InterventionPriority
from pymia.domain.types.intervention_status import InterventionStatus
from pymia.domain.types.intervention_type import InterventionType


@dataclass
class InterventionPlan:
    """Plan de intervención organizacional, sin ejecución runtime."""

    id: UUID
    title: str
    description: str
    intervention_type: InterventionType
    priority: InterventionPriority
    pathology_ids: List[UUID]
    objectives: List[str]
    actions: List[str]
    success_criteria: List[str]
    status: InterventionStatus = InterventionStatus.PROPOSED
    diagnostic_report_id: Optional[UUID] = None
    risk_notes: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.title or len(self.title.strip()) < 5:
            raise ValueError("title debe tener mínimo 5 caracteres")
        if not self.description or len(self.description.strip()) < 10:
            raise ValueError("description debe tener mínimo 10 caracteres")
        if not isinstance(self.intervention_type, InterventionType):
            raise ValueError("intervention_type debe ser InterventionType")
        if not isinstance(self.priority, InterventionPriority):
            raise ValueError("priority debe ser InterventionPriority")
        if not isinstance(self.status, InterventionStatus):
            raise ValueError("status debe ser InterventionStatus")
        self._validate_non_empty_uuid_list(self.pathology_ids, "pathology_ids")
        self._validate_text_list(self.objectives, "objectives")
        self._validate_text_list(self.actions, "actions")
        self._validate_text_list(self.success_criteria, "success_criteria")
        self._validate_optional_text_list(self.risk_notes, "risk_notes")
        if self.owner is not None and not self.owner.strip():
            raise ValueError("owner no puede estar vacío")
        self._validate_status_invariants()
        self._validate_temporal_coherence()

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    @staticmethod
    def _validate_text_list(values: List[str], field_name: str) -> None:
        if not values:
            raise ValueError(f"{field_name} no puede estar vacío")
        if any(not value or not value.strip() for value in values):
            raise ValueError(f"{field_name} no puede contener strings vacíos")
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} no puede contener duplicados")

    @staticmethod
    def _validate_optional_text_list(values: List[str], field_name: str) -> None:
        if any(not value or not value.strip() for value in values):
            raise ValueError(f"{field_name} no puede contener strings vacíos")
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} no puede contener duplicados")

    @staticmethod
    def _validate_non_empty_uuid_list(values: List[UUID], field_name: str) -> None:
        if not values:
            raise ValueError(f"{field_name} no puede estar vacío")
        if len(values) != len(set(values)):
            raise ValueError(f"{field_name} no puede contener duplicados")
        if any(not isinstance(value, UUID) for value in values):
            raise ValueError(f"{field_name} debe contener UUIDs")

    def _validate_status_invariants(self) -> None:
        if self.status in (InterventionStatus.APPROVED, InterventionStatus.IN_PROGRESS, InterventionStatus.COMPLETED):
            if self.approved_at is None:
                raise ValueError(f"status {self.status.value} requiere approved_at")
        if self.status in (InterventionStatus.IN_PROGRESS, InterventionStatus.COMPLETED):
            if self.started_at is None:
                raise ValueError(f"status {self.status.value} requiere started_at")
        if self.status == InterventionStatus.COMPLETED:
            if self.completed_at is None:
                raise ValueError("status completed requiere completed_at")
            if self.cancelled_at is not None or self.cancellation_reason is not None:
                raise ValueError("status completed no admite cancelación")
        if self.status == InterventionStatus.CANCELLED:
            if self.cancelled_at is None or not self.cancellation_reason:
                raise ValueError("status cancelled requiere cancelled_at y cancellation_reason")
            if self.completed_at is not None:
                raise ValueError("status cancelled no admite completed_at")

    def _validate_temporal_coherence(self) -> None:
        self._require_timezone_aware(self.created_at, "created_at")
        self._require_timezone_aware(self.updated_at, "updated_at")
        for field_name, value in [
            ("approved_at", self.approved_at),
            ("started_at", self.started_at),
            ("completed_at", self.completed_at),
            ("cancelled_at", self.cancelled_at),
        ]:
            if value is not None:
                self._require_timezone_aware(value, field_name)
        ordered = [self.created_at, self.approved_at, self.started_at, self.completed_at]
        previous = None
        for value in ordered:
            if value is not None:
                if previous is not None and value < previous:
                    raise ValueError("timestamps deben ser monótonos no decrecientes")
                previous = value
        if self.cancelled_at is not None and self.cancelled_at < self.created_at:
            raise ValueError("cancelled_at debe ser >= created_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")

    def _revalidate_after_mutation(self) -> None:
        self._validate_status_invariants()
        self._validate_temporal_coherence()

    def approve(self, approved_at: datetime) -> None:
        if self.status != InterventionStatus.PROPOSED:
            raise ValueError(f"approve requiere status proposed, status actual: {self.status.value}")
        self.status = InterventionStatus.APPROVED
        self.approved_at = approved_at
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def start(self, started_at: datetime) -> None:
        if self.status != InterventionStatus.APPROVED:
            raise ValueError(f"start requiere status approved, status actual: {self.status.value}")
        self.status = InterventionStatus.IN_PROGRESS
        self.started_at = started_at
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def complete(self, completed_at: datetime) -> None:
        if self.status != InterventionStatus.IN_PROGRESS:
            raise ValueError(f"complete requiere status in_progress, status actual: {self.status.value}")
        self.status = InterventionStatus.COMPLETED
        self.completed_at = completed_at
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def cancel(self, reason: str, cancelled_at: datetime) -> None:
        if self.status in (InterventionStatus.COMPLETED, InterventionStatus.CANCELLED):
            raise ValueError(f"cancel no admite status terminal: {self.status.value}")
        if not reason or not reason.strip():
            raise ValueError("cancellation_reason no puede estar vacío")
        self.status = InterventionStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_at = cancelled_at
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "intervention_type": self.intervention_type.value,
            "priority": self.priority.value,
            "pathology_ids": [str(pid) for pid in self.pathology_ids],
            "objectives": list(self.objectives),
            "actions": list(self.actions),
            "success_criteria": list(self.success_criteria),
            "status": self.status.value,
            "diagnostic_report_id": str(self.diagnostic_report_id) if self.diagnostic_report_id else None,
            "risk_notes": list(self.risk_notes),
            "owner": self.owner,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterventionPlan":
        return cls(
            id=UUID(data["id"]),
            title=data["title"],
            description=data["description"],
            intervention_type=InterventionType(data["intervention_type"]),
            priority=InterventionPriority(data["priority"]),
            pathology_ids=[UUID(pid) for pid in data.get("pathology_ids", [])],
            objectives=list(data.get("objectives", [])),
            actions=list(data.get("actions", [])),
            success_criteria=list(data.get("success_criteria", [])),
            status=InterventionStatus(data.get("status", InterventionStatus.PROPOSED.value)),
            diagnostic_report_id=UUID(data["diagnostic_report_id"]) if data.get("diagnostic_report_id") else None,
            risk_notes=list(data.get("risk_notes", [])),
            owner=data.get("owner"),
            created_at=datetime.fromisoformat(data["created_at"]),
            approved_at=datetime.fromisoformat(data["approved_at"]) if data.get("approved_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data.get("cancelled_at") else None,
            cancellation_reason=data.get("cancellation_reason"),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata"),
        )
