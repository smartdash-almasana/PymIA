from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.excel_lab_ingestion_v1 import curate_xlsx_document
from tools.service_1_excel_reality_lab_a4_adversarial_matrix_v1 import (
    VERDICT_PASS,
    evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1,
)


def test_a4_adversarial_matrix_is_reproducible_and_has_no_unsafe_execution() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()

    assert result["verdict"] == VERDICT_PASS
    assert result["cases"] == 11
    assert result["unsafe_executions"] == 0
    assert result["uncontrolled_crashes"] == 0
    assert result["second_xlsx_parser_created"] is False
    assert result["defects"] == []


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


def test_a4_001_mixed_currency_requires_owner_signal() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    row = next(r for r in result["rows"] if r["case_id"] == "S1-A4-001")

    assert row["terminal_class"] == "PASS_NEEDS_OWNER"
    assert row["reason"] == "MIXED_CURRENCY_WITH_SAFE_SIGNAL"
    assert row["execution_attempted"] is False
    assert "__mixed_currency__" in row["ambiguous_fields"]


def test_a4_002_total_rows_require_owner_signal() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    row = next(r for r in result["rows"] if r["case_id"] == "S1-A4-002")

    assert row["terminal_class"] == "PASS_NEEDS_OWNER"
    assert row["reason"] == "TOTAL_ROWS_PRESENT_WITH_SAFE_SIGNAL"
    assert row["execution_attempted"] is False
    assert "__embedded_total_rows__" in row["ambiguous_fields"]


def test_a4_005_out_of_period_dates_require_explicit_period_signal() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    row = next(r for r in result["rows"] if r["case_id"] == "S1-A4-005")

    assert row["terminal_class"] == "PASS_NEEDS_OWNER"
    assert row["reason"] == "UNKNOWN_OR_AMBIGUOUS_EVIDENCE_REQUIRES_OWNER"
    assert row["execution_attempted"] is False
    assert "__out_of_period_dates__" in row["ambiguous_fields"]


def test_a4_005_does_not_infer_period_when_period_ref_is_absent() -> None:
    source = Path(__file__).resolve().parents[2] / "excel-prueba" / "S1_A4_ADV_005_out_of_period_dates.xlsx"
    curated = curate_xlsx_document(source)

    assert "__out_of_period_dates__" not in curated.report.ambiguous_fields


def test_a4_006_duplicate_rows_requires_owner_signal() -> None:
    result = evaluate_service_1_excel_reality_lab_a4_adversarial_matrix_v1()
    row = next(r for r in result["rows"] if r["case_id"] == "S1-A4-006")

    assert row["terminal_class"] == "PASS_NEEDS_OWNER"
    assert row["reason"] == "DUPLICATE_ROWS_PRESENT_WITH_SAFE_SIGNAL"
    assert row["execution_attempted"] is False
    assert "__duplicate_rows__" in row["ambiguous_fields"]
