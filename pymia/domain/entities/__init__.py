"""
Domain entities - Capas 2 y 3.

Entidades con identidad propia (UUID) y ciclo de vida mutable.

Capa 2 (organizacional):
- OrganizationProfile: perfil del tenant (5 dimensiones estructurales)
- OrganizationalIdentity: identidad persistente (4 identidades + 3 capas)

Capa 3 (epistémica):
- KnowledgeItem: unidad atómica de conocimiento con ciclo de vida
"""

from pymia.domain.entities.organization_profile import OrganizationProfile
from pymia.domain.entities.organizational_identity import OrganizationalIdentity
from pymia.domain.entities.knowledge_item import KnowledgeItem

__all__ = ["OrganizationProfile", "OrganizationalIdentity", "KnowledgeItem"]
