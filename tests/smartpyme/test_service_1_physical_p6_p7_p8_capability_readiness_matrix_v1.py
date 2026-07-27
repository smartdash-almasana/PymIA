from __future__ import annotations

from tools.service_1_physical_p6_p7_p8_capability_readiness_matrix_v1 import (
    VERDICT_READY,
    evaluate_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1,
)


def test_physical_p6_p7_p8_matrix_is_structurally_clean_and_fail_closed() -> None:
    result = evaluate_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1()

    assert result["verdict"] == VERDICT_READY
    assert result["cases_count"] == 7
    assert result["p6_cases_passed"] == 7
    assert result["p7_cases_passed"] == 7
    assert result["p8_probes_count"] == 14
    assert result["p8_probes_passed"] == 14
    assert result["computable_positive_cases"] == 3
    assert result["positive_controls"]["controls_passed"] == 3
    assert result["positive_controls"]["executed_positive_cases"] == 3
    assert result["unsafe_executions"] == 0
    assert result["failures"] == []
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False


def test_physical_p8_negative_controls_never_carry_governed_execution_input() -> None:
    result = evaluate_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1()

    assert all(row["status_ok"] for row in result["p8_rows"])
    assert all(row["governed_input_present"] is False for row in result["p8_rows"])
    assert all(row["execution_attempted"] is False for row in result["p8_rows"])
