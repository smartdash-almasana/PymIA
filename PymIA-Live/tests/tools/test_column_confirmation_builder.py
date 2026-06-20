from __future__ import annotations

from typing import Any

from tools.document_ingestion import (
    ColumnConfirmationBuilder,
    CuratedDocument,
    DocumentCurationReport,
    FieldMapping,
    NormalizedTable,
    RawTable,
    StructuredEvidenceExporter,
)


def _build_curated(
    *,
    columns: list[str],
    records: list[dict[str, Any]],
    context: str = "ventas",
    file_name: str = "test.xlsx",
) -> CuratedDocument:
    from tools.document_ingestion import SemanticFieldMapper
    mapper = SemanticFieldMapper()
    mappings = mapper.map_columns(columns)
    raw = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=columns,
        records=records,
        context=context,
    )
    normalized = NormalizedTable(
        sheet_name="Ventas",
        context=context,
        header_row=1,
        columns=columns,
        mappings=mappings,
        records=records,
    )
    report = DocumentCurationReport(
        file_name=file_name,
        status="CURATED",
        tables_count=1,
        rows_count=len(records),
        mapped_fields={col: col.lower() for col in columns},
    )
    return CuratedDocument(
        file_name=file_name,
        document_type="xlsx_operational_evidence",
        raw_tables=[raw],
        normalized_tables=[normalized],
        report=report,
    )


def test_builder_generates_matrix_with_entries() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    assert matrix.file_name == "test.xlsx"
    assert len(matrix.entries) == 2


def test_builder_marks_venta_total_as_pending_confirmation() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["VentaTotal"],
        records=[{"VentaTotal": 1000.0}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    assert entry.original_column_name == "VentaTotal"
    assert entry.suggested_semantic_role == "venta_total"
    assert entry.confirmation_status.value == "PENDING_OWNER_CONFIRMATION"
    assert entry.owner_question is not None


def test_builder_marks_producto_as_ignored() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["Producto"],
        records=[{"Producto": "Café"}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    assert entry.suggested_semantic_role == "producto"
    assert entry.confirmation_status.value == "PENDING_OWNER_CONFIRMATION"
    assert entry.owner_question is not None


def test_builder_negative_pattern_blocks_metodopago_as_pago() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["MetodoPago"],
        records=[{"MetodoPago": "Efectivo"}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    # Negative pattern should demote to unknown + INFORMATIONAL
    assert entry.suggested_semantic_role == "unknown"
    assert entry.calculation_relevance.value == "INFORMATIONAL"
    # And it should still ask the owner what this column means
    assert entry.owner_question is not None
    assert "forma de pago" in entry.owner_question.lower() or "significa" in entry.owner_question.lower()


def test_builder_blocks_precio_when_ambiguous() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["Precio"],
        records=[{"Precio": 100.0}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    # "Precio" should be marked as pending or blocked because it's ambiguous
    assert entry.confirmation_status.value in {
        "PENDING_OWNER_CONFIRMATION",
        "BLOCKED_AMBIGUOUS",
    }
    assert entry.owner_question is not None


def test_builder_includes_sample_values() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["Cantidad"],
        records=[{"Cantidad": 10}, {"Cantidad": 20}, {"Cantidad": 30}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    assert entry.sample_values == [10, 20, 30]


def test_builder_infers_number_type() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["PrecioVenta"],
        records=[{"PrecioVenta": 100.0}, {"PrecioVenta": 200.0}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    assert entry.inferred_type == "number"


def test_builder_infers_text_type() -> None:
    builder = ColumnConfirmationBuilder()
    curated = _build_curated(
        columns=["Producto"],
        records=[{"Producto": "Café"}, {"Producto": "Té"}],
    )
    matrix = builder.build(
        file_name="test.xlsx",
        normalized_tables=curated.normalized_tables,
        raw_tables=curated.raw_tables,
    )
    entry = matrix.entries[0]
    assert entry.inferred_type == "text"


def test_exporter_propagates_column_confirmation_matrix_to_metadata() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    # Manually build matrix via curator
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    assert "column_confirmation_matrix" in evidence.metadata
    assert evidence.metadata["column_confirmation_matrix"] is not None
    assert "entries" in evidence.metadata["column_confirmation_matrix"]


def test_exporter_propagates_owner_questions_to_metadata() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    assert "owner_questions" in evidence.metadata
    assert isinstance(evidence.metadata["owner_questions"], list)


def test_exporter_sets_calculation_blocked_when_pending_columns() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    assert evidence.metadata["calculation_blocked"] is True


def test_exporter_blocks_ventas_total_when_columns_not_confirmed() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    # ventas_total should NOT be computed because columns are not confirmed
    assert "ventas_total" not in evidence.computed_variables


def test_exporter_blocks_margen_bruto_when_columns_not_confirmed() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta", "CostoUnitario"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0, "CostoUnitario": 50.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    assert "margen_bruto" not in evidence.computed_variables


def test_exporter_emits_column_confirmation_pending_warning() -> None:
    curated = _build_curated(
        columns=["Cantidad", "PrecioVenta"],
        records=[{"Cantidad": 10, "PrecioVenta": 100.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    warnings = evidence.metadata["evidence_warnings"]
    blocking_warnings = [w for w in warnings if w["reason_code"] == "COLUMN_CONFIRMATION_PENDING"]
    assert len(blocking_warnings) >= 1
    assert any("ventas_total" in w["source_field"] for w in blocking_warnings)


def test_exporter_metodopago_not_used_as_monto() -> None:
    curated = _build_curated(
        columns=["MetodoPago", "VentaTotal"],
        records=[{"MetodoPago": "Efectivo", "VentaTotal": 1000.0}],
    )
    from tools.document_ingestion import DocumentCurator
    curator = DocumentCurator()
    import dataclasses
    curated = dataclasses.replace(
        curated,
        report=curator.build_report(
            file_name="test.xlsx",
            raw_tables=curated.raw_tables,
            normalized_tables=curated.normalized_tables,
        )
    )
    evidence = StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")

    # MetodoPago should be classified as unknown/informational, not as pago
    matrix_data = evidence.metadata["column_confirmation_matrix"]
    metodo_entry = next(
        e for e in matrix_data["entries"] if e["original_column_name"] == "MetodoPago"
    )
    assert metodo_entry["suggested_semantic_role"] == "unknown"
    assert metodo_entry["calculation_relevance"] == "INFORMATIONAL"
