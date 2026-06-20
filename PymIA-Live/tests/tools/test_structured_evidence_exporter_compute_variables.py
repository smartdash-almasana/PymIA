from __future__ import annotations

from typing import Any

from tools.document_ingestion import (
    CuratedDocument,
    DocumentCurationReport,
    NormalizedTable,
    RawTable,
    SemanticFieldMapper,
    StructuredEvidenceExporter,
)


def _export_evidence(record: dict[str, Any]):
    curated = CuratedDocument(
        file_name="sample.xlsx",
        document_type="xlsx_operational_evidence",
        raw_tables=[
            RawTable(
                sheet_name="Ventas",
                header_row=1,
                columns=list(record.keys()),
                records=[record],
                context="ventas",
            )
        ],
        normalized_tables=[
            NormalizedTable(
                sheet_name="Ventas",
                context="ventas",
                header_row=1,
                columns=list(record.keys()),
                mappings=[],
                records=[record],
            )
        ],
        report=DocumentCurationReport(
            file_name="sample.xlsx",
            status="curated",
            tables_count=1,
            rows_count=1,
            mapped_fields={},
        ),
    )
    return StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")


def _export_mapped_evidence(record: dict[str, Any]):
    raw_table = RawTable(
        sheet_name="Ventas",
        header_row=1,
        columns=list(record.keys()),
        records=[record],
        context="ventas",
    )
    normalized_tables = SemanticFieldMapper().normalize_tables([raw_table])
    curated = CuratedDocument(
        file_name="sample.xlsx",
        document_type="xlsx_operational_evidence",
        raw_tables=[raw_table],
        normalized_tables=normalized_tables,
        report=DocumentCurationReport(
            file_name="sample.xlsx",
            status="curated",
            tables_count=1,
            rows_count=1,
            mapped_fields={},
        ),
    )
    return StructuredEvidenceExporter().export(curated=curated, tenant_id="tenant-1")


def test_compute_variables_after_semantic_field_mapper_normalization() -> None:
    evidence = _export_mapped_evidence({"cantidad": "2", "precio_venta": "$ 15,00"})

    assert evidence.computed_variables["ventas_total"] == 30.0
    assert evidence.computed_variables["cantidad_total"] == 2.0


def test_computes_ventas_total_from_cantidad_times_precio_venta() -> None:
    evidence = _export_evidence({"cantidad": 2, "precio_venta": 15})

    assert evidence.computed_variables["ventas_total"] == 30.0
    assert evidence.computed_variables["cantidad_total"] == 2.0
    assert all(isinstance(value, float) for value in evidence.computed_variables.values())


def test_excludes_ambiguous_number_from_computed_variables() -> None:
    evidence = _export_evidence({"venta_total": "12,34,56"})

    assert "ventas_total" not in evidence.computed_variables
    warnings = evidence.metadata["evidence_warnings"]
    assert warnings[0]["source_field"] == "venta_total"
    assert warnings[0]["reason_code"] == "AMBIGUOUS_FORMAT"


def test_zero_real_is_included_as_zero_not_missing() -> None:
    evidence = _export_evidence({"cantidad": 0, "precio_venta": 10, "costo_unitario": 5})

    assert evidence.computed_variables["ventas_total"] == 0.0
    assert evidence.computed_variables["costos_total"] == 0.0
    assert evidence.computed_variables["cantidad_total"] == 0.0
    assert evidence.metadata["evidence_warnings"] == []


def test_missing_field_is_excluded_from_computed_variables() -> None:
    evidence = _export_evidence({"venta_total": None})

    assert "ventas_total" not in evidence.computed_variables
    warnings = evidence.metadata["evidence_warnings"]
    assert warnings[0]["source_field"] == "venta_total"
    assert warnings[0]["reason_code"] == "MISSING_FIELD"


def test_metadata_includes_warnings_for_ambiguous_values() -> None:
    evidence = _export_evidence({"cantidad": 1, "precio_venta": "10.00", "margen": "12,34,56"})

    warnings = evidence.metadata["evidence_warnings"]
    assert warnings == [
        {
            "warning_id": "margen:AMBIGUOUS_FORMAT",
            "severity": "BLOCKING",
            "source_field": "margen",
            "reason_code": "AMBIGUOUS_FORMAT",
            "owner_message": "Este dato es ambiguo y no se usó para calcular.",
            "operator_detail": "field=margen; reason_code=AMBIGUOUS_FORMAT; availability_status=AMBIGUOUS",
            "blocks_calculation": True,
            "suggested_next_evidence": "Aclarar el significado o formato del dato.",
        }
    ]


def test_legacy_to_float_formats_remain_accepted_by_compute_boundary() -> None:
    cases = [
        ("$ 1.200,50", 1200.5),
        ("1.200,50", 1200.5),
        ("1,200.50", 1200.5),
        ("10%", 10.0),
    ]

    for raw_value, expected in cases:
        evidence = _export_evidence({"venta_total": raw_value})

        assert evidence.computed_variables["ventas_total"] == expected
        assert evidence.metadata["evidence_warnings"] == []


def test_semantic_field_mapper_legacy_formats_remain_accepted() -> None:
    """All 6 legacy numeric formats survive SemanticFieldMapper._coerce_semantic_value → export."""
    cases = [
        ("1,200.50", 1200.5),
        ("1.200,50", 1200.5),
        ("$ 1.200,50", 1200.5),
        ("10%", 10.0),
        ("1200,50", 1200.5),
        ("1200.50", 1200.5),
    ]
    for raw_value, expected in cases:
        evidence = _export_mapped_evidence({"venta_total": raw_value})
        assert evidence.computed_variables["ventas_total"] == expected, f"Failed for {raw_value}"
        assert evidence.metadata["evidence_warnings"] == [], f"Unexpected warnings for {raw_value}"


def test_semantic_field_mapper_boundary_values_handled_correctly() -> None:
    """ZERO_REAL preserved, missing/ambiguous excluded via SemanticFieldMapper path."""
    evidence = _export_mapped_evidence({"venta_total": "0"})
    assert evidence.computed_variables["ventas_total"] == 0.0

    evidence = _export_mapped_evidence({"venta_total": None})
    assert "ventas_total" not in evidence.computed_variables

    evidence = _export_mapped_evidence({"venta_total": ""})
    assert "ventas_total" not in evidence.computed_variables

    evidence = _export_mapped_evidence({"venta_total": "nan"})
    assert "ventas_total" not in evidence.computed_variables

    evidence = _export_mapped_evidence({"venta_total": "12,34,56"})
    assert "ventas_total" not in evidence.computed_variables
    # Note: SemanticFieldMapper._coerce_semantic_value drops unparseable strings
    # to None before the normalizer sees them, so no AMBIGUOUS_FORMAT warning
    # is emitted here. This is a known behavior gap compared to the direct path.


def test_semantic_field_mapper_computed_variables_is_dict_str_float() -> None:
    """computed_variables remains dict[str, float] after full SemanticFieldMapper → export."""
    evidence = _export_mapped_evidence({"cantidad": 3, "precio_venta": 25})
    assert isinstance(evidence.computed_variables, dict)
    for k, v in evidence.computed_variables.items():
        assert isinstance(k, str)
        assert isinstance(v, float)


def test_unavailable_number_tokens_are_excluded_from_computed_variables() -> None:
    for raw_value in ("nan", "null", "-"):
        evidence = _export_evidence({"venta_total": raw_value})

        assert "ventas_total" not in evidence.computed_variables
        warnings = evidence.metadata["evidence_warnings"]
        assert warnings[0]["source_field"] == "venta_total"
        assert warnings[0]["blocks_calculation"] is True
