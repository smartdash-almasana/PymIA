"""Tests para DecisionCapabilityAssessment."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from pymia.domain.snapshots.decision_capability_assessment import DecisionCapabilityAssessment
from pymia.domain.types.decision_capability_rating import DecisionCapabilityRating


def _make_assessment(**kwargs):
    defaults = {
        "id": uuid4(),
        "organization_id": uuid4(),
        "decision_record_ids": [uuid4()],
        "learning_cycle_ids": [uuid4()],
        "rating": DecisionCapabilityRating.MEDIA,
        "summary": "Evaluación suficiente de capacidad decisional",
        "strengths": ["Registra decisiones relevantes"],
        "weaknesses": [],
        "recommended_improvements": ["Mejorar cierre de aprendizaje"],
        "assessed_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return DecisionCapabilityAssessment(**defaults)


def test_valid_minimal_assessment():
    assessment = _make_assessment(learning_cycle_ids=[])
    assert assessment.decision_count() == 1
    assert assessment.learning_cycle_count() == 0
    assert not assessment.has_learning_evidence()
    assert not assessment.is_low_capability()


def test_valid_low_capability_assessment():
    assessment = _make_assessment(
        rating=DecisionCapabilityRating.BAJA,
        weaknesses=["No cierra aprendizajes posteriores a decisiones"],
    )
    assert assessment.is_low_capability()
    assert assessment.has_learning_evidence()


def test_is_frozen():
    assessment = _make_assessment()
    with pytest.raises(FrozenInstanceError):
        assessment.summary = "otro"


def test_rejects_missing_organization_id():
    with pytest.raises(ValueError, match="organization_id"):
        _make_assessment(organization_id=None)


def test_rejects_empty_decision_record_ids():
    with pytest.raises(ValueError, match="decision_record_ids"):
        _make_assessment(decision_record_ids=[])


def test_rejects_duplicate_decision_record_ids():
    did = uuid4()
    with pytest.raises(ValueError, match="decision_record_ids"):
        _make_assessment(decision_record_ids=[did, did])


def test_rejects_duplicate_learning_cycle_ids():
    lid = uuid4()
    with pytest.raises(ValueError, match="learning_cycle_ids"):
        _make_assessment(learning_cycle_ids=[lid, lid])


def test_rejects_invalid_rating():
    with pytest.raises(ValueError, match="DecisionCapabilityRating"):
        _make_assessment(rating="media")


def test_rejects_short_summary():
    with pytest.raises(ValueError, match="summary"):
        _make_assessment(summary="corto")


def test_rejects_empty_recommended_improvements():
    with pytest.raises(ValueError, match="recommended_improvements"):
        _make_assessment(recommended_improvements=[])


def test_low_or_critical_rating_requires_weaknesses():
    with pytest.raises(ValueError, match="weaknesses"):
        _make_assessment(rating=DecisionCapabilityRating.BAJA, weaknesses=[])
    with pytest.raises(ValueError, match="weaknesses"):
        _make_assessment(rating=DecisionCapabilityRating.CRITICA, weaknesses=[])


def test_rejects_naive_assessed_at():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_assessment(assessed_at=datetime.now())


def test_rejects_empty_assessor():
    with pytest.raises(ValueError, match="assessor"):
        _make_assessment(assessor="   ")


def test_to_dict_and_from_dict_roundtrip():
    assessment = _make_assessment(
        rating=DecisionCapabilityRating.ALTA,
        organization_id=uuid4(),
        decision_record_ids=[uuid4(), uuid4()],
        learning_cycle_ids=[uuid4()],
        strengths=["Aprendizaje consistente"],
        weaknesses=["Poca evidencia cuantitativa"],
        recommended_improvements=["Aumentar trazabilidad"],
        assessor="PymIA",
        metadata={"k": "v"},
    )
    data = assessment.to_dict()
    restored = DecisionCapabilityAssessment.from_dict(data)
    assert restored == assessment
    assert data["rating"] == "alta"
    assert data["metadata"] == {"k": "v"}
