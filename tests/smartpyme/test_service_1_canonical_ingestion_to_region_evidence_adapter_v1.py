from __future__ import annotations

from pathlib import Path

import pytest

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
        "row_count": 3, "column_count": 4,
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
    assert relation["coverage_ratio"] == 1.0
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
