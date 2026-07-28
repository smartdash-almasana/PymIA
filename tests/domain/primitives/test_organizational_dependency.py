"""
Tests for OrganizationalDependency value object

Valida invariantes de dominio de dependencias organizacionales.
Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §9
"""
import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError

from pymia.domain.primitives.organizational_dependency import (
    OrganizationalDependency,
    VALID_CRITICALITIES,
)


def test_valid_construction():
    """Construcción válida."""
    d = OrganizationalDependency(
        id=uuid4(),
        dependency_type="cliente_concentrado",
        criticality="critica",
        dependency_target="Cliente Mayorista SA",
        description="Representa 55% de ingresos",
    )
    assert d.dependency_type == "cliente_concentrado"
    assert d.criticality == "critica"
    assert d.dependency_target == "Cliente Mayorista SA"


def test_all_criticalities_valid():
    """Las 4 criticalities deben ser aceptadas."""
    for crit in VALID_CRITICALITIES:
        d = OrganizationalDependency(
            id=uuid4(),
            dependency_type="test",
            criticality=crit,
            dependency_target="Target",
            description="Test",
        )
        assert d.criticality == crit


def test_invalid_criticality():
    """criticality fuera de válidos debe rechazarse."""
    with pytest.raises(ValueError, match="criticality debe estar en"):
        OrganizationalDependency(
            id=uuid4(),
            dependency_type="test",
            criticality="extrema",  # no válido
            dependency_target="Target",
            description="Test",
        )


def test_invalid_criticality_case_sensitive():
    """criticality es case-sensitive."""
    with pytest.raises(ValueError, match="criticality debe estar en"):
        OrganizationalDependency(
            id=uuid4(),
            dependency_type="test",
            criticality="Critica",  # mayúscula
            dependency_target="Target",
            description="Test",
        )


def test_invalid_empty_dependency_type():
    """dependency_type vacío debe rechazarse."""
    with pytest.raises(ValueError, match="dependency_type no vacío"):
        OrganizationalDependency(
            id=uuid4(),
            dependency_type="",
            criticality="alta",
            dependency_target="Target",
            description="Test",
        )


def test_invalid_empty_dependency_target():
    """dependency_target vacío debe rechazarse."""
    with pytest.raises(ValueError, match="dependency_target no vacío"):
        OrganizationalDependency(
            id=uuid4(),
            dependency_type="test",
            criticality="alta",
            dependency_target="",
            description="Test",
        )


def test_invalid_empty_description():
    """Description vacía debe rechazarse."""
    with pytest.raises(ValueError, match="descripción no vacía"):
        OrganizationalDependency(
            id=uuid4(),
            dependency_type="test",
            criticality="alta",
            dependency_target="Target",
            description="",
        )


def test_immutability():
    """Value object debe ser inmutable."""
    d = OrganizationalDependency(
        id=uuid4(),
        dependency_type="test",
        criticality="alta",
        dependency_target="Target",
        description="Test",
    )
    with pytest.raises(FrozenInstanceError):
        d.criticality = "critica"


def test_to_dict_serialization():
    """Serialización a diccionario JSON-compatible."""
    did = uuid4()
    d = OrganizationalDependency(
        id=did,
        dependency_type="cliente_concentrado",
        criticality="critica",
        dependency_target="Cliente Mayorista SA",
        description="55% de ingresos",
    )
    data = d.to_dict()
    assert data["id"] == str(did)
    assert data["dependency_type"] == "cliente_concentrado"
    assert data["criticality"] == "critica"
    assert data["dependency_target"] == "Cliente Mayorista SA"
    assert data["description"] == "55% de ingresos"
    assert data["metadata"] == {}


def test_to_dict_with_metadata():
    """Serialización con metadata."""
    d = OrganizationalDependency(
        id=uuid4(),
        dependency_type="cliente_concentrado",
        criticality="critica",
        dependency_target="Cliente",
        description="Test",
        metadata={"revenue_pct": 0.55},
    )
    data = d.to_dict()
    assert data["metadata"] == {"revenue_pct": 0.55}


def test_equality():
    """Value objects con mismos datos deben ser iguales."""
    did = uuid4()
    d1 = OrganizationalDependency(
        id=did,
        dependency_type="test",
        criticality="alta",
        dependency_target="Target",
        description="Test",
    )
    d2 = OrganizationalDependency(
        id=did,
        dependency_type="test",
        criticality="alta",
        dependency_target="Target",
        description="Test",
    )
    assert d1 == d2


def test_from_dict_roundtrip():
    original = OrganizationalDependency(
        id=uuid4(),
        dependency_type="cliente_concentrado",
        criticality="critica",
        dependency_target="Cliente X",
        description="Alta concentracion",
        metadata={"src": "obs"},
    )
    restored = OrganizationalDependency.from_dict(original.to_dict())
    assert restored == original


def test_same_business_value_as_ignores_id_and_metadata():
    d1 = OrganizationalDependency(
        id=uuid4(),
        dependency_type="cliente_concentrado",
        criticality="alta",
        dependency_target="Cliente X",
        description="Dependencia",
        metadata={"x": 1},
    )
    d2 = OrganizationalDependency(
        id=uuid4(),
        dependency_type="cliente_concentrado",
        criticality="alta",
        dependency_target="Cliente X",
        description="Dependencia",
        metadata={"x": 2},
    )
    assert d1.same_business_value_as(d2) is True
