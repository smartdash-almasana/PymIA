"""
Tests for docling_document_metadata_adapter.

Verifica:
1. Archivo inexistente devuelve ParsedDocumentMetadata FAILED con file_not_found.
2. Extensión no soportada devuelve FAILED con unsupported_extension.
3. Si docling no está instalado o import falla, devuelve FAILED con optional_dependency_missing:docling.
4. No hay import global de docling en el módulo.
5. No importa pandas/openpyxl/tools/excel_evidence.
6. No llama EvidenceRecord.
7. No llama evidence_gate/post_ficha/intake.
8. No llama ClinicalConversationalPort.
9. Con mock de Docling exitoso con headings/texts, devuelve sections.
10. Con mock de Docling exitoso con tables/headers, devuelve tables y fields.
11. Si Docling falla durante convert, devuelve FAILED con docling_parse_error.
12. Metadata serializa con to_dict().
13. Confidence queda entre 0 y 0.9.
14. No ejecuta fórmulas ni diagnóstico por AST.
"""

import ast
from unittest.mock import patch, MagicMock

from pymia.smartpyme.docling_document_metadata_adapter import parse_docling_to_document_metadata
from pymia.smartpyme.parsed_document_metadata import ParsedDocumentMetadata, PARSE_STATUS_FAILED, PARSE_STATUS_OK

# 1. Archivo inexistente devuelve ParsedDocumentMetadata FAILED con file_not_found.
def test_missing_file_returns_failed():
    result = parse_docling_to_document_metadata("does_not_exist_999.pdf")
    assert isinstance(result, ParsedDocumentMetadata)
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("file_not_found" in w for w in result.warnings)

# 2. Extensión no soportada devuelve FAILED con unsupported_extension.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
def test_unsupported_extension_returns_failed(mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    result = parse_docling_to_document_metadata("dummy.xyz")
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("unsupported_extension:.xyz" in w for w in result.warnings)

# 3. Si docling no está instalado o import falla, devuelve FAILED con optional_dependency_missing:docling.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
def test_docling_missing_returns_failed(mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_ensure.return_value = (None, "simulated missing")
    result = parse_docling_to_document_metadata("dummy.pdf")
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("optional_dependency_missing:docling" in w for w in result.warnings)

# 9. Con mock de Docling exitoso con headings/texts, devuelve sections.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
@patch("pymia.smartpyme.docling_document_metadata_adapter._run_docling")
def test_docling_success_with_headings_returns_sections(mock_run, mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_docling_mod = MagicMock()
    mock_docling_mod.__version__ = "1.0.0"
    mock_ensure.return_value = (mock_docling_mod, None)

    mock_doc = MagicMock()
    mock_heading = MagicMock()
    mock_heading.text = "Introduction"
    mock_heading.level = 1
    mock_doc.headings = [mock_heading]
    mock_doc.texts = []
    mock_doc.tables = []
    mock_run.return_value = mock_doc

    result = parse_docling_to_document_metadata("dummy.pdf")
    assert result.parse_status == PARSE_STATUS_OK
    assert len(result.sections) == 1
    assert result.sections[0].heading == "Introduction"

# 10. Con mock de Docling exitoso con tables/headers, devuelve tables y fields.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
@patch("pymia.smartpyme.docling_document_metadata_adapter._run_docling")
def test_docling_success_with_tables_returns_tables_and_fields(mock_run, mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_ensure.return_value = (MagicMock(), None)

    mock_doc = MagicMock()
    mock_doc.headings = []
    mock_doc.texts = []
    mock_table = MagicMock()
    mock_table.self_ref = "table_1"
    mock_table.num_cols = 2
    mock_table.num_rows = 5
    mock_table.column_headers = ["Amount", "Date"]
    mock_doc.tables = [mock_table]
    mock_run.return_value = mock_doc

    result = parse_docling_to_document_metadata("dummy.pdf")
    assert result.parse_status == PARSE_STATUS_OK
    assert len(result.tables) == 1
    assert "Amount" in result.fields
    assert "Date" in result.fields

# 11. Si Docling falla durante convert, devuelve FAILED con docling_parse_error.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
@patch("pymia.smartpyme.docling_document_metadata_adapter._run_docling")
def test_docling_convert_failure_returns_failed(mock_run, mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_ensure.return_value = (MagicMock(), None)
    mock_run.side_effect = Exception("simulated conversion error")

    result = parse_docling_to_document_metadata("dummy.pdf")
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("docling_parse_error" in w for w in result.warnings)

# 12. Metadata serializa con to_dict().
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
@patch("pymia.smartpyme.docling_document_metadata_adapter._run_docling")
def test_metadata_serializes_with_to_dict(mock_run, mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_ensure.return_value = (MagicMock(), None)

    mock_doc = MagicMock()
    mock_doc.headings = []
    mock_doc.texts = []
    mock_table = MagicMock()
    mock_table.self_ref = "table_1"
    mock_table.num_cols = 2
    mock_table.num_rows = 5
    mock_table.column_headers = ["Amount"]
    mock_doc.tables = [mock_table]
    mock_run.return_value = mock_doc

    result = parse_docling_to_document_metadata("dummy.pdf")
    d = result.to_dict()
    assert d["file_type"] == "pdf"
    assert "Amount" in d["fields"]

# 13. Confidence queda entre 0 y 0.9.
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.exists")
@patch("pymia.smartpyme.docling_document_metadata_adapter.Path.is_file")
@patch("pymia.smartpyme.docling_document_metadata_adapter._ensure_docling")
@patch("pymia.smartpyme.docling_document_metadata_adapter._run_docling")
def test_confidence_is_bounded(mock_run, mock_ensure, mock_is_file, mock_exists):
    mock_exists.return_value = True
    mock_is_file.return_value = True
    mock_ensure.return_value = (MagicMock(), None)

    mock_doc = MagicMock()
    # huge amount of sections/tables to try to overflow confidence
    mock_heading = MagicMock()
    mock_heading.text = "Section"
    mock_heading.level = 1
    mock_doc.headings = [mock_heading] * 100

    mock_table = MagicMock()
    mock_table.self_ref = "table"
    mock_table.column_headers = ["Field"] * 50
    mock_doc.tables = [mock_table] * 100
    mock_run.return_value = mock_doc

    result = parse_docling_to_document_metadata("dummy.pdf")
    assert result.confidence <= 0.9
    assert result.confidence >= 0.0

# 4, 5, 6, 7, 8, 14. AST Checks for docling, pandas, openpyxl, excel_evidence, EvidenceRecord, gates, intake, ClinicalConversationalPort, formula, diagnostico.
def test_docling_adapter_ast_rules():
    with open("pymia/smartpyme/docling_document_metadata_adapter.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_imports = {
        "pandas",
        "openpyxl",
        "excel_evidence",
        "EvidenceRecord",
        "evidence_gate",
        "post_ficha_evidence_gate",
        "intake",
        "ClinicalConversationalPort",
        "formula",
        "diagnostico"
    }

    # Docling se puede importar, pero sólo localmente en funciones, no a nivel global.
    global_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                global_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                global_imports.append(node.module)

    for gi in global_imports:
        assert "docling" not in gi, f"docling was imported globally: {gi}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden not in alias.name, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in forbidden_imports:
                    assert forbidden not in node.module, f"Forbidden import from found: {node.module}"
            for alias in node.names:
                for forbidden in forbidden_imports:
                    assert forbidden not in alias.name, f"Forbidden imported name found: {alias.name}"
