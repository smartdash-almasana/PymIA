"""Tests para DiagnosticReport."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from pymia.domain.snapshots.diagnostic_report import DiagnosticReport
from pymia.domain.types.diagnostic_status import DiagnosticStatus


def _make_report(**kwargs):
    defaults = {
        "id": uuid4(),
        "health_assessment_id": uuid4(),
        "summary": "Resumen ejecutivo del diagnóstico organizacional",
        "clinical_conclusion": "Conclusión clínica suficientemente específica",
        "issued_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return DiagnosticReport(**defaults)


def test_valid_minimal_report():
    report = _make_report()
    assert report.diagnostic_status == DiagnosticStatus.PRELIMINAR
    assert not report.has_pathologies()
    assert report.pathology_count() == 0
    assert report.evidence_count() == 0


def test_valid_full_report():
    p1 = uuid4()
    p2 = uuid4()
    k1 = uuid4()
    report = _make_report(
        pathology_ids=[p1, p2],
        evidence_knowledge_item_ids=[k1],
        diagnostic_status=DiagnosticStatus.CONFIRMADO,
        organization_id=uuid4(),
        issuer="PymIA",
        notes="Notas clínicas",
        metadata={"source": "unit_test"},
    )
    assert report.has_pathologies()
    assert report.pathology_count() == 2
    assert report.evidence_count() == 1
    assert report.metadata == {"source": "unit_test"}


def test_is_frozen():
    report = _make_report()
    with pytest.raises(FrozenInstanceError):
        report.summary = "otro"


def test_rejects_empty_health_assessment_id():
    with pytest.raises(ValueError, match="health_assessment_id"):
        _make_report(health_assessment_id=None)


def test_rejects_short_summary():
    with pytest.raises(ValueError, match="summary"):
        _make_report(summary="corto")


def test_rejects_short_clinical_conclusion():
    with pytest.raises(ValueError, match="clinical_conclusion"):
        _make_report(clinical_conclusion="corta")


def test_rejects_invalid_status_type():
    with pytest.raises(ValueError, match="DiagnosticStatus"):
        _make_report(diagnostic_status="preliminar")


def test_rejects_duplicate_pathology_ids():
    pid = uuid4()
    with pytest.raises(ValueError, match="pathology_ids"):
        _make_report(pathology_ids=[pid, pid])


def test_rejects_duplicate_evidence_ids():
    kid = uuid4()
    with pytest.raises(ValueError, match="evidence_knowledge_item_ids"):
        _make_report(evidence_knowledge_item_ids=[kid, kid])


def test_rejects_naive_issued_at():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_report(issued_at=datetime.now())


def test_rejects_empty_issuer():
    with pytest.raises(ValueError, match="issuer"):
        _make_report(issuer="   ")


def test_to_dict_and_from_dict_roundtrip():
    report = _make_report(
        pathology_ids=[uuid4()],
        evidence_knowledge_item_ids=[uuid4(), uuid4()],
        diagnostic_status=DiagnosticStatus.CONFIRMADO,
        organization_id=uuid4(),
        issuer="PymIA",
        notes="Notas",
        metadata={"k": "v"},
    )
    data = report.to_dict()
    restored = DiagnosticReport.from_dict(data)
    assert restored == report
    assert data["diagnostic_status"] == "confirmado"
    assert data["metadata"] == {"k": "v"}
