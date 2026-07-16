from __future__ import annotations

from pymia.contracts.column_confirmation_v1 import (
    _CALCULATION_FEEDING_LABELS,
    _INFORMATIONAL_LABELS,
    _SEGMENTATION_LABELS,
    CalculationRelevance,
)
from pymia.smartpyme.service_1_owner_facing_role_explanation_catalog_v1 import (
    SCHEMA_VERSION,
    UNKNOWN_ROLE,
    explain_owner_facing_semantic_role_v1,
    known_owner_facing_semantic_roles_v1,
    normalize_semantic_role_v1,
)


def test_catalog_covers_all_column_confirmation_contract_roles() -> None:
    contract_roles = set(_CALCULATION_FEEDING_LABELS) | set(_INFORMATIONAL_LABELS) | set(_SEGMENTATION_LABELS)
    catalog_roles = set(known_owner_facing_semantic_roles_v1())

    assert contract_roles <= catalog_roles


def test_explains_sales_total_for_owner() -> None:
    result = explain_owner_facing_semantic_role_v1("venta_total")

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == "SERVICE_1"
    assert result.semantic_role == "venta_total"
    assert result.owner_label == "Ventas del periodo"
    assert "vendido" in result.owner_facing_role_explanation
    assert result.calculation_relevance == CalculationRelevance.VENTAS.value
    assert result.known_role is True


def test_explains_unit_cost_for_owner() -> None:
    result = explain_owner_facing_semantic_role_v1("costo_unitario")

    assert result.owner_label == "Costo por unidad"
    assert "cuesta cada unidad" in result.owner_facing_role_explanation
    assert result.calculation_relevance == CalculationRelevance.COSTOS.value


def test_explains_quantity_for_owner() -> None:
    result = explain_owner_facing_semantic_role_v1("cantidad")

    assert result.owner_label == "Cantidad"
    assert "unidades" in result.owner_facing_role_explanation
    assert result.calculation_relevance == CalculationRelevance.CANTIDADES.value


def test_explains_informational_roles_for_owner() -> None:
    product = explain_owner_facing_semantic_role_v1("producto")
    date = explain_owner_facing_semantic_role_v1("fecha")
    client = explain_owner_facing_semantic_role_v1("cliente")

    assert product.calculation_relevance == CalculationRelevance.INFORMATIONAL.value
    assert date.calculation_relevance == CalculationRelevance.INFORMATIONAL.value
    assert client.calculation_relevance == CalculationRelevance.INFORMATIONAL.value
    assert "producto" in product.owner_facing_role_explanation
    assert "fecha" in date.owner_facing_role_explanation
    assert "cliente" in client.owner_facing_role_explanation


def test_explains_segmentation_role_for_owner() -> None:
    result = explain_owner_facing_semantic_role_v1("canal")

    assert result.owner_label == "Canal"
    assert result.calculation_relevance == CalculationRelevance.SEGMENTATION.value
    assert "canal" in result.owner_facing_role_explanation


def test_unknown_role_uses_safe_manual_review_copy() -> None:
    result = explain_owner_facing_semantic_role_v1("campo_raro")

    assert result.semantic_role == "campo_raro"
    assert result.owner_label == "Rol no reconocido"
    assert result.owner_facing_role_explanation == "Esta columna necesita revision manual antes de usarla para calculos o conclusiones."
    assert result.calculation_relevance == CalculationRelevance.INFORMATIONAL.value
    assert result.known_role is False


def test_blank_and_none_roles_normalize_to_unknown() -> None:
    assert normalize_semantic_role_v1(None) == UNKNOWN_ROLE
    assert normalize_semantic_role_v1("") == UNKNOWN_ROLE
    assert normalize_semantic_role_v1("   ") == UNKNOWN_ROLE

    result = explain_owner_facing_semantic_role_v1(None)
    assert result.semantic_role == UNKNOWN_ROLE
    assert result.known_role is False


def test_role_normalization_is_lowercase_and_trimmed() -> None:
    result = explain_owner_facing_semantic_role_v1("  VENTA_TOTAL  ")

    assert result.semantic_role == "venta_total"
    assert result.known_role is True


def test_catalog_preserves_security_flags() -> None:
    result = explain_owner_facing_semantic_role_v1("venta_total")

    assert result.human_review_required is True
    assert result.runtime_authorized is False
    assert result.recalculation_authorized is False


def test_to_dict_is_serializable_and_stable() -> None:
    result = explain_owner_facing_semantic_role_v1("saldo")

    data = result.to_dict()
    assert data["schema_version"] == SCHEMA_VERSION
    assert data["semantic_role"] == "saldo"
    assert data["owner_label"] == "Saldo"
    assert data["known_role"] is True


def test_every_known_role_has_owner_label_and_explanation() -> None:
    for role in known_owner_facing_semantic_roles_v1():
        result = explain_owner_facing_semantic_role_v1(role)
        assert result.owner_label.strip()
        assert result.owner_facing_role_explanation.strip()
        assert "computed_variables" not in result.owner_facing_role_explanation
        assert "suggested_semantic_role" not in result.owner_facing_role_explanation


def test_known_role_count_is_more_complete_than_previous_owner_view_mapping() -> None:
    assert len(known_owner_facing_semantic_roles_v1()) >= 25
