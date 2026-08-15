from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.service_1_excel_reality_lab_a1_structural_matrix_v1 import (
    ALLOWED_OUTCOMES,
    DIMENSION_PROBES,
    VERDICT_PASS,
    evaluate_a1_structural_matrix_v1,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _manifest() -> dict:
    path = _repo_root() / "docs" / "service_1_excel_reality_lab_corpus.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _structural_cases() -> list[dict]:
    manifest = _manifest()
    return [case for case in manifest["cases"] if case["coverage_lane"] == "STRUCTURAL"]


def test_a1_manifest_reaches_expansion_target_with_valid_cases() -> None:
    manifest = _manifest()
    cases = manifest["cases"]
    structural = _structural_cases()

    assert manifest["a1_status"] == "PASS_STRUCTURAL_MATRIX_V1"
    assert len(cases) >= manifest["expansion_target"]["minimum_cases"] == 20
    assert len(cases) <= 35
    assert len(structural) >= 13
    assert set(manifest["structural_dimensions"]) == set(DIMENSION_PROBES)
    assert manifest["authority_rules"]["second_xlsx_parser_forbidden"] is True


def test_a1_every_structural_case_is_physical_and_declares_dimensions() -> None:
    root = _repo_root()
    manifest = _manifest()
    fixture_root = root / manifest["canonical_fixture_root"]
    required = set(manifest["required_case_fields"])

    for case in _structural_cases():
        assert required <= set(case)
        assert case["structure_profile_status"] == "A1_EVALUATED"
        assert case["calculation_profile_status"] == "PENDING_A2"
        assert case["expected_outcome"] in ALLOWED_OUTCOMES
        assert (fixture_root / case["fixture"]).is_file(), f"fixture missing: {case['fixture']}"
        dims = case.get("structural_dimensions")
        assert dims, f"{case['case_id']} declares no structural dimension"
        assert set(dims) <= set(manifest["structural_dimensions"])
        assert isinstance(case.get("row_count"), int)
        assert isinstance(case.get("sheet_count"), int)


def test_a1_terminal_classes_are_valid_and_cover_all_lanes() -> None:
    outcomes = [case["expected_outcome"] for case in _structural_cases()]
    for outcome in outcomes:
        assert outcome in ALLOWED_OUTCOMES

    for outcome in ("PASS_COMPUTABLE", "PASS_NEEDS_OWNER"):
        assert outcome in outcomes


def test_a1_known_defect_is_declared_not_silenced() -> None:
    manifest = _manifest()
    defect = manifest.get("a1_known_defect")
    assert defect is not None
    assert defect["case_id"] == "S1-SYN-006"
    assert defect["fixture"] == "S1_A1_SYNTH_006_ventas_duplicate_columns.xlsx"
    assert defect["root_cause_candidate"]
    assert defect["affected_authority"]
    assert defect["minimal_change_surface"]
    assert defect["fix_authorized"] is True
    assert "PASS_BLOCKED_FAIL_CLOSED" in defect["resolution"]
    case = next(c for c in manifest["cases"] if c["case_id"] == defect["case_id"])
    assert case["expected_outcome"] == "PASS_BLOCKED_FAIL_CLOSED"


def test_a1_no_fail_defect_remains_open() -> None:
    manifest = _manifest()
    outcomes = {case["expected_outcome"] for case in manifest["cases"]}
    assert "FAIL_DEFECT" not in outcomes


def test_profiler_duplicate_columns_fail_closed_regression() -> None:
    root = _repo_root()
    from tools.bem_schema_builder.excel_profile_builder import ExcelProfileBuilder

    builder = ExcelProfileBuilder()
    profile = builder.build_profile(root / "prueba_excels" / "S1_A1_SYNTH_006_ventas_duplicate_columns.xlsx")
    sheet = next(s for s in profile.sheets if s.sheet_name == "Ventas")
    duplicates = [c for c in sheet.columns if c.duplicate_column]
    assert len(duplicates) == 2
    for column in duplicates:
        assert column.inferred_type == "duplicate"
        assert column.is_ambiguous is True
        assert column.ambiguity_reason == "duplicate_column_name"
        assert column.name == "venta_total"
    assert len({c.index for c in sheet.columns}) == len(sheet.columns)


def test_a1_evaluator_consumes_canonical_intake_and_classifies_without_parallel_authority() -> None:
    result = evaluate_a1_structural_matrix_v1()

    assert result["schema_version"] == "SERVICE_1_EXCEL_REALITY_LAB_A1_STRUCTURAL_MATRIX_V1"
    assert result["verdict"] == VERDICT_PASS
    assert result["manifest_mismatches"] == []
    assert result["unverified_dimensions"] == []
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["product_ready"] is False
    assert result["a2_calculation_not_claimed"] is True

    by_case = {row["case_id"]: row for row in result["case_results"]}
    for case in _structural_cases():
        row = by_case[case["case_id"]]
        assert row["terminal_class"] in ALLOWED_OUTCOMES
        assert row["manifest_class"] == case["expected_outcome"]


def test_a1_duplicate_columns_case_is_fail_closed_not_patched() -> None:
    result = evaluate_a1_structural_matrix_v1()
    by_case = {row["case_id"]: row for row in result["case_results"]}
    duplicate = by_case["S1-SYN-006"]
    assert duplicate["terminal_class"] == "PASS_BLOCKED_FAIL_CLOSED"
    assert duplicate["curation_status"] == "BLOCKED"
    assert "DUPLICATE_COLUMNS" in duplicate["declared_dimensions"]
    assert result["undeclared_defects"] == []


def test_a1_materially_incomplete_case_fails_closed() -> None:
    result = evaluate_a1_structural_matrix_v1()
    by_case = {row["case_id"]: row for row in result["case_results"]}
    incomplete = by_case["S1-SYN-003"]
    assert incomplete["terminal_class"] == "PASS_NEEDS_EVIDENCE"
    assert "MISSING_COLUMNS" in incomplete["declared_dimensions"]


def test_a1_no_second_xlsx_parser_created() -> None:
    root = _repo_root()
    lab_module = (root / "pymia" / "smartpyme" / "excel_lab_ingestion_v1.py").read_text(encoding="utf-8")
    evaluator = (root / "tools" / "service_1_excel_reality_lab_a1_structural_matrix_v1.py").read_text(encoding="utf-8")

    assert "excel_lab_ingestion_v1" in evaluator
    assert "openpyxl" not in evaluator
    assert "load_workbook" not in evaluator
    assert "pandas.read_excel" not in evaluator
    assert "ExcelProfileBuilder" in lab_module
