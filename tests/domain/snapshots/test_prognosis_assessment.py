"""Tests para PrognosisAssessment."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.snapshots.prognosis_assessment import PrognosisAssessment
from pymia.domain.types.prognosis_risk_level import PrognosisRiskLevel
from pymia.domain.types.prognosis_trajectory import PrognosisTrajectory


def _make_assessment(**kwargs):
    now = kwargs.get("assessed_at", datetime.now(timezone.utc))
    defaults = {
        "id": uuid4(),
        "diagnostic_report_id": uuid4(),
        "pathology_ids": [uuid4()],
        "trajectory": PrognosisTrajectory.DETERIORO_GRADUAL,
        "risk_level": PrognosisRiskLevel.MEDIO,
        "summary": "Resumen pronóstico organizacional suficiente",
        "projected_outcome": "La organización tenderá a deterioro moderado",
        "recommended_monitoring": ["Revisar margen semanalmente"],
        "assessed_at": now,
    }
    defaults.update(kwargs)
    return PrognosisAssessment(**defaults)


def test_valid_minimal_assessment():
    assessment = _make_assessment()
    assert assessment.pathology_count() == 1
    assert assessment.monitoring_count() == 1
    assert not assessment.is_high_risk()
    assert not assessment.has_intervention_plan()
    assert not assessment.has_point_of_no_return()


def test_valid_full_assessment():
    now = datetime.now(timezone.utc)
    assessment = _make_assessment(
        risk_level=PrognosisRiskLevel.ALTO,
        key_risks=["Pérdida de liquidez"],
        intervention_plan_id=uuid4(),
        point_of_no_return=now + timedelta(days=30),
        point_of_no_return_description="Sin intervención se pierde caja operativa",
        intervention_window_days=14,
        organization_id=uuid4(),
        assessed_at=now,
        assessor="PymIA",
        notes="Notas pronósticas",
        metadata={"source": "unit_test"},
    )
    assert assessment.is_high_risk()
    assert assessment.has_intervention_plan()
    assert assessment.has_point_of_no_return()
    assert assessment.metadata == {"source": "unit_test"}


def test_is_frozen():
    assessment = _make_assessment()
    with pytest.raises(FrozenInstanceError):
        assessment.summary = "otro"


def test_rejects_empty_pathology_ids():
    with pytest.raises(ValueError, match="pathology_ids"):
        _make_assessment(pathology_ids=[])


def test_rejects_duplicate_pathology_ids():
    pid = uuid4()
    with pytest.raises(ValueError, match="pathology_ids"):
        _make_assessment(pathology_ids=[pid, pid])


def test_rejects_invalid_enums():
    with pytest.raises(ValueError, match="PrognosisTrajectory"):
        _make_assessment(trajectory="estable")
    with pytest.raises(ValueError, match="PrognosisRiskLevel"):
        _make_assessment(risk_level="alto")


def test_rejects_short_summary():
    with pytest.raises(ValueError, match="summary"):
        _make_assessment(summary="corto")


def test_rejects_short_projected_outcome():
    with pytest.raises(ValueError, match="projected_outcome"):
        _make_assessment(projected_outcome="corto")


def test_rejects_empty_monitoring():
    with pytest.raises(ValueError, match="recommended_monitoring"):
        _make_assessment(recommended_monitoring=[])


def test_high_risk_requires_key_risks():
    with pytest.raises(ValueError, match="key_risks"):
        _make_assessment(risk_level=PrognosisRiskLevel.ALTO, key_risks=[])
    with pytest.raises(ValueError, match="key_risks"):
        _make_assessment(risk_level=PrognosisRiskLevel.CRITICO, key_risks=[])


def test_rejects_naive_assessed_at():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_assessment(assessed_at=datetime.now())


def test_point_of_no_return_must_be_after_assessed_at():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="posterior"):
        _make_assessment(
            assessed_at=now,
            point_of_no_return=now - timedelta(days=1),
            point_of_no_return_description="Descripción válida",
        )


def test_point_of_no_return_requires_description():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="descripción"):
        _make_assessment(point_of_no_return=now + timedelta(days=1))


def test_description_requires_point_of_no_return():
    with pytest.raises(ValueError, match="requiere point_of_no_return"):
        _make_assessment(point_of_no_return_description="Descripción huérfana")


def test_rejects_invalid_intervention_window_days():
    with pytest.raises(ValueError, match="intervention_window_days"):
        _make_assessment(intervention_window_days=0)


def test_rejects_empty_assessor():
    with pytest.raises(ValueError, match="assessor"):
        _make_assessment(assessor="   ")


def test_to_dict_and_from_dict_roundtrip():
    now = datetime.now(timezone.utc)
    assessment = _make_assessment(
        risk_level=PrognosisRiskLevel.CRITICO,
        key_risks=["Riesgo crítico de caja"],
        intervention_plan_id=uuid4(),
        point_of_no_return=now + timedelta(days=10),
        point_of_no_return_description="Caja negativa irreversible",
        intervention_window_days=5,
        organization_id=uuid4(),
        assessed_at=now,
        assessor="Equipo",
        notes="Notas",
        metadata={"k": "v"},
    )
    data = assessment.to_dict()
    restored = PrognosisAssessment.from_dict(data)
    assert restored == assessment
    assert data["trajectory"] == "deterioro_gradual"
    assert data["risk_level"] == "critico"
    assert data["metadata"] == {"k": "v"}
