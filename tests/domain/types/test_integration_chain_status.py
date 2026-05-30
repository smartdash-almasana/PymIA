"""Tests para IntegrationChainStatus."""

import pytest

from pymia.domain.types.integration_chain_status import IntegrationChainStatus


def test_integration_chain_status_values():
    assert IntegrationChainStatus.COMPLETA.value == "completa"
    assert IntegrationChainStatus.PARCIAL.value == "parcial"
    assert IntegrationChainStatus.BLOQUEADA.value == "bloqueada"
    assert IntegrationChainStatus.DIFERIDA.value == "diferida"


def test_integration_chain_status_from_value():
    assert IntegrationChainStatus("completa") == IntegrationChainStatus.COMPLETA
    assert IntegrationChainStatus("parcial") == IntegrationChainStatus.PARCIAL


def test_integration_chain_status_rejects_unknown_value():
    with pytest.raises(ValueError):
        IntegrationChainStatus("unknown")
