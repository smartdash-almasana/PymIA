"""Tests para tipos de InterventionPlan."""

import pytest

from pymia.domain.types.intervention_priority import InterventionPriority
from pymia.domain.types.intervention_status import InterventionStatus
from pymia.domain.types.intervention_type import InterventionType


def test_intervention_type_values():
    assert InterventionType.SINTOMATICA.value == "sintomatica"
    assert InterventionType.CURATIVA.value == "curativa"
    assert InterventionType.PALIATIVA.value == "paliativa"
    assert InterventionType.PREVENTIVA.value == "preventiva"


def test_intervention_priority_values():
    assert InterventionPriority.BAJA.value == "baja"
    assert InterventionPriority.MEDIA.value == "media"
    assert InterventionPriority.ALTA.value == "alta"
    assert InterventionPriority.CRITICA.value == "critica"


def test_intervention_status_values():
    assert InterventionStatus.PROPOSED.value == "proposed"
    assert InterventionStatus.APPROVED.value == "approved"
    assert InterventionStatus.IN_PROGRESS.value == "in_progress"
    assert InterventionStatus.COMPLETED.value == "completed"
    assert InterventionStatus.CANCELLED.value == "cancelled"


def test_intervention_enums_from_value():
    assert InterventionType("curativa") == InterventionType.CURATIVA
    assert InterventionPriority("alta") == InterventionPriority.ALTA
    assert InterventionStatus("completed") == InterventionStatus.COMPLETED


def test_intervention_enums_reject_unknown_value():
    with pytest.raises(ValueError):
        InterventionType("unknown")
    with pytest.raises(ValueError):
        InterventionPriority("unknown")
    with pytest.raises(ValueError):
        InterventionStatus("unknown")
