"""
Tests for document_parser_front.

Verifica:
1. source_ref inexistente devuelve parse_status FAILED.
2. extensión desconocida devuelve file_type="unknown" y warning unknown_extension.
3. .pdf delega a parse_docling_to_document_metadata.
4. .docx delega a parse_docling_to_document_metadata.
5. .txt devuelve FAILED y warning parser_not_configured:.txt.
6. .csv devuelve FAILED y warning parser_not_configured:.csv.
7. .xlsx delega a parse_xlsx_to_document_metadata.
8. .xlsm delega a parse_xlsx_to_document_metadata.
9. No importa docling.
10. No importa tools/excel_evidence.py.
11. No llama ClinicalConversationalPort.
12. No crea EvidenceRecord.
13. No toca gates/intake.
14. Todo devuelve ParsedDocumentMetadata.
"""

import ast
from unittest.mock import patch, MagicMock

from pymia.smartpyme.document_parser_front import parse_document_to_metadata
from pymia.smartpyme.parsed_document_metadata import ParsedDocumentMetadata, PARSE_STATUS_FAILED, PARSE_STATUS_OK


# 1. source_ref inexistente devuelve parse_status FAILED.
def test_missing_source_ref_returns_failed():
    result = parse_document_to_metadata("does_not_exist_999.pdf")
    assert isinstance(result, ParsedDocumentMetadata)
    assert result.parse_status == PARSE_STATUS_FAILED
    assert any("file_not_found" in w for w in result.warnings)


# 2. extensión desconocida devuelve file_type="unknown" y warning unknown_extension.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
def test_unknown_extension_returns_unknown_and_warning(mock_exists):
    mock_exists.return_value = True
    result = parse_document_to_metadata("dummy.xyz123")
    assert isinstance(result, ParsedDocumentMetadata)
    assert result.parse_status == PARSE_STATUS_FAILED
    assert result.file_type == "unknown"
    assert any("unknown_extension:.xyz123" in w for w in result.warnings)


# 3. .pdf delega a parse_docling_to_document_metadata.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
@patch("pymia.smartpyme.document_parser_front.parse_docling_to_document_metadata")
def test_pdf_delegates_to_docling_adapter(mock_parse_docling, mock_exists):
    mock_exists.return_value = True
    mock_meta = MagicMock(spec=ParsedDocumentMetadata)
    mock_meta.file_type = "pdf"
    mock_meta.parse_status = PARSE_STATUS_OK
    mock_parse_docling.return_value = mock_meta

    result = parse_document_to_metadata("dummy.pdf")
    mock_parse_docling.assert_called_once()
    assert result.file_type == "pdf"
    assert result.parse_status == PARSE_STATUS_OK


# 4. .docx delega a parse_docling_to_document_metadata.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
@patch("pymia.smartpyme.document_parser_front.parse_docling_to_document_metadata")
def test_docx_delegates_to_docling_adapter(mock_parse_docling, mock_exists):
    mock_exists.return_value = True
    mock_meta = MagicMock(spec=ParsedDocumentMetadata)
    mock_meta.file_type = "docx"
    mock_meta.parse_status = PARSE_STATUS_OK
    mock_parse_docling.return_value = mock_meta

    result = parse_document_to_metadata("dummy.docx")
    mock_parse_docling.assert_called_once()
    assert result.file_type == "docx"
    assert result.parse_status == PARSE_STATUS_OK


# 4b. .pptx delega a parse_docling_to_document_metadata.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
@patch("pymia.smartpyme.document_parser_front.parse_docling_to_document_metadata")
def test_pptx_delegates_to_docling_adapter(mock_parse_docling, mock_exists):
    mock_exists.return_value = True
    mock_meta = MagicMock(spec=ParsedDocumentMetadata)
    mock_meta.file_type = "pptx"
    mock_meta.parse_status = PARSE_STATUS_OK
    mock_parse_docling.return_value = mock_meta

    result = parse_document_to_metadata("dummy.pptx")
    mock_parse_docling.assert_called_once()
    assert result.file_type == "pptx"
    assert result.parse_status == PARSE_STATUS_OK


# 5. .txt devuelve FAILED y warning parser_not_configured:.txt.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
def test_txt_returns_failed_and_warning(mock_exists):
    mock_exists.return_value = True
    result = parse_document_to_metadata("dummy.txt")
    assert isinstance(result, ParsedDocumentMetadata)
    assert result.parse_status == PARSE_STATUS_FAILED
    assert result.file_type == "txt"
    assert result.parser_name == "plaintext_v1"
    assert any("parser_not_configured:.txt" in w for w in result.warnings)


# 6. .csv devuelve FAILED y warning parser_not_configured:.csv.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
def test_csv_returns_failed_and_warning(mock_exists):
    mock_exists.return_value = True
    result = parse_document_to_metadata("dummy.csv")
    assert isinstance(result, ParsedDocumentMetadata)
    assert result.parse_status == PARSE_STATUS_FAILED
    assert result.file_type == "csv"
    assert result.parser_name == "csv_parser_v1"
    assert any("parser_not_configured:.csv" in w for w in result.warnings)


# 7. .xlsx delega a parse_xlsx_to_document_metadata.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
@patch("pymia.smartpyme.document_parser_front.parse_xlsx_to_document_metadata")
def test_xlsx_delegates_to_xlsx_adapter(mock_parse_xlsx, mock_exists):
    mock_exists.return_value = True
    mock_meta = MagicMock(spec=ParsedDocumentMetadata)
    mock_meta.file_type = "xlsx"
    mock_meta.parse_status = PARSE_STATUS_OK
    mock_parse_xlsx.return_value = mock_meta
    
    result = parse_document_to_metadata("dummy.xlsx")
    mock_parse_xlsx.assert_called_once()
    assert result.file_type == "xlsx"
    assert result.parse_status == PARSE_STATUS_OK


# 8. .xlsm delega a parse_xlsx_to_document_metadata.
@patch("pymia.smartpyme.document_parser_front.Path.exists")
@patch("pymia.smartpyme.document_parser_front.parse_xlsx_to_document_metadata")
def test_xlsm_delegates_to_xlsx_adapter(mock_parse_xlsx, mock_exists):
    mock_exists.return_value = True
    mock_meta = MagicMock(spec=ParsedDocumentMetadata)
    mock_meta.file_type = "xlsx"
    mock_meta.parse_status = PARSE_STATUS_OK
    mock_parse_xlsx.return_value = mock_meta
    
    result = parse_document_to_metadata("dummy.xlsm")
    mock_parse_xlsx.assert_called_once()
    assert result.file_type == "xlsx"
    assert result.parse_status == PARSE_STATUS_OK


# 9-13. AST checks for docling, excel_evidence, ClinicalConversationalPort, EvidenceRecord, gates, intake.
def test_document_parser_front_ast_rules():
    with open("pymia/smartpyme/document_parser_front.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_imports = {
        "docling", 
        "excel_evidence", 
        "ClinicalConversationalPort", 
        "EvidenceRecord", 
        "evidence_gate", 
        "post_ficha_evidence_gate", 
        "intake"
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_imports:
                    if forbidden == "docling":
                        assert alias.name != "docling", f"Forbidden import found: {alias.name}"
                    else:
                        assert forbidden not in alias.name, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in forbidden_imports:
                    if forbidden == "docling":
                        assert node.module != "docling" and not node.module.startswith("docling."), f"Forbidden import from found: {node.module}"
                    else:
                        assert forbidden not in node.module, f"Forbidden import from found: {node.module}"
            for alias in node.names:
                for forbidden in forbidden_imports:
                    if forbidden == "docling":
                        assert alias.name != "docling", f"Forbidden imported name found: {alias.name}"
                    else:
                        assert forbidden not in alias.name, f"Forbidden imported name found: {alias.name}"


# 14. Todo devuelve ParsedDocumentMetadata.
# Esto ya está cubierto por las anotaciones de tipo y los asserts isinstance() en los tests anteriores.
