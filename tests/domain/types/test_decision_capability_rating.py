"""Tests para DecisionCapabilityRating."""

import pytest

from pymia.domain.types.decision_capability_rating import DecisionCapabilityRating


def test_decision_capability_rating_values():
    assert DecisionCapabilityRating.BAJA.value == "baja"
    assert DecisionCapabilityRating.MEDIA.value == "media"
    assert DecisionCapabilityRating.ALTA.value == "alta"
    assert DecisionCapabilityRating.CRITICA.value == "critica"


def test_decision_capability_rating_from_value():
    assert DecisionCapabilityRating("baja") == DecisionCapabilityRating.BAJA
    assert DecisionCapabilityRating("alta") == DecisionCapabilityRating.ALTA


def test_decision_capability_rating_rejects_unknown_value():
    with pytest.raises(ValueError):
        DecisionCapabilityRating("unknown")
