from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import classify_file_intake


def test_supported_xlsx_becomes_received_evidence_but_requires_column_confirmation() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_001",
        source_channel="upload",
        asset={
            "asset_id": "asset_001",
            "filename": "caja_diaria.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 18422,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["service_name"] == "SERVICE_1"
    assert patch["input_assets"] == [
        {
            "asset_id": "asset_001",
            "file_intake_id": "file_intake_001",
            "filename": "caja_diaria.xlsx",
            "detected_file_type": "xlsx",
            "support_status": "SUPPORTED",
            "reason_code": "SUPPORTED_XLSX_V1",
            "risk_flags": ["requires_column_confirmation"],
        }
    ]
    assert patch["evidence_received"][0]["evidence_status"] == "RECEIVED_SUPPORTED"
    assert patch["missing_evidence"] == []
    assert patch["blocking_state"] == "BLOCKED_COLUMN_CONFIRMATION"
    assert patch["next_allowed_action"] == "ask_owner_to_confirm_columns_after_curation"
    assert patch["column_confirmation_required"] is True
    assert patch["runtime_authorized"] is False


def test_csv_becomes_rejected_unsupported_and_requests_xlsx() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_csv",
        asset={
            "asset_id": "asset_csv",
            "filename": "ventas.csv",
            "declared_mime_type": "text/csv",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["input_assets"][0]["detected_file_type"] == "csv"
    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNSUPPORTED"
    assert patch["missing_evidence"] == ["xlsx_file"]
    assert patch["blocking_state"] == "BLOCKED_UNSUPPORTED_FILE_TYPE"
    assert patch["next_allowed_action"] == "ask_owner_to_upload_xlsx"
    assert patch["column_confirmation_required"] is False
    assert patch["runtime_authorized"] is False


def test_pdf_becomes_rejected_unsupported_and_does_not_require_confirmation() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_pdf",
        asset={
            "asset_id": "asset_pdf",
            "filename": "extracto.pdf",
            "declared_mime_type": "application/pdf",
            "size_bytes": 200,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNSUPPORTED"
    assert patch["blocking_state"] == "BLOCKED_UNSUPPORTED_FILE_TYPE"
    assert patch["column_confirmation_required"] is False
    assert patch["runtime_authorized"] is False


def test_unknown_file_type_maps_to_unknown_blocking_state() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_unknown",
        asset={
            "asset_id": "asset_unknown",
            "filename": "archivo.bin",
            "declared_mime_type": "application/octet-stream",
            "size_bytes": 200,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNKNOWN"
    assert patch["missing_evidence"] == ["xlsx_file"]
    assert patch["blocking_state"] == "BLOCKED_UNKNOWN_FILE_TYPE"
    assert patch["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert patch["runtime_authorized"] is False


def test_empty_xlsx_maps_to_unsafe_file_blocking_state() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_empty",
        asset={
            "asset_id": "asset_empty",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 0,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["input_assets"][0]["detected_file_type"] == "xlsx"
    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNSAFE"
    assert patch["missing_evidence"] == ["valid_xlsx_file"]
    assert patch["blocking_state"] == "BLOCKED_UNSAFE_FILE"
    assert patch["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert patch["runtime_authorized"] is False


def test_mime_extension_mismatch_maps_to_unsafe_file_blocking_state() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_mismatch",
        asset={
            "asset_id": "asset_mismatch",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/pdf",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNSAFE"
    assert patch["input_assets"][0]["reason_code"] == "MIME_EXTENSION_MISMATCH"
    assert patch["blocking_state"] == "BLOCKED_UNSAFE_FILE"
    assert patch["runtime_authorized"] is False


def test_unsafe_filename_maps_to_unsafe_file_blocking_state() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_unsafe",
        asset={
            "asset_id": "asset_unsafe",
            "filename": "../ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    patch = derive_taskspec_patch_from_file_intake(file_intake)

    assert patch["evidence_received"][0]["evidence_status"] == "REJECTED_UNSAFE"
    assert patch["input_assets"][0]["reason_code"] == "UNSAFE_FILENAME"
    assert patch["blocking_state"] == "BLOCKED_UNSAFE_FILE"
    assert patch["runtime_authorized"] is False


def test_boundary_does_not_authorize_runtime_for_any_status() -> None:
    supported = classify_file_intake(
        file_intake_id="file_intake_supported",
        asset={
            "asset_id": "asset_supported",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 100,
            "source": "upload",
        },
    )
    unsupported = classify_file_intake(
        file_intake_id="file_intake_unsupported",
        asset={
            "asset_id": "asset_unsupported",
            "filename": "ventas.csv",
            "declared_mime_type": "text/csv",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert derive_taskspec_patch_from_file_intake(supported)["runtime_authorized"] is False
    assert derive_taskspec_patch_from_file_intake(unsupported)["runtime_authorized"] is False
