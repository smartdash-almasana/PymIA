from pathlib import Path
import pytest
from openpyxl import Workbook

from pymia.cli import vertical_slice
from pymia.faithful_operator import (
    handle_owner_message,
    receive_excel_and_build_candidate,
    OperatorPhase,
    OperatorState,
)

def _write_excel(path: Path, rows: list[list[object]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    workbook.save(path)

def test_build_pipeline_includes_catalog_reconciliation(tmp_path: Path):
    excel = tmp_path / "test_reconciliation.xlsx"
    _write_excel(excel, [
        ["fecha", "producto", "ventas", "costo"],
        ["2026-06-01", "A", 100, 60]
    ])
    
    result = vertical_slice.build_pipeline(
        excel,
        message="mi mensaje",
        tenant_id="test_tenant",
        intake_id="test_intake",
    )
    
    assert "catalog_reconciliation" in result
    reconciliation = result["catalog_reconciliation"]
    assert isinstance(reconciliation, list)
    assert len(reconciliation) > 0
    
    # Verify that each entry contains the required keys
    for entry in reconciliation:
        assert "formula_id" in entry
        assert "pathology_code" in entry
        assert "status" in entry
        assert "available_evidence" in entry
        assert "missing_evidence" in entry
        assert "next_audit_questions" in entry
        assert "matched_sources" in entry
        assert "required_evidence" in entry
        assert "required_variables" in entry

def test_build_pipeline_filters_catalog_reconciliation_by_formula_ids(tmp_path: Path):
    excel = tmp_path / "test_reconciliation.xlsx"
    _write_excel(excel, [
        ["fecha", "producto", "ventas", "costo"],
        ["2026-06-01", "A", 100, 60]
    ])
    
    formula_ids_filter = ["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real"]
    result = vertical_slice.build_pipeline(
        excel,
        message="mi mensaje",
        tenant_id="test_tenant",
        intake_id="test_intake",
        formula_ids=formula_ids_filter,
    )
    
    reconciliation = result["catalog_reconciliation"]
    assert isinstance(reconciliation, list)
    assert len(reconciliation) > 0
    
    # Verify that only the filtered formulas are present
    for entry in reconciliation:
        assert entry["formula_id"] in formula_ids_filter

def test_faithful_operator_preserves_catalog_reconciliation(tmp_path: Path):
    excel = tmp_path / "test_reconciliation.xlsx"
    _write_excel(excel, [
        ["fecha", "producto", "ventas", "costo"],
        ["2026-06-01", "A", 100, 60]
    ])
    
    state = handle_owner_message("tengo un problema con el margen bruto")
    assert state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    
    new_state = receive_excel_and_build_candidate(state, excel, storage_dir=tmp_path / "storage")
    assert new_state.current_state == OperatorPhase.OWNER_CONFIRMATION_PENDING
    
    # Verify that catalog_reconciliation is preserved in the OperatorState
    assert hasattr(new_state, "catalog_reconciliation")
    assert isinstance(new_state.catalog_reconciliation, list)
    assert len(new_state.catalog_reconciliation) > 0
    
    # Check that candidate_response has the sober reference
    assert "Reconciliación de catálogos:" in new_state.candidate_response
    assert "fórmulas" in new_state.candidate_response

def test_static_check_for_forbidden_references():
    # Read source code of faithful_operator and vertical_slice
    slice_code = Path(vertical_slice.__file__).read_text(encoding="utf-8")
    operator_file = receive_excel_and_build_candidate.__globals__["__file__"]
    operator_code = Path(operator_file).read_text(encoding="utf-8")
    
    forbidden_terms = ["cafeteria_margin_focus", "margin_evidence_request"]
    for term in forbidden_terms:
        assert term not in slice_code, f"Forbidden term '{term}' found in vertical_slice.py"
        assert term not in operator_code, f"Forbidden term '{term}' found in faithful_operator.py"
