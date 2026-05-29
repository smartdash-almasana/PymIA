"""
Tests for OrganizationalConstraint value object

Valida invariantes de dominio de restricciones organizacionales.
Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §7
"""
import pytest
from datetime import datetime
from uuid import uuid4
from dataclasses import FrozenInstanceError

from pymia.domain.types import ConstraintType
from pymia.domain.primitives.organizational_constraint import OrganizationalConstraint


def test_valid_construction_string_magnitude():
    """Construcción válida con magnitude string."""
    c = OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.CAJA,
        magnitude="150000 ARS",
        description="Caja mensual disponible",
        observed_at=datetime(2026, 5, 31, 10, 0, 0),
    )
    assert c.constraint_type == ConstraintType.CAJA
    assert c.magnitude == "150000 ARS"


def test_valid_construction_numeric_magnitude():
    """Construcción válida con magnitude numérico."""
    c = OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.TIEMPO,
        magnitude=160,
        description="Horas-hombre mensuales",
        observed_at=datetime.now(),
    )
    assert c.magnitude == 160


def test_valid_construction_zero_magnitude():
    """Magnitude 0 es válido."""
    c = OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.CAJA,
        magnitude=0,
        description="Caja agotada",
        observed_at=datetime.now(),
    )
    assert c.magnitude == 0


def test_invalid_negative_numeric_magnitude():
    """Magnitude numérica negativa debe rechazarse."""
    with pytest.raises(ValueError, match="magnitude numérica debe ser >= 0"):
        OrganizationalConstraint(
            id=uuid4(),
            constraint_type=ConstraintType.CAJA,
            magnitude=-100,
            description="Caja negativa",
            observed_at=datetime.now(),
        )


def test_invalid_empty_string_magnitude():
    """Magnitude string vacío debe rechazarse."""
    with pytest.raises(ValueError, match="magnitude string no puede estar vacía"):
        OrganizationalConstraint(
            id=uuid4(),
            constraint_type=ConstraintType.CAJA,
            magnitude="",
            description="Sin magnitude",
            observed_at=datetime.now(),
        )


def test_invalid_empty_description():
    """Description vacía debe rechazarse."""
    with pytest.raises(ValueError, match="descripción no vacía"):
        OrganizationalConstraint(
            id=uuid4(),
            constraint_type=ConstraintType.CAJA,
            magnitude="150000",
            description="",
            observed_at=datetime.now(),
        )


def test_invalid_constraint_type():
    """constraint_type debe ser ConstraintType válido."""
    with pytest.raises(ValueError, match="constraint_type debe ser ConstraintType"):
        OrganizationalConstraint(
            id=uuid4(),
            constraint_type="caja",  # string, no enum
            magnitude="150000",
            description="Algo",
            observed_at=datetime.now(),
        )


def test_immutability():
    """Value object debe ser inmutable."""
    c = OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.CAJA,
        magnitude="150000",
        description="Caja",
        observed_at=datetime.now(),
    )
    with pytest.raises(FrozenInstanceError):
        c.magnitude = "200000"


def test_to_dict_serialization():
    """Serialización a diccionario JSON-compatible."""
    cid = uuid4()
    observed_at = datetime(2026, 5, 31, 10, 0, 0)
    c = OrganizationalConstraint(
        id=cid,
        constraint_type=ConstraintType.CAJA,
        magnitude="150000 ARS",
        description="Caja",
        observed_at=observed_at,
    )
    data = c.to_dict()
    assert data["id"] == str(cid)
    assert data["constraint_type"] == "caja"
    assert data["magnitude"] == "150000 ARS"
    assert data["description"] == "Caja"
    assert data["observed_at"] == "2026-05-31T10:00:00"
    assert data["metadata"] == {}


def test_to_dict_with_metadata():
    """Serialización con metadata."""
    c = OrganizationalConstraint(
        id=uuid4(),
        constraint_type=ConstraintType.CAJA,
        magnitude="150000",
        description="Caja",
        observed_at=datetime.now(),
        metadata={"source": "extracto_bancario"},
    )
    data = c.to_dict()
    assert data["metadata"] == {"source": "extracto_bancario"}


def test_equality():
    """Value objects con mismos datos deben ser iguales."""
    cid = uuid4()
    ts = datetime(2026, 5, 31, 10, 0, 0)
    c1 = OrganizationalConstraint(
        id=cid,
        constraint_type=ConstraintType.CAJA,
        magnitude="150000",
        description="Caja",
        observed_at=ts,
    )
    c2 = OrganizationalConstraint(
        id=cid,
        constraint_type=ConstraintType.CAJA,
        magnitude="150000",
        description="Caja",
        observed_at=ts,
    )
    assert c1 == c2
