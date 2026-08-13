from __future__ import annotations

import inspect

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import (
    get_capability_definition_v1,
    list_capability_refs_v1,
)


EXPECTED_PRODUCTIVE_PATHOLOGIES = {
    "LIQ_001",
    "REN_001",
    "LIQ_002",
    "PYME_011",
    "PYME_013",
    "INV_001",
    "INV_002",
    "PYME_024",
    "PYME_033",
    "REN_002",
    "PYME_027",
    "PYME_026",
}

EXPECTED_GENERIC_PRODUCTIVE_REFS = {
    "projected_closing_cash_balance",
    "dso",
    "payment_collection_gap",
    "reorder_point",
    "inventory_turnover",
    "current_ratio",
    "sales_concentration",
    "index_update_ratio",
    "interest_burden_ratio",
    "adjusted_operating_cash_flow",
}

EXPECTED_ROOT_REFS = EXPECTED_GENERIC_PRODUCTIVE_REFS | {
    "sold_vs_collected_gap",
    "net_margin_real",
}


def _generic_productive_definitions():
    return [
        definition
        for ref in EXPECTED_GENERIC_PRODUCTIVE_REFS
        if (definition := get_capability_definition_v1(ref)) is not None
    ]


def test_cycle_053_certifies_exactly_twelve_productive_pathologies() -> None:
    generic_codes = {definition.pathology_code for definition in _generic_productive_definitions()}
    legacy_codes = {"LIQ_001", "REN_001"}

    assert generic_codes | legacy_codes == EXPECTED_PRODUCTIVE_PATHOLOGIES
    assert len(generic_codes | legacy_codes) == 12


def test_cycle_053_generic_registry_has_no_missing_or_duplicate_productive_codes() -> None:
    definitions = _generic_productive_definitions()

    assert len(definitions) == len(EXPECTED_GENERIC_PRODUCTIVE_REFS) == 10
    assert len({definition.pathology_code for definition in definitions}) == 10
    assert EXPECTED_GENERIC_PRODUCTIVE_REFS <= set(list_capability_refs_v1())


def test_cycle_053_dpo_remains_a_prerequisite_not_a_thirteenth_pathology() -> None:
    dpo = get_capability_definition_v1("dpo")

    assert dpo is not None
    assert dpo.pathology_code == "PYME_013_PREREQUISITE_DPO"
    assert dpo.pathology_code not in EXPECTED_PRODUCTIVE_PATHOLOGIES


def test_cycle_053_single_product_root_uses_registry_for_generic_capabilities() -> None:
    specialized_refs = {
        product.LIQ_001_CAPABILITY_REF,
        product.REN_001_CAPABILITY_REF,
    }
    registry_refs = set(list_capability_refs_v1())

    assert specialized_refs | EXPECTED_GENERIC_PRODUCTIVE_REFS == EXPECTED_ROOT_REFS
    assert EXPECTED_GENERIC_PRODUCTIVE_REFS <= registry_refs
    source = inspect.getsource(product.run_service_1_product_pipeline_v1)
    for generic_ref in EXPECTED_GENERIC_PRODUCTIVE_REFS:
        assert f'requested_capability == "{generic_ref}"' not in source


def test_cycle_053_all_generic_outcomes_remain_bounded_and_non_causal() -> None:
    for definition in _generic_productive_definitions():
        assert definition.outcome_policy.findings
        assert definition.outcome_policy.treatments
        assert definition.outcome_policy.limitations
        assert definition.outcome_policy.forbidden_claims


def test_cycle_053_delivery_is_closed_for_every_non_authorized_generic_pathology() -> None:
    for definition in _generic_productive_definitions():
        assert product._delivery_block_reason(definition) == (
            f"{definition.pathology_code}_DELIVERY_NOT_AUTHORIZED"
        )

    source = inspect.getsource(product.run_service_1_product_pipeline_v1)
    assert "deliver_ren_001_outcome_xlsx_v1" in source


def test_cycle_053_preserves_explicit_selection_and_no_automatic_capability_choice() -> None:
    signature = inspect.signature(product.run_service_1_product_pipeline_v1)
    source = inspect.getsource(product.run_service_1_product_pipeline_v1)

    assert signature.parameters["requested_capability"].default is None
    assert "if requested_capability is not None:" in source
    assert "requested_capability=" not in source.split("def run_service_1_product_pipeline_v1", 1)[0]
