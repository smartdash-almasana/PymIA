"""
Tests para enums de decisión.
"""

import pytest
from pymia.domain.types.decision_type import DecisionType
from pymia.domain.types.decision_outcome import DecisionOutcome
from pymia.domain.types.decision_reversibility import DecisionReversibility


class TestDecisionType:
    def test_has_6_values(self):
        assert len(DecisionType) == 6
    
    def test_values(self):
        assert DecisionType.ESTRATEGICA.value == "estrategica"
        assert DecisionType.OPERATIVA.value == "operativa"
        assert DecisionType.FINANCIERA.value == "financiera"
        assert DecisionType.COMERCIAL.value == "comercial"
        assert DecisionType.HUMANA.value == "humana"
        assert DecisionType.REGULATORIA.value == "regulatoria"
    
    def test_from_value(self):
        assert DecisionType("estrategica") == DecisionType.ESTRATEGICA
        assert DecisionType("comercial") == DecisionType.COMERCIAL


class TestDecisionOutcome:
    def test_has_5_values(self):
        assert len(DecisionOutcome) == 5
    
    def test_values(self):
        assert DecisionOutcome.PENDIENTE.value == "pendiente"
        assert DecisionOutcome.EXITOSO.value == "exitoso"
        assert DecisionOutcome.PARCIAL.value == "parcial"
        assert DecisionOutcome.FALLIDO.value == "fallido"
        assert DecisionOutcome.NO_EVALUABLE.value == "no_evaluable"
    
    def test_from_value(self):
        assert DecisionOutcome("pendiente") == DecisionOutcome.PENDIENTE
        assert DecisionOutcome("exitoso") == DecisionOutcome.EXITOSO


class TestDecisionReversibility:
    def test_has_3_values(self):
        assert len(DecisionReversibility) == 3
    
    def test_values(self):
        assert DecisionReversibility.REVERSIBLE.value == "reversible"
        assert DecisionReversibility.IRREVERSIBLE.value == "irreversible"
        assert DecisionReversibility.PARCIALMENTE_REVERSIBLE.value == "parcialmente_reversible"
    
    def test_from_value(self):
        assert DecisionReversibility("reversible") == DecisionReversibility.REVERSIBLE
        assert DecisionReversibility("irreversible") == DecisionReversibility.IRREVERSIBLE
