"""
Tests for ParsedDocumentMetadata.

Verifica:
1. Metadata mínima válida serializa a dict.
2. fields se normaliza: trim, elimina vacíos y deduplica.
3. confidence fuera de rango falla.
4. confidence bool falla.
5. parse_status inválido falla.
6. file_type vacío falla.
7. parser_name vacío falla.
8. sheets/tables/sections serializan correctamente.
9. raw_artifact_refs serializa como dict.
10. No hay imports prohibidos.
11. No hay lectura de archivos.
12. to_dict() es compatible con evidence_gate.
"""

import ast
from typing import Any

import pytest

from pymia.smartpyme.parsed_document_metadata import (
    ParsedDocumentMetadata,
    SheetSummary,
    TableSummary,
    SectionSummary,
    PARSE_STATUS_OK,
)
from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency


# 1. Metadata mínima válida serializa a dict.
def test_minimal_valid_metadata_serializes_to_dict():
    meta = ParsedDocumentMetadata(
        file_type="xlsx",
        parser_name="excel_profile_v1",
        parser_version="1.0",
        parse_status=PARSE_STATUS_OK,
    )
    d = meta.to_dict()
    assert isinstance(d, dict)
    assert d["file_type"] == "xlsx"
    assert d["parser_name"] == "excel_profile_v1"
    assert d["parse_status"] == "OK"
    assert "parsed_at" in d
    assert isinstance(d["fields"], list)
    assert len(d["fields"]) == 0


# 2. fields se normaliza: trim, elimina vacíos y deduplica.
def test_fields_normalization():
    meta = ParsedDocumentMetadata(
        file_type="csv",
        parser_name="csv_v1",
        parser_version="1.0",
        parse_status=PARSE_STATUS_OK,
        fields=[" field1 ", "field2", "", None, "field1", "  field3  "],
    )
    assert meta.fields == ["field1", "field2", "field3"]


# 3. confidence fuera de rango falla.
def test_confidence_out_of_range_fails():
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        ParsedDocumentMetadata(
            file_type="csv",
            parser_name="csv_v1",
            parser_version="1.0",
            parse_status=PARSE_STATUS_OK,
            confidence=-0.1,
        )
    with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
        ParsedDocumentMetadata(
            file_type="csv",
            parser_name="csv_v1",
            parser_version="1.0",
            parse_status=PARSE_STATUS_OK,
            confidence=1.1,
        )


# 4. confidence bool falla.
def test_confidence_bool_fails():
    with pytest.raises(ValueError, match="confidence must be a number"):
        ParsedDocumentMetadata(
            file_type="csv",
            parser_name="csv_v1",
            parser_version="1.0",
            parse_status=PARSE_STATUS_OK,
            confidence=True, # type: ignore
        )


# 5. parse_status inválido falla.
def test_invalid_parse_status_fails():
    with pytest.raises(ValueError, match="parse_status must be one of"):
        ParsedDocumentMetadata(
            file_type="csv",
            parser_name="csv_v1",
            parser_version="1.0",
            parse_status="INVALID_STATUS",
        )


# 6. file_type vacío falla.
def test_empty_file_type_fails():
    with pytest.raises(ValueError, match="file_type is required and must be a non-empty string"):
        ParsedDocumentMetadata(
            file_type="  ",
            parser_name="csv_v1",
            parser_version="1.0",
            parse_status=PARSE_STATUS_OK,
        )


# 7. parser_name vacío falla.
def test_empty_parser_name_fails():
    with pytest.raises(ValueError, match="parser_name is required and must be a non-empty string"):
        ParsedDocumentMetadata(
            file_type="csv",
            parser_name="",
            parser_version="1.0",
            parse_status=PARSE_STATUS_OK,
        )


# 8. sheets/tables/sections serializan correctamente.
def test_summaries_serialize_correctly():
    meta = ParsedDocumentMetadata(
        file_type="mixed",
        parser_name="mixed_v1",
        parser_version="1.0",
        parse_status=PARSE_STATUS_OK,
        sheets=[SheetSummary(name="Sheet1", kind="tabular", column_count=5)],
        tables=[TableSummary(table_id="t1", origin="page:1", row_count=10)],
        sections=[SectionSummary(heading="Intro", level=1, char_count=100)],
    )
    d = meta.to_dict()
    assert len(d["sheets"]) == 1
    assert d["sheets"][0]["name"] == "Sheet1"
    assert d["sheets"][0]["column_count"] == 5

    assert len(d["tables"]) == 1
    assert d["tables"][0]["table_id"] == "t1"
    assert d["tables"][0]["row_count"] == 10

    assert len(d["sections"]) == 1
    assert d["sections"][0]["heading"] == "Intro"
    assert d["sections"][0]["char_count"] == 100


# 9. raw_artifact_refs serializa como dict.
def test_raw_artifact_refs_serializes_as_dict():
    meta = ParsedDocumentMetadata(
        file_type="csv",
        parser_name="csv_v1",
        parser_version="1.0",
        parse_status=PARSE_STATUS_OK,
        raw_artifact_refs={"ref1": "url1", " ref2 ": " url2 "},
    )
    d = meta.to_dict()
    assert isinstance(d["raw_artifact_refs"], dict)
    assert d["raw_artifact_refs"] == {"ref1": "url1", "ref2": "url2"}


# 10. No hay imports prohibidos.
def test_no_forbidden_imports():
    with open("pymia/smartpyme/parsed_document_metadata.py", "r", encoding="utf-8") as f:
        source = f.read()
    
    tree = ast.parse(source)
    forbidden_modules = {"pandas", "openpyxl", "docling", "tools"}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                assert base_module not in forbidden_modules, f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                assert base_module not in forbidden_modules, f"Forbidden import from found: {node.module}"


# 11. No hay lectura de archivos.
def test_no_file_reading():
    with open("pymia/smartpyme/parsed_document_metadata.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_calls = {"open", "Path", "read_text", "read_bytes"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls, f"Forbidden call found: {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls, f"Forbidden method call found: {node.func.attr}"


# 12. to_dict() es compatible con evidence_gate.
def test_to_dict_compatible_with_evidence_gate():
    # Creamos un intake_record mock con un requirement que pide "ventas"
    intake_record = {
        "tenant_id": "t1",
        "intake_id": "i1",
        "evidence_requests": [
            {
                "request_id": "req_1",
                "evidence_type": "doc_ventas",
                "required_fields": ["ventas_mensuales", "costos"],
                "blocks_analysis": True,
            }
        ]
    }
    
    # Creamos la metadata con el parser
    meta = ParsedDocumentMetadata(
        file_type="xlsx",
        parser_name="excel_v1",
        parser_version="1.0",
        parse_status=PARSE_STATUS_OK,
        fields=["ventas_mensuales", "costos", "otro_campo"],
    )
    
    # Creamos un evidence_record mock que usa la metadata producida por nuestro objeto
    evidence_records = [
        {
            "tenant_id": "t1",
            "intake_id": "i1",
            "evidence_id": "ev_1",
            "evidence_type": "doc_ventas",
            "status": "RECEIVED",
            "request_id": "req_1",
            "metadata": meta.to_dict(),
        }
    ]
    
    # Evaluamos en el gate
    result = evaluate_evidence_sufficiency(intake_record, evidence_records)
    
    # Debe estar SATISFIED porque fields cubre required_fields
    assert result.status == "READY"
    assert result.assessments[0].status == "SATISFIED"
