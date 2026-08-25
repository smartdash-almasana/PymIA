from __future__ import annotations

from pymia.smartpyme.service_1_capability_registry_v1 import list_capability_refs_v1
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)
from pymia.smartpyme.service_1_computability_v1 import (
    build_service_1_composite_governed_computation_input_v1,
)


def _source(capability_ref: str, result_key: str, value: object, **overrides: object) -> dict[str, object]:
    source = {
        "status": "EVALUATED",
        "capability_ref": capability_ref,
        "computed": {
            result_key: value,
            "typed_result": {"value": value, "unit": "days", "provenance": "governed"},
        },
        "outcome": {"causal_diagnosis_generated": False},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    source.update(overrides)
    return source


def _execute(governed_results: object) -> dict[str, object]:
    governed = build_service_1_composite_governed_computation_input_v1(
        case_id="case_pyme_013_direct",
        capability_ref="payment_collection_gap",
    )
    return execute_generic_capability_v1(
        capability_ref="payment_collection_gap",
        computation_plan=None,
        governed_computation_input=governed,
        normalized_tables=[{"sheet_name": "must_not_be_read", "rows": [{"dso_days": 999}]}],
        column_refs=[{"sheet_name": "must_not_be_read", "column_name": "dso_days"}],
        governed_results=governed_results,
    )


def test_registry_registers_pyme_013_as_composite() -> None:
    assert "payment_collection_gap" in list_capability_refs_v1()


def test_composite_classifies_positive_zero_and_negative_without_table_inputs() -> None:
    cases = (
        (30, 10, "COLLECTIONS_AFTER_PAYMENTS", 20.0),
        (30, 30, "COLLECTIONS_MATCH_PAYMENTS", 0.0),
        (10, 30, "COLLECTIONS_BEFORE_PAYMENTS", -20.0),
    )
    for dso_days, dpo_days, classification, expected in cases:
        result = _execute([_source("dso", "dso_days", dso_days), _source("dpo", "dpo_days", dpo_days)])
        assert result["status"] == STATUS_EVALUATED
        assert result["classification"] == classification
        assert result["computed"]["payment_collection_gap_days"] == expected
        assert result["computed"]["typed_result"]["unit"] == "days"
        assert result["delivery_authorized"] is False
        assert result["diagnosis_generated"] is False


def test_composite_blocks_absent_duplicate_or_invalid_governed_sources() -> None:
    absent = _execute([])
    duplicate = _execute([_source("dso", "dso_days", 30), _source("dso", "dso_days", 30), _source("dpo", "dpo_days", 10)])
    invalid = _execute([_source("dso", "dso_days", 30), _source("dpo", "dpo_days", 10, delivery_authorized=True)])

    assert absent["status"] == STATUS_BLOCKED
    assert duplicate["status"] == STATUS_BLOCKED
    assert invalid["status"] == STATUS_BLOCKED
    assert any("exactly once" in error for error in duplicate["errors"])
    assert any("safety flags" in error for error in invalid["errors"])


def test_composite_blocks_bad_identity_values_units_and_causality() -> None:
    bad_value = _source("dso", "dso_days", 30)
    bad_value["computed"] = {"dso_days": 30, "typed_result": {"value": 29, "unit": "days"}}
    bad_unit = _source("dpo", "dpo_days", 10)
    bad_unit["computed"] = {"dpo_days": 10, "typed_result": {"value": 10, "unit": "currency"}}
    causal = _source("dpo", "dpo_days", 10, outcome={"causal_diagnosis_generated": True})

    result = _execute([bad_value, bad_unit])
    causal_result = _execute([_source("dso", "dso_days", 30), causal])

    assert result["status"] == STATUS_BLOCKED
    assert any("typed_result.value" in error for error in result["errors"])
    assert any("unit" in error for error in result["errors"])
    assert causal_result["status"] == STATUS_BLOCKED
    assert any("causal diagnosis" in error for error in causal_result["errors"])
