"""DiagnosticReport — Snapshot inmutable de diagnóstico organizacional."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.diagnostic_status import DiagnosticStatus


@dataclass(frozen=True)
class DiagnosticReport:
    """Reporte diagnóstico que conecta salud, patologías y evidencia."""

    id: UUID
    health_assessment_id: UUID
    summary: str
    clinical_conclusion: str
    pathology_ids: List[UUID] = field(default_factory=list)
    evidence_knowledge_item_ids: List[UUID] = field(default_factory=list)
    diagnostic_status: DiagnosticStatus = DiagnosticStatus.PRELIMINAR
    organization_id: Optional[UUID] = None
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    issuer: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.health_assessment_id:
            raise ValueError("health_assessment_id es obligatorio")
        if not self.summary or len(self.summary.strip()) < 10:
            raise ValueError("summary debe tener mínimo 10 caracteres")
        if not self.clinical_conclusion or len(self.clinical_conclusion.strip()) < 10:
            raise ValueError("clinical_conclusion debe tener mínimo 10 caracteres")
        if not isinstance(self.diagnostic_status, DiagnosticStatus):
            raise ValueError("diagnostic_status debe ser DiagnosticStatus")
        if len(self.pathology_ids) != len(set(self.pathology_ids)):
            raise ValueError("pathology_ids no puede contener duplicados")
        if len(self.evidence_knowledge_item_ids) != len(set(self.evidence_knowledge_item_ids)):
            raise ValueError("evidence_knowledge_item_ids no puede contener duplicados")
        self._require_timezone_aware(self.issued_at, "issued_at")
        if self.issuer is not None and not self.issuer.strip():
            raise ValueError("issuer no puede estar vacío")

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    def has_pathologies(self) -> bool:
        return bool(self.pathology_ids)

    def pathology_count(self) -> int:
        return len(self.pathology_ids)

    def evidence_count(self) -> int:
        return len(self.evidence_knowledge_item_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "health_assessment_id": str(self.health_assessment_id),
            "summary": self.summary,
            "clinical_conclusion": self.clinical_conclusion,
            "pathology_ids": [str(pid) for pid in self.pathology_ids],
            "evidence_knowledge_item_ids": [str(kid) for kid in self.evidence_knowledge_item_ids],
            "diagnostic_status": self.diagnostic_status.value,
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "issued_at": self.issued_at.isoformat(),
            "issuer": self.issuer,
            "notes": self.notes,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticReport":
        return cls(
            id=UUID(data["id"]),
            health_assessment_id=UUID(data["health_assessment_id"]),
            summary=data["summary"],
            clinical_conclusion=data["clinical_conclusion"],
            pathology_ids=[UUID(pid) for pid in data.get("pathology_ids", [])],
            evidence_knowledge_item_ids=[UUID(kid) for kid in data.get("evidence_knowledge_item_ids", [])],
            diagnostic_status=DiagnosticStatus(data["diagnostic_status"]),
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            issued_at=datetime.fromisoformat(data["issued_at"]),
            issuer=data.get("issuer"),
            notes=data.get("notes"),
            metadata=data.get("metadata"),
        )
