"""
FunctionalOrganType - Tipos de órganos funcionales de la organización

Doctrina: PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md §4

Siete órganos funcionales (analogía biológica):
- CIRCULATORIO:    Caja / flujo de dinero
- RESPIRATORIO:    Ventas / ingresos (oxígeno organizacional)
- DIGESTIVO:       Operaciones / transformación de insumos
- NERVIOSO:        Decisión / información
- SENSORIAL:       Lectura de entorno / mercado
- INMUNOLOGICO:    Riesgos / defensas
- REPRODUCTIVO:    Aprendizaje / evolución
"""
from enum import Enum


class FunctionalOrganType(Enum):
    """
    Tipos de órganos funcionales de la organización.

    Cada órgano representa una función vital que debe evaluarse
    para determinar la salud organizacional. Los 7 órganos son
    cerrados según HEALTH_MODEL §4.
    """
    CIRCULATORIO = "circulatorio"
    RESPIRATORIO = "respiratorio"
    DIGESTIVO = "digestivo"
    NERVIOSO = "nervioso"
    SENSORIAL = "sensorial"
    INMUNOLOGICO = "inmunologico"
    REPRODUCTIVO = "reproductivo"
