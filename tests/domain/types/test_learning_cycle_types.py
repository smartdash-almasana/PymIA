"""Tests para LearningCycleState y AttributionType enums."""

import pytest

from pymia.domain.types.learning_cycle_state import (
    LEARNING_CYCLE_STATE_ORDER,
    LearningCycleState,
    TERMINAL_STATES,
    state_index,
)
from pymia.domain.types.attribution_type import AttributionType


class TestLearningCycleState:
    def test_has_7_values(self):
        assert len(LearningCycleState) == 7

    def test_values(self):
        assert LearningCycleState.INICIADO.value == "iniciado"
        assert LearningCycleState.RESULTADO_REGISTRADO.value == "resultado_registrado"
        assert LearningCycleState.ATRIBUCION_COMPLETADA.value == "atribucion_completada"
        assert LearningCycleState.APRENDIZAJE_EXTRAIDO.value == "aprendizaje_extraido"
        assert LearningCycleState.KI_ACTUALIZADO.value == "ki_actualizado"
        assert LearningCycleState.CERRADO.value == "cerrado"
        assert LearningCycleState.ABORTADO.value == "abortado"

    def test_from_value(self):
        assert LearningCycleState("iniciado") == LearningCycleState.INICIADO
        assert LearningCycleState("cerrado") == LearningCycleState.CERRADO
        assert LearningCycleState("abortado") == LearningCycleState.ABORTADO


class TestLearningCycleStateOrder:
    def test_order_has_6_elements(self):
        assert len(LEARNING_CYCLE_STATE_ORDER) == 6

    def test_order_ends_with_cerrado(self):
        assert LEARNING_CYCLE_STATE_ORDER[-1] == LearningCycleState.CERRADO

    def test_order_starts_with_iniciado(self):
        assert LEARNING_CYCLE_STATE_ORDER[0] == LearningCycleState.INICIADO

    def test_terminal_states(self):
        assert LearningCycleState.CERRADO in TERMINAL_STATES
        assert LearningCycleState.ABORTADO in TERMINAL_STATES
        assert len(TERMINAL_STATES) == 2

    def test_state_index(self):
        assert state_index(LearningCycleState.INICIADO) == 0
        assert state_index(LearningCycleState.CERRADO) == 5
        assert state_index(LearningCycleState.ABORTADO) == -1


class TestAttributionType:
    def test_has_4_values(self):
        assert len(AttributionType) == 4

    def test_values(self):
        assert AttributionType.INTERNA.value == "interna"
        assert AttributionType.EXTERNA.value == "externa"
        assert AttributionType.MIXTA.value == "mixta"
        assert AttributionType.AZAR.value == "azar"

    def test_from_value(self):
        assert AttributionType("interna") == AttributionType.INTERNA
        assert AttributionType("azar") == AttributionType.AZAR

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            AttributionType("invalido")
