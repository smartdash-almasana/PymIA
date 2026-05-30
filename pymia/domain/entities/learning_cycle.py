"""LearningCycle — Entidad que modela el ciclo de aprendizaje organizacional."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from pymia.domain.types.attribution_type import AttributionType
from pymia.domain.types.learning_cycle_state import LearningCycleState, TERMINAL_STATES


@dataclass
class LearningCycle:
    """Ciclo de aprendizaje organizacional (entidad mutable)."""

    id: UUID
    decision_record_id: UUID
    state: LearningCycleState = LearningCycleState.INICIADO
    outcome_observed: Optional[str] = None
    outcome_matches_expectation: Optional[bool] = None
    attribution_type: Optional[AttributionType] = None
    attribution_reasoning: Optional[str] = None
    extracted_learning_statement: Optional[str] = None
    confidence_delta: Optional[float] = None
    knowledge_item_ids_produced: List[UUID] = field(default_factory=list)
    knowledge_item_ids_updated: List[UUID] = field(default_factory=list)
    organization_id: Optional[UUID] = None
    initiated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result_registered_at: Optional[datetime] = None
    attribution_completed_at: Optional[datetime] = None
    learning_extracted_at: Optional[datetime] = None
    ki_updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    aborted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    abort_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.decision_record_id:
            raise ValueError("decision_record_id es obligatorio")
        if not isinstance(self.state, LearningCycleState):
            raise ValueError("state debe ser LearningCycleState")
        if self.outcome_matches_expectation is not None and self.outcome_observed is None:
            raise ValueError("outcome_matches_expectation requiere outcome_observed")
        if self.confidence_delta is not None and not (-1.0 <= self.confidence_delta <= 1.0):
            raise ValueError("confidence_delta debe estar en [-1.0, 1.0]")
        if len(self.knowledge_item_ids_produced) != len(set(self.knowledge_item_ids_produced)):
            raise ValueError("knowledge_item_ids_produced no puede contener duplicados")
        if len(self.knowledge_item_ids_updated) != len(set(self.knowledge_item_ids_updated)):
            raise ValueError("knowledge_item_ids_updated no puede contener duplicados")
        if set(self.knowledge_item_ids_produced) & set(self.knowledge_item_ids_updated):
            raise ValueError("knowledge_item_ids_produced y knowledge_item_ids_updated no pueden tener intersección")
        self._validate_state_invariants()
        self._validate_temporal_coherence()

    def _validate_state_invariants(self) -> None:
        s = self.state
        if s == LearningCycleState.INICIADO:
            if any(v is not None for v in [self.outcome_observed, self.outcome_matches_expectation, self.attribution_type, self.attribution_reasoning, self.extracted_learning_statement, self.result_registered_at, self.attribution_completed_at, self.learning_extracted_at, self.ki_updated_at, self.closed_at, self.aborted_at, self.abort_reason]):
                raise ValueError("Estado INICIADO no admite campos opcionales seteados")
            if self.knowledge_item_ids_produced or self.knowledge_item_ids_updated:
                raise ValueError("Estado INICIADO no admite KIs producidos ni actualizados")
        elif s == LearningCycleState.RESULTADO_REGISTRADO:
            if self.outcome_observed is None or self.result_registered_at is None:
                raise ValueError("RESULTADO_REGISTRADO requiere outcome_observed y result_registered_at")
            if any(v is not None for v in [self.attribution_type, self.attribution_reasoning, self.extracted_learning_statement, self.attribution_completed_at, self.learning_extracted_at, self.ki_updated_at, self.closed_at, self.aborted_at, self.abort_reason]):
                raise ValueError("RESULTADO_REGISTRADO no admite campos de estados posteriores")
            if self.knowledge_item_ids_produced or self.knowledge_item_ids_updated:
                raise ValueError("RESULTADO_REGISTRADO no admite KIs")
        elif s == LearningCycleState.ATRIBUCION_COMPLETADA:
            if any(v is None for v in [self.outcome_observed, self.result_registered_at, self.attribution_type, self.attribution_reasoning, self.attribution_completed_at]):
                raise ValueError("ATRIBUCION_COMPLETADA requiere campos de resultado y atribución seteados")
            if any(v is not None for v in [self.extracted_learning_statement, self.learning_extracted_at, self.ki_updated_at, self.closed_at, self.aborted_at, self.abort_reason]):
                raise ValueError("ATRIBUCION_COMPLETADA no admite campos de estados posteriores")
            if self.knowledge_item_ids_produced or self.knowledge_item_ids_updated:
                raise ValueError("ATRIBUCION_COMPLETADA no admite KIs")
        elif s == LearningCycleState.APRENDIZAJE_EXTRAIDO:
            if any(v is None for v in [self.outcome_observed, self.result_registered_at, self.attribution_type, self.attribution_reasoning, self.attribution_completed_at, self.extracted_learning_statement, self.learning_extracted_at]):
                raise ValueError("APRENDIZAJE_EXTRAIDO requiere todos los campos previos seteados")
            if any(v is not None for v in [self.ki_updated_at, self.closed_at, self.aborted_at, self.abort_reason]):
                raise ValueError("APRENDIZAJE_EXTRAIDO no admite campos de estados posteriores")
            if self.knowledge_item_ids_produced or self.knowledge_item_ids_updated:
                raise ValueError("APRENDIZAJE_EXTRAIDO no admite KIs")
        elif s == LearningCycleState.KI_ACTUALIZADO:
            if any(v is None for v in [self.outcome_observed, self.result_registered_at, self.attribution_type, self.attribution_reasoning, self.attribution_completed_at, self.extracted_learning_statement, self.learning_extracted_at, self.ki_updated_at]):
                raise ValueError("KI_ACTUALIZADO requiere todos los campos previos seteados")
            if not self.knowledge_item_ids_produced and not self.knowledge_item_ids_updated:
                raise ValueError("KI_ACTUALIZADO requiere al menos una lista de KI no vacía")
            if any(v is not None for v in [self.closed_at, self.aborted_at, self.abort_reason]):
                raise ValueError("KI_ACTUALIZADO no admite closed_at, aborted_at ni abort_reason")
        elif s == LearningCycleState.CERRADO:
            if any(v is None for v in [self.outcome_observed, self.result_registered_at, self.attribution_type, self.attribution_reasoning, self.attribution_completed_at, self.extracted_learning_statement, self.learning_extracted_at, self.ki_updated_at, self.closed_at]):
                raise ValueError("CERRADO requiere todos los campos previos y closed_at seteados")
            if not self.knowledge_item_ids_produced and not self.knowledge_item_ids_updated:
                raise ValueError("CERRADO requiere al menos una lista de KI no vacía")
            if self.aborted_at is not None or self.abort_reason is not None:
                raise ValueError("CERRADO no admite aborted_at ni abort_reason")
        elif s == LearningCycleState.ABORTADO:
            if self.aborted_at is None or not self.abort_reason:
                raise ValueError("ABORTADO requiere aborted_at y abort_reason no vacío")
            if self.closed_at is not None:
                raise ValueError("ABORTADO no admite closed_at")

    def _validate_temporal_coherence(self) -> None:
        self._require_timezone_aware(
            self.initiated_at,
            "initiated_at",
        )
        self._require_timezone_aware(
            self.created_at,
            "created_at",
        )
        self._require_timezone_aware(
            self.updated_at,
            "updated_at",
        )
        for name, ts in [
            ("result_registered_at", self.result_registered_at),
            ("attribution_completed_at", self.attribution_completed_at),
            ("learning_extracted_at", self.learning_extracted_at),
            ("ki_updated_at", self.ki_updated_at),
            ("closed_at", self.closed_at),
            ("aborted_at", self.aborted_at),
        ]:
            if ts is not None:
                self._require_timezone_aware(ts, name)

        prev = None
        for ts in [
            self.initiated_at,
            self.result_registered_at,
            self.attribution_completed_at,
            self.learning_extracted_at,
            self.ki_updated_at,
            self.closed_at,
        ]:
            if ts is not None:
                if prev is not None and ts < prev:
                    raise ValueError("Timestamps deben ser monótonos no decrecientes")
                prev = ts
        if self.aborted_at is not None and self.aborted_at < self.initiated_at:
            raise ValueError("aborted_at debe ser >= initiated_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at debe ser >= created_at")

    @staticmethod
    def _require_timezone_aware(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} debe ser timezone-aware")

    def _revalidate_after_mutation(self) -> None:
        self._validate_state_invariants()
        self._validate_temporal_coherence()

    def register_result(self, outcome_observed: str, outcome_matches_expectation: bool, observed_at: datetime) -> None:
        if self.state != LearningCycleState.INICIADO:
            raise ValueError(f"register_result requiere estado INICIADO, estado actual: {self.state.value}")
        if not outcome_observed or not outcome_observed.strip():
            raise ValueError("outcome_observed no puede estar vacío")
        self.outcome_observed = outcome_observed
        self.outcome_matches_expectation = outcome_matches_expectation
        self.result_registered_at = observed_at
        self.state = LearningCycleState.RESULTADO_REGISTRADO
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def complete_attribution(self, attribution_type: AttributionType, attribution_reasoning: str, completed_at: datetime) -> None:
        if self.state != LearningCycleState.RESULTADO_REGISTRADO:
            raise ValueError(f"complete_attribution requiere estado RESULTADO_REGISTRADO, estado actual: {self.state.value}")
        if not attribution_reasoning or not attribution_reasoning.strip():
            raise ValueError("attribution_reasoning no puede estar vacío")
        self.attribution_type = attribution_type
        self.attribution_reasoning = attribution_reasoning
        self.attribution_completed_at = completed_at
        self.state = LearningCycleState.ATRIBUCION_COMPLETADA
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def extract_learning(self, statement: str, confidence_delta: Optional[float], extracted_at: datetime) -> None:
        if self.state != LearningCycleState.ATRIBUCION_COMPLETADA:
            raise ValueError(f"extract_learning requiere estado ATRIBUCION_COMPLETADA, estado actual: {self.state.value}")
        if not statement or len(statement.strip()) < 10:
            raise ValueError("extracted_learning_statement debe tener mínimo 10 caracteres")
        if confidence_delta is not None and not (-1.0 <= confidence_delta <= 1.0):
            raise ValueError("confidence_delta debe estar en [-1.0, 1.0]")
        self.extracted_learning_statement = statement
        self.confidence_delta = confidence_delta
        self.learning_extracted_at = extracted_at
        self.state = LearningCycleState.APRENDIZAJE_EXTRAIDO
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def register_knowledge_updates(self, produced: List[UUID], updated: List[UUID], updated_at: datetime) -> None:
        if self.state != LearningCycleState.APRENDIZAJE_EXTRAIDO:
            raise ValueError(f"register_knowledge_updates requiere estado APRENDIZAJE_EXTRAIDO, estado actual: {self.state.value}")
        if not produced and not updated:
            raise ValueError("register_knowledge_updates requiere al menos una lista no vacía")
        if len(produced) != len(set(produced)):
            raise ValueError("produced no puede contener duplicados")
        if len(updated) != len(set(updated)):
            raise ValueError("updated no puede contener duplicados")
        if set(produced) & set(updated):
            raise ValueError("produced y updated no pueden tener intersección")
        self.knowledge_item_ids_produced = produced
        self.knowledge_item_ids_updated = updated
        self.ki_updated_at = updated_at
        self.state = LearningCycleState.KI_ACTUALIZADO
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def close(self, closed_at: datetime) -> None:
        if self.state != LearningCycleState.KI_ACTUALIZADO:
            raise ValueError(f"close requiere estado KI_ACTUALIZADO, estado actual: {self.state.value}")
        self.closed_at = closed_at
        self.state = LearningCycleState.CERRADO
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def abort(self, reason: str, aborted_at: datetime) -> None:
        if self.state in TERMINAL_STATES:
            raise ValueError(f"abort no puede ejecutarse desde estado terminal: {self.state.value}")
        if not reason or not reason.strip():
            raise ValueError("abort_reason no puede estar vacío")
        self.abort_reason = reason
        self.aborted_at = aborted_at
        self.state = LearningCycleState.ABORTADO
        self.updated_at = datetime.now(timezone.utc)
        self._revalidate_after_mutation()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "decision_record_id": str(self.decision_record_id),
            "state": self.state.value,
            "outcome_observed": self.outcome_observed,
            "outcome_matches_expectation": self.outcome_matches_expectation,
            "attribution_type": self.attribution_type.value if self.attribution_type else None,
            "attribution_reasoning": self.attribution_reasoning,
            "extracted_learning_statement": self.extracted_learning_statement,
            "confidence_delta": self.confidence_delta,
            "knowledge_item_ids_produced": [str(ki) for ki in self.knowledge_item_ids_produced],
            "knowledge_item_ids_updated": [str(ki) for ki in self.knowledge_item_ids_updated],
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "initiated_at": self.initiated_at.isoformat(),
            "result_registered_at": self.result_registered_at.isoformat() if self.result_registered_at else None,
            "attribution_completed_at": self.attribution_completed_at.isoformat() if self.attribution_completed_at else None,
            "learning_extracted_at": self.learning_extracted_at.isoformat() if self.learning_extracted_at else None,
            "ki_updated_at": self.ki_updated_at.isoformat() if self.ki_updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "aborted_at": self.aborted_at.isoformat() if self.aborted_at else None,
            "abort_reason": self.abort_reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningCycle":
        return cls(
            id=UUID(data["id"]),
            decision_record_id=UUID(data["decision_record_id"]),
            state=LearningCycleState(data["state"]),
            outcome_observed=data.get("outcome_observed"),
            outcome_matches_expectation=data.get("outcome_matches_expectation"),
            attribution_type=AttributionType(data["attribution_type"]) if data.get("attribution_type") else None,
            attribution_reasoning=data.get("attribution_reasoning"),
            extracted_learning_statement=data.get("extracted_learning_statement"),
            confidence_delta=data.get("confidence_delta"),
            knowledge_item_ids_produced=[UUID(ki) for ki in data.get("knowledge_item_ids_produced", [])],
            knowledge_item_ids_updated=[UUID(ki) for ki in data.get("knowledge_item_ids_updated", [])],
            organization_id=UUID(data["organization_id"]) if data.get("organization_id") else None,
            initiated_at=datetime.fromisoformat(data["initiated_at"]),
            result_registered_at=datetime.fromisoformat(data["result_registered_at"]) if data.get("result_registered_at") else None,
            attribution_completed_at=datetime.fromisoformat(data["attribution_completed_at"]) if data.get("attribution_completed_at") else None,
            learning_extracted_at=datetime.fromisoformat(data["learning_extracted_at"]) if data.get("learning_extracted_at") else None,
            ki_updated_at=datetime.fromisoformat(data["ki_updated_at"]) if data.get("ki_updated_at") else None,
            closed_at=datetime.fromisoformat(data["closed_at"]) if data.get("closed_at") else None,
            aborted_at=datetime.fromisoformat(data["aborted_at"]) if data.get("aborted_at") else None,
            abort_reason=data.get("abort_reason"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata"),
        )
