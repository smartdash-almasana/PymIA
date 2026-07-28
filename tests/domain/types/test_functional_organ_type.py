"""Tests para FunctionalOrganType enum."""
from pymia.domain.types.functional_organ_type import FunctionalOrganType


def test_functional_organ_type_has_7_values():
    """FunctionalOrganType debe tener exactamente 7 valores (HEALTH_MODEL §4)."""
    assert len(FunctionalOrganType) == 7


def test_functional_organ_type_values():
    """Verifica los 7 órganos funcionales específicos."""
    assert FunctionalOrganType.CIRCULATORIO.value == "circulatorio"
    assert FunctionalOrganType.RESPIRATORIO.value == "respiratorio"
    assert FunctionalOrganType.DIGESTIVO.value == "digestivo"
    assert FunctionalOrganType.NERVIOSO.value == "nervioso"
    assert FunctionalOrganType.SENSORIAL.value == "sensorial"
    assert FunctionalOrganType.INMUNOLOGICO.value == "inmunologico"
    assert FunctionalOrganType.REPRODUCTIVO.value == "reproductivo"


def test_functional_organ_type_from_value():
    """Verifica conversión string → enum."""
    assert FunctionalOrganType("circulatorio") is FunctionalOrganType.CIRCULATORIO
    assert FunctionalOrganType("nervioso") is FunctionalOrganType.NERVIOSO


def test_functional_organ_type_invalid_value_raises():
    """Verifica que un valor inválido levanta ValueError."""
    import pytest
    with pytest.raises(ValueError):
        FunctionalOrganType("inexistente")
