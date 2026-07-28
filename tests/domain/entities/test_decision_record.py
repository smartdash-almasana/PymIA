"""
Tests para DecisionRecord.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from pymia.domain.entities.decision_record import DecisionRecord
from pymia.domain.types.decision_type import DecisionType
from pymia.domain.types.decision_outcome import DecisionOutcome
from pymia.domain.types.decision_reversibility import DecisionReversibility


def _make_record(**kwargs):
    """Helper para crear DecisionRecord con valores por defecto."""
    # Usar un timestamp base consistente para evitar condiciones de carrera
    base_time = kwargs.get('proposed_at', datetime.now(timezone.utc))
    
    defaults = {
        "id": uuid4(),
        "title": "Decisión estratégica de inversión en nuevo canal",
        "context": "Caída de ventas en canal tradicional",
        "decision_type": DecisionType.COMERCIAL,
        "alternatives": ["E-commerce", "Fuerza de ventas", "Alianza estratégica"],
        "reasoning": "Canal con mayor crecimiento en el sector",
        "proposed_at": base_time,
        "created_at": base_time,
        "updated_at": base_time,
    }
    defaults.update(kwargs)
    return DecisionRecord(**defaults)


class TestDecisionRecordConstruction:
    def test_valid_construction_minimal(self):
        record = _make_record()
        assert record.chosen_alternative is None
        assert record.outcome == DecisionOutcome.PENDIENTE
    
    def test_valid_construction_full(self):
        now = datetime.now(timezone.utc)
        record = _make_record(
            chosen_alternative="E-commerce",
            proposed_at=now,
            decided_at=now,
            executed_at=now + timedelta(days=1),
            evaluated_at=now + timedelta(days=30),
            outcome=DecisionOutcome.EXITOSO,
            knowledge_item_ids=[uuid4(), uuid4()],
        )
        assert record.chosen_alternative == "E-commerce"
        assert record.outcome == DecisionOutcome.EXITOSO
    
    def test_entity_has_uuid_id(self):
        record = _make_record()
        assert isinstance(record.id, type(uuid4()))


class TestDecisionRecordInvariants:
    def test_rejects_short_title(self):
        with pytest.raises(ValueError, match="title debe tener mínimo 10 caracteres"):
            _make_record(title="Corto")
    
    def test_rejects_empty_context(self):
        with pytest.raises(ValueError, match="context no puede estar vacío"):
            _make_record(context="")
    
    def test_rejects_single_alternative(self):
        with pytest.raises(ValueError, match="alternatives debe tener mínimo 2"):
            _make_record(alternatives=["Solo una"])
    
    def test_rejects_chosen_not_in_alternatives(self):
        with pytest.raises(ValueError, match="chosen_alternative debe estar en alternatives"):
            _make_record(alternatives=["A", "B"], chosen_alternative="C")
    
    def test_rejects_confidence_out_of_range(self):
        with pytest.raises(ValueError, match="confidence_at_decision"):
            _make_record(confidence_at_decision=1.5)
    
    def test_rejects_duplicate_knowledge_item_ids(self):
        ki_id = uuid4()
        with pytest.raises(ValueError, match="knowledge_item_ids"):
            _make_record(knowledge_item_ids=[ki_id, ki_id])
    
    def test_pendiente_requires_null_evaluated_at(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="PENDIENTE"):
            _make_record(
                proposed_at=now,
                outcome=DecisionOutcome.PENDIENTE,
                evaluated_at=now,
            )
    
    def test_evaluated_requires_evaluated_at(self):
        with pytest.raises(ValueError, match="requiere evaluated_at"):
            _make_record(outcome=DecisionOutcome.EXITOSO, evaluated_at=None)
    
    def test_rejects_inconsistent_timestamps(self):
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="updated_at debe ser >= created_at"):
            _make_record(created_at=now, updated_at=now - timedelta(days=1))


class TestDecisionRecordMethods:
    def test_decide_sets_chosen_alternative(self):
        record = _make_record()
        decided_at = datetime.now(timezone.utc)
        record.decide("E-commerce", decided_at)
        assert record.chosen_alternative == "E-commerce"
        assert record.decided_at == decided_at
    
    def test_execute_requires_decided_at(self):
        record = _make_record()
        with pytest.raises(ValueError, match="debe ser decidido antes"):
            record.execute(datetime.now(timezone.utc))
    
    def test_evaluate_requires_executed_at(self):
        now = datetime.now(timezone.utc)
        record = _make_record(
            proposed_at=now,
            chosen_alternative="E-commerce",
            decided_at=now,
        )
        with pytest.raises(ValueError, match="debe ser ejecutado antes"):
            record.evaluate(DecisionOutcome.EXITOSO, now)
    
    def test_evaluate_rejects_pendiente_outcome(self):
        now = datetime.now(timezone.utc)
        record = _make_record(
            proposed_at=now,
            chosen_alternative="E-commerce",
            decided_at=now,
            executed_at=now,
        )
        with pytest.raises(ValueError, match="no puede ser PENDIENTE"):
            record.evaluate(DecisionOutcome.PENDIENTE, now)
    
    def test_rejects_execute_twice(self):
        now = datetime.now(timezone.utc)
        record = _make_record(
            proposed_at=now,
            chosen_alternative="E-commerce",
            decided_at=now,
            executed_at=now,
        )
        with pytest.raises(ValueError, match="ya fue ejecutado"):
            record.execute(now)
    
    def test_add_knowledge_item_validates_uniqueness(self):
        record = _make_record()
        ki_id = uuid4()
        record.add_knowledge_item(ki_id)
        with pytest.raises(ValueError, match="ya está referenciado"):
            record.add_knowledge_item(ki_id)


class TestDecisionRecordSerialization:
    def test_to_dict_and_from_dict_roundtrip(self):
        now = datetime.now(timezone.utc)
        original = _make_record(
            proposed_at=now,
            chosen_alternative="E-commerce",
            decided_at=now,
            knowledge_item_ids=[uuid4(), uuid4()],
            organization_id=uuid4(),
            metadata={"key": "value"},
        )
        
        data = original.to_dict()
        restored = DecisionRecord.from_dict(data)
        
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.chosen_alternative == original.chosen_alternative
        assert restored.knowledge_item_ids == original.knowledge_item_ids
        assert restored.organization_id == original.organization_id
        assert restored.metadata == original.metadata
