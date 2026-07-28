"""Guard the XLSX normalization source of truth without a product module."""
from __future__ import annotations

from pathlib import Path

CANONICAL_RUNTIME_TABLE_READER = "service_1_xlsx_to_normalized_table_v1.py"
P10_XLSX_QUALITY_GATE = "service_1_xlsx_quality_gate_v1.py"
CANONICAL_CURATION_PIPELINE = "excel_lab_ingestion_v1.py"
CANONICAL_DOCUMENT_INGESTION_SHIM = "tools/document_ingestion.py"
ALLOWED_LOAD_WORKBOOK_FILES = {
    CANONICAL_RUNTIME_TABLE_READER,
    P10_XLSX_QUALITY_GATE,
}


def _live_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _smartpyme_root() -> Path:
    return _live_root() / "pymia" / "smartpyme"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _detected_load_workbook_files() -> set[str]:
    return {
        path.name
        for path in _smartpyme_root().glob("*.py")
        if "load_workbook" in _read(path)
    }


def test_only_sanctioned_smartpyme_modules_open_xlsx_workbooks() -> None:
    assert _detected_load_workbook_files() == ALLOWED_LOAD_WORKBOOK_FILES


def test_legacy_first_aid_minimal_module_is_removed() -> None:
    assert not (_smartpyme_root() / "service_1_first_aid_minimal_v1.py").exists()


def test_document_ingestion_shim_delegates_to_excel_lab_ingestion() -> None:
    shim = _read(_live_root() / CANONICAL_DOCUMENT_INGESTION_SHIM)
    curation = _read(_smartpyme_root() / CANONICAL_CURATION_PIPELINE)

    assert "pymia.smartpyme.excel_lab_ingestion_v1" in shim
    assert "XlsxCurationPipeline" in curation


def test_xlsx_source_of_truth_guard_is_not_a_product_module() -> None:
    assert not (_smartpyme_root() / "service_1_xlsx_normalization_source_of_truth_lock_v1.py").exists()
