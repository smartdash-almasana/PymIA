from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    FAMILY_CASH_COLLECTIONS,
    FAMILY_CASH_PROJECTION,
    FAMILY_INVENTORY_CONTROL,
    FAMILY_OPERATION_CORE,
    FAMILY_PURCHASES_SUPPLIERS,
    FAMILY_SALES_MARGIN,
    STATUS_MISSING_REQUIRED_ROLES,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_NOT_OBSERVED,
    STATUS_READY,
    VARIABLE_FAMILY_DEFINITIONS,
    Service1VariableFamilyBindingV1,
    build_service_1_variable_family_bindings_v1,
    ready_service_1_variable_family_ids_v1,
)


def _candidate(
    column: str,
    role: str,
    *,
    owner_confirmation_required: bool = False,
    ignored: bool = False,
) -> Service1ColumnSemanticCandidateV1:
    return Service1ColumnSemanticCandidateV1(
        source_column_name=column,
        normalized_column_name=column.lower(),
        sheet_name="sheet1",
        observed_data_type="number",
        sample_values=(1, 2),
        candidate_semantic_roles=(role,),
        candidate_variable_names=(role,),
        confidence=0.95,
        ambiguity_reason=("ambiguous" if owner_confirmation_required else None),
        owner_confirmation_required=owner_confirmation_required,
        metadata={"owner_ignored_not_relevant": ignored},
    )


def _by_id(bindings: tuple[Service1VariableFamilyBindingV1, ...]) -> dict[str, Service1VariableFamilyBindingV1]:
    return {binding.family_id: binding for binding in bindings}


def test_defines_six_prioritized_business_families() -> None:
    assert [definition.family_id for definition in VARIABLE_FAMILY_DEFINITIONS] == [
        FAMILY_OPERATION_CORE,
        FAMILY_SALES_MARGIN,
        FAMILY_CASH_COLLECTIONS,
        FAMILY_PURCHASES_SUPPLIERS,
        FAMILY_INVENTORY_CONTROL,
        FAMILY_CASH_PROJECTION,
    ]
    assert [definition.priority for definition in VARIABLE_FAMILY_DEFINITIONS] == [1, 2, 3, 4, 5, 6]


def test_sales_margin_family_ready_from_coherent_role_set() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [
            _candidate("Producto", "product_name"),
            _candidate("Cantidad", "quantity"),
            _candidate("Precio", "unit_sale_price"),
            _candidate("Costo", "unit_cost_candidate"),
            _candidate("IVA", "tax_amount"),
        ]
    )
    family = _by_id(bindings)[FAMILY_SALES_MARGIN]

    assert family.status == STATUS_READY
    assert family.coverage_ratio == 1.0
    assert set(family.bound_roles) >= {
        "product_name",
        "quantity",
        "unit_sale_price",
        "unit_cost_candidate",
    }
    assert family.optional_roles_present == ("tax_amount",)
    assert family.runtime_authorized is False
    assert family.tool_execution_authorized is False


def test_operation_family_accepts_product_name_or_identifier() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [
            _candidate("Fecha", "operation_date"),
            _candidate("SKU", "product_identifier"),
            _candidate("Cantidad", "quantity"),
            _candidate("Total", "sales_amount"),
        ]
    )
    family = _by_id(bindings)[FAMILY_OPERATION_CORE]
    assert family.status == STATUS_READY
    assert family.missing_role_groups == ()


def test_cash_family_needs_owner_confirmation_when_required_role_is_ambiguous() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [
            _candidate("Fecha", "operation_date"),
            _candidate("Venta", "sales_amount"),
            _candidate(
                "Cobrado",
                "collected_amount",
                owner_confirmation_required=True,
            ),
        ]
    )
    family = _by_id(bindings)[FAMILY_CASH_COLLECTIONS]

    assert family.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert family.coverage_ratio == pytest.approx(2 / 3)
    assert family.ambiguous_role_groups == (("collected_amount",),)


def test_partial_family_reports_missing_groups_instead_of_selecting_a_tool() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [_candidate("Precio", "unit_sale_price")]
    )
    family = _by_id(bindings)[FAMILY_SALES_MARGIN]

    assert family.status == STATUS_MISSING_REQUIRED_ROLES
    assert family.coverage_ratio == 0.25
    assert ("quantity",) in family.missing_role_groups
    assert ("unit_cost_candidate",) in family.missing_role_groups
    assert family.metadata["tool_selection_authorized"] is False


def test_unobserved_families_remain_explicit() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [_candidate("Fecha", "operation_date")]
    )
    by_id = _by_id(bindings)

    assert by_id[FAMILY_INVENTORY_CONTROL].status == STATUS_NOT_OBSERVED
    assert by_id[FAMILY_PURCHASES_SUPPLIERS].status == STATUS_MISSING_REQUIRED_ROLES


def test_ignored_column_does_not_satisfy_family() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [_candidate("Costo", "unit_cost_candidate", ignored=True)]
    )
    assert _by_id(bindings)[FAMILY_SALES_MARGIN].status == STATUS_NOT_OBSERVED


def test_ready_family_ids_are_priority_ordered() -> None:
    bindings = build_service_1_variable_family_bindings_v1(
        [
            _candidate("Fecha", "operation_date"),
            _candidate("Producto", "product_name"),
            _candidate("Cantidad", "quantity"),
            _candidate("Total", "sales_amount"),
            _candidate("Precio", "unit_sale_price"),
            _candidate("Costo", "unit_cost_candidate"),
            _candidate("Cobrado", "collected_amount"),
        ]
    )
    assert ready_service_1_variable_family_ids_v1(bindings) == (
        FAMILY_OPERATION_CORE,
        FAMILY_SALES_MARGIN,
        FAMILY_CASH_COLLECTIONS,
    )


def test_invalid_candidate_type_fails_closed() -> None:
    with pytest.raises(TypeError, match="Service1ColumnSemanticCandidateV1"):
        build_service_1_variable_family_bindings_v1([{"role": "quantity"}])  # type: ignore[list-item]


def test_deterministic_same_candidates_same_bindings() -> None:
    candidates = [
        _candidate("Producto", "product_name"),
        _candidate("Cantidad", "quantity"),
        _candidate("Precio", "unit_sale_price"),
        _candidate("Costo", "unit_cost_candidate"),
    ]
    assert build_service_1_variable_family_bindings_v1(candidates) == build_service_1_variable_family_bindings_v1(candidates)
