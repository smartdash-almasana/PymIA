from __future__ import annotations

import math

import pytest

from pymia.smartpyme.service_1_liq_001_evaluator_v1 import (
    CLASS_COLLECTIONS_EXCEED_PERIOD_SALES,
    CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES,
    CLASS_NO_ACTIVITY,
    CLASS_NO_GAP,
    CLASS_SALES_PENDING_COLLECTION,
    PLAN_VALIDATED,
    STATUS_EVALUATED,
    STATUS_EVIDENCE_BLOCKED,
    STATUS_INVALID_INPUT,
    STATUS_PLAN_BLOCKED,
    evaluate_liq_001_from_computation_plan_v1,
    evaluate_liq_001_from_normalized_tables_v1,
    evaluate_liq_001_v1,
)


def _ready_plan() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "sold_vs_collected_gap",
        "pathology_code": "LIQ_001",
        "formula_id": "LIQ_001_vendido_cobrado",
        "required_variables": ["sold_amount", "collected_amount"],
        "source_bindings": {
            "sold_amount": "Venta Total",
            "collected_amount": "Cobrado",
        },
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _normalized_tables() -> list[dict[str, object]]:
    return [
        {
            "sheet_name": "Ventas",
            "rows": [
                {"venta_total": "1000", "cobrado": "800"},
                {"venta_total": "2000.50", "cobrado": "1500.25"},
            ],
        }
    ]


def _column_refs() -> list[dict[str, str]]:
    return [
        {
            "sheet_name": "Ventas",
            "column_name": "Venta Total",
            "normalized_column_name": "venta_total",
        },
        {
            "sheet_name": "Ventas",
            "column_name": "Cobrado",
            "normalized_column_name": "cobrado",
        },
    ]


def test_positive_gap_means_sales_pending_collection() -> None:
    result = evaluate_liq_001_v1(sold_amount=1000, collected_amount=700)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_SALES_PENDING_COLLECTION
    assert result["computed"] == {
        "gap_amount": 300.0,
        "collection_ratio": 0.7,
        "gap_ratio": 0.3,
    }


def test_zero_gap_means_no_gap() -> None:
    result = evaluate_liq_001_v1(sold_amount=1000, collected_amount=1000)

    assert result["classification"] == CLASS_NO_GAP
    assert result["computed"]["gap_amount"] == 0.0
    assert result["computed"]["collection_ratio"] == 1.0
    assert result["computed"]["gap_ratio"] == 0.0


def test_negative_gap_means_collections_exceed_period_sales() -> None:
    result = evaluate_liq_001_v1(sold_amount=1000, collected_amount=1200)

    assert result["classification"] == CLASS_COLLECTIONS_EXCEED_PERIOD_SALES
    assert result["computed"]["gap_amount"] == -200.0
    assert result["computed"]["collection_ratio"] == 1.2
    assert result["computed"]["gap_ratio"] == -0.2


def test_zero_sales_and_zero_collections_means_no_activity() -> None:
    result = evaluate_liq_001_v1(sold_amount=0, collected_amount=0)

    assert result["classification"] == CLASS_NO_ACTIVITY
    assert result["computed"] == {
        "gap_amount": 0.0,
        "collection_ratio": None,
        "gap_ratio": None,
    }


def test_collections_without_period_sales_preserve_undefined_ratios() -> None:
    result = evaluate_liq_001_v1(sold_amount=0, collected_amount=250)

    assert result["classification"] == CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES
    assert result["computed"] == {
        "gap_amount": -250.0,
        "collection_ratio": None,
        "gap_ratio": None,
    }


@pytest.mark.parametrize(
    ("sold_amount", "collected_amount", "expected_error"),
    [
        (-1, 0, "sold_amount must be greater than or equal to 0."),
        (0, -1, "collected_amount must be greater than or equal to 0."),
        (True, 0, "sold_amount must be numeric."),
        ("100", 0, "sold_amount must be numeric."),
        (math.inf, 0, "sold_amount must be finite."),
        (0, math.nan, "collected_amount must be finite."),
    ],
)
def test_invalid_domain_is_rejected(
    sold_amount: object,
    collected_amount: object,
    expected_error: str,
) -> None:
    result = evaluate_liq_001_v1(
        sold_amount=sold_amount,
        collected_amount=collected_amount,
    )

    assert result["status"] == STATUS_INVALID_INPUT
    assert result["classification"] is None
    assert result["computed"] == {}
    assert expected_error in result["errors"]
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False


def test_packet_exposes_formula_and_mathematical_boundaries() -> None:
    result = evaluate_liq_001_v1(sold_amount=100, collected_amount=80)

    assert result["pathology_code"] == "LIQ_001"
    assert result["formula_ref"] == "LIQ_001_vendido_cobrado"
    assert result["capability_ref"] == "sold_vs_collected_gap"
    assert result["mathematical_limits"]["sold_amount_min_inclusive"] == 0.0
    assert result["mathematical_limits"]["collected_amount_min_inclusive"] == 0.0
    assert result["mathematical_limits"]["ratios_defined_when"] == "sold_amount > 0"


def test_ready_plan_with_explicit_inputs_is_evaluated() -> None:
    result = evaluate_liq_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs={"sold_amount": 3000, "collected_amount": 2300},
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_SALES_PENDING_COLLECTION
    assert result["computed"]["gap_amount"] == 700.0
    assert result["plan_validation"] == {
        "status": PLAN_VALIDATED,
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "requested_capability": "sold_vs_collected_gap",
        "pathology_code": "LIQ_001",
        "formula_id": "LIQ_001_vendido_cobrado",
        "required_variables": ["sold_amount", "collected_amount"],
    }


def test_plan_identity_drift_is_blocked() -> None:
    plan = _ready_plan()
    plan["formula_id"] = "REN_001_margen_neto_real"

    result = evaluate_liq_001_from_computation_plan_v1(
        computation_plan=plan,
        inputs={"sold_amount": 3000, "collected_amount": 2300},
    )

    assert result["status"] == STATUS_PLAN_BLOCKED
    assert result["computed"] == {}
    assert "computation_plan formula_id must equal LIQ_001_vendido_cobrado." in result["errors"]


def test_non_ready_plan_is_blocked() -> None:
    plan = _ready_plan()
    plan["status"] = "NEEDS_EVIDENCE"

    result = evaluate_liq_001_from_computation_plan_v1(
        computation_plan=plan,
        inputs={"sold_amount": 3000, "collected_amount": 2300},
    )

    assert result["status"] == STATUS_PLAN_BLOCKED
    assert "computation_plan status must equal READY_FOR_COMPUTATION." in result["errors"]


def test_plan_evaluation_rejects_missing_or_unknown_inputs() -> None:
    result = evaluate_liq_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs={"sold_amount": 3000, "unexpected": 1},
    )

    assert result["status"] == STATUS_INVALID_INPUT
    assert "missing required input: collected_amount." in result["errors"]
    assert "unknown input: unexpected." in result["errors"]
    assert result["plan_validation"]["status"] == PLAN_VALIDATED


def test_normalized_rows_are_fully_aggregated_without_samples() -> None:
    result = evaluate_liq_001_from_normalized_tables_v1(
        computation_plan=_ready_plan(),
        normalized_tables=_normalized_tables(),
        column_refs=_column_refs(),
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["inputs"] == {
        "sold_amount": 3000.5,
        "collected_amount": 2300.25,
    }
    assert result["computed"]["gap_amount"] == 700.25
    assert result["aggregation"]["status"] == "AGGREGATED"
    assert result["aggregation"]["row_count"] == 2
    assert result["aggregation"]["sample_based"] is False


def test_normalized_aggregation_rejects_blank_values_instead_of_partial_sum() -> None:
    tables = _normalized_tables()
    tables[0]["rows"][1]["cobrado"] = ""

    result = evaluate_liq_001_from_normalized_tables_v1(
        computation_plan=_ready_plan(),
        normalized_tables=tables,
        column_refs=_column_refs(),
    )

    assert result["status"] == STATUS_EVIDENCE_BLOCKED
    assert "Ventas.cobrado row 2: value is required." in result["errors"]
    assert result["computed"] == {}


def test_normalized_aggregation_rejects_ambiguous_column_resolution() -> None:
    refs = _column_refs() + [dict(_column_refs()[0])]

    result = evaluate_liq_001_from_normalized_tables_v1(
        computation_plan=_ready_plan(),
        normalized_tables=_normalized_tables(),
        column_refs=refs,
    )

    assert result["status"] == STATUS_EVIDENCE_BLOCKED
    assert (
        "source binding for sold_amount must resolve exactly once: Venta Total."
        in result["errors"]
    )


def test_normalized_aggregation_rejects_negative_and_non_numeric_values() -> None:
    tables = _normalized_tables()
    tables[0]["rows"][0]["venta_total"] = "no-number"
    tables[0]["rows"][1]["cobrado"] = "-1"

    result = evaluate_liq_001_from_normalized_tables_v1(
        computation_plan=_ready_plan(),
        normalized_tables=tables,
        column_refs=_column_refs(),
    )

    assert result["status"] == STATUS_EVIDENCE_BLOCKED
    assert "Ventas.venta_total row 1: value must be numeric." in result["errors"]
    assert "Ventas.cobrado row 2: value must be greater than or equal to 0." in result["errors"]


def test_normalized_aggregation_keeps_all_authority_flags_closed() -> None:
    result = evaluate_liq_001_from_normalized_tables_v1(
        computation_plan=_ready_plan(),
        normalized_tables=_normalized_tables(),
        column_refs=_column_refs(),
    )

    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False
