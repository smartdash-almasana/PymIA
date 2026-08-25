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
from tests.smartpyme.service_1_p8_test_support import (
    computable_decision_from_governed_payload,
    governed_payload_from_legacy_plan,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "interest_burden_ratio",
        "pathology_code": "PYME_027",
        "formula_id": "PYME_027_intereses_ebitda",
        "required_variables": ["interest_expense", "ebitda"],
        "source_bindings": {
            "interest_expense": "interest_expense",
            "ebitda": "ebitda",
        },
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _refs() -> list[dict[str, str]]:
    return [
        {"sheet_name": "results", "column_name": name, "normalized_column_name": name}
        for name in ("interest_expense", "ebitda")
    ]


def _tables(*, interest_expense: object = 20, ebitda: object = 100) -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "results",
            "rows": [{"interest_expense": interest_expense, "ebitda": ebitda}],
        }
    ]


def _execute(
    *,
    interest_expense: object = 20,
    ebitda: object = 100,
    plan: dict[str, object] | None = None,
) -> dict[str, object]:
    return execute_generic_capability_v1(
        capability_ref="interest_burden_ratio",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(plan or _plan()),
        normalized_tables=_tables(interest_expense=interest_expense, ebitda=ebitda),
        column_refs=_refs(),
    )


def test_pyme_027_registry_contract_is_atomic_and_explicit() -> None:
    definition = get_capability_definition_v1("interest_burden_ratio")

    assert definition is not None
    assert definition.kind == "ATOMIC"
    assert definition.pathology_code == "PYME_027"
    assert definition.formula_ref == "PYME_027_intereses_ebitda"
    assert definition.result_key == "interest_burden_ratio_value"
    assert definition.result_unit == "ratio"
    assert tuple(variable.name for variable in definition.variables) == (
        "interest_expense",
        "ebitda",
    )
    assert "interest_burden_ratio" in list_capability_refs_v1()


def test_pyme_027_calculates_interest_burden_ratio() -> None:
    result = _execute(interest_expense=20, ebitda=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "POSITIVE_INTEREST_BURDEN"
    assert result["computed"]["interest_burden_ratio_value"] == 0.2


def test_pyme_027_classifies_zero_interest_burden() -> None:
    result = _execute(interest_expense=0, ebitda=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "ZERO_INTEREST_BURDEN"
    assert result["computed"]["interest_burden_ratio_value"] == 0.0


def test_pyme_027_blocks_zero_or_negative_ebitda() -> None:
    zero = _execute(ebitda=0)
    negative = _execute(ebitda=-1)

    assert zero["status"] == STATUS_BLOCKED
    assert negative["status"] == STATUS_BLOCKED
    assert "ebitda must be greater than 0." in zero["errors"]


def test_pyme_027_blocks_negative_interest_expense() -> None:
    result = _execute(interest_expense=-1)

    assert result["status"] == STATUS_BLOCKED


def test_pyme_027_blocks_non_finite_values() -> None:
    result = _execute(interest_expense="Infinity")

    assert result["status"] == STATUS_BLOCKED
    assert any("value must be finite" in error for error in result["errors"])


def test_pyme_027_requires_single_consistent_values() -> None:
    tables = _tables()
    tables[0]["rows"].append({"interest_expense": 25, "ebitda": 100})

    result = execute_generic_capability_v1(
        capability_ref="interest_burden_ratio",
        computation_plan=None,
        governed_computation_input=governed_payload_from_legacy_plan(_plan()),
        normalized_tables=tables,
        column_refs=_refs(),
    )

    assert result["status"] == STATUS_BLOCKED
    assert "interest_expense must resolve to one consistent confirmed value." in result["errors"]


def test_pyme_027_requires_explicitly_false_safety_flags() -> None:
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


def test_pyme_027_outcome_remains_non_causal() -> None:
    result = _execute(interest_expense=50, ebitda=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["outcome"]["causal_diagnosis_generated"] is False
    assert result["outcome"]["delivery_authorized"] is False
