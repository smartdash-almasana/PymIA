"""
KnowledgeItem - entidad epistémica de Capa 3.

Unidad atómica de conocimiento con ciclo de vida propio.
Es el sustrato epistémico del sistema: persiste a través de
decisiones y ciclos de aprendizaje.

Trazabilidad doctrinal:
- PYMIA_EPISTEMIC_CORE.md
- PYMIA_KNOWLEDGE_LIFECYCLE_MANAGEMENT.md
- PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md (KnowledgeItem)
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID

from pymia.domain.types.epistemic_state import EpistemicState


# Constantes de dominio
VALID_SOURCES = ("evidence", "hypothesis", "observation", "inference")
MIN_STATEMENT_LENGTH = 10


@dataclass
class KnowledgeItem:
    """
    KnowledgeItem - unidad atómica de conocimiento (EPISTEMIC_CORE).
    
    Entidad mutable con ciclo de vida epistémico propio.
    Puede transicionar entre estados: DECLARED → OBSERVED → INFERRED 
    → VALIDATED → REFUTED → ARCHIVED.
    
    Referenciada por DecisionRecord (M7) y LearningCycle (M8).
    """
    # Identificación
    id: UUID
    
    # Contenido epistémico
    statement: str
    source: str
    evidence: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Estado epistémico
    epistemic_state: EpistemicState = EpistemicState.DECLARED
    confidence: float = 0.5
    
    # Red epistémica
    related_ki_ids: List[UUID] = field(default_factory=list)
    
    # Asociación débil
    tenant_id: Optional[UUID] = None
    
    # Timestamps timezone-aware
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validated_at: Optional[datetime] = None
    refuted_at: Optional[datetime] = None
    
    # Extensibilidad
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validación de invariantes de dominio."""
        # 1. Statement mínimo
        if not self.statement or len(self.statement.strip()) < MIN_STATEMENT_LENGTH:
            raise ValueError(
                f"statement debe tener al menos {MIN_STATEMENT_LENGTH} caracteres"
            )
        
        # 2. Source válido
        if self.source not in VALID_SOURCES:
            raise ValueError(
                f"source debe estar en {VALID_SOURCES}, got {self.source}"
            )
        
        # 3. Confidence en rango
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence debe estar en [0.0, 1.0], got {self.confidence}"
            )
        
        # 4. Evidence requerida para OBSERVED y VALIDATED
        if self.epistemic_state in (EpistemicState.OBSERVED, EpistemicState.VALIDATED):
            if not self.evidence:
                raise ValueError(
                    f"KnowledgeItem en estado {self.epistemic_state.value} requiere evidence no vacía"
                )
        
        # 5. validated_at solo si VALIDATED
        if self.validated_at is not None and self.epistemic_state != EpistemicState.VALIDATED:
            raise ValueError(
                "validated_at solo puede existir si epistemic_state es VALIDATED"
            )
        
        # 6. refuted_at solo si REFUTED
        if self.refuted_at is not None and self.epistemic_state != EpistemicState.REFUTED:
            raise ValueError(
                "refuted_at solo puede existir si epistemic_state es REFUTED"
            )
        
        # 7. related_ki_ids sin duplicados
        if len(self.related_ki_ids) != len(set(self.related_ki_ids)):
            raise ValueError("related_ki_ids no puede contener duplicados")
        
        # 8. related_ki_ids sin auto-referencia
        if self.id in self.related_ki_ids:
            raise ValueError("related_ki_ids no puede contener auto-referencia")
        
        # 9. tags sin duplicados ni strings vacíos
        if self.tags:
            if any(not tag.strip() for tag in self.tags):
                raise ValueError("tags no puede contener strings vacíos")
            if len(self.tags) != len(set(self.tags)):
                raise ValueError("tags no puede contener duplicados")
        
        # 10. Coherencia temporal
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")
        
        if self.validated_at is not None and self.validated_at < self.created_at:
            raise ValueError("validated_at debe ser >= created_at")
        
        if self.refuted_at is not None and self.refuted_at < self.created_at:
            raise ValueError("refuted_at debe ser >= created_at")
    
    def validate(self, evidence: List[str]) -> None:
        """
        Transición: OBSERVED → VALIDATED
        
        Args:
            evidence: lista de evidencias que validan el conocimiento
            
        Raises:
            ValueError: si la transición no es válida
        """
        if self.epistemic_state == EpistemicState.ARCHIVED:
            raise ValueError("ARCHIVED es terminal")

        if self.epistemic_state != EpistemicState.OBSERVED:
            raise ValueError(
                f"Solo se puede validar desde OBSERVED, estado actual: {self.epistemic_state.value}"
            )
        
        if not evidence:
            raise ValueError("validate requiere al menos una evidencia")
        
        self.epistemic_state = EpistemicState.VALIDATED
        self.evidence.extend(evidence)
        self.validated_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def refute(self, reason: str) -> None:
        """
        Transición: VALIDATED → REFUTED
        
        Args:
            reason: razón de la refutación
            
        Raises:
            ValueError: si la transición no es válida
        """
        if self.epistemic_state == EpistemicState.ARCHIVED:
            raise ValueError("ARCHIVED es terminal")

        if self.epistemic_state != EpistemicState.VALIDATED:
            raise ValueError(
                f"Solo se puede refutar desde VALIDATED, estado actual: {self.epistemic_state.value}"
            )
        
        if not reason or not reason.strip():
            raise ValueError("refute requiere razón no vacía")
        
        self.epistemic_state = EpistemicState.REFUTED
        self.refuted_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        if self.metadata is None:
            self.metadata = {}
        if "refutation_reasons" not in self.metadata:
            self.metadata["refutation_reasons"] = []
        self.metadata["refutation_reasons"].append(reason)
    
    def archive(self, reason: str) -> None:
        """
        Transición: cualquier estado → ARCHIVED (terminal)
        
        Args:
            reason: razón del archivado
            
        Raises:
            ValueError: si ya está archivado o razón vacía
        """
        if self.epistemic_state == EpistemicState.ARCHIVED:
            raise ValueError("ARCHIVED es terminal")
        
        if not reason or not reason.strip():
            raise ValueError("archive requiere razón no vacía")
        
        self.epistemic_state = EpistemicState.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)
        
        if self.metadata is None:
            self.metadata = {}
        self.metadata["archive_reason"] = reason
    
    def reopen(self) -> None:
        """
        Transición: REFUTED → DECLARED
        
        Raises:
            ValueError: si no está en estado REFUTED
        """
        if self.epistemic_state == EpistemicState.ARCHIVED:
            raise ValueError("ARCHIVED es terminal")

        if self.epistemic_state != EpistemicState.REFUTED:
            raise ValueError(
                f"Solo se puede reabrir desde REFUTED, estado actual: {self.epistemic_state.value}"
            )
        
        self.epistemic_state = EpistemicState.DECLARED
        self.refuted_at = None
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario JSON-compatible."""
        return {
            "id": str(self.id),
            "statement": self.statement,
            "source": self.source,
            "evidence": self.evidence,
            "tags": self.tags,
            "epistemic_state": self.epistemic_state.value,
            "confidence": self.confidence,
            "related_ki_ids": [str(ki_id) for ki_id in self.related_ki_ids],
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "refuted_at": self.refuted_at.isoformat() if self.refuted_at else None,
            "metadata": self.metadata or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeItem":
        """Reconstrucción desde diccionario."""
        return cls(
            id=UUID(data["id"]),
            statement=data["statement"],
            source=data["source"],
            evidence=data.get("evidence", []),
            tags=data.get("tags", []),
            epistemic_state=EpistemicState(data["epistemic_state"]),
            confidence=float(data["confidence"]),
            related_ki_ids=[UUID(ki_id) for ki_id in data.get("related_ki_ids", [])],
            tenant_id=UUID(data["tenant_id"]) if data.get("tenant_id") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            validated_at=datetime.fromisoformat(data["validated_at"]) if data.get("validated_at") else None,
            refuted_at=datetime.fromisoformat(data["refuted_at"]) if data.get("refuted_at") else None,
            metadata=data.get("metadata"),
        )
