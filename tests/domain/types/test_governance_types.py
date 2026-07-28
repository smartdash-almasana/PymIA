"""Tests para tipos de GovernanceProfile."""

import pytest

from pymia.domain.types.decision_authority_type import DecisionAuthorityType
from pymia.domain.types.governance_formality_level import GovernanceFormalityLevel


def test_decision_authority_type_values():
    assert DecisionAuthorityType.CENTRALIZADA.value == "centralizada"
    assert DecisionAuthorityType.DISTRIBUIDA.value == "distribuida"
    assert DecisionAuthorityType.CONSULTIVA.value == "consultiva"
    assert DecisionAuthorityType.CONSENSUAL.value == "consensual"


def test_governance_formality_level_values():
    assert GovernanceFormalityLevel.INFORMAL.value == "informal"
    assert GovernanceFormalityLevel.PARCIAL.value == "parcial"
    assert GovernanceFormalityLevel.FORMAL.value == "formal"
    assert GovernanceFormalityLevel.INSTITUCIONALIZADA.value == "institucionalizada"


def test_governance_enums_from_value():
    assert DecisionAuthorityType("centralizada") == DecisionAuthorityType.CENTRALIZADA
    assert GovernanceFormalityLevel("formal") == GovernanceFormalityLevel.FORMAL


def test_governance_enums_reject_unknown_value():
    with pytest.raises(ValueError):
        DecisionAuthorityType("unknown")
    with pytest.raises(ValueError):
        GovernanceFormalityLevel("unknown")
