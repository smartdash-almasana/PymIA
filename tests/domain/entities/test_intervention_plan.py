"""Tests para InterventionPlan."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.entities.intervention_plan import InterventionPlan
from pymia.domain.types.intervention_priority import InterventionPriority
from pymia.domain.types.intervention_status import InterventionStatus
from pymia.domain.types.intervention_type import InterventionType


def _make_plan(**kwargs):
    now = kwargs.get("created_at", datetime.now(timezone.utc))
    defaults = {
        "id": uuid4(),
        "title": "Plan de intervención comercial",
        "description": "Plan terapéutico para corregir patología comercial",
        "intervention_type": InterventionType.CURATIVA,
        "priority": InterventionPriority.ALTA,
        "pathology_ids": [uuid4()],
        "objectives": ["Recuperar margen operativo"],
        "actions": ["Ajustar lista de precios"],
        "success_criteria": ["Margen bruto mayor al 30%"],
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return InterventionPlan(**defaults)


def test_valid_minimal_plan():
    plan = _make_plan()
    assert plan.status == InterventionStatus.PROPOSED
    assert plan.pathology_ids
    assert plan.objectives
    assert plan.actions


def test_valid_full_plan():
    plan = _make_plan(
        diagnostic_report_id=uuid4(),
        risk_notes=["Riesgo de resistencia comercial"],
        owner="PymIA",
        metadata={"source": "unit_test"},
    )
    assert plan.owner == "PymIA"
    assert plan.metadata == {"source": "unit_test"}


def test_rejects_short_title():
    with pytest.raises(ValueError, match="title"):
        _make_plan(title="abc")


def test_rejects_short_description():
    with pytest.raises(ValueError, match="description"):
        _make_plan(description="corta")


def test_rejects_invalid_enums():
    with pytest.raises(ValueError, match="InterventionType"):
        _make_plan(intervention_type="curativa")
    with pytest.raises(ValueError, match="InterventionPriority"):
        _make_plan(priority="alta")
    with pytest.raises(ValueError, match="InterventionStatus"):
        _make_plan(status="proposed")


def test_rejects_empty_pathology_ids():
    with pytest.raises(ValueError, match="pathology_ids"):
        _make_plan(pathology_ids=[])


def test_rejects_duplicate_pathology_ids():
    pid = uuid4()
    with pytest.raises(ValueError, match="pathology_ids"):
        _make_plan(pathology_ids=[pid, pid])


def test_rejects_empty_text_lists():
    with pytest.raises(ValueError, match="objectives"):
        _make_plan(objectives=[])
    with pytest.raises(ValueError, match="actions"):
        _make_plan(actions=[])
    with pytest.raises(ValueError, match="success_criteria"):
        _make_plan(success_criteria=[])


def test_rejects_duplicate_text_values():
    with pytest.raises(ValueError, match="objectives"):
        _make_plan(objectives=["A", "A"])


def test_rejects_empty_owner():
    with pytest.raises(ValueError, match="owner"):
        _make_plan(owner="   ")


def test_approve_start_complete_flow():
    base = datetime.now(timezone.utc)
    plan = _make_plan(created_at=base, updated_at=base)
    plan.approve(base + timedelta(hours=1))
    assert plan.status == InterventionStatus.APPROVED
    plan.start(base + timedelta(hours=2))
    assert plan.status == InterventionStatus.IN_PROGRESS
    plan.complete(base + timedelta(hours=3))
    assert plan.status == InterventionStatus.COMPLETED
    assert plan.completed_at == base + timedelta(hours=3)


def test_cancel_from_proposed():
    base = datetime.now(timezone.utc)
    plan = _make_plan(created_at=base, updated_at=base)
    plan.cancel("Cambio de prioridad", base + timedelta(hours=1))
    assert plan.status == InterventionStatus.CANCELLED
    assert plan.cancellation_reason == "Cambio de prioridad"


def test_rejects_invalid_transition():
    plan = _make_plan()
    with pytest.raises(ValueError, match="approved"):
        plan.start(datetime.now(timezone.utc))


def test_rejects_terminal_cancel():
    base = datetime.now(timezone.utc)
    plan = _make_plan(created_at=base, updated_at=base)
    plan.approve(base + timedelta(hours=1))
    plan.start(base + timedelta(hours=2))
    plan.complete(base + timedelta(hours=3))
    with pytest.raises(ValueError, match="terminal"):
        plan.cancel("No", base + timedelta(hours=4))


def test_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_plan(created_at=datetime.now())


def test_rejects_non_monotonic_timestamps():
    base = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="monótonos"):
        _make_plan(
            status=InterventionStatus.APPROVED,
            approved_at=base - timedelta(hours=1),
            created_at=base,
            updated_at=base,
        )


def test_to_dict_and_from_dict_roundtrip():
    base = datetime.now(timezone.utc)
    plan = _make_plan(
        diagnostic_report_id=uuid4(),
        risk_notes=["Riesgo operativo"],
        owner="Equipo",
        metadata={"k": "v"},
        created_at=base,
        updated_at=base,
    )
    plan.approve(base + timedelta(hours=1))
    data = plan.to_dict()
    restored = InterventionPlan.from_dict(data)
    assert restored == plan
    assert data["status"] == "approved"
    assert data["metadata"] == {"k": "v"}
