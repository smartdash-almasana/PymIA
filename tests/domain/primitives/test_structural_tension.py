"""
Tests for StructuralTension value object

Valida invariantes de dominio de tensiones estructurales.
Doctrina: PYMIA_ORGANIZATIONAL_MODEL_THEORY.md §8
"""
import pytest
from uuid import uuid4
from dataclasses import FrozenInstanceError

from pymia.domain.types import TensionType
from pymia.domain.primitives.structural_tension import StructuralTension


def test_valid_construction():
    """Construcción válida."""
    t = StructuralTension(
        id=uuid4(),
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=7,
        pole_b_intensity=4,
        description="Presión por volumen vs necesidad de margen",
    )
    assert t.tension_type == TensionType.VOLUMEN_VS_RENTABILIDAD
    assert t.pole_a_intensity == 7
    assert t.pole_b_intensity == 4


def test_valid_construction_zero_intensities():
    """Intensidades 0 son válidas (tensión no activa)."""
    t = StructuralTension(
        id=uuid4(),
        tension_type=TensionType.CALIDAD_VS_COSTO,
        pole_a_intensity=0,
        pole_b_intensity=0,
        description="Tensión inactiva",
    )
    assert t.pole_a_intensity == 0
    assert t.pole_b_intensity == 0


def test_valid_construction_max_intensities():
    """Intensidades 10 son válidas."""
    t = StructuralTension(
        id=uuid4(),
        tension_type=TensionType.CALIDAD_VS_COSTO,
        pole_a_intensity=10,
        pole_b_intensity=10,
        description="Tensión extrema",
    )
    assert t.pole_a_intensity == 10
    assert t.pole_b_intensity == 10


def test_invalid_pole_a_above_range():
    """pole_a > 10 debe rechazarse."""
    with pytest.raises(ValueError, match="pole_a_intensity debe estar en"):
        StructuralTension(
            id=uuid4(),
            tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
            pole_a_intensity=11,
            pole_b_intensity=5,
            description="Tensión",
        )


def test_invalid_pole_a_negative():
    """pole_a < 0 debe rechazarse."""
    with pytest.raises(ValueError, match="pole_a_intensity debe estar en"):
        StructuralTension(
            id=uuid4(),
            tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
            pole_a_intensity=-1,
            pole_b_intensity=5,
            description="Tensión",
        )


def test_invalid_pole_b_above_range():
    """pole_b > 10 debe rechazarse."""
    with pytest.raises(ValueError, match="pole_b_intensity debe estar en"):
        StructuralTension(
            id=uuid4(),
            tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
            pole_a_intensity=5,
            pole_b_intensity=11,
            description="Tensión",
        )


def test_invalid_empty_description():
    """Description vacía debe rechazarse."""
    with pytest.raises(ValueError, match="descripción no vacía"):
        StructuralTension(
            id=uuid4(),
            tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
            pole_a_intensity=5,
            pole_b_intensity=5,
            description="",
        )


def test_invalid_tension_type():
    """tension_type debe ser TensionType válido."""
    with pytest.raises(ValueError, match="tension_type debe ser TensionType"):
        StructuralTension(
            id=uuid4(),
            tension_type="volumen_vs_rentabilidad",  # string, no enum
            pole_a_intensity=5,
            pole_b_intensity=5,
            description="Tensión",
        )


def test_immutability():
    """Value object debe ser inmutable."""
    t = StructuralTension(
        id=uuid4(),
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=5,
        pole_b_intensity=5,
        description="Tensión",
    )
    with pytest.raises(FrozenInstanceError):
        t.pole_a_intensity = 7


def test_to_dict_serialization():
    """Serialización a diccionario JSON-compatible."""
    tid = uuid4()
    t = StructuralTension(
        id=tid,
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=7,
        pole_b_intensity=4,
        description="Tensión volumen-rentabilidad",
    )
    data = t.to_dict()
    assert data["id"] == str(tid)
    assert data["tension_type"] == "volumen_vs_rentabilidad"
    assert data["pole_a_intensity"] == 7
    assert data["pole_b_intensity"] == 4
    assert data["description"] == "Tensión volumen-rentabilidad"
    assert data["metadata"] == {}


def test_to_dict_with_metadata():
    """Serialización con metadata."""
    t = StructuralTension(
        id=uuid4(),
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=7,
        pole_b_intensity=4,
        description="Tensión",
        metadata={"source": "entrevista_dueno"},
    )
    data = t.to_dict()
    assert data["metadata"] == {"source": "entrevista_dueno"}


def test_equality():
    """Value objects con mismos datos deben ser iguales."""
    tid = uuid4()
    t1 = StructuralTension(
        id=tid,
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=7,
        pole_b_intensity=4,
        description="Tensión",
    )
    t2 = StructuralTension(
        id=tid,
        tension_type=TensionType.VOLUMEN_VS_RENTABILIDAD,
        pole_a_intensity=7,
        pole_b_intensity=4,
        description="Tensión",
    )
    assert t1 == t2
