from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_capability_registry_v1 import (
    INV_001,
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
        "case_id": "case_inv_001",
        "requested_capability": "reorder_point",
        "family_id": "TEST_FAMILY",
        "pathology_code": "INV_001",
        "formula_id": "INV_001_punto_reposicion",
        "formula_expression": "fixture_expression",
        "required_variables": ["average_sales", "lead_time", "safety_stock"],
        "required_evidence": [],
        "source_bindings": {
            "average_sales": "average_sales",
            "lead_time": "lead_time",
            "safety_stock": "safety_stock",
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
            "sheet_name": "inventory",
            "column_name": name,
            "normalized_column_name": name,
        }
        for name in ("average_sales", "lead_time", "safety_stock")
    ]


def _tables(
    *,
    average_sales: object = 10,
    lead_time: object = 5,
    safety_stock: object = 20,
) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "inventory",
            "rows": [
                {
                    "average_sales": average_sales,
                    "lead_time": lead_time,
                    "safety_stock": safety_stock,
                }
            ],
        }
    ]


def _execute(
    *,
    average_sales: object = 10,
    lead_time: object = 5,
    safety_stock: object = 20,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="reorder_point",
        computation_plan=None,
        governed_computation_input=plan or _plan(),
        normalized_tables=_tables(
            average_sales=average_sales,
            lead_time=lead_time,
            safety_stock=safety_stock,
        ),
        column_refs=_refs(),
    )


def test_inv_001_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("reorder_point")

    assert definition is INV_001
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "INV_001"
    assert definition.formula_ref == "INV_001_punto_reposicion"
    assert definition.result_key == "reorder_point_units"
    assert definition.result_unit == "units"
    assert tuple(variable.name for variable in definition.variables) == (
        "average_sales",
        "lead_time",
        "safety_stock",
    )
    assert "reorder_point" in list_capability_refs_v1()


def test_inv_001_calculates_reorder_point() -> None:
    result = _execute(average_sales=10, lead_time=5, safety_stock=20)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "REORDER_POINT_CALCULATED"
    assert result["inputs"] == {
        "average_sales": 10.0,
        "lead_time": 5.0,
        "safety_stock": 20.0,
    }
    assert result["computed"]["reorder_point_units"] == 70.0


def test_inv_001_classifies_zero_requirement() -> None:
    result = _execute(average_sales=0, lead_time=5, safety_stock=0)

    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["reorder_point_units"] == 0.0
    assert result["classification"] == "NO_REORDER_REQUIREMENT"


def test_inv_001_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append(
        {"average_sales": 11, "lead_time": 5, "safety_stock": 20}
    )

    result = execute_generic_capability_v1(
        capability_ref="reorder_point",
        computation_plan=None,
        governed_computation_input=_plan(),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "average_sales must resolve to one consistent confirmed value." in result["errors"]


def test_inv_001_blocks_zero_lead_time() -> None:
    result = _execute(lead_time=0)

    assert result["status"] == STATUS_BLOCKED
    assert "lead_time must be greater than 0." in result["errors"]


def test_inv_001_blocks_negative_average_sales() -> None:
    result = _execute(average_sales=-1)

    assert result["status"] == STATUS_BLOCKED
    assert "average_sales must be greater than or equal to 0." in result["errors"]


def test_inv_001_blocks_negative_safety_stock() -> None:
    result = _execute(safety_stock=-1)

    assert result["status"] == STATUS_BLOCKED
    assert "safety_stock must be greater than or equal to 0." in result["errors"]


def test_inv_001_blocks_non_finite_values() -> None:
    result = _execute(average_sales="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_inv_001_requires_explicitly_false_safety_flags() -> None:
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


def test_inv_001_result_is_typed_and_bounded() -> None:
    result = _execute()

    assert result["computed"]["typed_result"] == {
        "value": 70.0,
        "unit": "units",
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
