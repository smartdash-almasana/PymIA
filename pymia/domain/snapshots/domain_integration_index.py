"""DomainIntegrationIndex — Snapshot de cierre e integración del núcleo dominio V1."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.integration_chain_status import IntegrationChainStatus


@dataclass(frozen=True)
class DomainIntegrationIndex:
    """Índice inmutable de integración del núcleo de dominio V1."""

    id: UUID
    integration_summary: str
    completed_chains: Dict[str, IntegrationChainStatus]
    open_gaps: List[str]
    included_entity_ids: List[UUID] = field(default_factory=list)
    included_snapshot_ids: List[UUID] = field(default_factory=list)
    included_knowledge_item_ids: List[UUID] = field(default_factory=list)
    organization_id: Optional[UUID] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.integration_summary or len(self.integration_summary.strip()) < 10:
            raise ValueError("integration_summary debe tener mínimo 10 caracteres")
        self._validate_chain_map()
        self._validate_text_list(self.open_gaps, "open_gaps", allow_empty=True)
        self._validate_uuid_list(self.included_entity_ids, "included_entity_ids")
        self._validate_uuid_list(self.included_snapshot_ids, "included_snapshot_ids")
        self._validate_uuid_list(self.included_knowledge_item_ids, "included_knowledge_item_ids")
        self._require_timezone_aware(self.generated_at, "generated_at")
        if self.generated_by is not None and not self.generated_by.strip():
            raise ValueError("generated_by no puede estar vacío")

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    @staticmethod
    def _validate_uuid_list(values: List[UUID], field_name: str) -> None:
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

    def _validate_chain_map(self) -> None:
        if not self.completed_chains:
            raise ValueError("completed_chains no puede estar vacío")
        for name, status in self.completed_chains.items():
            if not name or not name.strip():
                raise ValueError("completed_chains no puede contener nombres vacíos")
            if not isinstance(status, IntegrationChainStatus):
                raise ValueError("completed_chains debe mapear a IntegrationChainStatus")

    def is_v1_closed(self) -> bool:
        return all(status == IntegrationChainStatus.COMPLETA for status in self.completed_chains.values()) and not self.open_gaps

    def has_open_gaps(self) -> bool:
        return bool(self.open_gaps)

    def chain_count(self) -> int:
        return len(self.completed_chains)

    def entity_count(self) -> int:
        return len(self.included_entity_ids)

    def snapshot_count(self) -> int:
        return len(self.included_snapshot_ids)

    def knowledge_item_count(self) -> int:
        return len(self.included_knowledge_item_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "integration_summary": self.integration_summary,
            "completed_chains": {name: status.value for name, status in self.completed_chains.items()},
            "open_gaps": list(self.open_gaps),
            "included_entity_ids": [str(value) for value in self.included_entity_ids],
            "included_snapshot_ids": [str(value) for value in self.included_snapshot_ids],
            "included_knowledge_item_ids": [str(value) for value in self.included_knowledge_item_ids],
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainIntegrationIndex":
        return cls(
            id=UUID(data["id"]),
            integration_summary=data["integration_summary"],
            completed_chains={
                name: IntegrationChainStatus(status)
                for name, status in data.get("completed_chains", {}).items()
            },
            open_gaps=list(data.get("open_gaps", [])),
            included_entity_ids=[UUID(value) for value in data.get("included_entity_ids", [])],
            included_snapshot_ids=[UUID(value) for value in data.get("included_snapshot_ids", [])],
            included_knowledge_item_ids=[UUID(value) for value in data.get("included_knowledge_item_ids", [])],
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            generated_at=datetime.fromisoformat(data["generated_at"]),
            generated_by=data.get("generated_by"),
            metadata=data.get("metadata"),
        )
