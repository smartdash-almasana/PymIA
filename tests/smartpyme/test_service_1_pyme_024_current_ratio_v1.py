from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import (
    get_capability_definition_v1,
    list_capability_refs_v1,
)
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)
from tests.smartpyme.service_1_p8_test_support import computable_decision_from_governed_payload


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1",
        "case_id": "case_pyme_024",
        "requested_capability": "current_ratio",
        "family_id": "TEST_FAMILY",
        "pathology_code": "PYME_024",
        "formula_id": "PYME_024_liquidez_corriente",
        "formula_expression": "fixture_expression",
        "required_variables": ["current_assets", "current_liabilities"],
        "required_evidence": [],
        "source_bindings": {
            "current_assets": "current_assets",
            "current_liabilities": "current_liabilities",
        },
        "grain": {"structural_scope": "REGION"},
        "catalog_versions": {},
        "provenance": {"source": "TEST_P8"},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _refs() -> list[dict[str, str]]:
    return [
        {
            "sheet_name": "balance",
            "column_name": name,
            "normalized_column_name": name,
        }
        for name in ("current_assets", "current_liabilities")
    ]


def _tables(
    *,
    current_assets: object = 150,
    current_liabilities: object = 100,
) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "balance",
            "rows": [
                {
                    "current_assets": current_assets,
                    "current_liabilities": current_liabilities,
                }
            ],
        }
    ]


def _execute(
    *,
    current_assets: object = 150,
    current_liabilities: object = 100,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="current_ratio",
        computation_plan=None,
        governed_computation_input=plan or _plan(),
        normalized_tables=_tables(
            current_assets=current_assets,
            current_liabilities=current_liabilities,
        ),
        column_refs=_refs(),
    )


def test_pyme_024_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("current_ratio")

    assert definition is not None
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "PYME_024"
    assert definition.formula_ref == "PYME_024_liquidez_corriente"
    assert definition.result_key == "current_ratio_value"
    assert definition.result_unit == "ratio"
    assert tuple(variable.name for variable in definition.variables) == (
        "current_assets",
        "current_liabilities",
    )
    assert "current_ratio" in list_capability_refs_v1()


def test_pyme_024_calculates_current_ratio() -> None:
    result = _execute(current_assets=150, current_liabilities=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "POSITIVE_CURRENT_RATIO"
    assert result["inputs"] == {
        "current_assets": 150.0,
        "current_liabilities": 100.0,
    }
    assert result["computed"]["current_ratio_value"] == 1.5


def test_pyme_024_classifies_zero_ratio() -> None:
    result = _execute(current_assets=0, current_liabilities=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["current_ratio_value"] == 0.0
    assert result["classification"] == "ZERO_CURRENT_RATIO"


def test_pyme_024_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append(
        {"current_assets": 151, "current_liabilities": 100}
    )

    result = execute_generic_capability_v1(
        capability_ref="current_ratio",
        computation_plan=None,
        governed_computation_input=_plan(),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "current_assets must resolve to one consistent confirmed value." in result["errors"]


def test_pyme_024_blocks_zero_current_liabilities() -> None:
    result = _execute(current_liabilities=0)

    assert result["status"] == STATUS_BLOCKED
    assert "current_liabilities must be greater than 0." in result["errors"]


def test_pyme_024_blocks_negative_current_assets() -> None:
    result = _execute(current_assets=-1)

    assert result["status"] == STATUS_BLOCKED
    assert "current_assets must be greater than or equal to 0." in result["errors"]


def test_pyme_024_blocks_negative_current_liabilities() -> None:
    result = _execute(current_liabilities=-1)

    assert result["status"] == STATUS_BLOCKED
    assert "current_liabilities must be greater than 0." in result["errors"]


def test_pyme_024_blocks_non_finite_values() -> None:
    result = _execute(current_assets="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_pyme_024_requires_explicitly_false_safety_flags() -> None:
    plan = _plan()
    del plan["delivery_authorized"]
    absent = _execute(plan=plan)

    plan = _plan()
    plan["runtime_authorized"] = True
    opened = _execute(plan=plan)

    assert absent["status"] == STATUS_BLOCKED
    assert opened["status"] == STATUS_BLOCKED
    assert absent["errors"] == ["governed input safety flags must be explicitly false."]
    assert opened["errors"] == ["governed input safety flags must be explicitly false."]


def test_pyme_024_result_is_typed_and_bounded() -> None:
    result = _execute()

    assert result["computed"]["typed_result"] == {
        "value": 1.5,
        "unit": "ratio",
        "period": None,
        "provenance": "owner_confirmed_normalized_evidence",
    }
    assert result["outcome"]["status"] == "OUTCOME_READY"
    assert result["outcome"]["bounded_finding_generated"] is True
    assert result["outcome"]["causal_diagnosis_generated"] is False
    assert result["runtime_authorized"] is False
    assert result["tool_execution_authorized"] is False
    assert result["product_ready"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False
