"""
OrganizationalConstraint - Restricción organizacional

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §7

Límite real dentro del cual la organización opera.
Las restricciones no se eliminan, se navegan.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, Union
from uuid import UUID

from pymia.domain.types import ConstraintType


@dataclass(frozen=True)
class OrganizationalConstraint:
    """
    Restricción organizacional - límite real de operación.

    Value object inmutable que representa una restricción activa.

    Invariantes de dominio:
    - constraint_type debe ser ConstraintType válido
    - magnitude: si es numérico debe ser >= 0; si es string no puede estar vacío
    - description no puede estar vacía

    Ejemplo:
        constraint = OrganizationalConstraint(
            id=uuid4(),
            constraint_type=ConstraintType.CAJA,
            magnitude="150000 ARS",
            description="Caja disponible para operación mensual",
            observed_at=datetime.utcnow(),
        )
    """
    id: UUID
    constraint_type: ConstraintType
    magnitude: Union[str, int, float]
    description: str
    observed_at: datetime
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if not isinstance(self.constraint_type, ConstraintType):
            raise ValueError(
                f"constraint_type debe ser ConstraintType, "
                f"recibió {type(self.constraint_type).__name__}"
            )
        if isinstance(self.magnitude, (int, float)):
            if self.magnitude < 0:
                raise ValueError(
                    f"magnitude numérica debe ser >= 0, "
                    f"recibió {self.magnitude}"
                )
        elif isinstance(self.magnitude, str):
            if not self.magnitude.strip():
                raise ValueError(
                    "magnitude string no puede estar vacía"
                )
        else:
            raise ValueError(
                f"magnitude debe ser str, int o float, "
                f"recibió {type(self.magnitude).__name__}"
            )
        if not self.description or not self.description.strip():
            raise ValueError(
                "OrganizationalConstraint requiere descripción no vacía"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "constraint_type": self.constraint_type.value,
            "magnitude": self.magnitude,
            "description": self.description,
            "observed_at": self.observed_at.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationalConstraint":
        """Reconstrucción desde diccionario serializado."""
        return cls(
            id=UUID(data["id"]),
            constraint_type=ConstraintType(data["constraint_type"]),
            magnitude=data["magnitude"],
            description=data["description"],
            observed_at=datetime.fromisoformat(data["observed_at"]),
            metadata=data.get("metadata", {}) or {},
        )

    def same_business_value_as(self, other: object) -> bool:
        """Compara contenido de negocio ignorando identidad técnica."""
        if not isinstance(other, OrganizationalConstraint):
            return False
        return (
            self.constraint_type == other.constraint_type
            and self.magnitude == other.magnitude
            and self.description == other.description
        )
