"""
PathologyStatus — Estado del ciclo de vida de enfermedad organizacional.

Doctrina fuente: PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
"""

from enum import Enum


class PathologyStatus(Enum):
    """Estado del ciclo de vida de la patología."""

    ACTIVA = "activa"
    RESUELTA = "resuelta"
    CRONIFICADA = "cronificada"
