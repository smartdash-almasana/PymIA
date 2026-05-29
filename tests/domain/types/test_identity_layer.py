"""
Tests for IdentityLayer enum

Valida que el enum tenga los 3 valores doctrinales.
Doctrina: PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md §3
"""
from pymia.domain.types.identity_layer import IdentityLayer


def test_identity_layer_has_3_values():
    """IdentityLayer debe tener exactamente 3 capas."""
    assert len(IdentityLayer) == 3


def test_identity_layer_values():
    """IdentityLayer debe tener los 3 valores doctrinales."""
    assert IdentityLayer.NUCLEO_PERSISTENTE.value == "nucleo_persistente"
    assert IdentityLayer.CAPA_ADAPTABLE.value == "capa_adaptable"
    assert IdentityLayer.CAPA_PERIFERICA.value == "capa_periferica"


def test_identity_layer_from_value():
    """IdentityLayer debe poder construirse desde su valor string."""
    assert IdentityLayer("nucleo_persistente") is IdentityLayer.NUCLEO_PERSISTENTE
    assert IdentityLayer("capa_adaptable") is IdentityLayer.CAPA_ADAPTABLE
    assert IdentityLayer("capa_periferica") is IdentityLayer.CAPA_PERIFERICA


def test_identity_layer_invalid_value():
    """IdentityLayer debe rechazar valores inválidos."""
    import pytest
    with pytest.raises(ValueError):
        IdentityLayer("inexistente")
