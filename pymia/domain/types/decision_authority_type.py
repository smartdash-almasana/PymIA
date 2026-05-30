"""DecisionAuthorityType — Tipo de autoridad decisional en gobernanza."""

from enum import Enum


class DecisionAuthorityType(Enum):
    """Tipos de distribución de autoridad decisional."""

    CENTRALIZADA = "centralizada"
    DISTRIBUIDA = "distribuida"
    CONSULTIVA = "consultiva"
    CONSENSUAL = "consensual"
