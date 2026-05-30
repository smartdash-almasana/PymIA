"""InterventionType — Tipo terapéutico de un plan de intervención."""

from enum import Enum


class InterventionType(Enum):
    """Tipos de intervención organizacional."""

    SINTOMATICA = "sintomatica"
    CURATIVA = "curativa"
    PALIATIVA = "paliativa"
    PREVENTIVA = "preventiva"
