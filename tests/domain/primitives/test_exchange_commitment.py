"""
Tests for ExchangeCommitment value object

Valida invariantes de dominio del átomo organizacional.
"""
import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError
from pymia.domain.primitives import ExchangeCommitment


def test_exchange_commitment_valid_construction():
    """Construcción válida con 2 partes."""
    commitment = ExchangeCommitment(
        id=uuid4(),
        parties=["Textiles SA", "Cliente Mayorista"],
        object="Venta de 100 remeras",
        conditions="Pago contado, entrega 7 días",
    )
    assert commitment.parties == ["Textiles SA", "Cliente Mayorista"]
    assert commitment.object == "Venta de 100 remeras"
    assert commitment.conditions == "Pago contado, entrega 7 días"


def test_exchange_commitment_rejects_single_party():
    """Rechaza compromiso con menos de 2 partes."""
    with pytest.raises(ValueError, match="al menos 2 partes"):
        ExchangeCommitment(
            id=uuid4(),
            parties=["Solo una parte"],
            object="Algo",
            conditions="Alguna condición",
        )


def test_exchange_commitment_rejects_empty_parties():
    """Rechaza compromiso sin partes."""
    with pytest.raises(ValueError, match="al menos 2 partes"):
        ExchangeCommitment(
            id=uuid4(),
            parties=[],
            object="Algo",
            conditions="Alguna condición",
        )


def test_exchange_commitment_rejects_empty_object():
    """Rechaza compromiso con objeto vacío."""
    with pytest.raises(ValueError, match="objeto no vacío"):
        ExchangeCommitment(
            id=uuid4(),
            parties=["A", "B"],
            object="",
            conditions="Alguna condición",
        )


def test_exchange_commitment_rejects_empty_conditions():
    """Rechaza compromiso con condiciones vacías."""
    with pytest.raises(ValueError, match="condiciones no vacías"):
        ExchangeCommitment(
            id=uuid4(),
            parties=["A", "B"],
            object="Algo",
            conditions="",
        )


def test_exchange_commitment_is_immutable():
    """Value object debe ser inmutable."""
    commitment = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
    )
    with pytest.raises(FrozenInstanceError):
        commitment.object = "Otro objeto"


def test_exchange_commitment_to_dict():
    """Serialización a diccionario."""
    commitment_id = uuid4()
    commitment = ExchangeCommitment(
        id=commitment_id,
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
    )
    
    data = commitment.to_dict()
    assert data["id"] == str(commitment_id)
    assert data["parties"] == ["A", "B"]
    assert data["object"] == "Objeto"
    assert data["conditions"] == "Condiciones"
    assert data["metadata"] == {}


def test_exchange_commitment_with_metadata():
    """Construcción con metadata opcional."""
    commitment = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
        metadata={"source": "manual", "confidence": 0.9},
    )
    assert commitment.metadata == {"source": "manual", "confidence": 0.9}


def test_exchange_commitment_from_dict_roundtrip():
    original = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
        metadata={"src": "x"},
    )
    restored = ExchangeCommitment.from_dict(original.to_dict())
    assert restored == original


def test_exchange_commitment_same_business_value_as_ignores_id_and_metadata():
    c1 = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
        metadata={"k": "v1"},
    )
    c2 = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto",
        conditions="Condiciones",
        metadata={"k": "v2"},
    )
    assert c1.same_business_value_as(c2) is True


def test_exchange_commitment_same_business_value_as_detects_content_difference():
    c1 = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto A",
        conditions="Condiciones",
    )
    c2 = ExchangeCommitment(
        id=uuid4(),
        parties=["A", "B"],
        object="Objeto B",
        conditions="Condiciones",
    )
    assert c1.same_business_value_as(c2) is False
