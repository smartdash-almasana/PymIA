"""
PathologyStage — Temporalidad de enfermedad organizacional.

Doctrina fuente: PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
"""

from enum import Enum


class PathologyStage(Enum):
    """Estado temporal de la enfermedad."""

    AGUDA = "aguda"
    CRONICA = "cronica"
