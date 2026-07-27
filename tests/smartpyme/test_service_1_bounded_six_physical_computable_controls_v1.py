from __future__ import annotations

from tools.service_1_bounded_six_physical_computable_controls_v1 import (
    VERDICT_PASS,
    evaluate_service_1_bounded_six_physical_computable_controls_v1,
)


def test_bounded_six_physical_positive_and_negative_controls_pass() -> None:
    result = evaluate_service_1_bounded_six_physical_computable_controls_v1()
    assert result["verdict"] == VERDICT_PASS
    assert result["positive_controls"] == 6
    assert result["positive_passed"] == 6
    assert result["negative_controls"] == 6
    assert result["negative_passed"] == 6
    assert result["unsafe_executions"] == 0
    assert result["failures"] == []
    assert all(row["p8_status"] == "COMPUTABLE" for row in result["positive_rows"])
    assert all(row["governed_input_present"] is True for row in result["positive_rows"])
    assert all(row["execution_status"] == "EVALUATED" for row in result["positive_rows"])
    assert all(row["p8_status"] == "NEEDS_EVIDENCE" for row in result["negative_rows"])
    assert all(row["governed_input_present"] is False for row in result["negative_rows"])


def test_bounded_six_physical_results_match_ground_truth() -> None:
    result = evaluate_service_1_bounded_six_physical_computable_controls_v1()
    observed = {row["capability"]: row["result_value"] for row in result["positive_rows"]}
    assert observed == {
        "reorder_point": 70.0,
        "inventory_turnover": 4.0,
        "current_ratio": 1.5,
        "sales_concentration": 40.0,
        "interest_burden_ratio": 0.2,
        "index_update_ratio": 1.5,
    }
