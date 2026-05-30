"""Tests para tipos de PrognosisAssessment."""

import pytest

from pymia.domain.types.prognosis_risk_level import PrognosisRiskLevel
from pymia.domain.types.prognosis_trajectory import PrognosisTrajectory


def test_prognosis_trajectory_values():
    assert PrognosisTrajectory.ESTABLE.value == "estable"
    assert PrognosisTrajectory.MEJORA_GRADUAL.value == "mejora_gradual"
    assert PrognosisTrajectory.RECUPERACION_ACELERADA.value == "recuperacion_acelerada"
    assert PrognosisTrajectory.DETERIORO_GRADUAL.value == "deterioro_gradual"
    assert PrognosisTrajectory.DETERIORO_ACELERADO.value == "deterioro_acelerado"
    assert PrognosisTrajectory.ERRATICA.value == "erratica"


def test_prognosis_risk_level_values():
    assert PrognosisRiskLevel.BAJO.value == "bajo"
    assert PrognosisRiskLevel.MEDIO.value == "medio"
    assert PrognosisRiskLevel.ALTO.value == "alto"
    assert PrognosisRiskLevel.CRITICO.value == "critico"


def test_prognosis_enums_from_value():
    assert PrognosisTrajectory("estable") == PrognosisTrajectory.ESTABLE
    assert PrognosisTrajectory("deterioro_acelerado") == PrognosisTrajectory.DETERIORO_ACELERADO
    assert PrognosisRiskLevel("alto") == PrognosisRiskLevel.ALTO


def test_prognosis_enums_reject_unknown_value():
    with pytest.raises(ValueError):
        PrognosisTrajectory("unknown")
    with pytest.raises(ValueError):
        PrognosisRiskLevel("unknown")
