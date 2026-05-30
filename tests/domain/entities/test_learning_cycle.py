"""Tests para LearningCycle entity."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.types.attribution_type import AttributionType
from pymia.domain.types.learning_cycle_state import LearningCycleState
from pymia.domain.entities.learning_cycle import LearningCycle


def _make_cycle(**kwargs):
    base_time = kwargs.get("initiated_at", datetime.now(timezone.utc))
    defaults = {
        "id": uuid4(),
        "decision_record_id": uuid4(),
        "initiated_at": base_time,
        "created_at": base_time,
        "updated_at": base_time,
    }
    defaults.update(kwargs)
    return LearningCycle(**defaults)


def _advance_to_result(cycle, base_time=None):
    if base_time is None:
        base_time = cycle.initiated_at
    cycle.register_result(
        outcome_observed="Ventas subieron 15%",
        outcome_matches_expectation=True,
        observed_at=base_time + timedelta(hours=1),
    )
    return cycle


def _advance_to_attribution(cycle, base_time=None):
    if base_time is None:
        base_time = cycle.initiated_at
    _advance_to_result(cycle, base_time)
    cycle.complete_attribution(
        attribution_type=AttributionType.INTERNA,
        attribution_reasoning="La campaña de marketing causó el aumento",
        completed_at=base_time + timedelta(hours=2),
    )
    return cycle


def _advance_to_learning(cycle, base_time=None):
    if base_time is None:
        base_time = cycle.initiated_at
    _advance_to_attribution(cycle, base_time)
    cycle.extract_learning(
        statement="Las campañas de email marketing tienen mayor ROI en PyMEs",
        confidence_delta=0.2,
        extracted_at=base_time + timedelta(hours=3),
    )
    return cycle


def _advance_to_ki(cycle, base_time=None):
    if base_time is None:
        base_time = cycle.initiated_at
    _advance_to_learning(cycle, base_time)
    cycle.register_knowledge_updates(
        produced=[uuid4()],
        updated=[uuid4()],
        updated_at=base_time + timedelta(hours=4),
    )
    return cycle


class TestLearningCycleConstruction:
    def test_valid_construction_iniciado(self):
        cycle = _make_cycle()
        assert cycle.state == LearningCycleState.INICIADO
        assert cycle.decision_record_id is not None
        assert cycle.outcome_observed is None
        assert cycle.knowledge_item_ids_produced == []
        assert cycle.knowledge_item_ids_updated == []

    def test_valid_construction_cerrado(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(
            state=LearningCycleState.CERRADO,
            outcome_observed="Ventas subieron 15%",
            outcome_matches_expectation=True,
            attribution_type=AttributionType.INTERNA,
            attribution_reasoning="La campaña causó el aumento",
            extracted_learning_statement="Email marketing tiene mayor ROI en PyMEs",
            confidence_delta=0.2,
            knowledge_item_ids_produced=[uuid4()],
            knowledge_item_ids_updated=[uuid4()],
            result_registered_at=base_time + timedelta(hours=1),
            attribution_completed_at=base_time + timedelta(hours=2),
            learning_extracted_at=base_time + timedelta(hours=3),
            ki_updated_at=base_time + timedelta(hours=4),
            closed_at=base_time + timedelta(hours=5),
        )
        assert cycle.state == LearningCycleState.CERRADO
        assert cycle.closed_at is not None

    def test_entity_has_uuid_id(self):
        c1 = _make_cycle()
        c2 = _make_cycle()
        assert c1.id != c2.id


class TestLearningCycleInvariants:
    def test_rejects_iniciado_with_outcome_observed(self):
        with pytest.raises(ValueError, match="INICIADO"):
            _make_cycle(outcome_observed="Algo pasó")

    def test_rejects_cerrado_without_ki_fields(self):
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="CERRADO"):
            _make_cycle(
                state=LearningCycleState.CERRADO,
                outcome_observed="Resultado",
                result_registered_at=base_time,
                closed_at=base_time + timedelta(hours=1),
            )

    def test_rejects_abort_reason_without_abortado_state(self):
        with pytest.raises(ValueError, match="INICIADO"):
            _make_cycle(abort_reason="Cancelado por falta de datos")

    def test_rejects_confidence_delta_out_of_range(self):
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="confidence_delta"):
            _make_cycle(
                state=LearningCycleState.APRENDIZAJE_EXTRAIDO,
                outcome_observed="Resultado",
                result_registered_at=base_time,
                attribution_type=AttributionType.INTERNA,
                attribution_reasoning="Causa interna",
                attribution_completed_at=base_time + timedelta(hours=1),
                extracted_learning_statement="Aprendizaje extraído del ciclo",
                learning_extracted_at=base_time + timedelta(hours=2),
                confidence_delta=1.5,
            )

    def test_rejects_ki_intersection_between_produced_and_updated(self):
        shared_ki = uuid4()
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="intersección"):
            _make_cycle(
                state=LearningCycleState.KI_ACTUALIZADO,
                outcome_observed="Resultado",
                result_registered_at=base_time,
                attribution_type=AttributionType.INTERNA,
                attribution_reasoning="Causa interna",
                attribution_completed_at=base_time + timedelta(hours=1),
                extracted_learning_statement="Aprendizaje extraído del ciclo",
                learning_extracted_at=base_time + timedelta(hours=2),
                knowledge_item_ids_produced=[shared_ki],
                knowledge_item_ids_updated=[shared_ki],
                ki_updated_at=base_time + timedelta(hours=3),
            )

    def test_rejects_inconsistent_timestamps(self):
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="monótonos"):
            _make_cycle(
                state=LearningCycleState.RESULTADO_REGISTRADO,
                outcome_observed="Resultado",
                result_registered_at=base_time - timedelta(hours=1),
            )

    def test_rejects_naive_initiated_at(self):
        naive_time = datetime.now()
        with pytest.raises(ValueError, match="timezone-aware"):
            _make_cycle(initiated_at=naive_time)

    def test_rejects_naive_result_registered_at(self):
        base_time = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="timezone-aware"):
            _make_cycle(
                state=LearningCycleState.RESULTADO_REGISTRADO,
                outcome_observed="Resultado",
                result_registered_at=datetime.now(),
                initiated_at=base_time,
                created_at=base_time,
                updated_at=base_time,
            )


class TestLearningCycleTransitions:
    def test_register_result_transitions_correctly(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        cycle.register_result(
            outcome_observed="Ventas subieron 15%",
            outcome_matches_expectation=True,
            observed_at=base_time + timedelta(hours=1),
        )
        assert cycle.state == LearningCycleState.RESULTADO_REGISTRADO
        assert cycle.outcome_observed == "Ventas subieron 15%"
        assert cycle.result_registered_at is not None

    def test_complete_attribution_transitions_correctly(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_result(cycle, base_time)
        cycle.complete_attribution(
            attribution_type=AttributionType.MIXTA,
            attribution_reasoning="Decisión + factores externos",
            completed_at=base_time + timedelta(hours=2),
        )
        assert cycle.state == LearningCycleState.ATRIBUCION_COMPLETADA
        assert cycle.attribution_type == AttributionType.MIXTA

    def test_extract_learning_transitions_correctly(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_attribution(cycle, base_time)
        cycle.extract_learning(
            statement="Las campañas de email tienen mayor ROI en PyMEs",
            confidence_delta=0.3,
            extracted_at=base_time + timedelta(hours=3),
        )
        assert cycle.state == LearningCycleState.APRENDIZAJE_EXTRAIDO
        assert cycle.confidence_delta == 0.3

    def test_register_knowledge_updates_transitions_correctly(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_learning(cycle, base_time)
        cycle.register_knowledge_updates(
            produced=[uuid4(), uuid4()],
            updated=[uuid4()],
            updated_at=base_time + timedelta(hours=4),
        )
        assert cycle.state == LearningCycleState.KI_ACTUALIZADO
        assert len(cycle.knowledge_item_ids_produced) == 2
        assert len(cycle.knowledge_item_ids_updated) == 1

    def test_close_transitions_to_cerrado(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_ki(cycle, base_time)
        cycle.close(closed_at=base_time + timedelta(hours=5))
        assert cycle.state == LearningCycleState.CERRADO
        assert cycle.closed_at is not None

    def test_abort_transitions_to_abortado_from_iniciado(self):
        cycle = _make_cycle()
        aborted_at = datetime.now(timezone.utc)
        cycle.abort(reason="Falta de datos suficientes", aborted_at=aborted_at)
        assert cycle.state == LearningCycleState.ABORTADO
        assert cycle.abort_reason == "Falta de datos suficientes"
        assert cycle.aborted_at == aborted_at

    def test_abort_transitions_to_abortado_from_resultado(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_result(cycle, base_time)
        cycle.abort(
            reason="Resultado no confiable por error de medición",
            aborted_at=base_time + timedelta(hours=2),
        )
        assert cycle.state == LearningCycleState.ABORTADO

    def test_rejects_close_from_iniciado(self):
        cycle = _make_cycle()
        with pytest.raises(ValueError, match="KI_ACTUALIZADO"):
            cycle.close(closed_at=datetime.now(timezone.utc))

    def test_rejects_any_transition_from_terminal_state(self):
        base_time = datetime.now(timezone.utc)
        cycle = _make_cycle(initiated_at=base_time)
        _advance_to_ki(cycle, base_time)
        cycle.close(closed_at=base_time + timedelta(hours=5))

        with pytest.raises(ValueError, match="INICIADO"):
            cycle.register_result("x", True, base_time)

        with pytest.raises(ValueError, match="terminal"):
            cycle.abort("razón", base_time)


class TestLearningCycleSerialization:
    def test_to_dict_and_from_dict_roundtrip(self):
        base_time = datetime.now(timezone.utc)
        original = _make_cycle(
            state=LearningCycleState.KI_ACTUALIZADO,
            organization_id=uuid4(),
            outcome_observed="Ventas subieron 20%",
            outcome_matches_expectation=True,
            attribution_type=AttributionType.EXTERNA,
            attribution_reasoning="Factor estacional",
            extracted_learning_statement="Factores estacionales dominan en Q4",
            confidence_delta=-0.1,
            knowledge_item_ids_produced=[uuid4()],
            knowledge_item_ids_updated=[uuid4()],
            result_registered_at=base_time + timedelta(hours=1),
            attribution_completed_at=base_time + timedelta(hours=2),
            learning_extracted_at=base_time + timedelta(hours=3),
            ki_updated_at=base_time + timedelta(hours=4),
            metadata={"source": "quarterly_review"},
        )

        data = original.to_dict()
        restored = LearningCycle.from_dict(data)

        assert restored.id == original.id
        assert restored.decision_record_id == original.decision_record_id
        assert restored.state == original.state
        assert restored.outcome_observed == original.outcome_observed
        assert restored.attribution_type == original.attribution_type
        assert restored.extracted_learning_statement == original.extracted_learning_statement
        assert restored.confidence_delta == original.confidence_delta
        assert restored.knowledge_item_ids_produced == original.knowledge_item_ids_produced
        assert restored.knowledge_item_ids_updated == original.knowledge_item_ids_updated
        assert restored.organization_id == original.organization_id
        assert restored.metadata == {"source": "quarterly_review"}
