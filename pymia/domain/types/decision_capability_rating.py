"""DecisionCapabilityRating — Evaluación agregada de capacidad decisional."""

from enum import Enum


class DecisionCapabilityRating(Enum):
    """Niveles de capacidad decisional organizacional."""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
