from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import classify_file_intake
from pymia.smartpyme.service_1_excel_triage_report_v1 import (
    build_service_1_excel_triage_report_from_taskspec_patch,
)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_supported_xlsx_report_requires_column_confirmation() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_xlsx",
        source_channel="upload",
        asset={
            "asset_id": "asset_xlsx",
            "filename": "ventas.xlsx",
            "declared_mime_type": XLSX_MIME,
            "size_bytes": 1024,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    report = build_service_1_excel_triage_report_from_taskspec_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
    )

    assert report["service_name"] == "SERVICE_1"
    assert report["report_type"] == "EXCEL_TRIAGE_REPORT"
    assert report["support_status"] == "SUPPORTED"
    assert report["column_confirmation_required"] is True
    assert "confirmá las columnas" in report["owner_next_action"]
    assert report["runtime_authorized"] is False


def test_pdf_report_requests_xlsx() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_pdf",
        asset={
            "asset_id": "asset_pdf",
            "filename": "extracto.pdf",
            "declared_mime_type": "application/pdf",
            "size_bytes": 2048,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    report = build_service_1_excel_triage_report_from_taskspec_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
    )

    assert report["detected_file_type"] == "pdf"
    assert report["support_status"] == "UNSUPPORTED_IN_V1"
    assert "enviá el archivo en formato XLSX" in report["owner_next_action"]
    assert report["runtime_authorized"] is False


def test_unknown_file_report_requests_clearer_file() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_unknown",
        asset={
            "asset_id": "asset_unknown",
            "filename": "archivo.bin",
            "declared_mime_type": "application/octet-stream",
            "size_bytes": 100,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    report = build_service_1_excel_triage_report_from_taskspec_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
    )

    assert report["support_status"] == "UNKNOWN"
    assert report["missing_evidence"] == ["xlsx_file"]
    assert "archivo más claro y válido" in report["owner_next_action"]
    assert report["runtime_authorized"] is False


def test_unsafe_file_report_blocks_and_requests_valid_file() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_unsafe",
        asset={
            "asset_id": "asset_unsafe",
            "filename": "../ventas.xlsx",
            "declared_mime_type": XLSX_MIME,
            "size_bytes": 100,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    report = build_service_1_excel_triage_report_from_taskspec_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
    )

    assert report["support_status"] == "UNSUPPORTED_IN_V1"
    assert report["detected_file_type"] == "xlsx"
    assert report["missing_evidence"] == ["valid_xlsx_file"]
    assert "archivo más claro y válido" in report["owner_next_action"]
    assert report["runtime_authorized"] is False


def test_report_runtime_is_always_false() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_runtime_guard",
        asset={
            "asset_id": "asset_runtime_guard",
            "filename": "ventas.csv",
            "declared_mime_type": "text/csv",
            "size_bytes": 100,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    report = build_service_1_excel_triage_report_from_taskspec_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
    )

    assert report["runtime_authorized"] is False
