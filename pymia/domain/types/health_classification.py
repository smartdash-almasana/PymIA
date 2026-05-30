"""
HealthClassification — Clasificación clínica derivada de un HealthAssessment.

Doctrina: PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md

Enum de 4 valores que clasifica el estado global de una organización
a partir del estado de sus 7 órganos funcionales.

Reglas de derivación (orden de prioridad):
1. Si algún órgano está en "critico" -> CRITICO
2. Si algún órgano está en "enfermo" -> ENFERMO
3. Si global_score < 60 o algún órgano en "fragil" -> FRAGIL
4. En otro caso -> SANO
"""

from enum import Enum


class HealthClassification(Enum):
    """Clasificación clínica global derivada de un HealthAssessment."""

    SANO = "sano"
    FRAGIL = "fragil"
    ENFERMO = "enfermo"
    CRITICO = "critico"
