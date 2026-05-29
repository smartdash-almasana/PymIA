"""
TensionType - Trade-offs permanentes en PyMEs

Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §8
"""
from enum import Enum


class TensionType(Enum):
    """
    10 tensiones estructurales que las PyMEs deben navegar sin resolver.
    
    Las tensiones no se eliminan, se equilibran.
    """
    CRECER_VS_MANTENER_CAJA = "crecer_vs_mantener_caja"
    VOLUMEN_VS_RENTABILIDAD = "volumen_vs_rentabilidad"
    VELOCIDAD_VS_ORDEN = "velocidad_vs_orden"
    CALIDAD_VS_COSTO = "calidad_vs_costo"
    CORTO_VS_LARGO_PLAZO = "corto_vs_largo_plazo"
    DELEGAR_VS_CONTROLAR = "delegar_vs_controlar"
    ESPECIALIZAR_VS_DIVERSIFICAR = "especializar_vs_diversificar"
    FABRICAR_VS_REVENDER = "fabricar_vs_revender"
    PRECIO_VS_VOLUMEN = "precio_vs_volumen"
    TRANSPARENCIA_VS_PROTECCION = "transparencia_vs_proteccion"
