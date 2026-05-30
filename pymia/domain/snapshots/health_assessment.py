"""
HealthAssessment — Snapshot de salud organizacional (Capa 4).

Doctrina: PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md

Snapshot inmutable que compone exactamente 7 FunctionalOrgan (uno por
cada FunctionalOrganType) evaluados en un instante temporal. Deriva
global_score (promedio) y clinical_classification según reglas
doctrinales de prioridad.

Es frozen dataclass: la salud cambia creando un nuevo assessment,
no mutando el existente. Esto permite historial clínico.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.primitives.functional_organ import FunctionalOrgan
from pymia.domain.types.functional_organ_type import FunctionalOrganType
from pymia.domain.types.health_classification import HealthClassification


# Umbral doctrinal: score global por debajo del cual la organización
# se considera frágil incluso si ningún órgano individual está en enfermo
FRAGILE_GLOBAL_SCORE_THRESHOLD = 60.0

# Número exacto de órganos que debe tener un assessment completo
REQUIRED_ORGAN_COUNT = 7


@dataclass(frozen=True)
class HealthAssessment:
    """
    Snapshot inmutable de salud organizacional.

    Compone exactamente 7 FunctionalOrgan (uno por tipo) y deriva
    global_score y clinical_classification. Al ser frozen, la
    evolución temporal se captura creando nuevos assessments.
    """

    id: UUID
    organization_id: Optional[UUID]
    organs: List[FunctionalOrgan]
    assessed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    assessor: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validación de invariantes de dominio."""
        # 1. organs debe tener exactamente 7 elementos
        if not self.organs or len(self.organs) != REQUIRED_ORGAN_COUNT:
            raise ValueError(
                f"organs debe tener exactamente {REQUIRED_ORGAN_COUNT} "
                f"elementos, recibió {len(self.organs) if self.organs else 0}"
            )

        # 2. Todos deben ser FunctionalOrgan
        for organ in self.organs:
            if not isinstance(organ, FunctionalOrgan):
                raise ValueError(
                    f"Todos los elementos de organs deben ser "
                    f"FunctionalOrgan, recibió {type(organ).__name__}"
                )

        # 3. Cada FunctionalOrganType debe estar representado exactamente una vez
        organ_types = [o.organ_type for o in self.organs]
        if len(organ_types) != len(set(organ_types)):
            raise ValueError(
                "organs no puede contener dos órganos del mismo organ_type"
            )
        expected_types = set(FunctionalOrganType)
        actual_types = set(organ_types)
        if actual_types != expected_types:
            missing = expected_types - actual_types
            raise ValueError(
                f"organs debe contener exactamente un órgano por cada "
                f"FunctionalOrganType. Faltan: "
                f"{[t.value for t in missing]}"
            )

        # 4. assessed_at debe ser timezone-aware
        if self.assessed_at.tzinfo is None or self.assessed_at.utcoffset() is None:
            raise ValueError("assessed_at debe ser timezone-aware")

        # 5. assessor, si está seteado, no puede estar vacío
        if self.assessor is not None and not self.assessor.strip():
            raise ValueError("assessor no puede estar vacío")

    # ---- Properties derivadas ----

    @property
    def global_score(self) -> float:
        """Promedio de capacity_score de los 7 órganos."""
        return sum(o.capacity_score for o in self.organs) / len(self.organs)

    @property
    def clinical_classification(self) -> HealthClassification:
        """
        Clasificación clínica derivada con prioridad doctrinal:
        1. Si algún órgano está en 'critico' -> CRITICO
        2. Si algún órgano está en 'enfermo' -> ENFERMO
        3. Si global_score < 60 o algún órgano en 'fragil' -> FRAGIL
        4. En otro caso -> SANO
        """
        states = {o.state for o in self.organs}
        if "critico" in states:
            return HealthClassification.CRITICO
        if "enfermo" in states:
            return HealthClassification.ENFERMO
        if self.global_score < FRAGILE_GLOBAL_SCORE_THRESHOLD or "fragil" in states:
            return HealthClassification.FRAGIL
        return HealthClassification.SANO

    # ---- Queries ----

    def critical_organs(self) -> List[FunctionalOrgan]:
        """Órganos con state == 'critico'."""
        return [o for o in self.organs if o.state == "critico"]

    def unhealthy_organs(self) -> List[FunctionalOrgan]:
        """Órganos con state in ('enfermo', 'critico')."""
        return [o for o in self.organs if o.state in ("enfermo", "critico")]

    def fragile_organs(self) -> List[FunctionalOrgan]:
        """Órganos con state == 'fragil'."""
        return [o for o in self.organs if o.state == "fragil"]

    def healthy_organs(self) -> List[FunctionalOrgan]:
        """Órganos con state == 'sano'."""
        return [o for o in self.organs if o.state == "sano"]

    def get_organ(self, organ_type: FunctionalOrganType) -> FunctionalOrgan:
        """
        Busca un órgano por tipo. Siempre retorna un FunctionalOrgan
        porque la invariante garantiza que los 7 tipos están presentes.
        """
        for organ in self.organs:
            if organ.organ_type == organ_type:
                return organ
        raise ValueError(f"Órgano de tipo {organ_type.value} no encontrado")

    # ---- Serialización ----

    def to_dict(self) -> Dict[str, Any]:
        """Serialización JSON-compatible."""
        return {
            "id": str(self.id),
            "organization_id": (
                str(self.organization_id) if self.organization_id else None
            ),
            "organs": [o.to_dict() for o in self.organs],
            "assessed_at": self.assessed_at.isoformat(),
            "assessor": self.assessor,
            "notes": self.notes,
            "global_score": self.global_score,
            "clinical_classification": self.clinical_classification.value,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthAssessment":
        """Reconstrucción desde diccionario."""
        return cls(
            id=UUID(data["id"]),
            organization_id=(
                UUID(data["organization_id"])
                if data.get("organization_id")
                else None
            ),
            organs=[FunctionalOrgan.from_dict(o) for o in data["organs"]],
            assessed_at=datetime.fromisoformat(data["assessed_at"]),
            assessor=data.get("assessor"),
            notes=data.get("notes"),
            metadata=data.get("metadata"),
        )
