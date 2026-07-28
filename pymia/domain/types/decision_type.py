"""
DecisionType enum - Tipos de decisión organizacional.

Doctrina: PYMIA_DECISION_QUALITY_THEORY.md
"""

from enum import Enum


class DecisionType(Enum):
    """Tipo de decisión según su naturaleza organizacional."""
    
    ESTRATEGICA = "estrategica"
    OPERATIVA = "operativa"
    FINANCIERA = "financiera"
    COMERCIAL = "comercial"
    HUMANA = "humana"
    REGULATORIA = "regulatoria"
