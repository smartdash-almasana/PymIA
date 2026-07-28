"""GovernanceFormalityLevel — Nivel de formalización de gobernanza."""

from enum import Enum


class GovernanceFormalityLevel(Enum):
    """Niveles de formalización de la infraestructura de gobernanza."""

    INFORMAL = "informal"
    PARCIAL = "parcial"
    FORMAL = "formal"
    INSTITUCIONALIZADA = "institucionalizada"
