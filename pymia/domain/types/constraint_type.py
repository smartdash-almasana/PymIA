"""
ConstraintType - Tipos de restricción organizacional

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §7
"""
from enum import Enum


class ConstraintType(Enum):
    """
    8 tipos de restricción que limitan la operación de una PyME.
    
    CAJA: dinero disponible
    TIEMPO: horas-hombre disponibles
    CAPACIDAD: límite de producción/atención
    ATENCION: capacidad de procesar decisiones
    INFORMACION: qué sabe y qué no sabe
    REGULATORIA: qué puede hacer legalmente
    MERCADO: qué demanda existe
    CREDITO: cuánto puede endeudarse
    """
    CAJA = "caja"
    TIEMPO = "tiempo"
    CAPACIDAD = "capacidad"
    ATENCION = "atencion"
    INFORMACION = "informacion"
    REGULATORIA = "regulatoria"
    MERCADO = "mercado"
    CREDITO = "credito"
