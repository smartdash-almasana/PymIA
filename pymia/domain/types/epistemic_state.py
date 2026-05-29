"""
EpistemicState - Estados de conocimiento

Doctrina: PYMIA_EPISTEMIC_CORE.md, PYMIA_KNOWLEDGE_LIFECYCLE_MANAGEMENT.md
"""
from enum import Enum


class EpistemicState(Enum):
    """
    Estados epistémicos de un Knowledge Item.
    
    DECLARED: afirmación sin verificar
    OBSERVED: confirmado por evidencia
    INFERRED: derivado de otros KIs
    VALIDATED: verificado y estable
    REFUTED: contradicho por evidencia
    ARCHIVED: histórico, ya no activo
    """
    DECLARED = "declared"
    OBSERVED = "observed"
    INFERRED = "inferred"
    VALIDATED = "validated"
    REFUTED = "refuted"
    ARCHIVED = "archived"
