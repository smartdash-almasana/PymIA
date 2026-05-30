"""
PathologyType — Catálogo doctrinal cerrado de enfermedades organizacionales.

Doctrina fuente: PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
"""

from enum import Enum


class PathologyType(Enum):
    """Tipo de enfermedad organizacional según catálogo doctrinal."""

    MARGEN_EROSIONADO_POR_CANAL = "margen_erosionado_por_canal"
    DEPENDENCIA_CLIENTE_CONCENTRADO = "dependencia_cliente_concentrado"
    DESCAPITALIZACION_SILENCIOSA = "descapitalizacion_silenciosa"
    CENTRALISMO_ASFIXIANTE = "centralismo_asfixiante"
    CRECIMIENTO_NO_DIGESTIDO = "crecimiento_no_digerido"
    ESTANCAMIENTO_ADAPTATIVO = "estancamiento_adaptativo"
    CONFLICTO_SOCIETARIO_LATENTE = "conflicto_societario_latente"
    FATIGA_DECISIONAL_CRONICA = "fatiga_decisional_cronica"
