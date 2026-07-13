"""
SERVICE_1_XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCK_V1

Read-only lock for Servicio 1 XLSX ingestion responsibilities. The runtime
bridge must use the narrow normalized-table reader. Structural inspection may
use the structural reader. Full curation remains delegated through the product
Excel Lab ingestion pipeline. No other smartpyme module should open XLSX files
with load_workbook.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "SERVICE_1_XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCK_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_LOCKED: Final[str] = "XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCKED"
STATUS_BLOCKED_BY_PARALLEL_READER: Final[str] = "XLSX_NORMALIZATION_BLOCKED_BY_PARALLEL_READER"
STATUS_BLOCKED_BY_MISSING_CANONICAL: Final[str] = "XLSX_NORMALIZATION_BLOCKED_BY_MISSING_CANONICAL"

CANONICAL_RUNTIME_TABLE_READER: Final[str] = "service_1_xlsx_to_normalized_table_v1.py"
CANONICAL_STRUCTURAL_READER: Final[str] = "service_1_xlsx_structure_v1.py"
CANONICAL_CURATION_PIPELINE: Final[str] = "excel_lab_ingestion_v1.py"
CANONICAL_DOCUMENT_INGESTION_SHIM: Final[str] = "tools/document_ingestion.py"

_ALLOWED_LOAD_WORKBOOK_FILES: Final[tuple[str, ...]] = (
    CANONICAL_RUNTIME_TABLE_READER,
    CANONICAL_STRUCTURAL_READER,
)


@dataclass(frozen=True)
class Service1XlsxNormalizationSourceOfTruthLockResultV1:
    schema_version: str = SCHEMA_VERSION
    service_name: str = SERVICE_NAME
    lock_status: str = STATUS_BLOCKED_BY_MISSING_CANONICAL
    package_root: str = ""
    canonical_runtime_table_reader: str = CANONICAL_RUNTIME_TABLE_READER
    canonical_structural_reader: str = CANONICAL_STRUCTURAL_READER
    canonical_curation_pipeline: str = CANONICAL_CURATION_PIPELINE
    canonical_document_ingestion_shim: str = CANONICAL_DOCUMENT_INGESTION_SHIM
    allowed_load_workbook_files: tuple[str, ...] = _ALLOWED_LOAD_WORKBOOK_FILES
    detected_load_workbook_files: tuple[str, ...] = ()
    parallel_reader_files: tuple[str, ...] = ()
    runtime_bridge_reader_locked: bool = False
    curation_pipeline_locked: bool = False
    first_aid_uses_normalized_reader: bool = False
    runtime_authorized: bool = False
    delivery_authorized: bool = False
    product_ready: bool = False
    blocking_layer: str | None = None
    blocking_reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


def build_service_1_xlsx_normalization_source_of_truth_lock_v1(
    *,
    package_root: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxNormalizationSourceOfTruthLockResultV1:
    smartpyme_root = Path(package_root) if package_root is not None else Path(__file__).resolve().parent
    pymia_live_root = smartpyme_root.parents[1]
    tools_document_ingestion = pymia_live_root / "tools" / "document_ingestion.py"

    required_files = (
        smartpyme_root / CANONICAL_RUNTIME_TABLE_READER,
        smartpyme_root / CANONICAL_STRUCTURAL_READER,
        smartpyme_root / CANONICAL_CURATION_PIPELINE,
        tools_document_ingestion,
    )
    missing = tuple(str(path.name) for path in required_files if not path.exists())

    _lock_self_name = Path(__file__).name
    detected_load_workbook = tuple(
        path
        for path in _files_containing(smartpyme_root, "load_workbook")
        if path.name != _lock_self_name
    )
    detected_names = tuple(path.name for path in detected_load_workbook)
    parallel_readers = tuple(
        name for name in detected_names if name not in _ALLOWED_LOAD_WORKBOOK_FILES
    )

    runtime_reader_text = _read(smartpyme_root / CANONICAL_RUNTIME_TABLE_READER)
    bridge_contract_text = _read(smartpyme_root / "service_1_xlsx_runtime_bridge_contract_v1.py")
    curation_pipeline_text = _read(smartpyme_root / CANONICAL_CURATION_PIPELINE)
    shim_text = _read(tools_document_ingestion)
    first_aid_text = _read(smartpyme_root / "service_1_first_aid_minimal_v1.py")

    base = Service1XlsxNormalizationSourceOfTruthLockResultV1(
        package_root=str(smartpyme_root),
        detected_load_workbook_files=detected_names,
        parallel_reader_files=parallel_readers,
        runtime_bridge_reader_locked=(
            "read_xlsx_to_normalized_table_v1" in bridge_contract_text
            and "from openpyxl" in runtime_reader_text
            and "load_workbook" in runtime_reader_text
        ),
        curation_pipeline_locked=(
            "excel_lab_ingestion_v1" in shim_text
            and "XlsxCurationPipeline" in curation_pipeline_text
        ),
        first_aid_uses_normalized_reader=(
            "read_xlsx_to_normalized_table_v1" in first_aid_text
            and "openpyxl" not in first_aid_text
        ),
        runtime_authorized=False,
        delivery_authorized=False,
        product_ready=False,
        metadata=dict(metadata or {}),
    )

    if missing:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_MISSING_CANONICAL,
            "canonical_files",
            tuple(f"missing:{name}" for name in missing),
        )

    missing_contracts: list[str] = []
    if not base.runtime_bridge_reader_locked:
        missing_contracts.append("runtime_bridge_reader_not_locked")
    if not base.curation_pipeline_locked:
        missing_contracts.append("curation_pipeline_not_locked")
    if not base.first_aid_uses_normalized_reader:
        missing_contracts.append("first_aid_not_using_normalized_reader")
    if missing_contracts:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_MISSING_CANONICAL,
            "canonical_contracts",
            tuple(missing_contracts),
        )

    if parallel_readers:
        return _blocked(
            base,
            STATUS_BLOCKED_BY_PARALLEL_READER,
            "parallel_xlsx_reader",
            tuple(f"parallel_reader:{name}" for name in parallel_readers),
        )

    return Service1XlsxNormalizationSourceOfTruthLockResultV1(
        **{
            **base.__dict__,
            "lock_status": STATUS_LOCKED,
            "blocking_layer": None,
            "blocking_reasons": (),
            "runtime_authorized": False,
            "delivery_authorized": False,
            "product_ready": False,
            "metadata": {"rule": "xlsx_source_of_truth_locked", **dict(metadata or {})},
        }
    )


def _blocked(
    base: Service1XlsxNormalizationSourceOfTruthLockResultV1,
    status: str,
    layer: str,
    reasons: tuple[str, ...],
) -> Service1XlsxNormalizationSourceOfTruthLockResultV1:
    return Service1XlsxNormalizationSourceOfTruthLockResultV1(
        **{
            **base.__dict__,
            "lock_status": status,
            "runtime_authorized": False,
            "delivery_authorized": False,
            "product_ready": False,
            "blocking_layer": layer,
            "blocking_reasons": reasons,
            "metadata": {"rule": reasons[0] if reasons else "blocked", **base.metadata},
        }
    )


def _files_containing(root: Path, pattern: str) -> tuple[Path, ...]:
    return tuple(
        path
        for path in sorted(root.glob("*.py"))
        if pattern in _read(path)
    )


def _read(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_LOCKED",
    "STATUS_BLOCKED_BY_PARALLEL_READER",
    "STATUS_BLOCKED_BY_MISSING_CANONICAL",
    "CANONICAL_RUNTIME_TABLE_READER",
    "CANONICAL_STRUCTURAL_READER",
    "CANONICAL_CURATION_PIPELINE",
    "CANONICAL_DOCUMENT_INGESTION_SHIM",
    "Service1XlsxNormalizationSourceOfTruthLockResultV1",
    "build_service_1_xlsx_normalization_source_of_truth_lock_v1",
]
