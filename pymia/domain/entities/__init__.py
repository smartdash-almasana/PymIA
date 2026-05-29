"""
Domain entities - Capa 2.

Entidades con identidad propia (UUID) y ciclo de vida mutable.
"""

from pymia.domain.entities.organization_profile import OrganizationProfile
from pymia.domain.entities.organizational_identity import OrganizationalIdentity

__all__ = ["OrganizationProfile", "OrganizationalIdentity"]
