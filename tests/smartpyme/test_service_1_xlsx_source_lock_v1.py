"""Focal tests for SERVICE_1_XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCK_V1."""
from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_xlsx_normalization_source_of_truth_lock_v1 import (
    CANONICAL_CURATION_PIPELINE,
    CANONICAL_DOCUMENT_INGESTION_SHIM,
    CANONICAL_RUNTIME_TABLE_READER,
    CANONICAL_STRUCTURAL_READER,
    STATUS_LOCKED,
    build_service_1_xlsx_normalization_source_of_truth_lock_v1,
)


def _live_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _smartpyme_root() -> Path:
    return _live_root() / "pymia" / "smartpyme"


def test_xlsx_normalization_source_of_truth_is_locked() -> None:
    result = build_service_1_xlsx_normalization_source_of_truth_lock_v1()

    assert result.lock_status == STATUS_LOCKED
    assert result.canonical_runtime_table_reader == CANONICAL_RUNTIME_TABLE_READER
    assert result.canonical_structural_reader == CANONICAL_STRUCTURAL_READER
    assert result.canonical_curation_pipeline == CANONICAL_CURATION_PIPELINE
    assert result.canonical_document_ingestion_shim == CANONICAL_DOCUMENT_INGESTION_SHIM
    assert result.runtime_bridge_reader_locked is True
    assert result.curation_pipeline_locked is True
    assert result.first_aid_uses_normalized_reader is True
    assert result.parallel_reader_files == ()
    assert result.runtime_authorized is False
    assert result.delivery_authorized is False
    assert result.product_ready is False


def test_only_sanctioned_smartpyme_modules_open_xlsx_workbooks() -> None:
    result = build_service_1_xlsx_normalization_source_of_truth_lock_v1()

    assert set(result.detected_load_workbook_files) == {
        CANONICAL_RUNTIME_TABLE_READER,
        CANONICAL_STRUCTURAL_READER,
    }
    assert set(result.allowed_load_workbook_files) == {
        CANONICAL_RUNTIME_TABLE_READER,
        CANONICAL_STRUCTURAL_READER,
    }


def test_first_aid_minimal_uses_normalized_reader_not_openpyxl() -> None:
    source = (_smartpyme_root() / "service_1_first_aid_minimal_v1.py").read_text(encoding="utf-8")

    assert "read_xlsx_to_normalized_table_v1" in source
    assert "openpyxl" not in source
    assert "load_workbook" not in source


def test_runtime_bridge_contract_uses_normalized_table_reader() -> None:
    source = (_smartpyme_root() / "service_1_xlsx_runtime_bridge_contract_v1.py").read_text(encoding="utf-8")

    assert "read_xlsx_to_normalized_table_v1" in source
    assert "load_workbook" not in source
    assert "openpyxl" not in source


def test_document_ingestion_shim_delegates_to_excel_lab_ingestion() -> None:
    shim = (_live_root() / "tools" / "document_ingestion.py").read_text(encoding="utf-8")
    curation = (_smartpyme_root() / CANONICAL_CURATION_PIPELINE).read_text(encoding="utf-8")

    assert "pymia.smartpyme.excel_lab_ingestion_v1" in shim
    assert "XlsxCurationPipeline" in curation


def test_lock_module_has_no_runtime_cli_or_delivery_paths() -> None:
    source = (_smartpyme_root() / "service_1_xlsx_normalization_source_of_truth_lock_v1.py").read_text(encoding="utf-8")
    forbidden = [
        "pymia.cli",
        "runtime_authorized=True",
        '"runtime_authorized": True',
        "delivery_authorized=True",
        "product_ready=True",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in source
