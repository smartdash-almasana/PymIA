"""
DecisionRecord - Registro de decisión organizacional.

Doctrina: PYMIA_DECISION_QUALITY_THEORY.md
Capa: 3 (entidad con ciclo de vida)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID

from pymia.domain.types.decision_type import DecisionType
from pymia.domain.types.decision_outcome import DecisionOutcome
from pymia.domain.types.decision_reversibility import DecisionReversibility


@dataclass
class DecisionRecord:
    """
    Registro de decisión organizacional.
    
    Entidad mutable que captura una decisión completa desde propuesta hasta evaluación.
    Referencia KnowledgeItems por UUID (asociación débil).
    """
    
    # Identificación
    id: UUID
    
    # Contenido decisional
    title: str
    context: str
    decision_type: DecisionType
    alternatives: List[str]
    reasoning: str
    chosen_alternative: Optional[str] = None
    
    # Riesgo
    risks_identified: List[str] = field(default_factory=list)
    reversibility: DecisionReversibility = DecisionReversibility.REVERSIBLE
    
    # Sustrato epistémico (referencias a KnowledgeItem por UUID)
    knowledge_item_ids: List[UUID] = field(default_factory=list)
    
    # Estado y confianza
    outcome: DecisionOutcome = DecisionOutcome.PENDIENTE
    confidence_at_decision: float = 0.5
    
    # Asociación débil
    organization_id: Optional[UUID] = None
    
    # Timestamps timezone-aware
    proposed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    evaluated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Extensibilidad
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validación de invariantes de dominio."""
        # 1. title mínimo 10 caracteres
        if not self.title or len(self.title.strip()) < 10:
            raise ValueError("title debe tener mínimo 10 caracteres")
        
        # 2. context no vacío
        if not self.context or not self.context.strip():
            raise ValueError("context no puede estar vacío")
        
        # 3. alternatives mínimo 2 elementos
        if not self.alternatives or len(self.alternatives) < 2:
            raise ValueError("alternatives debe tener mínimo 2 elementos")
        
        # 4. alternatives sin strings vacíos ni duplicados
        if any(not alt.strip() for alt in self.alternatives):
            raise ValueError("alternatives no puede contener strings vacíos")
        if len(self.alternatives) != len(set(self.alternatives)):
            raise ValueError("alternatives no puede contener duplicados")
        
        # 5. Si chosen_alternative es not None, debe estar en alternatives
        if self.chosen_alternative is not None:
            if self.chosen_alternative not in self.alternatives:
                raise ValueError("chosen_alternative debe estar en alternatives")
        
        # 6. reasoning no vacío
        if not self.reasoning or not self.reasoning.strip():
            raise ValueError("reasoning no puede estar vacío")
        
        # 7. confidence_at_decision en [0.0, 1.0]
        if not (0.0 <= self.confidence_at_decision <= 1.0):
            raise ValueError("confidence_at_decision debe estar en [0.0, 1.0]")
        
        # 8. knowledge_item_ids sin duplicados
        if len(self.knowledge_item_ids) != len(set(self.knowledge_item_ids)):
            raise ValueError("knowledge_item_ids no puede contener duplicados")
        
        # 9. risks_identified sin strings vacíos ni duplicados
        if self.risks_identified:
            if any(not risk.strip() for risk in self.risks_identified):
                raise ValueError("risks_identified no puede contener strings vacíos")
            if len(self.risks_identified) != len(set(self.risks_identified)):
                raise ValueError("risks_identified no puede contener duplicados")
        
        # 10. Si outcome == PENDIENTE, evaluated_at debe ser None
        if self.outcome == DecisionOutcome.PENDIENTE:
            if self.evaluated_at is not None:
                raise ValueError("outcome PENDIENTE requiere evaluated_at = None")
        
        # 11. Si outcome in (EXITOSO, PARCIAL, FALLIDO, NO_EVALUABLE), evaluated_at debe estar seteado
        if self.outcome in (DecisionOutcome.EXITOSO, DecisionOutcome.PARCIAL, 
                           DecisionOutcome.FALLIDO, DecisionOutcome.NO_EVALUABLE):
            if self.evaluated_at is None:
                raise ValueError(f"outcome {self.outcome.value} requiere evaluated_at")
        
        # 12. Coherencia temporal
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")
        
        if self.decided_at is not None and self.decided_at < self.proposed_at:
            raise ValueError("decided_at debe ser >= proposed_at")
        
        if self.executed_at is not None:
            if self.decided_at is None:
                raise ValueError("executed_at requiere decided_at")
            if self.executed_at < self.decided_at:
                raise ValueError("executed_at debe ser >= decided_at")
        
        if self.evaluated_at is not None:
            if self.executed_at is None:
                raise ValueError("evaluated_at requiere executed_at")
            if self.evaluated_at < self.executed_at:
                raise ValueError("evaluated_at debe ser >= executed_at")
    
    def decide(self, chosen: str, decided_at: datetime) -> None:
        """Transición: propuesta → decisión."""
        if self.decided_at is not None:
            raise ValueError("DecisionRecord ya fue decidido")
        if chosen not in self.alternatives:
            raise ValueError("chosen debe estar en alternatives")
        if decided_at.tzinfo is None:
            raise ValueError("decided_at debe ser timezone-aware")
        self.chosen_alternative = chosen
        self.decided_at = decided_at
        self.updated_at = datetime.now(timezone.utc)
    
    def execute(self, executed_at: datetime) -> None:
        """Transición: decisión → ejecución."""
        if self.decided_at is None:
            raise ValueError("DecisionRecord debe ser decidido antes de ejecutar")
        if self.executed_at is not None:
            raise ValueError("DecisionRecord ya fue ejecutado")
        if executed_at.tzinfo is None:
            raise ValueError("executed_at debe ser timezone-aware")
        self.executed_at = executed_at
        self.updated_at = datetime.now(timezone.utc)
    
    def evaluate(self, outcome: DecisionOutcome, evaluated_at: datetime) -> None:
        """Transición: ejecución → evaluación."""
        if self.executed_at is None:
            raise ValueError("DecisionRecord debe ser ejecutado antes de evaluar")
        if self.evaluated_at is not None:
            raise ValueError("DecisionRecord ya fue evaluado")
        if outcome == DecisionOutcome.PENDIENTE:
            raise ValueError("outcome no puede ser PENDIENTE en evaluate()")
        if evaluated_at.tzinfo is None:
            raise ValueError("evaluated_at debe ser timezone-aware")
        self.outcome = outcome
        self.evaluated_at = evaluated_at
        self.updated_at = datetime.now(timezone.utc)
    
    def add_knowledge_item(self, ki_id: UUID) -> None:
        """Agrega referencia a KnowledgeItem."""
        if ki_id in self.knowledge_item_ids:
            raise ValueError("ki_id ya está referenciado")
        self.knowledge_item_ids.append(ki_id)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialización a diccionario."""
        return {
            "id": str(self.id),
            "title": self.title,
            "context": self.context,
            "decision_type": self.decision_type.value,
            "alternatives": self.alternatives,
            "chosen_alternative": self.chosen_alternative,
            "reasoning": self.reasoning,
            "risks_identified": self.risks_identified,
            "reversibility": self.reversibility.value,
            "knowledge_item_ids": [str(ki_id) for ki_id in self.knowledge_item_ids],
            "outcome": self.outcome.value,
            "confidence_at_decision": self.confidence_at_decision,
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "proposed_at": self.proposed_at.isoformat(),
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionRecord":
        """Reconstrucción desde diccionario."""
        return cls(
            id=UUID(data["id"]),
            title=data["title"],
            context=data["context"],
            decision_type=DecisionType(data["decision_type"]),
            alternatives=data["alternatives"],
            chosen_alternative=data.get("chosen_alternative"),
            reasoning=data["reasoning"],
            risks_identified=data.get("risks_identified", []),
            reversibility=DecisionReversibility(data["reversibility"]),
            knowledge_item_ids=[UUID(ki_id) for ki_id in data.get("knowledge_item_ids", [])],
            outcome=DecisionOutcome(data["outcome"]),
            confidence_at_decision=float(data["confidence_at_decision"]),
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            proposed_at=datetime.fromisoformat(data["proposed_at"]),
            decided_at=datetime.fromisoformat(data["decided_at"]) if data.get("decided_at") else None,
            executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else None,
            evaluated_at=datetime.fromisoformat(data["evaluated_at"]) if data.get("evaluated_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata"),
        )
