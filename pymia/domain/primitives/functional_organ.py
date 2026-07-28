"""
FunctionalOrgan - Órgano funcional evaluado en un momento específico

Doctrina: PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md §4

Value object inmutable que captura el estado de un órgano funcional
en un snapshot temporal. Se compone en HealthAssessment (Capa 4)
para formar la evaluación completa de salud organizacional.

Los 7 órganos funcionales son cerrados (ver FunctionalOrganType).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List

from pymia.domain.types.functional_organ_type import FunctionalOrganType


# Estados válidos de un órgano funcional según HEALTH_MODEL
VALID_ORGAN_STATES = (
    "sano",      # órgano funcionando correctamente
    "fragil",    # funciona pero vulnerable a shocks
    "enfermo",   # disfunción activa, requiere descripción + síntomas
    "critico",   # disfunción grave, requiere descripción + síntomas
)


@dataclass(frozen=True)
class FunctionalOrgan:
    """
    Órgano funcional evaluado en un momento específico.

    Value object inmutable que captura el estado de un órgano funcional
    en un snapshot temporal. No tiene ID propio: se identifica por
    (organ_type, observed_at) dentro de un HealthAssessment.

    Invariantes de dominio:
    - organ_type debe ser FunctionalOrganType
    - state debe estar en VALID_ORGAN_STATES
    - capacity_score en rango [0, 100]
    - observed_at debe ser timezone-aware
    - Si state es "enfermo" o "critico", description no puede estar vacía
    - Si state es "enfermo" o "critico", symptoms no puede estar vacío

    Ejemplo:
        organ = FunctionalOrgan(
            organ_type=FunctionalOrganType.CIRCULATORIO,
            state="sano",
            capacity_score=85.0,
            observed_at=datetime.now(timezone.utc),
            description="Flujo de caja estable con 3 meses de runway",
        )
    """
    organ_type: FunctionalOrganType
    state: str
    capacity_score: float
    observed_at: datetime
    description: str
    symptoms: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de invariantes de dominio."""
        if not isinstance(self.organ_type, FunctionalOrganType):
            raise ValueError(
                f"organ_type debe ser FunctionalOrganType, "
                f"recibió {type(self.organ_type).__name__}"
            )
        if self.state not in VALID_ORGAN_STATES:
            raise ValueError(
                f"state debe estar en {VALID_ORGAN_STATES}, "
                f"recibió '{self.state}'"
            )
        if not (0 <= self.capacity_score <= 100):
            raise ValueError(
                f"capacity_score debe estar en [0, 100], "
                f"recibió {self.capacity_score}"
            )
        if self.observed_at.tzinfo is None:
            raise ValueError(
                "observed_at debe ser timezone-aware"
            )
        if self.state in ("enfermo", "critico"):
            if not self.description or not self.description.strip():
                raise ValueError(
                    f"Órgano en estado '{self.state}' requiere descripción"
                )
            if not self.symptoms:
                raise ValueError(
                    f"Órgano en estado '{self.state}' requiere al menos un síntoma"
                )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialización a diccionario JSON-compatible.

        Returns:
            Dict con todos los campos serializados
        """
        return {
            "organ_type": self.organ_type.value,
            "state": self.state,
            "capacity_score": self.capacity_score,
            "observed_at": self.observed_at.isoformat(),
            "description": self.description,
            "symptoms": list(self.symptoms),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionalOrgan":
        """
        Reconstrucción desde diccionario.

        Args:
            data: Dict previamente serializado con to_dict()

        Returns:
            FunctionalOrgan reconstruido
        """
        return cls(
            organ_type=FunctionalOrganType(data["organ_type"]),
            state=data["state"],
            capacity_score=float(data["capacity_score"]),
            observed_at=datetime.fromisoformat(data["observed_at"]),
            description=data["description"],
            symptoms=data.get("symptoms", []),
            metadata=data.get("metadata", {}) or {},
        )

    def same_business_value_as(self, other: object) -> bool:
        """Compara contenido de negocio ignorando metadatos técnicos."""
        if not isinstance(other, FunctionalOrgan):
            return False
        return (
            self.organ_type == other.organ_type
            and self.state == other.state
            and self.capacity_score == other.capacity_score
            and self.description == other.description
            and self.symptoms == other.symptoms
        )
