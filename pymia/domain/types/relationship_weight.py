"""
RelationshipWeight - Niveles de peso estructural

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §6
"""
from enum import Enum


class RelationshipWeight(Enum):
    """
    4 niveles de peso estructural de una relación.
    
    BAJO: prescindible
    MEDIO: reemplazable con costo
    ALTO: condiciona la operación
    CRITICO: su pérdida amenaza supervivencia
    """
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"
