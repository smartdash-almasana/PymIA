from __future__ import annotations

from tools.service_1_excel_reality_lab_a4_adversarial_matrix_v1 import (
    FAIL_DEFECT,
    VERDICT_FAIL,
    evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1,
)


def test_a4_adversarial_matrix_is_reproducible_and_has_no_unsafe_execution() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()

    assert result["verdict"] == VERDICT_FAIL
    assert result["cases"] == 11
    assert result["unsafe_executions"] == 0
    assert result["uncontrolled_crashes"] == 0
    assert result["second_xlsx_parser_created"] is False

    defects = {row["case_id"]: row for row in result["defects"]}
    assert set(defects) == {"S1-A4-001", "S1-A4-002", "S1-A4-005"}
    assert all(row["terminal_class"] == FAIL_DEFECT for row in defects.values())


def test_a4_safe_cases_keep_expected_terminal_classes() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    rows = {row["case_id"]: row for row in result["rows"]}

    assert rows["S1-A4-003"]["terminal_class"] == "PASS_NEEDS_EVIDENCE"
    assert rows["S1-A4-004"]["terminal_class"] == "PASS_NEEDS_OWNER"
    assert rows["S1-A4-007"]["terminal_class"] == "PASS_NEEDS_OWNER"
    assert rows["S1-A4-008"]["terminal_class"] == "PASS_NEEDS_EVIDENCE"
    assert rows["S1-A4-009"]["terminal_class"] == "PASS_COMPUTABLE"
    assert rows["S1-A4-010"]["terminal_class"] == "PASS_NEEDS_OWNER"
    assert rows["S1-A4-011"]["terminal_class"] == "PASS_NEEDS_OWNER"


def test_a4_006_duplicate_rows_requires_owner_signal() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    row = next(r for r in result["rows"] if r["case_id"] == "S1-A4-006")

    assert row["terminal_class"] == "PASS_NEEDS_OWNER"
    assert row["reason"] == "DUPLICATE_ROWS_PRESENT_WITH_SAFE_SIGNAL"
    assert row["execution_attempted"] is False
    assert "__duplicate_rows__" in row["ambiguous_fields"]
