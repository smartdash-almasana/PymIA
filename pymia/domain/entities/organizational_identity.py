"""
OrganizationalIdentity — Entidad de dominio (Capa 2).

Representa el patrón estructural persistente que hace que una organización
sea reconocible como ella misma a través del tiempo.

Fuente doctrinal: PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from uuid import UUID

from pymia.domain.types.epistemic_state import EpistemicState
from pymia.domain.primitives.identity_crisis import IdentityCrisis


@dataclass
class OrganizationalIdentity:
    """
    Identidad organizacional — entidad núcleo (IDENTITY §2, §3, §5).
    
    Patrón estructural persistente compuesto por:
    - 4 identidades (declarada, observada, deseada, percibida)
    - 3 capas estructurales (núcleo persistente, adaptable, periférica)
    - Crisis activas (divergencias severas entre identidades)
    - Métricas de divergencia (cuantificación de tensión entre identidades)
    
    Entidad mutable con ciclo de vida. Validación en __post_init__ y en métodos
    de mutación.
    """
    
    # Identificación
    id: UUID
    
    # Las 4 identidades (IDENTITY §2)
    identity_declared: str       # lo que dice ser
    identity_observed: str       # lo que la evidencia muestra
    identity_desired: str        # lo que quiere llegar a ser
    identity_perceived: str      # lo que el mercado ve
    
    # Las 3 capas estructurales (IDENTITY §3)
    core_persistent: List[str]         # núcleo persistente (no negociable)
    layer_adaptable: List[str] = field(default_factory=list)
    layer_peripheral: List[str] = field(default_factory=list)
    
    # Crisis activas (IDENTITY §5)
    active_crises: List[IdentityCrisis] = field(default_factory=list)
    
    # Métricas de divergencia (IDENTITY §2.5)
    divergence_declared_observed: float = 0.0    # [0.0, 1.0]
    divergence_desired_observed: float = 0.0
    divergence_perceived_declared: float = 0.0
    
    # Estado epistémico
    epistemic_state: EpistemicState = EpistemicState.DECLARED
    
    # Timestamps timezone-aware
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadata opcional
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validación de invariantes de dominio."""
        # 1-4. Las 4 identidades no vacías (largo mínimo 3)
        if not self.identity_declared or len(self.identity_declared.strip()) < 3:
            raise ValueError(
                "OrganizationalIdentity.identity_declared debe tener al menos 3 caracteres"
            )
        if not self.identity_observed or len(self.identity_observed.strip()) < 3:
            raise ValueError(
                "OrganizationalIdentity.identity_observed debe tener al menos 3 caracteres"
            )
        if not self.identity_desired or len(self.identity_desired.strip()) < 3:
            raise ValueError(
                "OrganizationalIdentity.identity_desired debe tener al menos 3 caracteres"
            )
        if not self.identity_perceived or len(self.identity_perceived.strip()) < 3:
            raise ValueError(
                "OrganizationalIdentity.identity_perceived debe tener al menos 3 caracteres"
            )
        
        # 5. Núcleo persistente no vacío
        if not self.core_persistent or len(self.core_persistent) == 0:
            raise ValueError(
                "OrganizationalIdentity.core_persistent no puede estar vacío"
            )
        
        # 6. Divergencias en rango [0.0, 1.0]
        if not (0.0 <= self.divergence_declared_observed <= 1.0):
            raise ValueError(
                f"divergence_declared_observed debe estar en [0.0, 1.0], "
                f"recibido: {self.divergence_declared_observed}"
            )
        if not (0.0 <= self.divergence_desired_observed <= 1.0):
            raise ValueError(
                f"divergence_desired_observed debe estar en [0.0, 1.0], "
                f"recibido: {self.divergence_desired_observed}"
            )
        if not (0.0 <= self.divergence_perceived_declared <= 1.0):
            raise ValueError(
                f"divergence_perceived_declared debe estar en [0.0, 1.0], "
                f"recibido: {self.divergence_perceived_declared}"
            )
        
        # 7. Crisis sin IDs duplicados
        crisis_ids = [c.id for c in self.active_crises]
        if len(crisis_ids) != len(set(crisis_ids)):
            raise ValueError(
                "OrganizationalIdentity.active_crises no puede contener IDs duplicados"
            )
        
        # 8. Coherencia cruzada: crisis severa requiere divergencia alta
        for crisis in self.active_crises:
            if crisis.severity >= 7 and self.divergence_declared_observed < 0.5:
                raise ValueError(
                    f"Crisis con severity >= 7 requiere divergence_declared_observed >= 0.5, "
                    f"pero divergence={self.divergence_declared_observed}"
                )
        
        # 9. Capas adaptable/periférica: si tienen contenido, no strings vacíos
        if self.layer_adaptable:
            if any(not item.strip() for item in self.layer_adaptable):
                raise ValueError(
                    "OrganizationalIdentity.layer_adaptable no puede contener strings vacíos"
                )
        if self.layer_peripheral:
            if any(not item.strip() for item in self.layer_peripheral):
                raise ValueError(
                    "OrganizationalIdentity.layer_peripheral no puede contener strings vacíos"
                )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "identities": {
                "declared": self.identity_declared,
                "observed": self.identity_observed,
                "desired": self.identity_desired,
                "perceived": self.identity_perceived,
            },
            "layers": {
                "core_persistent": self.core_persistent,
                "adaptable": self.layer_adaptable,
                "peripheral": self.layer_peripheral,
            },
            "active_crises": [c.to_dict() for c in self.active_crises],
            "divergences": {
                "declared_observed": self.divergence_declared_observed,
                "desired_observed": self.divergence_desired_observed,
                "perceived_declared": self.divergence_perceived_declared,
            },
            "epistemic_state": self.epistemic_state.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationalIdentity":
        """Reconstrucción desde diccionario."""
        crises = [
            IdentityCrisis.from_dict(c)
            for c in data.get("active_crises", [])
        ]
        
        return cls(
            id=UUID(data["id"]),
            identity_declared=data["identities"]["declared"],
            identity_observed=data["identities"]["observed"],
            identity_desired=data["identities"]["desired"],
            identity_perceived=data["identities"]["perceived"],
            core_persistent=data["layers"]["core_persistent"],
            layer_adaptable=data["layers"].get("adaptable", []),
            layer_peripheral=data["layers"].get("peripheral", []),
            active_crises=crises,
            divergence_declared_observed=data["divergences"]["declared_observed"],
            divergence_desired_observed=data["divergences"]["desired_observed"],
            divergence_perceived_declared=data["divergences"]["perceived_declared"],
            epistemic_state=EpistemicState(data["epistemic_state"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata"),
        )
    
    def register_crisis(self, crisis: IdentityCrisis) -> None:
        """Registra una crisis activa con validación de unicidad."""
        existing_ids = {c.id for c in self.active_crises}
        if crisis.id in existing_ids:
            raise ValueError(
                f"Ya existe una crisis con ID {crisis.id} en active_crises"
            )
        self.active_crises.append(crisis)
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve_crisis(self, crisis_id: UUID) -> None:
        """Remueve una crisis de la lista de activas."""
        original_len = len(self.active_crises)
        self.active_crises = [c for c in self.active_crises if c.id != crisis_id]
        if len(self.active_crises) == original_len:
            raise ValueError(f"No se encontró crisis con ID {crisis_id}")
        self.updated_at = datetime.now(timezone.utc)
    
    def update_divergences(self) -> None:
        """
        Recalcula divergencias basándose en similitud de strings.
        
        Implementación simplificada: usa diferencia de largo normalizada.
        En producción, esto debería usar NLP o embedding similarity.
        """
        def simple_divergence(s1: str, s2: str) -> float:
            """Divergencia simplificada basada en diferencia de largo."""
            if not s1 or not s2:
                return 1.0
            len_diff = abs(len(s1) - len(s2))
            max_len = max(len(s1), len(s2))
            return min(len_diff / max_len, 1.0)
        
        self.divergence_declared_observed = simple_divergence(
            self.identity_declared, self.identity_observed
        )
        self.divergence_desired_observed = simple_divergence(
            self.identity_desired, self.identity_observed
        )
        self.divergence_perceived_declared = simple_divergence(
            self.identity_perceived, self.identity_declared
        )
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_validated(self) -> None:
        """Cambia estado epistémico a VALIDATED."""
        self.epistemic_state = EpistemicState.VALIDATED
        self.updated_at = datetime.now(timezone.utc)
