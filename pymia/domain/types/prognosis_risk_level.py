"""PrognosisRiskLevel — Nivel de riesgo pronóstico."""

from enum import Enum


class PrognosisRiskLevel(Enum):
    """Niveles de riesgo pronóstico."""

    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"
