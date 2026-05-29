"""
Tests for IdentityCrisis value object

Valida invariantes de dominio de crisis de identidad.
Doctrina: PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md §5
"""
import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError

from pymia.domain.types.identity_layer import IdentityLayer
from pymia.domain.primitives.identity_crisis import (
    IdentityCrisis,
    VALID_CRISIS_TYPES,
)


def test_valid_construction():
    """Construcción válida."""
    c = IdentityCrisis(
        id=uuid4(),
        crisis_type="negacion",
        affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
        severity=7,
        description="La organización declara ser premium pero compite por precio",
    )
    assert c.crisis_type == "negacion"
    assert c.affected_layers == [IdentityLayer.NUCLEO_PERSISTENTE]
    assert c.severity == 7


def test_valid_construction_multiple_layers():
    """Construcción válida con múltiples capas afectadas."""
    c = IdentityCrisis(
        id=uuid4(),
        crisis_type="proposito",
        affected_layers=[
            IdentityLayer.NUCLEO_PERSISTENTE,
            IdentityLayer.CAPA_ADAPTABLE,
            IdentityLayer.CAPA_PERIFERICA,
        ],
        severity=9,
        description="Crisis de propósito generalizada",
    )
    assert len(c.affected_layers) == 3


def test_all_crisis_types_valid():
    """Los 4 tipos de crisis deben ser aceptados."""
    for crisis_type in VALID_CRISIS_TYPES:
        c = IdentityCrisis(
            id=uuid4(),
            crisis_type=crisis_type,
            affected_layers=[IdentityLayer.CAPA_ADAPTABLE],
            severity=5,
            description="Test",
        )
        assert c.crisis_type == crisis_type


def test_invalid_crisis_type():
    """crisis_type fuera de válidos debe rechazarse."""
    with pytest.raises(ValueError, match="crisis_type debe estar en"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="inexistente",
            affected_layers=[IdentityLayer.CAPA_ADAPTABLE],
            severity=5,
            description="Test",
        )


def test_invalid_empty_affected_layers():
    """affected_layers vacío debe rechazarse."""
    with pytest.raises(ValueError, match="affected_layers no vacío"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[],
            severity=5,
            description="Test",
        )


def test_invalid_affected_layers_type():
    """affected_layers debe contener IdentityLayer."""
    with pytest.raises(ValueError, match="affected_layers debe contener IdentityLayer"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=["nucleo_persistente"],  # string, no enum
            severity=5,
            description="Test",
        )


def test_invalid_severity_below_range():
    """severity < 1 debe rechazarse."""
    with pytest.raises(ValueError, match="severity debe estar en"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
            severity=0,
            description="Test",
        )


def test_invalid_severity_above_range():
    """severity > 10 debe rechazarse."""
    with pytest.raises(ValueError, match="severity debe estar en"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
            severity=11,
            description="Test",
        )


def test_valid_severity_boundaries():
    """severity en límites 1 y 10 es válido."""
    for sev in [1, 10]:
        c = IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
            severity=sev,
            description="Test",
        )
        assert c.severity == sev


def test_invalid_empty_description():
    """Description vacía debe rechazarse."""
    with pytest.raises(ValueError, match="descripción no vacía"):
        IdentityCrisis(
            id=uuid4(),
            crisis_type="negacion",
            affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
            severity=5,
            description="",
        )


def test_immutability():
    """Value object debe ser inmutable."""
    c = IdentityCrisis(
        id=uuid4(),
        crisis_type="negacion",
        affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
        severity=5,
        description="Test",
    )
    with pytest.raises(FrozenInstanceError):
        c.severity = 8


def test_to_dict_serialization():
    """Serialización a diccionario JSON-compatible."""
    cid = uuid4()
    c = IdentityCrisis(
        id=cid,
        crisis_type="negacion",
        affected_layers=[
            IdentityLayer.NUCLEO_PERSISTENTE,
            IdentityLayer.CAPA_ADAPTABLE,
        ],
        severity=7,
        description="Test crisis",
    )
    data = c.to_dict()
    assert data["id"] == str(cid)
    assert data["crisis_type"] == "negacion"
    assert data["affected_layers"] == ["nucleo_persistente", "capa_adaptable"]
    assert data["severity"] == 7
    assert data["description"] == "Test crisis"
    assert data["metadata"] == {}


def test_to_dict_with_metadata():
    """Serialización con metadata."""
    c = IdentityCrisis(
        id=uuid4(),
        crisis_type="negacion",
        affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
        severity=7,
        description="Test",
        metadata={"source": "entrevista"},
    )
    data = c.to_dict()
    assert data["metadata"] == {"source": "entrevista"}


def test_equality():
    """Value objects con mismos datos deben ser iguales."""
    cid = uuid4()
    c1 = IdentityCrisis(
        id=cid,
        crisis_type="negacion",
        affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
        severity=7,
        description="Test",
    )
    c2 = IdentityCrisis(
        id=cid,
        crisis_type="negacion",
        affected_layers=[IdentityLayer.NUCLEO_PERSISTENTE],
        severity=7,
        description="Test",
    )
    assert c1 == c2
