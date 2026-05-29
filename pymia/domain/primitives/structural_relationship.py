"""
StructuralRelationship - Relación estructural con peso

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §6

Vínculo de intercambio con consecuencias.
Las relaciones no son contactos, son vínculos con peso estructural.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import UUID

from pymia.domain.types import RelationshipWeight


@dataclass(frozen=True)
class StructuralRelationship:
    """
    Relación estructural - vínculo con peso.

    Value object inmutable que representa una relación entre nodos.

    Invariantes de dominio:
    - source_id != target_id (no auto-relaciones)
    - weight debe ser RelationshipWeight válido
    - relationship_kind no puede estar vacío
    - description no puede estar vacía

    Ejemplo:
        relationship = StructuralRelationship(
            id=uuid4(),
            source_id=uuid_org,
            target_id=uuid_cliente,
            weight=RelationshipWeight.CRITICO,
            relationship_kind="cliente_mayorista",
            description="Cliente que concentra 45% de ingresos",
        )
    """
    id: UUID
    source_id: UUID
    target_id: UUID
    weight: RelationshipWeight
    relationship_kind: str
    description: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if self.source_id == self.target_id:
            raise ValueError(
                "source_id y target_id deben ser distintos "
                "(no se permiten auto-relaciones)"
            )
        if not isinstance(self.weight, RelationshipWeight):
            raise ValueError(
                f"weight debe ser RelationshipWeight, "
                f"recibió {type(self.weight).__name__}"
            )
        if not self.relationship_kind or not self.relationship_kind.strip():
            raise ValueError(
                "StructuralRelationship requiere relationship_kind no vacío"
            )
        if not self.description or not self.description.strip():
            raise ValueError(
                "StructuralRelationship requiere descripción no vacía"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "weight": self.weight.value,
            "relationship_kind": self.relationship_kind,
            "description": self.description,
            "metadata": self.metadata or {},
        }
