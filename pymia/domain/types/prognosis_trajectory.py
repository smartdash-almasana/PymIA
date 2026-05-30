"""PrognosisTrajectory — Trayectoria pronóstica organizacional."""

from enum import Enum


class PrognosisTrajectory(Enum):
    """Trayectorias posibles de evolución organizacional."""

    ESTABLE = "estable"
    MEJORA_GRADUAL = "mejora_gradual"
    RECUPERACION_ACELERADA = "recuperacion_acelerada"
    DETERIORO_GRADUAL = "deterioro_gradual"
    DETERIORO_ACELERADO = "deterioro_acelerado"
    ERRATICA = "erratica"
