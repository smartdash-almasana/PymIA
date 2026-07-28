"""
OrganizationalDependency - Dependencia organizacional

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §9

Condición externa necesaria para operar.
Las dependencias son vulnerabilidades estructurales.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import UUID


# Criticalidades admitidas (no se usa enum para mantener simplicidad M2)
VALID_CRITICALITIES = ("baja", "media", "alta", "critica")


@dataclass(frozen=True)
class OrganizationalDependency:
    """
    Dependencia organizacional - vulnerabilidad estructural.

    Value object inmutable que representa una dependencia externa.

    Invariantes de dominio:
    - dependency_type no puede estar vacío
    - criticality debe estar en VALID_CRITICALITIES
    - dependency_target no puede estar vacío
    - description no puede estar vacía

    Ejemplo:
        dependency = OrganizationalDependency(
            id=uuid4(),
            dependency_type="cliente_concentrado",
            criticality="critica",
            dependency_target="Cliente Mayorista SA",
            description="Representa 55% de ingresos",
        )
    """
    id: UUID
    dependency_type: str
    criticality: str
    dependency_target: str
    description: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if not self.dependency_type or not self.dependency_type.strip():
            raise ValueError(
                "OrganizationalDependency requiere dependency_type no vacío"
            )
        if self.criticality not in VALID_CRITICALITIES:
            raise ValueError(
                f"criticality debe estar en {VALID_CRITICALITIES}, "
                f"recibió '{self.criticality}'"
            )
        if not self.dependency_target or not self.dependency_target.strip():
            raise ValueError(
                "OrganizationalDependency requiere dependency_target no vacío"
            )
        if not self.description or not self.description.strip():
            raise ValueError(
                "OrganizationalDependency requiere descripción no vacía"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "dependency_type": self.dependency_type,
            "criticality": self.criticality,
            "dependency_target": self.dependency_target,
            "description": self.description,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationalDependency":
        """Reconstrucción desde diccionario serializado."""
        return cls(
            id=UUID(data["id"]),
            dependency_type=data["dependency_type"],
            criticality=data["criticality"],
            dependency_target=data["dependency_target"],
            description=data["description"],
            metadata=data.get("metadata", {}) or {},
        )

    def same_business_value_as(self, other: object) -> bool:
        """Compara contenido de negocio ignorando identidad técnica."""
        if not isinstance(other, OrganizationalDependency):
            return False
        return (
            self.dependency_type == other.dependency_type
            and self.criticality == other.criticality
            and self.dependency_target == other.dependency_target
            and self.description == other.description
        )
