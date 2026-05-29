"""
IdentityCrisis - Crisis de identidad organizacional

Doctrina: PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md §5

Divergencia severa y creciente entre las cuatro identidades
(declarada, observada, deseada, percibida) que compromete
la coherencia organizacional.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from uuid import UUID

from pymia.domain.types.identity_layer import IdentityLayer


# Tipos de crisis de identidad según doctrina
VALID_CRISIS_TYPES = (
    "negacion",       # divergencia declarada vs observada
    "frustracion",    # divergencia deseada vs observada
    "reputacion",     # divergencia declarada vs percibida
    "proposito",      # divergencia múltiple entre todas
)


@dataclass(frozen=True)
class IdentityCrisis:
    """
    Crisis de identidad - divergencia severa entre identidades.

    Value object inmutable que representa una crisis de identidad.

    Invariantes de dominio:
    - crisis_type debe estar en VALID_CRISIS_TYPES
    - affected_layers no puede estar vacío
    - severity en rango [1, 10]
    - description no puede estar vacía

    Ejemplo:
        crisis = IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
            severity=7,
            description="La organización declara ser premium pero compite por precio",
        )
    """
    id: UUID
    crisis_type: str
    affected_layers: List[IdentityLayer]
    severity: int
    description: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if self.crisis_type not in VALID_CRISIS_TYPES:
            raise ValueError(
                f"crisis_type debe estar en {VALID_CRISIS_TYPES}, "
                f"recibió '{self.crisis_type}'"
            )
        if not self.affected_layers or len(self.affected_layers) == 0:
            raise ValueError(
                "IdentityCrisis requiere affected_layers no vacío"
            )
        for layer in self.affected_layers:
            if not isinstance(layer, IdentityLayer):
                raise ValueError(
                    f"affected_layers debe contener IdentityLayer, "
                    f"recibió {type(layer).__name__}"
                )
        if not (1 <= self.severity <= 10):
            raise ValueError(
                f"severity debe estar en [1, 10], "
                f"recibió {self.severity}"
            )
        if not self.description or not self.description.strip():
            raise ValueError(
                "IdentityCrisis requiere descripción no vacía"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "crisis_type": self.crisis_type,
            "affected_layers": [layer.value for layer in self.affected_layers],
            "severity": self.severity,
            "description": self.description,
            "metadata": self.metadata or {},
        }
