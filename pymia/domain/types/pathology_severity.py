"""
PathologySeverity — Severidad clínica de enfermedad organizacional.

Doctrina fuente: PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
"""

from enum import Enum


class PathologySeverity(Enum):
    """Nivel de severidad de la enfermedad."""

    LEVE = "leve"
    MODERADA = "moderada"
    GRAVE = "grave"
    CRITICA = "critica"
