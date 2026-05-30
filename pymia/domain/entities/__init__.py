"""
Domain entities - Capas 2 y 3.

Entidades con identidad propia (UUID) y ciclo de vida mutable.

Capa 2 (organizacional):
- OrganizationProfile: perfil del tenant (5 dimensiones estructurales)
- OrganizationalIdentity: identidad persistente (4 identidades + 3 capas)

Capa 3 (epistémica):
- KnowledgeItem: unidad atómica de conocimiento con ciclo de vida
- DecisionRecord: registro de decisión con ciclo propuesta→decisión→ejecución→evaluación
"""

from pymia.domain.entities.organization_profile import OrganizationProfile
from pymia.domain.entities.organizational_identity import OrganizationalIdentity
from pymia.domain.entities.knowledge_item import KnowledgeItem
from pymia.domain.entities.decision_record import DecisionRecord

__all__ = ["OrganizationProfile", "OrganizationalIdentity", "KnowledgeItem", "DecisionRecord"]
