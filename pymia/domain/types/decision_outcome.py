"""
DecisionOutcome enum - Resultados observados de decisiones.

Doctrina: PYMIA_DECISION_QUALITY_THEORY.md
"""

from enum import Enum


class DecisionOutcome(Enum):
    """Resultado observado de una decisión ejecutada."""
    
    PENDIENTE = "pendiente"
    EXITOSO = "exitoso"
    PARCIAL = "parcial"
    FALLIDO = "fallido"
    NO_EVALUABLE = "no_evaluable"
