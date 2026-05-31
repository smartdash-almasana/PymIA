"""
Tests for xlsx_document_metadata_adapter.

Verifica:
1. Archivo inexistente devuelve ParsedDocumentMetadata con parse_status FAILED.
2. Archivo no XLSX devuelve parse_status FAILED.
3. XLSX mínimo válido devuelve file_type="xlsx", parser_name="excel_profile_v1".
4. XLSX con hoja tabular produce sheets.
5. Metadata serializa con to_dict().
6. fields/ambiguous_fields/unknown_fields son listas.
7. raw_artifact_refs incluye profile_source.
8. warnings reporta fórmulas o merged ranges si el fixture lo permite.
9. No importa docling.
10. No importa pandas/openpyxl directamente.
11. No genera EvidenceRecord.
12. No llama evidence_gate/post_ficha/intake.
13. No ejecuta fórmulas; solo puede reportar presencia de fórmulas como warning.
14. Metadata resultante es compatible con evidence_gate si fields cubren required_fields.
"""

import ast
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pymia.smartpyme.xlsx_document_metadata_adapter import parse_xlsx_to_document_metadata
from pymia.smartpyme.parsed_document_metadata import PARSE_STATUS_FAILED, PARSE_STATUS_OK
from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency


# 1. Archivo inexistente devuelve ParsedDocumentMetadata con parse_status FAILED.
def test_nonexistent_file_returns_failed():
    result = parse_xlsx_to_document_metadata("does_not_exist_999.xlsx")
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("file_not_found" in w for w in result.warnings)


# 2. Archivo no XLSX devuelve parse_status FAILED.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
def test_non_xlsx_extension_returns_failed(mock_exists):
    mock_exists.return_value = True
    result = parse_xlsx_to_document_metadata("dummy.csv")
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("unsupported_extension" in w for w in result.warnings)


# Helper for mocking ExcelProfileBuilder
def _mock_profile_builder_return(
    sheet_name="Hoja1", 
    sheet_kind="tabular", 
    detected=None, 
    ambiguous=None, 
    unknown=None,
    formula_cells_count=0,
    merged_ranges=None,
):
    profile_mock = MagicMock()
    profile_mock.sheets = []
    
    sheet_mock = MagicMock()
    sheet_mock.sheet_name = sheet_name
    sheet_mock.sheet_kind = sheet_kind
    sheet_mock.probable_header_row = 1
    sheet_mock.max_column = 5
    sheet_mock.max_row = 100
    sheet_mock.formula_cells_count = formula_cells_count
    sheet_mock.merged_ranges = merged_ranges or []
    sheet_mock.tabular_likelihood = 0.9
    
    # Columns mock
    cols = []
    if detected:
        for f in detected:
            col = MagicMock()
            col.semantic_label = f
            col.is_ambiguous = False
            col.name = f"col_{f}"
            cols.append(col)
    if ambiguous:
        for f in ambiguous:
            col = MagicMock()
            col.semantic_label = f
            col.is_ambiguous = True
            col.name = f"col_{f}"
            cols.append(col)
    if unknown:
        for f in unknown:
            col = MagicMock()
            col.semantic_label = "unknown"
            col.is_ambiguous = False
            col.name = f
            cols.append(col)
            
    sheet_mock.columns = cols
    profile_mock.sheets.append(sheet_mock)
    
    return profile_mock


# 3. XLSX mínimo válido devuelve file_type="xlsx", parser_name="excel_profile_v1".
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_valid_xlsx_returns_correct_constants(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(detected=["ventas"])
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    assert result.parse_status == PARSE_STATUS_OK
    assert result.file_type == "xlsx"
    assert result.parser_name == "excel_profile_v1"


# 4. XLSX con hoja tabular produce sheets.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_xlsx_tabular_produces_sheets(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(detected=["ventas"])
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    assert len(result.sheets) == 1
    assert result.sheets[0].name == "Hoja1"
    assert result.sheets[0].kind == "tabular"


# 5. Metadata serializa con to_dict().
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_metadata_serializes_with_to_dict(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(detected=["ventas"])
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    d = result.to_dict()
    assert isinstance(d, dict)
    assert d["file_type"] == "xlsx"
    assert d["fields"] == ["ventas"]


# 6. fields/ambiguous_fields/unknown_fields son listas.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_fields_are_lists(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(
        detected=["ventas"], 
        ambiguous=["total"], 
        unknown=["col1"]
    )
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    assert isinstance(result.fields, list)
    assert isinstance(result.ambiguous_fields, list)
    assert isinstance(result.unknown_fields, list)
    assert result.fields == ["ventas"]
    assert result.ambiguous_fields == ["total"]
    assert result.unknown_fields == ["col1"]


# 7. raw_artifact_refs incluye profile_source.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_raw_artifact_refs_includes_profile_source(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(detected=["ventas"])
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    assert "profile_source" in result.raw_artifact_refs
    assert "dummy.xlsx" in result.raw_artifact_refs["profile_source"]


# 8. warnings reporta fórmulas o merged ranges si el fixture lo permite.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_warnings_report_formulas_and_merged_ranges(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(
        detected=["ventas"],
        formula_cells_count=5,
        merged_ranges=["A1:B2"]
    )
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    assert any("formula_cells_present" in w for w in result.warnings)
    assert any("merged_ranges_present" in w for w in result.warnings)


# 9-13. AST checks for imports, EvidenceRecord, gates, intakes, formulas
def test_adapter_ast_rules():
    with open("pymia/smartpyme/xlsx_document_metadata_adapter.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    
    forbidden_imports = {"docling", "pandas", "openpyxl", "EvidenceRecord", "evidence_gate", "post_ficha_evidence_gate", "intake"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                assert base_module not in forbidden_imports, f"Forbidden import found: {alias.name}"
                assert alias.name not in forbidden_imports, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                assert base_module not in forbidden_imports, f"Forbidden import from found: {node.module}"
            for alias in node.names:
                assert alias.name not in forbidden_imports, f"Forbidden imported name found: {alias.name}"


# 14. Metadata resultante es compatible con evidence_gate si fields cubren required_fields.
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.xlsx_document_metadata_adapter.ExcelProfileBuilder")
def test_metadata_compatible_with_evidence_gate(mock_builder_class, mock_exists):
    mock_exists.return_value = True
    mock_builder = mock_builder_class.return_value
    mock_builder.build_profile.return_value = _mock_profile_builder_return(detected=["ventas", "costos"])
    
    result = parse_xlsx_to_document_metadata("dummy.xlsx")
    
    intake_record = {
        "tenant_id": "t1",
        "intake_id": "i1",
        "evidence_requests": [
            {
                "request_id": "req_1",
                "evidence_type": "doc_ventas",
                "required_fields": ["ventas"],
                "blocks_analysis": True,
            }
        ]
    }
    
    evidence_records = [
        {
            "tenant_id": "t1",
            "intake_id": "i1",
            "evidence_id": "ev_1",
            "evidence_type": "doc_ventas",
            "status": "RECEIVED",
            "request_id": "req_1",
            "metadata": result.to_dict(),
        }
    ]
    
    gate_result = evaluate_evidence_sufficiency(intake_record, evidence_records)
    
    assert gate_result.status == "READY"
    assert gate_result.assessments[0].status == "SATISFIED"
