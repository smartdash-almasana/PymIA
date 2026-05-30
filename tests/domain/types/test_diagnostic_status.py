"""Unit tests for DiagnosticStatus."""

import pytest

from pymia.domain.types.diagnostic_status import DiagnosticStatus


def test_has_expected_values():
    assert len(DiagnosticStatus) == 4
    assert DiagnosticStatus.PRELIMINAR.value == "preliminar"
    assert DiagnosticStatus.CONFIRMADO.value == "confirmado"
    assert DiagnosticStatus.REFUTADO.value == "refutado"
    assert DiagnosticStatus.OBSOLETO.value == "obsoleto"


def test_can_build_from_value():
    assert DiagnosticStatus("preliminar") == DiagnosticStatus.PRELIMINAR
    assert DiagnosticStatus("confirmado") == DiagnosticStatus.CONFIRMADO


def test_rejects_unknown_value():
    with pytest.raises(ValueError):
        DiagnosticStatus("unknown")
