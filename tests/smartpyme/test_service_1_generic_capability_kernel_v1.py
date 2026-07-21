from __future__ import annotations

from pymia.smartpyme.service_1_capability_registry_v1 import list_capability_refs_v1
from pymia.smartpyme.service_1_generic_capability_engine_v1 import (
    STATUS_BLOCKED,
    STATUS_EVALUATED,
    execute_generic_capability_v1,
)


def _plan(*, capability: str, pathology: str, formula: str, variables: tuple[str, ...], bindings: dict[str, str]) -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": capability,
        "pathology_code": pathology,
        "formula_id": formula,
        "required_variables": list(variables),
        "source_bindings": bindings,
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _refs(columns: tuple[str, ...]) -> list[dict[str, str]]:
    return [
        {"sheet_name": "sheet1", "column_name": column, "normalized_column_name": column}
        for column in columns
    ]


def test_registry_has_dpo_dso_and_projected_closing() -> None:
    refs = list_capability_refs_v1()
    assert "dpo" in refs
    assert "dso" in refs
    assert "projected_closing_cash_balance" in refs


def test_liq_002_executes_sum_and_single_value_without_touching_product_root() -> None:
    plan = _plan(
        capability="projected_closing_cash_balance",
        pathology="LIQ_002",
        formula="LIQ_002_saldo_final_proyectado",
        variables=("initial_balance", "expected_collections", "expected_payments"),
        bindings={
            "initial_balance": "opening",
            "expected_collections": "collections",
            "expected_payments": "payments",
        },
    )
    result = execute_generic_capability_v1(
        capability_ref="projected_closing_cash_balance",
        computation_plan=plan,
        normalized_tables=[
            {
                "sheet_name": "sheet1",
                "rows": [
                    {"opening": 100, "collections": 30, "payments": 40},
                    {"opening": None, "collections": 20, "payments": 15},
                ],
            }
        ],
        column_refs=_refs(("opening", "collections", "payments")),
    )
    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == "POSITIVE_PROJECTED_BALANCE"
    assert result["computed"]["projected_closing_balance"] == 95.0
    assert result["computed"]["typed_result"]["unit"] == "currency"
    assert result["outcome"]["bounded_finding_generated"] is True
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False


def test_pyme_011_executes_dso_with_consistent_single_period() -> None:
    plan = _plan(
        capability="dso",
        pathology="PYME_011",
        formula="PYME_011_dso",
        variables=("accounts_receivable", "sales", "days"),
        bindings={"accounts_receivable": "receivables", "sales": "sales", "days": "days"},
    )
    result = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan=plan,
        normalized_tables=[
            {
                "sheet_name": "sheet1",
                "rows": [
                    {"receivables": 40, "sales": 100, "days": 30},
                    {"receivables": 20, "sales": 50, "days": 30},
                ],
            }
        ],
        column_refs=_refs(("receivables", "sales", "days")),
    )
    assert result["status"] == STATUS_EVALUATED
    assert result["computed"]["dso_days"] == 12.0
    assert result["computed"]["typed_result"] == {
        "value": 12.0,
        "unit": "days",
        "period": 30.0,
        "provenance": "owner_confirmed_normalized_evidence",
    }
    assert result["classification"] == "DSO_WITHIN_PERIOD"


def test_single_value_rejects_inconsistent_values() -> None:
    plan = _plan(
        capability="dso",
        pathology="PYME_011",
        formula="PYME_011_dso",
        variables=("accounts_receivable", "sales", "days"),
        bindings={"accounts_receivable": "receivables", "sales": "sales", "days": "days"},
    )
    result = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan=plan,
        normalized_tables=[
            {"sheet_name": "sheet1", "rows": [{"receivables": 10, "sales": 20, "days": 30}, {"days": 31}]}
        ],
        column_refs=_refs(("receivables", "sales", "days")),
    )
    assert result["status"] == STATUS_BLOCKED
    assert "days must resolve to one consistent confirmed value." in result["errors"]


def test_denominator_and_domain_are_closed() -> None:
    plan = _plan(
        capability="dso",
        pathology="PYME_011",
        formula="PYME_011_dso",
        variables=("accounts_receivable", "sales", "days"),
        bindings={"accounts_receivable": "receivables", "sales": "sales", "days": "days"},
    )
    result = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan=plan,
        normalized_tables=[{"sheet_name": "sheet1", "rows": [{"receivables": 10, "sales": 0, "days": 30}]}],
        column_refs=_refs(("receivables", "sales", "days")),
    )
    assert result["status"] == STATUS_BLOCKED
    assert "sales must be greater than 0." in result["errors"]
    assert all(result[flag] is False for flag in ("runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "diagnosis_generated"))


def test_wrong_plan_and_unknown_capability_fail_closed() -> None:
    wrong = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan={},
        normalized_tables=[],
        column_refs=[],
    )
    unknown = execute_generic_capability_v1(
        capability_ref="automatic_guess",
        computation_plan={},
        normalized_tables=[],
        column_refs=[],
    )
    assert wrong["status"] == STATUS_BLOCKED
    assert unknown["status"] == STATUS_BLOCKED
    assert unknown["errors"] == ["unsupported capability: automatic_guess."]


def test_plan_requires_explicitly_false_safety_flags() -> None:
    plan = _plan(
        capability="dso",
        pathology="PYME_011",
        formula="PYME_011_dso",
        variables=("accounts_receivable", "sales", "days"),
        bindings={"accounts_receivable": "receivables", "sales": "sales", "days": "days"},
    )
    del plan["delivery_authorized"]

    result = execute_generic_capability_v1(
        capability_ref="dso",
        computation_plan=plan,
        normalized_tables=[{"sheet_name": "sheet1", "rows": [{"receivables": 10, "sales": 20, "days": 30}]}],
        column_refs=_refs(("receivables", "sales", "days")),
    )

    assert result["status"] == STATUS_BLOCKED
    assert result["errors"] == ["computation_plan safety flags must be explicitly false."]
