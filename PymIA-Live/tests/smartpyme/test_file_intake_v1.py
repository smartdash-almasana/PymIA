from __future__ import annotations

from pymia.smartpyme.file_intake_v1 import (
    REASON_EMPTY_FILE,
    REASON_MIME_EXTENSION_MISMATCH,
    REASON_SUPPORTED_XLSX_V1,
    REASON_UNSAFE_FILENAME,
    REASON_UNKNOWN_FILE_TYPE,
    REASON_UNSUPPORTED_CSV_V1,
    REASON_UNSUPPORTED_IMAGE_V1,
    REASON_UNSUPPORTED_PDF_V1,
    REASON_UNSUPPORTED_ZIP_V1,
    classify_file_intake,
)


def test_xlsx_is_supported_and_routed_to_document_ingestion() -> None:
    result = classify_file_intake(
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

    assert result["schema_version"] == "1.0"
    assert result["service_name"] == "SERVICE_1"
    assert result["asset"]["detected_file_type"] == "xlsx"
    assert result["support"]["status"] == "SUPPORTED"
    assert result["support"]["reason_code"] == REASON_SUPPORTED_XLSX_V1
    assert result["routing"]["candidate_intake_engine"] == "document_ingestion_xlsx"
    assert result["routing"]["next_allowed_action"] == "send_to_xlsx_document_ingestion"
    assert result["curation_required"] is True
    assert result["column_confirmation_expected"] is True
    assert result["blocks_runtime"] is True
    assert "requires_column_confirmation" in result["risk_flags"]


def test_xlsm_is_supported_as_excel_but_still_blocks_runtime() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_xlsm",
        asset={
            "asset_id": "asset_xlsm",
            "filename": "ventas.xlsm",
            "declared_mime_type": "application/vnd.ms-excel.sheet.macroenabled.12",
            "size_bytes": 9000,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "xlsx"
    assert result["support"]["status"] == "SUPPORTED"
    assert result["blocks_runtime"] is True


def test_csv_is_unsupported_in_v1() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_csv",
        asset={
            "asset_id": "asset_csv",
            "filename": "ventas.csv",
            "declared_mime_type": "text/csv",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "csv"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_UNSUPPORTED_CSV_V1
    assert result["routing"]["candidate_intake_engine"] == "none"
    assert result["routing"]["next_allowed_action"] == "ask_owner_to_upload_xlsx"
    assert result["curation_required"] is False
    assert result["column_confirmation_expected"] is False
    assert result["blocks_runtime"] is True
    assert "unsupported_format" in result["risk_flags"]


def test_pdf_is_unsupported_in_v1() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_pdf",
        asset={
            "asset_id": "asset_pdf",
            "filename": "extracto_banco.pdf",
            "declared_mime_type": "application/pdf",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "pdf"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_UNSUPPORTED_PDF_V1
    assert result["routing"]["next_allowed_action"] == "ask_owner_to_upload_xlsx"


def test_zip_is_unsupported_in_v1() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_zip",
        asset={
            "asset_id": "asset_zip",
            "filename": "archivos.zip",
            "declared_mime_type": "application/zip",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "zip"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_UNSUPPORTED_ZIP_V1
    assert result["routing"]["next_allowed_action"] == "ask_owner_to_upload_xlsx"


def test_image_is_unsupported_in_v1() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_image",
        asset={
            "asset_id": "asset_image",
            "filename": "ticket.jpg",
            "declared_mime_type": "image/jpeg",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "image"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_UNSUPPORTED_IMAGE_V1
    assert result["routing"]["next_allowed_action"] == "ask_owner_to_upload_xlsx"


def test_unknown_file_type_is_unknown_and_asks_for_clearer_file() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_unknown",
        asset={
            "asset_id": "asset_unknown",
            "filename": "archivo.bin",
            "declared_mime_type": "application/octet-stream",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "unknown"
    assert result["support"]["status"] == "UNKNOWN"
    assert result["support"]["reason_code"] == REASON_UNKNOWN_FILE_TYPE
    assert result["routing"]["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert "ambiguous_file_type" in result["risk_flags"]


def test_detects_file_type_from_mime_when_filename_is_missing() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_mime_only",
        asset={
            "asset_id": "asset_mime_only",
            "filename": None,
            "declared_mime_type": "application/pdf",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "pdf"
    assert result["support"]["reason_code"] == REASON_UNSUPPORTED_PDF_V1


def test_empty_file_blocks_before_supported_routing() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_empty",
        asset={
            "asset_id": "asset_empty",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 0,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "xlsx"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_EMPTY_FILE
    assert result["routing"]["candidate_intake_engine"] == "none"
    assert result["routing"]["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert "empty_file" in result["risk_flags"]


def test_mime_extension_mismatch_blocks_routing() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_mismatch",
        asset={
            "asset_id": "asset_mismatch",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/pdf",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "xlsx"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_MIME_EXTENSION_MISMATCH
    assert result["routing"]["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert "mime_extension_mismatch" in result["risk_flags"]


def test_unsafe_filename_blocks_routing() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_unsafe",
        asset={
            "asset_id": "asset_unsafe",
            "filename": "../ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["asset"]["detected_file_type"] == "xlsx"
    assert result["support"]["status"] == "UNSUPPORTED_IN_V1"
    assert result["support"]["reason_code"] == REASON_UNSAFE_FILENAME
    assert result["routing"]["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert "unsafe_filename" in result["risk_flags"]


def test_result_does_not_authorize_runtime_even_when_supported() -> None:
    result = classify_file_intake(
        file_intake_id="file_intake_runtime_guard",
        asset={
            "asset_id": "asset_runtime_guard",
            "filename": "ventas.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 100,
            "source": "upload",
        },
    )

    assert result["support"]["status"] == "SUPPORTED"
    assert result["routing"]["next_allowed_action"] == "send_to_xlsx_document_ingestion"
    assert result["blocks_runtime"] is True
    assert result["notes"] == ["No calcular hasta completar curación y confirmación de columnas."]
