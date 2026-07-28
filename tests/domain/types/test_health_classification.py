"""Tests para HealthClassification enum."""

import pytest

from pymia.domain.types.health_classification import HealthClassification


class TestHealthClassification:
    """Tests para HealthClassification enum."""

    def test_has_4_values(self):
        """HealthClassification debe tener exactamente 4 valores."""
        assert len(HealthClassification) == 4

    def test_values(self):
        """Verifica los 4 valores específicos."""
        assert HealthClassification.SANO.value == "sano"
        assert HealthClassification.FRAGIL.value == "fragil"
        assert HealthClassification.ENFERMO.value == "enfermo"
        assert HealthClassification.CRITICO.value == "critico"

    def test_from_value(self):
        """Construcción desde string."""
        assert HealthClassification("sano") == HealthClassification.SANO
        assert HealthClassification("critico") == HealthClassification.CRITICO

    def test_invalid_value_raises(self):
        """Valor inválido eleva ValueError."""
        with pytest.raises(ValueError):
            HealthClassification("invalido")
