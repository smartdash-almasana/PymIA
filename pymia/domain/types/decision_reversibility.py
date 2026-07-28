"""
DecisionReversibility enum - Reversibilidad de decisiones.

Doctrina: PYMIA_DECISION_QUALITY_THEORY.md
"""

from enum import Enum


class DecisionReversibility(Enum):
    """Grado de reversibilidad de una decisión."""
    
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"
    PARCIALMENTE_REVERSIBLE = "parcialmente_reversible"
