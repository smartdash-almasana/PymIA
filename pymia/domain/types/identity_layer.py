"""
IdentityLayer - Capas estructurales de la identidad organizacional

Doctrina: PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md §3

Tres capas estructurales:
- NUCLEO_PERSISTENTE: lo que no puede cambiar sin perder identidad
- CAPA_ADAPTABLE: lo que puede cambiar coherentemente
- CAPA_PERIFERICA: lo que cambia constantemente sin afectar identidad
"""
from enum import Enum


class IdentityLayer(Enum):
    """
    Capas estructurales de la identidad organizacional.

    NUCLEO_PERSISTENTE: valores fundamentales, capacidades distintivas,
                        relaciones críticas, forma característica de operar
    CAPA_ADAPTABLE:     estrategia comercial, mix de productos, canales,
                        tecnología operativa, estructura organizacional
    CAPA_PERIFERICA:    precios específicos, campañas, proveedores no críticos,
                        empleados no clave, herramientas menores
    """
    NUCLEO_PERSISTENTE = "nucleo_persistente"
    CAPA_ADAPTABLE = "capa_adaptable"
    CAPA_PERIFERICA = "capa_periferica"
