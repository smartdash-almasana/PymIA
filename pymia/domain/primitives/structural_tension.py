"""
StructuralTension - Tensión estructural organizacional

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §8

Trade-off permanente que la organización debe navegar sin resolver.
Las tensiones no se resuelven, se equilibran.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import UUID

from pymia.domain.types import TensionType


@dataclass(frozen=True)
class StructuralTension:
    """
    Tensión estructural - trade-off permanente.

    Value object inmutable que representa una tensión activa.

    Invariantes de dominio:
    - tension_type debe ser TensionType válido
    - pole_a_intensity y pole_b_intensity en rango [0, 10]
    - description no puede estar vacía

    Ejemplo:
        tension = StructuralTension(
            id=uuid4(),
            tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
            pole_a_intensity=7,
            pole_b_intensity=4,
            description="Presión por volumen vs necesidad de margen",
        )
    """
    id: UUID
    tension_type: TensionType
    pole_a_intensity: int
    pole_b_intensity: int
    description: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if not isinstance(self.tension_type, TensionType):
            raise ValueError(
                f"tension_type debe ser TensionType, "
                f"recibió {type(self.tension_type).__name__}"
            )
        if not (0 <= self.pole_a_intensity <= 10):
            raise ValueError(
                f"pole_a_intensity debe estar en [0, 10], "
                f"recibió {self.pole_a_intensity}"
            )
        if not (0 <= self.pole_b_intensity <= 10):
            raise ValueError(
                f"pole_b_intensity debe estar en [0, 10], "
                f"recibió {self.pole_b_intensity}"
            )
        if not self.description or not self.description.strip():
            raise ValueError(
                "StructuralTension requiere descripción no vacía"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "tension_type": self.tension_type.value,
            "pole_a_intensity": self.pole_a_intensity,
            "pole_b_intensity": self.pole_b_intensity,
            "description": self.description,
            "metadata": self.metadata or {},
        }
