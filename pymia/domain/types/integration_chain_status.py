"""IntegrationChainStatus — Estado de integración de una cadena de dominio."""

from enum import Enum


class IntegrationChainStatus(Enum):
    """Estados posibles de completitud de cadenas de dominio."""

    COMPLETA = "completa"
    PARCIAL = "parcial"
    BLOQUEADA = "bloqueada"
    DIFERIDA = "diferida"
