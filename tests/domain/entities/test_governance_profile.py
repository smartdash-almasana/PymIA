"""Tests para GovernanceProfile."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from pymia.domain.entities.governance_profile import GovernanceProfile
from pymia.domain.types.decision_authority_type import DecisionAuthorityType
from pymia.domain.types.governance_formality_level import GovernanceFormalityLevel


def _make_profile(**kwargs):
    now = kwargs.get("created_at", datetime.now(timezone.utc))
    defaults = {
        "id": uuid4(),
        "organization_id": uuid4(),
        "authority_type": DecisionAuthorityType.CENTRALIZADA,
        "formality_level": GovernanceFormalityLevel.PARCIAL,
        "decision_makers": ["Dueño"],
        "decision_scope_by_maker": {"Dueño": ["precios", "compras"]},
        "decision_processes": ["Revisión semanal de decisiones críticas"],
        "coherence_mechanisms": ["Comparación contra objetivos mensuales"],
        "review_cadence": "mensual",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return GovernanceProfile(**defaults)


def test_valid_minimal_profile():
    profile = _make_profile()
    assert profile.decision_maker_count() == 1
    assert profile.process_count() == 1
    assert profile.coherence_mechanism_count() == 1
    assert not profile.has_reviewed_governance()


def test_valid_distributed_profile():
    profile = _make_profile(
        authority_type=DecisionAuthorityType.DISTRIBUIDA,
        decision_makers=["Dueño", "Gerente"],
        decision_scope_by_maker={"Dueño": ["estrategia"], "Gerente": ["operaciones"]},
        deviation_detection_method="Revisión mensual de desvíos operativos",
        correction_process_description="Corrección acordada en reunión de dirección",
        metadata={"source": "unit_test"},
    )
    assert profile.decision_maker_count() == 2
    assert profile.metadata == {"source": "unit_test"}


def test_rejects_missing_organization_id():
    with pytest.raises(ValueError, match="organization_id"):
        _make_profile(organization_id=None)


def test_rejects_invalid_enums():
    with pytest.raises(ValueError, match="DecisionAuthorityType"):
        _make_profile(authority_type="centralizada")
    with pytest.raises(ValueError, match="GovernanceFormalityLevel"):
        _make_profile(formality_level="formal")


def test_rejects_empty_decision_makers():
    with pytest.raises(ValueError, match="decision_makers"):
        _make_profile(decision_makers=[])


def test_rejects_scope_for_undeclared_maker():
    with pytest.raises(ValueError, match="maker no declarado"):
        _make_profile(decision_scope_by_maker={"Otro": ["precios"]})


def test_rejects_empty_scope_values():
    with pytest.raises(ValueError, match="strings vacíos"):
        _make_profile(decision_scope_by_maker={"Dueño": ["   "]})


def test_rejects_centralized_with_multiple_makers():
    with pytest.raises(ValueError, match="exactamente un"):
        _make_profile(
            authority_type=DecisionAuthorityType.CENTRALIZADA,
            decision_makers=["Dueño", "Gerente"],
            decision_scope_by_maker={"Dueño": ["estrategia"], "Gerente": ["operaciones"]},
        )


def test_rejects_distributed_with_single_maker():
    with pytest.raises(ValueError, match="al menos dos"):
        _make_profile(authority_type=DecisionAuthorityType.DISTRIBUIDA)


def test_rejects_short_optional_texts():
    with pytest.raises(ValueError, match="deviation_detection_method"):
        _make_profile(deviation_detection_method="corto")
    with pytest.raises(ValueError, match="correction_process_description"):
        _make_profile(correction_process_description="corto")


def test_rejects_naive_timestamps():
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_profile(created_at=datetime.now())


def test_rejects_last_reviewed_before_created_at():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="last_reviewed_at"):
        _make_profile(created_at=now, updated_at=now, last_reviewed_at=now - timedelta(days=1))


def test_update_authority_revalidates():
    now = datetime.now(timezone.utc)
    profile = _make_profile(created_at=now, updated_at=now)
    profile.update_authority(
        DecisionAuthorityType.DISTRIBUIDA,
        ["Dueño", "Gerente"],
        {"Dueño": ["estrategia"], "Gerente": ["operaciones"]},
        now + timedelta(hours=1),
    )
    assert profile.authority_type == DecisionAuthorityType.DISTRIBUIDA
    assert profile.decision_maker_count() == 2


def test_update_authority_rejects_invalid_scope():
    now = datetime.now(timezone.utc)
    profile = _make_profile(created_at=now, updated_at=now)
    with pytest.raises(ValueError, match="maker no declarado"):
        profile.update_authority(
            DecisionAuthorityType.DISTRIBUIDA,
            ["Dueño", "Gerente"],
            {"Dueño": ["estrategia"], "Otro": ["operaciones"]},
            now + timedelta(hours=1),
        )


def test_update_review():
    now = datetime.now(timezone.utc)
    profile = _make_profile(created_at=now, updated_at=now)
    reviewed_at = now + timedelta(days=1)
    profile.update_review(
        reviewed_at,
        deviation_detection_method="Análisis mensual de desvíos relevantes",
        correction_process_description="Reunión directiva para corregir desvíos",
    )
    assert profile.last_reviewed_at == reviewed_at
    assert profile.has_reviewed_governance()


def test_to_dict_and_from_dict_roundtrip():
    now = datetime.now(timezone.utc)
    profile = _make_profile(
        created_at=now,
        updated_at=now,
        last_reviewed_at=now + timedelta(days=1),
        deviation_detection_method="Revisión de indicadores de coherencia",
        correction_process_description="Ajuste de autoridad y procesos decisionales",
        metadata={"k": "v"},
    )
    data = profile.to_dict()
    restored = GovernanceProfile.from_dict(data)
    assert restored == profile
    assert data["authority_type"] == "centralizada"
    assert data["metadata"] == {"k": "v"}
