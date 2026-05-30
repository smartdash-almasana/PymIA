"""
Tests for StructuralRelationship value object

Valida invariantes de dominio de relaciones estructurales.
Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §6
"""
import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError

from pymia.domain.types import RelationshipWeight
from pymia.domain.primitives.structural_relationship import StructuralRelationship


def test_valid_construction():
    """Construcción válida."""
    source = uuid4()
    target = uuid4()
    r = StructuralRelationship(
        id=uuid4(),
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.CRITICO,
        relationship_kind="cliente_mayorista",
        description="Cliente que concentra 45% de ingresos",
    )
    assert r.source_id == source
    assert r.target_id == target
    assert r.weight == RelationshipWeight.CRITICO
    assert r.relationship_kind == "cliente_mayorista"


def test_all_weights_valid():
    """Los 4 pesos deben ser aceptados."""
    for weight in RelationshipWeight:
        r = StructuralRelationship(
            id=uuid4(),
            source_id=uuid4(),
            target_id=uuid4(),
            weight=weight,
            relationship_kind="test",
            description="Test",
        )
        assert r.weight == weight


def test_invalid_self_relationship():
    """source_id == target_id debe rechazarse."""
    same_id = uuid4()
    with pytest.raises(ValueError, match="source_id y target_id deben ser distintos"):
        StructuralRelationship(
            id=uuid4(),
            source_id=same_id,
            target_id=same_id,
            weight=RelationshipWeight.ALTO,
            relationship_kind="test",
            description="Auto-relación",
        )


def test_invalid_weight_type():
    """weight debe ser RelationshipWeight válido."""
    with pytest.raises(ValueError, match="weight debe ser RelationshipWeight"):
        StructuralRelationship(
            id=uuid4(),
            source_id=uuid4(),
            target_id=uuid4(),
            weight="critico",  # string, no enum
            relationship_kind="test",
            description="Test",
        )


def test_invalid_empty_relationship_kind():
    """relationship_kind vacío debe rechazarse."""
    with pytest.raises(ValueError, match="relationship_kind no vacío"):
        StructuralRelationship(
            id=uuid4(),
            source_id=uuid4(),
            target_id=uuid4(),
            weight=RelationshipWeight.ALTO,
            relationship_kind="",
            description="Test",
        )


def test_invalid_empty_description():
    """Description vacía debe rechazarse."""
    with pytest.raises(ValueError, match="descripción no vacía"):
        StructuralRelationship(
            id=uuid4(),
            source_id=uuid4(),
            target_id=uuid4(),
            weight=RelationshipWeight.ALTO,
            relationship_kind="test",
            description="",
        )


def test_immutability():
    """Value object debe ser inmutable."""
    r = StructuralRelationship(
        id=uuid4(),
        source_id=uuid4(),
        target_id=uuid4(),
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
    )
    with pytest.raises(FrozenInstanceError):
        r.description = "Otra"


def test_to_dict_serialization():
    """Serialización a diccionario JSON-compatible."""
    rid = uuid4()
    source = uuid4()
    target = uuid4()
    r = StructuralRelationship(
        id=rid,
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.CRITICO,
        relationship_kind="cliente_mayorista",
        description="Test",
    )
    data = r.to_dict()
    assert data["id"] == str(rid)
    assert data["source_id"] == str(source)
    assert data["target_id"] == str(target)
    assert data["weight"] == "critico"
    assert data["relationship_kind"] == "cliente_mayorista"
    assert data["description"] == "Test"
    assert data["metadata"] == {}


def test_to_dict_with_metadata():
    """Serialización con metadata."""
    r = StructuralRelationship(
        id=uuid4(),
        source_id=uuid4(),
        target_id=uuid4(),
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
        metadata={"revenue_share": 0.45},
    )
    data = r.to_dict()
    assert data["metadata"] == {"revenue_share": 0.45}


def test_equality():
    """Value objects con mismos datos deben ser iguales."""
    rid = uuid4()
    source = uuid4()
    target = uuid4()
    r1 = StructuralRelationship(
        id=rid,
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
    )
    r2 = StructuralRelationship(
        id=rid,
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
    )
    assert r1 == r2


def test_from_dict_roundtrip():
    original = StructuralRelationship(
        id=uuid4(),
        source_id=uuid4(),
        target_id=uuid4(),
        weight=RelationshipWeight.CRITICO,
        relationship_kind="cliente_mayorista",
        description="Vinculo central",
        metadata={"src": "obs"},
    )
    restored = StructuralRelationship.from_dict(original.to_dict())
    assert restored == original


def test_same_business_value_as_ignores_id_and_metadata():
    source = uuid4()
    target = uuid4()
    r1 = StructuralRelationship(
        id=uuid4(),
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
        metadata={"m": 1},
    )
    r2 = StructuralRelationship(
        id=uuid4(),
        source_id=source,
        target_id=target,
        weight=RelationshipWeight.ALTO,
        relationship_kind="test",
        description="Test",
        metadata={"m": 2},
    )
    assert r1.same_business_value_as(r2) is True
