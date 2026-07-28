"""GovernanceProfile — Entidad estructural de gobernanza organizacional."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.decision_authority_type import DecisionAuthorityType
from pymia.domain.types.governance_formality_level import GovernanceFormalityLevel


@dataclass
class GovernanceProfile:
    """Infraestructura mínima de coherencia organizacional."""

    id: UUID
    organization_id: UUID
    authority_type: DecisionAuthorityType
    formality_level: GovernanceFormalityLevel
    decision_makers: List[str]
    decision_scope_by_maker: Dict[str, List[str]]
    decision_processes: List[str]
    coherence_mechanisms: List[str]
    review_cadence: str
    deviation_detection_method: Optional[str] = None
    correction_process_description: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.organization_id:
            raise ValueError("organization_id es obligatorio")
        if not isinstance(self.authority_type, DecisionAuthorityType):
            raise ValueError("authority_type debe ser DecisionAuthorityType")
        if not isinstance(self.formality_level, GovernanceFormalityLevel):
            raise ValueError("formality_level debe ser GovernanceFormalityLevel")
        self._validate_text_list(self.decision_makers, "decision_makers")
        self._validate_scope_map()
        self._validate_text_list(self.decision_processes, "decision_processes")
        self._validate_text_list(self.coherence_mechanisms, "coherence_mechanisms")
        if not self.review_cadence or len(self.review_cadence.strip()) < 3:
            raise ValueError("review_cadence debe tener mínimo 3 caracteres")
        self._validate_optional_long_text(self.deviation_detection_method, "deviation_detection_method")
        self._validate_optional_long_text(self.correction_process_description, "correction_process_description")
        self._validate_authority_distribution()
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
    def _validate_optional_long_text(value: Optional[str], field_name: str) -> None:
        if value is not None:
            if not value.strip():
                raise ValueError(f"{field_name} no puede estar vacío")
            if len(value.strip()) < 10:
                raise ValueError(f"{field_name} debe tener mínimo 10 caracteres")

    def _validate_scope_map(self) -> None:
        if not self.decision_scope_by_maker:
            raise ValueError("decision_scope_by_maker no puede estar vacío")
        makers = set(self.decision_makers)
        for maker, scopes in self.decision_scope_by_maker.items():
            if maker not in makers:
                raise ValueError("decision_scope_by_maker contiene maker no declarado")
            self._validate_text_list(scopes, f"decision_scope_by_maker[{maker}]")
        if not set(self.decision_scope_by_maker).issubset(makers):
            raise ValueError("decision_scope_by_maker contiene makers inválidos")

    def _validate_authority_distribution(self) -> None:
        if self.authority_type == DecisionAuthorityType.CENTRALIZADA and len(self.decision_makers) != 1:
            raise ValueError("authority_type centralizada requiere exactamente un decision maker")
        if self.authority_type in (DecisionAuthorityType.DISTRIBUIDA, DecisionAuthorityType.CONSULTIVA, DecisionAuthorityType.CONSENSUAL) and len(self.decision_makers) < 2:
            raise ValueError(f"authority_type {self.authority_type.value} requiere al menos dos decision makers")

    def _validate_temporal_coherence(self) -> None:
        self._require_timezone_aware(self.created_at, "created_at")
        self._require_timezone_aware(self.updated_at, "updated_at")
        if self.last_reviewed_at is not None:
            self._require_timezone_aware(self.last_reviewed_at, "last_reviewed_at")
            if self.last_reviewed_at < self.created_at:
                raise ValueError("last_reviewed_at debe ser >= created_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")

    def _revalidate_after_mutation(self) -> None:
        self.__post_init__()

    def update_authority(
        self,
        authority_type: DecisionAuthorityType,
        decision_makers: List[str],
        decision_scope_by_maker: Dict[str, List[str]],
        updated_at: datetime,
    ) -> None:
        self.authority_type = authority_type
        self.decision_makers = decision_makers
        self.decision_scope_by_maker = decision_scope_by_maker
        self.updated_at = updated_at
        self._revalidate_after_mutation()

    def update_review(
        self,
        last_reviewed_at: datetime,
        deviation_detection_method: Optional[str] = None,
        correction_process_description: Optional[str] = None,
    ) -> None:
        self.last_reviewed_at = last_reviewed_at
        if deviation_detection_method is not None:
            self.deviation_detection_method = deviation_detection_method
        if correction_process_description is not None:
            self.correction_process_description = correction_process_description
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def decision_maker_count(self) -> int:
        return len(self.decision_makers)

    def process_count(self) -> int:
        return len(self.decision_processes)

    def coherence_mechanism_count(self) -> int:
        return len(self.coherence_mechanisms)

    def has_reviewed_governance(self) -> bool:
        return self.last_reviewed_at is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "authority_type": self.authority_type.value,
            "formality_level": self.formality_level.value,
            "decision_makers": list(self.decision_makers),
            "decision_scope_by_maker": {maker: list(scopes) for maker, scopes in self.decision_scope_by_maker.items()},
            "decision_processes": list(self.decision_processes),
            "coherence_mechanisms": list(self.coherence_mechanisms),
            "review_cadence": self.review_cadence,
            "deviation_detection_method": self.deviation_detection_method,
            "correction_process_description": self.correction_process_description,
            "last_reviewed_at": self.last_reviewed_at.isoformat() if self.last_reviewed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceProfile":
        return cls(
            id=UUID(data["id"]),
            organization_id=UUID(data["organization_id"]),
            authority_type=DecisionAuthorityType(data["authority_type"]),
            formality_level=GovernanceFormalityLevel(data["formality_level"]),
            decision_makers=list(data.get("decision_makers", [])),
            decision_scope_by_maker={maker: list(scopes) for maker, scopes in data.get("decision_scope_by_maker", {}).items()},
            decision_processes=list(data.get("decision_processes", [])),
            coherence_mechanisms=list(data.get("coherence_mechanisms", [])),
            review_cadence=data["review_cadence"],
            deviation_detection_method=data.get("deviation_detection_method"),
            correction_process_description=data.get("correction_process_description"),
            last_reviewed_at=datetime.fromisoformat(data["last_reviewed_at"]) if data.get("last_reviewed_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata"),
        )
