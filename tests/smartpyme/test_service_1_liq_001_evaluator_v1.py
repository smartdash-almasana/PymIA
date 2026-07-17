from __future__ import annotations

import math

import pytest

from pymia.smartpyme.service_1_liq_001_evaluator_v1 import (
    CLASS_COLLECTIONS_EXCEED_PERIOD_SALES,
    CLASS_COLLECTIONS_WITHOUT_PERIOD_SALES,
    CLASS_NO_ACTIVITY,
    CLASS_NO_GAP,
    CLASS_SALES_PENDING_COLLECTION,
    STATUS_EVALUATED,
    STATUS_INVALID_INPUT,
    evaluate_liq_001_v1,
)


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
