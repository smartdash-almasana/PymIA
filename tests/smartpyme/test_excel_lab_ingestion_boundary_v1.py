"""Boundary and characterization tests for excel_lab_ingestion_v1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import pandas as pd
import pytest

from pymia.contracts.column_confirmation_v1 import ConfirmationStatus, CalculationRelevance
from pymia.smartpyme.excel_lab_ingestion_v1 import (
    ContextClassifier,
    XlsxDocumentIngestor,
    SemanticFieldMapper,
    DocumentCurator,
    ColumnConfirmationBuilder,
    StructuredEvidenceExporter,
    RawTable,
    NormalizedTable,
    FieldMapping,
    DocumentCurationReport,
    CuratedDocument,
    persist_curation_artifacts,
)


@pytest.fixture
def temp_excel_file(tmp_path: Path) -> Path:
    """Fixture to create a valid Excel workbook with two sheets for ingestion tests."""
    file_path = tmp_path / "test_data.xlsx"
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        # Sheet 1: Ventas (tabular)
        df_ventas = pd.DataFrame([
            {"Fecha": "2026-06-01", "Producto": "Item A", "Cantidad": 5, "Precio Unitario": 100.0, "Costo Unitario": 60.0},
            {"Fecha": "2026-06-02", "Producto": "Item B", "Cantidad": 2, "Precio Unitario": 200.0, "Costo Unitario": 120.0},
        ])
        # Write df with headers starting at row 3 (header index 2) to test header detection
        df_empty = pd.DataFrame([[""] * 5] * 2)
        df_empty.to_excel(writer, sheet_name="Mis Ventas", index=False, header=False)
        df_ventas.to_excel(writer, sheet_name="Mis Ventas", index=False, startrow=2)

        # Sheet 2: Senales Operativas
        df_signals = pd.DataFrame([
            {"Signal ID": "SIG-001", "Mes": "2026-06", "Signal Type": "Warning", "Description": "Test Alert", "Severity": "Medium"},
        ])
        df_signals.to_excel(writer, sheet_name="Senales Operativas", index=False)
    
    return file_path


# ==============================================================================
# BOUNDARY 1: INGESTIÓN / LECTURA ESTRUCTURAL
# ==============================================================================

def test_context_classifier() -> None:
    classifier = ContextClassifier()
    assert classifier.classify("Mis Ventas", ["fecha", "cantidad", "precio"]) == "ventas"
    assert classifier.classify("Stock Real", ["stock", "deposito"]) == "stock"
    assert classifier.classify("Random Sheet", ["col1", "col2"]) == "generic"


def test_xlsx_document_ingestor(temp_excel_file: Path) -> None:
    ingestor = XlsxDocumentIngestor()
    tables = ingestor.ingest(temp_excel_file)
    
    assert len(tables) >= 2
    
    # Verify Ventas sheet was ingested
    ventas_table = next(t for t in tables if "Ventas" in t.sheet_name)
    assert ventas_table.context == "ventas"
    assert "Fecha" in ventas_table.columns
    assert "Producto" in ventas_table.columns
    assert len(ventas_table.records) == 2
    assert ventas_table.records[0]["Producto"] == "Item A"
    assert int(ventas_table.records[0]["Cantidad"]) == 5


# ==============================================================================
# BOUNDARY 2: PROFILING / EXTRACCIÓN
# ==============================================================================

def test_semantic_field_mapper() -> None:
    mapper = SemanticFieldMapper()
    columns = ["Fecha", "Producto", "Cantidad", "Precio Unitario", "Costo Unitario", "Desconocido"]
    
    mappings = mapper.map_columns(columns)
    assert len(mappings) == len(columns)
    
    mapping_dict = {m.source_column: m.target_field for m in mappings}
    assert mapping_dict["Fecha"] == "fecha"
    assert mapping_dict["Producto"] == "producto"
    assert mapping_dict["Cantidad"] == "cantidad"
    assert mapping_dict["Precio Unitario"] == "precio_venta"
    assert mapping_dict["Costo Unitario"] == "costo_unitario"
    assert mapping_dict["Desconocido"] == "unknown"

    # Test exact/fallback keys mapping
    fallbacks = mapper.map_columns(["Venta", "Total Venta", "Margen Bruto"])
    fallback_dict = {m.source_column: m.target_field for m in fallbacks}
    assert fallback_dict["Venta"] == "venta_total"
    assert fallback_dict["Total Venta"] == "venta_total"
    assert fallback_dict["Margen Bruto"] == "margen"


def test_document_curator_and_validation() -> None:
    raw_table = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=["Cantidad", "Precio", "Producto"],
        records=[
            {"Cantidad": "5", "Precio": "100.0", "Producto": "A"},
            {"Cantidad": "invalid_num", "Precio": "200.0", "Producto": "B"},
        ],
        context="ventas",
    )
    
    mapper = SemanticFieldMapper()
    normalized_tables = mapper.normalize_tables([raw_table])
    
    curator = DocumentCurator()
    report = curator.build_report(
        file_name="test.xlsx",
        raw_tables=[raw_table],
        normalized_tables=normalized_tables,
    )
    
    assert report.status == "PARTIAL"  # Has validation issues
    assert len(report.validation_issues) == 2
    issue_codes = {issue.code for issue in report.validation_issues}
    assert "invalid_number" in issue_codes
    assert "typed_validation_error" in issue_codes


def test_column_confirmation_builder_blocking_states() -> None:
    raw_table = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=["Cantidad", "Precio Venta", "Medio De Pago"],
        records=[
            {"Cantidad": 5, "Precio Venta": 100.0, "Medio De Pago": "Efectivo"},
        ],
        context="ventas",
    )
    
    mapper = SemanticFieldMapper()
    normalized_tables = mapper.normalize_tables([raw_table])
    
    builder = ColumnConfirmationBuilder()
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=normalized_tables,
        raw_tables=[raw_table],
    )
    
    # Verify that "Medio De Pago" negative pattern demoted it to unknown and informational
    entry_medio = next(e for e in matrix.entries if e.original_column_name == "Medio De Pago")
    assert entry_medio.suggested_semantic_role == "unknown"
    assert entry_medio.calculation_relevance == CalculationRelevance.INFORMATIONAL
    
    # Clean mappings require confirmation
    entry_cantidad = next(e for e in matrix.entries if e.original_column_name == "Cantidad")
    assert entry_cantidad.confirmation_status == ConfirmationStatus.PENDING_OWNER_CONFIRMATION


# ==============================================================================
# BOUNDARY 3: OUTPUT ESTRUCTURADO
# ==============================================================================

def test_structured_evidence_exporter_with_confirmation_blocking(temp_excel_file: Path) -> None:
    ingestor = XlsxDocumentIngestor()
    raw_tables = ingestor.ingest(temp_excel_file)
    
    mapper = SemanticFieldMapper()
    normalized_tables = mapper.normalize_tables(raw_tables)
    
    curator = DocumentCurator()
    report = curator.build_report(
        file_name="test_data.xlsx",
        raw_tables=raw_tables,
        normalized_tables=normalized_tables,
    )
    
    curated = CuratedDocument(
        file_name="test_data.xlsx",
        document_type="xlsx_operational_evidence",
        raw_tables=raw_tables,
        normalized_tables=normalized_tables,
        report=report,
    )
    
    exporter = StructuredEvidenceExporter()
    evidence = exporter.export(curated=curated, tenant_id="tenant_123")
    
    assert evidence.tenant_id == "tenant_123"
    assert evidence.metadata["curation_status"] == "PARTIAL"  # Needs confirmation
    
    # Since columns are not confirmed, calculation should be blocked and emit warnings
    assert evidence.metadata["calculation_blocked"] is True
    warnings = evidence.metadata["evidence_warnings"]
    assert any(w["reason_code"] == "COLUMN_CONFIRMATION_PENDING" for w in warnings)


def test_structured_evidence_exporter_with_confirmed_columns() -> None:
    # Build curated manually and set confirmation matrix to confirmed
    raw_table = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=["Cantidad", "Precio Unitario", "Costo Unitario"],
        records=[
            {"Cantidad": 10, "Precio Unitario": 100.0, "Costo Unitario": 60.0},
        ],
        context="ventas",
    )
    
    mapper = SemanticFieldMapper()
    normalized_tables = mapper.normalize_tables([raw_table])
    
    builder = ColumnConfirmationBuilder()
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=normalized_tables,
        raw_tables=[raw_table],
    )
    
    # Explicitly confirm all columns
    for entry in matrix.entries:
        entry.owner_confirmed_role = entry.suggested_semantic_role
        entry.confirmation_status = ConfirmationStatus.CONFIRMED
        
    report = DocumentCurationReport(
        file_name="test.xlsx",
        status="CURATED",
        tables_count=1,
        rows_count=1,
        mapped_fields={"Cantidad": "cantidad", "Precio Unitario": "precio_venta", "Costo Unitario": "costo_unitario"},
        column_confirmation_matrix=matrix,
    )
    
    curated = CuratedDocument(
        file_name="test.xlsx",
        document_type="xlsx_operational_evidence",
        raw_tables=[raw_table],
        normalized_tables=normalized_tables,
        report=report,
    )
    
    exporter = StructuredEvidenceExporter()
    evidence = exporter.export(curated=curated, tenant_id="tenant_123")
    
    assert evidence.metadata["calculation_blocked"] is False
    assert len(evidence.metadata["evidence_warnings"]) == 0
    
    # Verify calculated variables:
    # ventas_total = 100 * 10 = 1000
    # costos_total = 60 * 10 = 600
    # margen_bruto = 1000 - 600 = 400
    # margen_bruto_pct = 400 / 1000 = 0.4
    assert evidence.computed_variables["ventas_total"] == 1000.0
    assert evidence.computed_variables["costos_total"] == 600.0
    assert evidence.computed_variables["cantidad_total"] == 10.0
    assert evidence.computed_variables["margen_bruto"] == 400.0
    assert evidence.computed_variables["margen_bruto_pct"] == 0.4000


def test_persist_curation_artifacts(tmp_path: Path) -> None:
    raw_table = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=["ColA"],
        records=[{"ColA": 1}],
        context="ventas",
    )
    normalized_table = NormalizedTable(
        sheet_name="Ventas",
        context="ventas",
        header_row=1,
        columns=["ColA"],
        mappings=[FieldMapping(source_column="ColA", target_field="cantidad", confidence="mapped")],
        records=[{"cantidad": 1}],
    )
    report = DocumentCurationReport(
        file_name="test.xlsx",
        status="CURATED",
        tables_count=1,
        rows_count=1,
        mapped_fields={"ColA": "cantidad"},
    )
    curated = CuratedDocument(
        file_name="test.xlsx",
        document_type="xlsx_operational_evidence",
        raw_tables=[raw_table],
        normalized_tables=[normalized_table],
        report=report,
    )
    
    exporter = StructuredEvidenceExporter()
    evidence = exporter.export(curated=curated, tenant_id="tenant_123")
    
    output_dir = tmp_path / "artifacts"
    artifacts = persist_curation_artifacts(
        curated=curated,
        evidence=evidence,
        output_dir=output_dir,
        stem="curation_run",
    )
    
    assert Path(artifacts["raw_tables"]).exists()
    assert Path(artifacts["normalized_tables"]).exists()
    assert Path(artifacts["sheet_reports"]).exists()
    assert Path(artifacts["structured_evidence"]).exists()
    
    # Read structured evidence and verify
    data = json.loads(Path(artifacts["structured_evidence"]).read_text(encoding="utf-8"))
    assert data["tenant_id"] == "tenant_123"
