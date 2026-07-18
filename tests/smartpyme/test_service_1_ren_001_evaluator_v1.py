from __future__ import annotations

import math

from pymia.smartpyme.service_1_ren_001_evaluator_v1 import (
    CLASS_BREAK_EVEN,
    CLASS_NEGATIVE_MARGIN,
    CLASS_POSITIVE_MARGIN,
    STATUS_EVALUATED,
    STATUS_INVALID_INPUT,
    STATUS_PLAN_BLOCKED,
    evaluate_ren_001_from_computation_plan_v1,
    evaluate_ren_001_v1,
)


def _ready_plan() -> dict:
    return {
        "schema_version": "SERVICE_1_COMPUTATION_PLAN_V1",
        "status": "READY_FOR_COMPUTATION",
        "requested_capability": "net_margin_real",
        "pathology_code": "REN_001",
        "formula_id": "REN_001_margen_neto_real",
        "required_variables": ["sale_price", "costs", "taxes"],
        "computation_candidate_ready": True,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _assert_closed(packet: dict) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False


def test_positive_margin_is_computed_exactly() -> None:
    result = evaluate_ren_001_v1(sale_price=1000, costs=600, taxes=100)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_POSITIVE_MARGIN
    assert result["computed"] == {
        "net_margin_amount": 300.0,
        "net_margin_percentage": 30.0,
        "total_outflows": 700.0,
    }
    _assert_closed(result)


def test_break_even_is_classified_without_threshold() -> None:
    result = evaluate_ren_001_v1(sale_price=1000, costs=800, taxes=200)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_BREAK_EVEN
    assert result["computed"]["net_margin_amount"] == 0.0
    assert result["computed"]["net_margin_percentage"] == 0.0


def test_negative_margin_is_classified_without_causal_claim() -> None:
    result = evaluate_ren_001_v1(sale_price=1000, costs=900, taxes=200)

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_NEGATIVE_MARGIN
    assert result["computed"]["net_margin_amount"] == -100.0
    assert result["computed"]["net_margin_percentage"] == -10.0
    assert result["diagnosis_generated"] is False


def test_decimal_strings_are_accepted_deterministically() -> None:
    result = evaluate_ren_001_v1(
        sale_price="100.10",
        costs="70.05",
        taxes="10.05",
    )

    assert result["status"] == STATUS_EVALUATED
    assert math.isclose(result["computed"]["net_margin_amount"], 20.0)
    assert math.isclose(
        result["computed"]["net_margin_percentage"],
        19.98001998001998,
    )


def test_zero_or_negative_sale_price_is_rejected() -> None:
    zero = evaluate_ren_001_v1(sale_price=0, costs=0, taxes=0)
    negative = evaluate_ren_001_v1(sale_price=-1, costs=0, taxes=0)

    assert zero["status"] == STATUS_INVALID_INPUT
    assert negative["status"] == STATUS_INVALID_INPUT
    assert "sale_price must be greater than 0." in zero["errors"]
    assert "sale_price must be greater than 0." in negative["errors"]


def test_negative_costs_or_taxes_are_rejected() -> None:
    costs = evaluate_ren_001_v1(sale_price=100, costs=-1, taxes=0)
    taxes = evaluate_ren_001_v1(sale_price=100, costs=0, taxes=-1)

    assert costs["status"] == STATUS_INVALID_INPUT
    assert taxes["status"] == STATUS_INVALID_INPUT
    assert "costs must be greater than or equal to 0." in costs["errors"]
    assert "taxes must be greater than or equal to 0." in taxes["errors"]


def test_blank_boolean_nonnumeric_and_nonfinite_inputs_are_rejected() -> None:
    cases = (
        {"sale_price": "", "costs": 0, "taxes": 0},
        {"sale_price": True, "costs": 0, "taxes": 0},
        {"sale_price": "abc", "costs": 0, "taxes": 0},
        {"sale_price": float("inf"), "costs": 0, "taxes": 0},
        {"sale_price": 100, "costs": float("nan"), "taxes": 0},
    )

    for inputs in cases:
        result = evaluate_ren_001_v1(**inputs)
        assert result["status"] == STATUS_INVALID_INPUT
        assert result["errors"]
        _assert_closed(result)


def test_ready_plan_allows_explicit_input_evaluation() -> None:
    result = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs={"sale_price": 500, "costs": 300, "taxes": 50},
    )

    assert result["status"] == STATUS_EVALUATED
    assert result["classification"] == CLASS_POSITIVE_MARGIN
    assert result["plan_validation"]["status"] == "VALIDATED"
    assert result["computed"]["net_margin_amount"] == 150.0


def test_wrong_plan_identity_is_blocked() -> None:
    plan = _ready_plan()
    plan["formula_id"] = "LIQ_001_vendido_cobrado"

    result = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=plan,
        inputs={"sale_price": 500, "costs": 300, "taxes": 50},
    )

    assert result["status"] == STATUS_PLAN_BLOCKED
    assert result["errors"]
    assert result["computed"] == {}
    _assert_closed(result)


def test_plan_with_open_safety_flag_is_blocked() -> None:
    plan = _ready_plan()
    plan["delivery_authorized"] = True

    result = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=plan,
        inputs={"sale_price": 500, "costs": 300, "taxes": 50},
    )

    assert result["status"] == STATUS_PLAN_BLOCKED
    assert "computation_plan safety flags must remain false." in result["errors"]


def test_missing_or_unknown_plan_inputs_are_rejected() -> None:
    missing = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs={"sale_price": 500, "costs": 300},
    )
    unknown = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs={
            "sale_price": 500,
            "costs": 300,
            "taxes": 50,
            "discount": 10,
        },
    )

    assert missing["status"] == STATUS_INVALID_INPUT
    assert "missing required input: taxes." in missing["errors"]
    assert unknown["status"] == STATUS_INVALID_INPUT
    assert "unknown input: discount." in unknown["errors"]


def test_input_object_is_required() -> None:
    result = evaluate_ren_001_from_computation_plan_v1(
        computation_plan=_ready_plan(),
        inputs=None,
    )

    assert result["status"] == STATUS_INVALID_INPUT
    assert result["errors"] == ["inputs must be an object."]
