from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

import pytest

from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import read_xlsx_to_normalized_tables_v1

from pymia.smartpyme.service_1_canonical_ingestion_to_region_evidence_adapter_v1 import (
    build_service_1_region_evidence_from_canonical_ingestion_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def packet():
    table = {
        "sheet_name": "Ventas", "headers": ["Cantidad", "Precio", "Total", "Cliente"],
        "normalized_headers": ["cantidad", "precio", "total", "cliente"],
        "rows": [
            {"cantidad": "2", "precio": "10", "total": "20", "cliente": "A"},
            {"cantidad": "3", "precio": "5", "total": "15", "cliente": "B"},
            {"cantidad": "", "precio": "7", "total": "7", "cliente": "B"},
        ],
        "row_count": 3, "column_count": 4, "header_row_number": 1, "source_row_numbers": [2, 3, 4],
    }
    return {
        "schema_version": "X", "status": "INGESTION_OUTPUT_READY", "case_id": "C1",
        "filename": "ventas.xlsx", "runtime_authorized": False, "product_ready": False,
        "delivery_authorized": False,
        "ingestion_output": {
            "case_id": "C1", "source_file_ref": "ventas.xlsx", "normalized_tables": [table]
        },
    }


def test_adapter_builds_column_and_relational_evidence_without_parsing_xlsx():
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet(),
        identity_specs=[{
            "evidence_ref": "QPT", "evidence_kind": "MULTIPLICATION_EQUALS",
            "input_column_refs": ["cantidad", "precio"], "target_column_ref": "total",
            "tolerance": 0.01, "minimum_coverage": 0.6,
        }],
    )
    assert result["status"] == "REGION_EVIDENCE_READY"
    assert len(result["regions"]) == 1
    assert len(result["column_evidence"]) == 4
    relation = result["relational_evidence"][0]
    assert relation["rows_evaluated"] == 2
    assert relation["rows_matching"] == 2
    assert relation["evaluation_coverage_ratio"] == 2 / 3
    assert relation["match_ratio"] == 1.0
    assert relation["result"] == "INSUFFICIENT_EVIDENCE"
    assert result["temporary_adapter"] is True


def test_adapter_supports_two_regions_in_one_sheet():
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet(),
        region_specs=[
            {"sheet_ref": "Ventas", "region_ref": "R1", "column_refs": ["cantidad", "precio", "total"]},
            {"sheet_ref": "Ventas", "region_ref": "R2", "column_refs": ["cliente"]},
        ],
    )
    assert result["status"] == "REGION_EVIDENCE_READY"
    assert [r["region_ref"] for r in result["regions"]] == ["R1", "R2"]


def test_adapter_blocks_discontiguous_columns_and_forbidden_flags():
    blocked = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet(),
        region_specs=[{"sheet_ref": "Ventas", "column_refs": ["cantidad", "total"]}],
    )
    assert blocked["status"] == "BLOCKED"
    assert blocked["blocked_reason"] == "DISCONTIGUOUS_REGION_COLUMNS"
    blocked = build_service_1_region_evidence_from_canonical_ingestion_v1(canonical_packet=packet(), runtime_authorized=True)
    assert blocked["blocked_reason"] == "REQUEST_SAFETY_FLAGS_FORBIDDEN"


def test_real_xlsx_canonical_output_feeds_region_evidence_adapter():
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root.parent / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
        repo_root / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
    ]
    fixture = next((path for path in candidates if path.exists()), None)
    if fixture is None:
        pytest.skip("real CASE_001 XLSX fixture not available")
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(local_xlsx_path=str(fixture))
    assert intake["status"] == "NEEDS_OWNER_CONFIRMATION"
    answers = {column: f"meaning of {column}" for column in intake["columns"]}
    canonical = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=intake,
        owner_answers=answers,
    )
    assert canonical["status"] == "INGESTION_OUTPUT_READY"
    assert canonical["ingestion_output"]["normalized_tables"]
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(canonical_packet=canonical)
    assert result["status"] == "REGION_EVIDENCE_READY"
    assert result["regions"]
    assert all(item["provenance"]["source"] for item in result["regions"])


def test_adapter_blocks_identity_columns_outside_region():
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet(),
        region_specs=[{"sheet_ref": "Ventas", "region_ref": "R1", "column_refs": ["cantidad", "precio"]}],
        identity_specs=[{"region_ref": "R1", "input_column_refs": ["cantidad", "precio"], "target_column_ref": "total"}],
    )
    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "INVALID_IDENTITY_COLUMNS"


def test_adapter_uses_explicit_source_row_numbers_for_provenance():
    value = packet()
    table = value["ingestion_output"]["normalized_tables"][0]
    table["header_row_number"] = 2
    table["source_row_numbers"] = [3, 5, 6]
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(canonical_packet=value)
    assert result["status"] == "REGION_EVIDENCE_READY"
    assert result["regions"][0]["header_rows"] == (2,)
    assert result["column_evidence"][0]["provenance"]["source_row_numbers"] == [3, 5, 6]


def test_sparse_evaluable_rows_do_not_become_supported():
    value = packet()
    rows = value["ingestion_output"]["normalized_tables"][0]["rows"]
    rows.extend([{"cantidad": "", "precio": "", "total": "", "cliente": "X"} for _ in range(7)])
    value["ingestion_output"]["normalized_tables"][0]["source_row_numbers"] = list(range(2, 12))
    relation = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=value,
        identity_specs=[{"input_column_refs": ["cantidad", "precio"], "target_column_ref": "total", "minimum_evaluation_coverage": 0.8, "minimum_match_ratio": 0.8}],
    )["relational_evidence"][0]
    assert relation["evaluation_coverage_ratio"] == 0.2
    assert relation["match_ratio"] == 1.0
    assert relation["result"] == "INSUFFICIENT_EVIDENCE"


def test_xlsx_parser_preserves_real_header_and_sparse_source_rows(tmp_path):
    path = tmp_path / "sparse.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append([None, None])
    ws.append(["Cantidad", "Total"])
    ws.append(["2", "20"])
    ws.append([None, None])
    ws.append(["3", "30"])
    wb.save(path)
    wb.close()
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    assert table["header_row_number"] == 2
    assert table["source_row_numbers"] == [3, 5]
