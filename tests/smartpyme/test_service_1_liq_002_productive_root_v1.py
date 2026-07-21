from __future__ import annotations

from pymia.smartpyme import service_1_product_pipeline_v1 as product
from pymia.smartpyme.service_1_liq_002_evaluator_v1 import (
    CLASS_NEGATIVE_BALANCE,
    CLASS_POSITIVE_BALANCE,
    CLASS_ZERO_BALANCE,
    STATUS_INVALID_INPUT,
    evaluate_liq_002_v1,
)
from pymia.smartpyme.service_1_liq_002_normalized_evidence_v1 import (
    STATUS_EVIDENCE_BLOCKED,
    evaluate_liq_002_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_liq_002_outcome_v1 import (
    STATUS_READY,
    build_liq_002_outcome_v1,
)


def _plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "projected_closing_cash_balance",
        "pathology_code": "LIQ_002",
        "formula_id": "LIQ_002_saldo_final_proyectado",
        "required_variables": [
            "initial_balance",
            "expected_collections",
            "expected_payments",
        ],
        "source_bindings": {
            "initial_balance": "saldo_inicial",
            "expected_collections": "cobros_esperados",
            "expected_payments": "pagos_esperados",
        },
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _evidence() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    tables = [
        {
            "sheet_name": "flujo",
            "rows": [
                {
                    "saldo_inicial": 1000,
                    "cobros_esperados": 600,
                    "pagos_esperados": 400,
                },
                {
                    "saldo_inicial": None,
                    "cobros_esperados": 300,
                    "pagos_esperados": 250,
                },
            ],
        }
    ]
    refs = [
        {
            "sheet_name": "flujo",
            "column_name": "saldo_inicial",
            "normalized_column_name": "saldo_inicial",
        },
        {
            "sheet_name": "flujo",
            "column_name": "cobros_esperados",
            "normalized_column_name": "cobros_esperados",
        },
        {
            "sheet_name": "flujo",
            "column_name": "pagos_esperados",
            "normalized_column_name": "pagos_esperados",
        },
    ]
    return tables, refs


def test_liq_002_classifies_positive_zero_and_negative_balances() -> None:
    positive = evaluate_liq_002_v1(
        initial_balance=100, expected_collections=50, expected_payments=120
    )
    zero = evaluate_liq_002_v1(
        initial_balance=100, expected_collections=50, expected_payments=150
    )
    negative = evaluate_liq_002_v1(
        initial_balance=100, expected_collections=50, expected_payments=180
    )

    assert positive["classification"] == CLASS_POSITIVE_BALANCE
    assert zero["classification"] == CLASS_ZERO_BALANCE
    assert negative["classification"] == CLASS_NEGATIVE_BALANCE


def test_liq_002_rejects_negative_or_non_finite_inputs() -> None:
    negative = evaluate_liq_002_v1(
        initial_balance=-1, expected_collections=0, expected_payments=0
    )
    infinite = evaluate_liq_002_v1(
        initial_balance=0, expected_collections="Infinity", expected_payments=0
    )

    assert negative["status"] == STATUS_INVALID_INPUT
    assert infinite["status"] == STATUS_INVALID_INPUT
    assert negative["diagnosis_generated"] is False


def test_liq_002_aggregates_one_opening_balance_and_all_movements() -> None:
    tables, refs = _evidence()
    result = evaluate_liq_002_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )

    assert result["status"] == "EVALUATED"
    assert result["classification"] == CLASS_POSITIVE_BALANCE
    assert result["inputs"] == {
        "initial_balance": 1000.0,
        "expected_collections": 900.0,
        "expected_payments": 650.0,
    }
    assert result["computed"]["projected_closing_balance"] == 1250.0
    assert result["aggregation"]["sources"]["initial_balance"]["aggregation_mode"] == "SINGLE_VALUE"
    assert result["aggregation"]["sources"]["expected_collections"]["aggregation_mode"] == "SUM"
    assert result["aggregation"]["sample_based"] is False


def test_liq_002_blocks_multiple_opening_balances() -> None:
    tables, refs = _evidence()
    tables[0]["rows"][1]["saldo_inicial"] = 1000
    result = evaluate_liq_002_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )

    assert result["status"] == STATUS_EVIDENCE_BLOCKED
    assert any("exactly one" in error for error in result["errors"])
    assert result["diagnosis_generated"] is False


def test_liq_002_outcome_is_bounded_and_non_causal() -> None:
    tables, refs = _evidence()
    evaluation = evaluate_liq_002_from_normalized_tables_v1(
        computation_plan=_plan(), normalized_tables=tables, column_refs=refs
    )
    outcome = build_liq_002_outcome_v1(computation_result=evaluation)

    assert outcome["status"] == STATUS_READY
    assert outcome["bounded_finding_generated"] is True
    assert outcome["causal_diagnosis_generated"] is False
    assert outcome["runtime_authorized"] is False
    assert outcome["delivery_authorized"] is False
    assert outcome["treatment_actions"]
    assert outcome["forbidden_claims"]


def test_product_root_absorbs_only_explicit_liq_002_capability(monkeypatch, tmp_path) -> None:
    tables, refs = _evidence()
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
    )

    assert result["status"] == product.STATUS_COMPUTATION_PLAN_READY
    assert result["computation_executed"] is True
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["tools_executed"] is False
    assert result["diagnosis_generated"] is False
    assert result["runtime_authorized"] is False


def test_liq_002_delivery_remains_blocked(monkeypatch, tmp_path) -> None:
    tables, refs = _evidence()
    confirmed = {
        "status": product.STATUS_CONFIRMED_BINDINGS,
        "schema_version": "TEST",
        "service_name": "SERVICE_1",
    }
    monkeypatch.setattr(product, "run_initial_pass", lambda **_: confirmed)
    monkeypatch.setattr(product, "build_computation_plan", lambda **_: _plan())

    result = product.run_service_1_product_pipeline_v1(
        ingestion_output={"normalized_tables": tables, "column_refs": refs},
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        deliver_result=True,
    )

    assert result["status"] == product.STATUS_BLOCKED
    assert result["blocked_reason"] == "LIQ_002_DELIVERY_NOT_AUTHORIZED"
    assert result["bounded_finding_generated"] is True
    assert result["delivery_generated"] is False
    assert result["delivery_authorized"] is False
