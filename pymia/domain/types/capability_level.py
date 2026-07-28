"""
CapabilityLevel - Niveles de capacidad organizacional

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §9
"""
from enum import Enum


class CapabilityLevel(Enum):
    """
    4 niveles de capacidad organizacional.
    
    DECLARADA: lo que el dueño dice que puede hacer
    OBSERVADA: lo que la evidencia muestra que hace
    LATENTE: lo que podría hacer si activara recursos ociosos
    LIMITE: el techo real antes de colapsar
    """
    DECLARADA = "declarada"
    OBSERVADA = "observada"
    LATENTE = "latente"
    LIMITE = "limite"
