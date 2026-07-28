"""
AttributionType — Tipo de atribución causal en un ciclo de aprendizaje.

Doctrina fuente: PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md
"""

from enum import Enum


class AttributionType(Enum):
    """Tipo de atribución causal del resultado observado."""

    INTERNA = "interna"
    EXTERNA = "externa"
    MIXTA = "mixta"
    AZAR = "azar"
