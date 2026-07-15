from __future__ import annotations

import inspect
from pathlib import Path

from pymia.smartpyme import service_1_web_column_confirmation_intake_boundary_v1 as intake
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    BLOCK_DUPLICATE_COLUMNS,
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_xlsx_structure_extraction_to_adapter_chain_v1 import (
    build_service_1_xlsx_structure_extraction_to_adapter_chain_v1,
)


def _multisheet_structure(*, include_samples: bool) -> dict:
    ventas = {
        "name": "Ventas",
        "headers": ["fecha", "importe", "canal"],
    }
    cobros = {
        "name": "Cobros",
        "headers": ["fecha", "importe", "medio_pago"],
    }
    if include_samples:
        ventas["sample_rows"] = [
            ["2026-07-01", 1000, "Mostrador"],
            ["2026-07-02", 1500, "Online"],
        ]
        cobros["sample_rows"] = [
            ["2026-07-03", 800, "Transferencia"],
            ["2026-07-04", 700, "Efectivo"],
        ]
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "source_path_basename": "multisheet.xlsx",
        "workbook": {
            "sheet_count": 2,
            "sheets": [ventas, cobros],
        },
        "warnings": [],
        "runtime_authorized": False,
    }


def test_canonical_intake_has_no_sheet_selection_parameter() -> None:
    parameters = inspect.signature(
        intake.build_service_1_web_column_confirmation_intake_boundary_v1
    ).parameters

    assert "sheet_name" not in parameters
    assert "sheet_names" not in parameters


def test_canonical_owner_question_identity_is_not_sheet_qualified(
    tmp_path: Path,
    monkeypatch,
) -> None:
    xlsx = tmp_path / "multisheet.xlsx"
    xlsx.write_bytes(b"not-read-because-reader-is-patched")
    monkeypatch.setattr(
        intake,
        "read_xlsx_to_normalized_table_v1",
        lambda _: {
            "status": "OK",
            "sheet_name": "Ventas",
            "headers": ["fecha", "importe"],
            "normalized_headers": ["fecha", "importe"],
            "rows": [],
            "warnings": [],
            "blocking_errors": [],
        },
    )

    packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx
    )

    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert packet["normalized_table"]["sheet_name"] == "Ventas"
    assert all("sheet_name" not in question for question in packet["owner_questions"])
    assert [question["column_name"] for question in packet["owner_questions"]] == [
        "fecha",
        "importe",
    ]


def test_canonical_owner_connector_blocks_duplicate_unqualified_headers() -> None:
    owner_question_packet = {
        "schema_version": intake.SCHEMA_VERSION,
        "service_name": "SERVICE_1",
        "packet_type": intake.PACKET_TYPE,
        "status": "NEEDS_OWNER_CONFIRMATION",
        "blocked_reason": None,
        "case_id": "case_multisheet_duplicate",
        "source_kind": "local_path",
        "filename": "multisheet.xlsx",
        "columns": ["fecha", "fecha"],
        "question_count": 2,
        "owner_questions": [
            {"column_name": "fecha", "question_id": "col_confirm_001"},
            {"column_name": "fecha", "question_id": "col_confirm_002"},
        ],
        "normalized_table": {
            "status": "OK",
            "sheet_name": "Ventas",
            "headers": ["fecha", "fecha"],
            "rows": [],
        },
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }

    result = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=owner_question_packet,
        owner_answers={"fecha": "fecha de la operación"},
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_DUPLICATE_COLUMNS
    assert result["ingestion_output"] is None


def test_preserved_path_keeps_same_header_distinct_per_sheet() -> None:
    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=_multisheet_structure(include_samples=True)
    )
    entries = result.column_confirmation_result.matrix.entries

    fecha_entries = [entry for entry in entries if entry.original_column_name == "fecha"]
    importe_entries = [
        entry for entry in entries if entry.original_column_name == "importe"
    ]

    assert len(entries) == 6
    assert {(entry.sheet_name, entry.original_column_name) for entry in entries} == {
        ("Ventas", "fecha"),
        ("Ventas", "importe"),
        ("Ventas", "canal"),
        ("Cobros", "fecha"),
        ("Cobros", "importe"),
        ("Cobros", "medio_pago"),
    }
    assert {entry.sheet_name for entry in fecha_entries} == {"Ventas", "Cobros"}
    assert {entry.sheet_name for entry in importe_entries} == {"Ventas", "Cobros"}
    assert all(entry.sample_values for entry in entries)


def test_real_structure_shape_leaves_multisheet_samples_and_types_empty() -> None:
    result = build_service_1_xlsx_structure_extraction_to_adapter_chain_v1(
        extracted_structure=_multisheet_structure(include_samples=False)
    )
    entries = result.column_confirmation_result.matrix.entries

    assert len(entries) == 6
    assert all(entry.sample_values == [] for entry in entries)
    assert all(entry.inferred_type == "empty" for entry in entries)
    assert result.runtime_authorized is False
    assert result.tool_execution_authorized is False
    assert result.delivery_authorized is False
