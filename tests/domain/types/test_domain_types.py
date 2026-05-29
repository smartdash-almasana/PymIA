"""
Tests for domain enums

Valida que los enums tienen los valores correctos según doctrina.
"""
import pytest
from pymia.domain.types import (
    EpistemicState,
    ConstraintType,
    TensionType,
    RelationshipWeight,
    CapabilityLevel,
)


def test_epistemic_state_has_all_values():
    """EpistemicState debe tener 6 estados."""
    assert len(EpistemicState) == 6
    assert EpistemicState.DECLARED.value == "declared"
    assert EpistemicState.OBSERVED.value == "observed"
    assert EpistemicState.INFERRED.value == "inferred"
    assert EpistemicState.VALIDATED.value == "validated"
    assert EpistemicState.REFUTED.value == "refuted"
    assert EpistemicState.ARCHIVED.value == "archived"


def test_constraint_type_has_8_types():
    """ConstraintType debe tener 8 tipos de restricción."""
    assert len(ConstraintType) == 8
    assert ConstraintType.CAJA.value == "caja"
    assert ConstraintType.TIEMPO.value == "tiempo"
    assert ConstraintType.CAPACIDAD.value == "capacidad"
    assert ConstraintType.ATENCION.value == "atencion"
    assert ConstraintType.INFORMACION.value == "informacion"
    assert ConstraintType.REGULATORIA.value == "regulatoria"
    assert ConstraintType.MERCADO.value == "mercado"
    assert ConstraintType.CREDITO.value == "credito"


def test_tension_type_has_10_types():
    """TensionType debe tener 10 trade-offs."""
    assert len(TensionType) == 10
    assert TensionType.CRECER_VS_MANTENER_CAJA.value == "crecer_vs_mantener_caja"
    assert TensionType.VOLUMEN_VS_RENTABILIDAD.value == "volumen_vs_rentabilidad"
    assert TensionType.VELOCIDAD_VS_ORDEN.value == "velocidad_vs_orden"
    assert TensionType.CALIDAD_VS_COSTO.value == "calidad_vs_costo"
    assert TensionType.CORTO_VS_LARGO_PLAZO.value == "corto_vs_largo_plazo"
    assert TensionType.DELEGAR_VS_CONTROLAR.value == "delegar_vs_controlar"
    assert TensionType.ESPECIALIZAR_VS_DIVERSIFICAR.value == "especializar_vs_diversificar"
    assert TensionType.FABRICAR_VS_REVENDER.value == "fabricar_vs_revender"
    assert TensionType.PRECIO_VS_VOLUMEN.value == "precio_vs_volumen"
    assert TensionType.TRANSPARENCIA_VS_PROTECCION.value == "transparencia_vs_proteccion"


def test_relationship_weight_has_4_levels():
    """RelationshipWeight debe tener 4 niveles."""
    assert len(RelationshipWeight) == 4
    assert RelationshipWeight.BAJO.value == "bajo"
    assert RelationshipWeight.MEDIO.value == "medio"
    assert RelationshipWeight.ALTO.value == "alto"
    assert RelationshipWeight.CRITICO.value == "critico"


def test_capability_level_has_4_levels():
    """CapabilityLevel debe tener 4 niveles."""
    assert len(CapabilityLevel) == 4
    assert CapabilityLevel.DECLARADA.value == "declarada"
    assert CapabilityLevel.OBSERVADA.value == "observada"
    assert CapabilityLevel.LATENTE.value == "latente"
    assert CapabilityLevel.LIMITE.value == "limite"
