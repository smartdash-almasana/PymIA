"""InterventionPriority — Prioridad clínica-operativa de intervención."""

from enum import Enum


class InterventionPriority(Enum):
    """Prioridad de un plan de intervención."""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
