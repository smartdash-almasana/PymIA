"""
OrganizationalPathology — Entidad que modela enfermedad organizacional.

Una patología organizacional es una disfunción de órganos funcionales que
compromete la viabilidad de la organización. Tiene ciclo de vida propio:
emerge, se diagnostica, puede tratarse, y se resuelve o cronifica.

Doctrina fuente: PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.functional_organ_type import FunctionalOrganType
from pymia.domain.types.pathology_severity import PathologySeverity
from pymia.domain.types.pathology_stage import PathologyStage
from pymia.domain.types.pathology_status import PathologyStatus
from pymia.domain.types.pathology_type import PathologyType


@dataclass
class OrganizationalPathology:
    """Enfermedad organizacional (entidad mutable)."""

    # Identificación
    id: UUID
    name: str  # mín 5 caracteres
    description: str  # mín 10 caracteres

    # Clasificación doctrinal
    pathology_type: PathologyType
    severity: PathologySeverity
    stage: PathologyStage
    status: PathologyStatus = PathologyStatus.ACTIVA

    # Manifestación
    affected_organ_types: List[FunctionalOrganType] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)

    # Sustrato epistémico (referencias por UUID)
    evidence_knowledge_item_ids: List[UUID] = field(default_factory=list)

    # Asociación débil
    organization_id: Optional[UUID] = None
    detected_in_assessment_id: Optional[UUID] = None

    # Timestamps timezone-aware
    diagnosed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Optional[datetime] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Razón de resolución (solo si RESUELTA)
    resolution_reason: Optional[str] = None

    # Extensibilidad
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validación de invariantes de dominio."""
        # 1. name mínimo 5 caracteres
        if not self.name or len(self.name.strip()) < 5:
            raise ValueError("name debe tener mínimo 5 caracteres")

        # 2. description mínimo 10 caracteres
        if not self.description or len(self.description.strip()) < 10:
            raise ValueError("description debe tener mínimo 10 caracteres")

        # 3-6. Tipos enum
        if not isinstance(self.pathology_type, PathologyType):
            raise ValueError("pathology_type debe ser PathologyType")
        if not isinstance(self.severity, PathologySeverity):
            raise ValueError("severity debe ser PathologySeverity")
        if not isinstance(self.stage, PathologyStage):
            raise ValueError("stage debe ser PathologyStage")
        if not isinstance(self.status, PathologyStatus):
            raise ValueError("status debe ser PathologyStatus")

        # 7. affected_organ_types no vacío
        if not self.affected_organ_types:
            raise ValueError("affected_organ_types no puede estar vacío")

        # 8. affected_organ_types sin duplicados
        if len(self.affected_organ_types) != len(set(self.affected_organ_types)):
            raise ValueError("affected_organ_types no puede contener duplicados")

        # 9. symptoms sin vacíos ni duplicados
        if self.symptoms:
            if any(not s.strip() for s in self.symptoms):
                raise ValueError("symptoms no puede contener strings vacíos")
            if len(self.symptoms) != len(set(self.symptoms)):
                raise ValueError("symptoms no puede contener duplicados")

        # 10. Si severity in (GRAVE, CRITICA), symptoms no vacío
        if self.severity in (PathologySeverity.GRAVE, PathologySeverity.CRITICA):
            if not self.symptoms:
                raise ValueError(
                    f"severity {self.severity.value} requiere symptoms no vacío"
                )

        # 11. timestamps timezone-aware
        self._require_timezone_aware(self.diagnosed_at, "diagnosed_at")
        self._require_timezone_aware(self.created_at, "created_at")
        self._require_timezone_aware(self.updated_at, "updated_at")
        if self.resolved_at is not None:
            self._require_timezone_aware(self.resolved_at, "resolved_at")

        # 12. Si status == RESUELTA, resolved_at debe estar seteado
        if self.status == PathologyStatus.RESUELTA:
            if self.resolved_at is None:
                raise ValueError("status RESUELTA requiere resolved_at")
            if self.resolved_at < self.diagnosed_at:
                raise ValueError("resolved_at debe ser >= diagnosed_at")

        # CORRECCIÓN 2: Si status == CRONIFICADA, resolved_at debe ser None
        if self.status == PathologyStatus.CRONIFICADA:
            if self.resolved_at is not None:
                raise ValueError("status CRONIFICADA no admite resolved_at")

        # Invariante adicional: si status == CRONIFICADA, stage debe ser CRONICA
        if self.status == PathologyStatus.CRONIFICADA:
            if self.stage != PathologyStage.CRONICA:
                raise ValueError(
                    "status CRONIFICADA requiere stage CRONICA"
                )

        # 14. Coherencia temporal
        if self.diagnosed_at < self.created_at:
            raise ValueError("diagnosed_at debe ser >= created_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    # ---- Métodos de dominio ----

    def mark_resolved(
        self, resolution_reason: str, resolved_at: datetime
    ) -> None:
        """Transición: ACTIVA → RESUELTA."""
        if self.status != PathologyStatus.ACTIVA:
            raise ValueError(
                f"mark_resolved requiere status ACTIVA, "
                f"status actual: {self.status.value}"
            )
        if not resolution_reason or not resolution_reason.strip():
            raise ValueError("resolution_reason no puede estar vacío")

        self.status = PathologyStatus.RESUELTA
        self.resolution_reason = resolution_reason
        self.resolved_at = resolved_at
        self.updated_at = datetime.now(timezone.utc)

    def mark_chronic(self, chronic_at: datetime) -> None:
        """Transición: ACTIVA + AGUDA → CRONIFICADA + CRONICA."""
        if self.status != PathologyStatus.ACTIVA:
            raise ValueError(
                f"mark_chronic requiere status ACTIVA, "
                f"status actual: {self.status.value}"
            )
        if self.stage != PathologyStage.AGUDA:
            raise ValueError(
                f"mark_chronic requiere stage AGUDA, "
                f"stage actual: {self.stage.value}"
            )

        self.status = PathologyStatus.CRONIFICADA
        self.stage = PathologyStage.CRONICA
        self.updated_at = chronic_at

    def reactivate(self, reactivated_at: datetime) -> None:
        """Transición: RESUELTA/CRONIFICADA → ACTIVA."""
        if self.status not in (PathologyStatus.RESUELTA, PathologyStatus.CRONIFICADA):
            raise ValueError(
                f"reactivate requiere status RESUELTA o CRONIFICADA, "
                f"status actual: {self.status.value}"
            )

        self.status = PathologyStatus.ACTIVA
        self.resolved_at = None
        self.resolution_reason = None
        self.updated_at = reactivated_at

    def add_symptom(self, symptom: str) -> None:
        """Agrega síntoma si no está duplicado."""
        if not symptom or not symptom.strip():
            raise ValueError("symptom no puede estar vacío")
        if symptom in self.symptoms:
            raise ValueError(f"symptom '{symptom}' ya existe")

        self.symptoms.append(symptom)
        self.updated_at = datetime.now(timezone.utc)

    def add_evidence(self, ki_id: UUID) -> None:
        """Agrega referencia a KnowledgeItem de evidencia."""
        if ki_id in self.evidence_knowledge_item_ids:
            raise ValueError(f"ki_id {ki_id} ya está en evidence_knowledge_item_ids")

        self.evidence_knowledge_item_ids.append(ki_id)
        self.updated_at = datetime.now(timezone.utc)

    # ---- Serialización ----

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "pathology_type": self.pathology_type.value,
            "severity": self.severity.value,
            "stage": self.stage.value,
            "status": self.status.value,
            "affected_organ_types": [ot.value for ot in self.affected_organ_types],
            "symptoms": self.symptoms,
            "evidence_knowledge_item_ids": [
                str(ki) for ki in self.evidence_knowledge_item_ids
            ],
            "organization_id": (
                str(self.organization_id) if self.organization_id else None
            ),
            "detected_in_assessment_id": (
                str(self.detected_in_assessment_id)
                if self.detected_in_assessment_id
                else None
            ),
            "diagnosed_at": self.diagnosed_at.isoformat(),
            "resolved_at": (
                self.resolved_at.isoformat() if self.resolved_at else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolution_reason": self.resolution_reason,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationalPathology":
        """Reconstrucción desde diccionario."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            description=data["description"],
            pathology_type=PathologyType(data["pathology_type"]),
            severity=PathologySeverity(data["severity"]),
            stage=PathologyStage(data["stage"]),
            status=PathologyStatus(data["status"]),
            affected_organ_types=[
                FunctionalOrganType(ot) for ot in data["affected_organ_types"]
            ],
            symptoms=data.get("symptoms", []),
            evidence_knowledge_item_ids=[
                UUID(ki) for ki in data.get("evidence_knowledge_item_ids", [])
            ],
            organization_id=(
                UUID(data["organization_id"])
                if data.get("organization_id")
                else None
            ),
            detected_in_assessment_id=(
                UUID(data["detected_in_assessment_id"])
                if data.get("detected_in_assessment_id")
                else None
            ),
            diagnosed_at=datetime.fromisoformat(data["diagnosed_at"]),
            resolved_at=(
                datetime.fromisoformat(data["resolved_at"])
                if data.get("resolved_at")
                else None
            ),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            resolution_reason=data.get("resolution_reason"),
            metadata=data.get("metadata"),
        )
