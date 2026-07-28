"""Tests para FunctionalOrgan value object."""
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from pymia.domain.primitives.functional_organ import (
    FunctionalOrgan,
    VALID_ORGAN_STATES,
)
from pymia.domain.types.functional_organ_type import FunctionalOrganType


def _valid_timestamp() -> datetime:
    """Helper: timestamp timezone-aware."""
    return datetime.now(timezone.utc)


def _make_organ(**overrides) -> FunctionalOrgan:
    """Helper: construye FunctionalOrgan válido con overrides opcionales."""
    defaults = {
        "organ_type": FunctionalOrganType.CIRCULATORIO,
        "state": "sano",
        "capacity_score": 85.0,
        "observed_at": _valid_timestamp(),
        "description": "Flujo de caja estable",
        "symptoms": [],
        "metadata": {},
    }
    defaults.update(overrides)
    return FunctionalOrgan(**defaults)


# ============================================================
# Construcción válida
# ============================================================

def test_valid_construction_sano():
    """Órgano sano: no requiere síntomas."""
    organ = _make_organ()
    assert organ.organ_type == FunctionalOrganType.CIRCULATORIO
    assert organ.state == "sano"
    assert organ.capacity_score == 85.0
    assert organ.symptoms == []


def test_valid_construction_enfermo():
    """Órgano enfermo: requiere descripción y síntomas."""
    organ = _make_organ(
        state="enfermo",
        capacity_score=35.0,
        description="Caída sostenida de ingresos",
        symptoms=["Ingresos -30% interanual", "Pérdida de 2 clientes clave"],
    )
    assert organ.state == "enfermo"
    assert len(organ.symptoms) == 2


def test_valid_construction_fragil():
    """Órgano frágil: funciona pero vulnerable."""
    organ = _make_organ(state="fragil", capacity_score=60.0)
    assert organ.state == "fragil"


def test_valid_construction_critico():
    """Órgano crítico: requiere descripción y síntomas."""
    organ = _make_organ(
        state="critico",
        capacity_score=10.0,
        description="Caja alcanza para 3 días",
        symptoms=["Sin acceso a crédito", "Deuda urgente"],
    )
    assert organ.state == "critico"


# ============================================================
# Invariantes de dominio (rechazos)
# ============================================================

def test_rejects_invalid_state():
    """state fuera de VALID_ORGAN_STATES debe rechazarse."""
    with pytest.raises(ValueError, match="state debe estar en"):
        _make_organ(state="desconocido")


def test_rejects_capacity_score_below_zero():
    """capacity_score < 0 debe rechazarse."""
    with pytest.raises(ValueError, match="capacity_score"):
        _make_organ(capacity_score=-1.0)


def test_rejects_capacity_score_above_hundred():
    """capacity_score > 100 debe rechazarse."""
    with pytest.raises(ValueError, match="capacity_score"):
        _make_organ(capacity_score=101.0)


def test_rejects_naive_datetime():
    """observed_at sin timezone debe rechazarse."""
    with pytest.raises(ValueError, match="timezone-aware"):
        _make_organ(observed_at=datetime(2026, 5, 31, 10, 0, 0))


def test_rejects_enfermo_without_description():
    """Estado enfermo sin descripción debe rechazarse."""
    with pytest.raises(ValueError, match="requiere descripción"):
        _make_organ(
            state="enfermo",
            description="",
            symptoms=["Algo está mal"],
        )


def test_rejects_enfermo_without_symptoms():
    """Estado enfermo sin síntomas debe rechazarse."""
    with pytest.raises(ValueError, match="requiere al menos un síntoma"):
        _make_organ(
            state="enfermo",
            description="Algo está mal",
            symptoms=[],
        )


def test_rejects_critico_without_description():
    """Estado crítico sin descripción debe rechazarse."""
    with pytest.raises(ValueError, match="requiere descripción"):
        _make_organ(
            state="critico",
            description="  ",
            symptoms=["Grave"],
        )


def test_rejects_critico_without_symptoms():
    """Estado crítico sin síntomas debe rechazarse."""
    with pytest.raises(ValueError, match="requiere al menos un síntoma"):
        _make_organ(
            state="critico",
            description="Grave",
            symptoms=[],
        )


def test_rejects_invalid_organ_type():
    """organ_type que no sea FunctionalOrganType debe rechazarse."""
    with pytest.raises(ValueError, match="organ_type debe ser FunctionalOrganType"):
        _make_organ(organ_type="circulatorio")


# ============================================================
# Inmutabilidad
# ============================================================

def test_immutability():
    """FunctionalOrgan debe ser frozen (inmutable)."""
    organ = _make_organ()
    with pytest.raises(FrozenInstanceError):
        organ.state = "enfermo"


# ============================================================
# Serialización
# ============================================================

def test_to_dict_serialization():
    """to_dict debe producir dict JSON-compatible."""
    ts = datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc)
    organ = FunctionalOrgan(
        organ_type=FunctionalOrganType.RESPIRATORIO,
        state="fragil",
        capacity_score=55.5,
        observed_at=ts,
        description="Ventas inestables",
        symptoms=["Estacionalidad alta"],
        metadata={"source": "observacion"},
    )
    d = organ.to_dict()
    assert d["organ_type"] == "respiratorio"
    assert d["state"] == "fragil"
    assert d["capacity_score"] == 55.5
    assert d["observed_at"] == ts.isoformat()
    assert d["description"] == "Ventas inestables"
    assert d["symptoms"] == ["Estacionalidad alta"]
    assert d["metadata"] == {"source": "observacion"}


def test_to_dict_metadata_default_empty_dict():
    """metadata=None debe serializarse como {}."""
    organ = _make_organ(metadata=None)
    d = organ.to_dict()
    assert d["metadata"] == {}


def test_from_dict_roundtrip():
    """from_dict(to_dict()) debe reconstruir el value object."""
    original = FunctionalOrgan(
        organ_type=FunctionalOrganType.NERVIOSO,
        state="sano",
        capacity_score=90.0,
        observed_at=datetime(2026, 5, 31, 12, 0, 0, tzinfo=timezone.utc),
        description="Decisiones ágiles",
        symptoms=[],
        metadata={"reviewer": "owner"},
    )
    d = original.to_dict()
    restored = FunctionalOrgan.from_dict(d)
    assert restored.organ_type == original.organ_type
    assert restored.state == original.state
    assert restored.capacity_score == original.capacity_score
    assert restored.description == original.description
    assert restored.symptoms == original.symptoms
    assert restored.metadata == original.metadata


# ============================================================
# Constantes exportadas
# ============================================================

def test_valid_organ_states_constant():
    """VALID_ORGAN_STATES debe contener exactamente 4 estados."""
    assert len(VALID_ORGAN_STATES) == 4
    assert "sano" in VALID_ORGAN_STATES
    assert "fragil" in VALID_ORGAN_STATES
    assert "enfermo" in VALID_ORGAN_STATES
    assert "critico" in VALID_ORGAN_STATES


def test_same_business_value_as_ignores_metadata_and_timestamp():
    o1 = _make_organ(
        observed_at=datetime(2026, 5, 31, 10, 0, 0, tzinfo=timezone.utc),
        metadata={"m": 1},
    )
    o2 = _make_organ(
        observed_at=datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
        metadata={"m": 2},
    )
    assert o1.same_business_value_as(o2) is True


def test_same_business_value_as_detects_real_content_difference():
    o1 = _make_organ(state="sano")
    o2 = _make_organ(state="fragil")
    assert o1.same_business_value_as(o2) is False
