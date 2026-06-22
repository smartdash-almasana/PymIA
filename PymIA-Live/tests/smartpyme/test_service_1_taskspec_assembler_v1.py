from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import derive_taskspec_patch_from_file_intake
from pymia.smartpyme.file_intake_v1 import classify_file_intake
from pymia.smartpyme.service_1_taskspec_assembler_v1 import (
    assemble_service_1_taskspec_from_file_intake_patch,
)


def test_supported_xlsx_assembles_taskspec_with_column_confirmation_request() -> None:
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

    task_spec = assemble_service_1_taskspec_from_file_intake_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
        task_id="task_001",
        owner_problem="Necesito revisar esta planilla.",
    )

    assert task_spec["task_id"] == "task_001"
    assert task_spec["service_name"] == "SERVICE_1"
    assert task_spec["service_depth"] == "UNKNOWN"
    assert task_spec["task_type"] == "FILE_INTAKE_XLSX"
    assert task_spec["owner_problem"] == "Necesito revisar esta planilla."
    assert task_spec["source_channel"] == "upload"
    assert task_spec["candidate_capability"] == "file_intake_xlsx"
    assert task_spec["candidate_tool_ref"] is None
    assert task_spec["input_assets"] == patch["input_assets"]
    assert task_spec["evidence_received"] == patch["evidence_received"]
    assert task_spec["evidence_required"] == ["xlsx_file"]
    assert task_spec["missing_evidence"] == []
    assert task_spec["column_confirmation_required"] is True
    assert task_spec["blocking_state"] == "BLOCKED_COLUMN_CONFIRMATION"
    assert task_spec["next_allowed_action"] == "ask_owner_to_confirm_columns_after_curation"
    assert task_spec["expected_output"]["output_type"] == "evidence_request"
    assert task_spec["expected_output"]["technical_annex_expected"] is True
    assert task_spec["runtime_authorized"] is False


def test_csv_assembles_blocked_taskspec_that_requests_xlsx() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_csv",
        source_channel="chat",
        asset={
            "asset_id": "asset_csv",
            "filename": "ventas.csv",
            "declared_mime_type": "text/csv",
            "size_bytes": 100,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    task_spec = assemble_service_1_taskspec_from_file_intake_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
        task_id="task_csv",
    )

    assert task_spec["task_type"] == "FILE_INTAKE_CSV"
    assert task_spec["owner_problem"] == "Revisar el archivo ventas.csv dentro de Servicio 1."
    assert task_spec["candidate_capability"] == "file_intake_csv"
    assert task_spec["evidence_required"] == ["xlsx_file"]
    assert task_spec["missing_evidence"] == ["xlsx_file"]
    assert task_spec["column_confirmation_required"] is False
    assert task_spec["blocking_state"] == "BLOCKED_UNSUPPORTED_FILE_TYPE"
    assert task_spec["next_allowed_action"] == "ask_owner_to_upload_xlsx"
    assert task_spec["expected_output"]["output_type"] == "blocked_notice"
    assert task_spec["runtime_authorized"] is False


def test_unknown_file_type_stays_conservative_and_does_not_infer_capability() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_unknown",
        source_channel="api",
        asset={
            "asset_id": "asset_unknown",
            "filename": "archivo.bin",
            "declared_mime_type": "application/octet-stream",
            "size_bytes": 200,
            "source": "api",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    task_spec = assemble_service_1_taskspec_from_file_intake_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
        task_id="task_unknown",
        owner_requested_output="clasificación inicial",
    )

    assert task_spec["task_type"] == "UNKNOWN"
    assert task_spec["candidate_capability"] is None
    assert task_spec["owner_requested_output"] == "clasificación inicial"
    assert task_spec["missing_evidence"] == ["xlsx_file"]
    assert task_spec["blocking_state"] == "BLOCKED_UNKNOWN_FILE_TYPE"
    assert task_spec["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert task_spec["expected_output"]["output_type"] == "blocked_notice"
    assert task_spec["runtime_authorized"] is False


def test_assembler_notes_preserve_traceability_without_authorizing_runtime() -> None:
    file_intake = classify_file_intake(
        file_intake_id="file_intake_pdf",
        source_channel="upload",
        asset={
            "asset_id": "asset_pdf",
            "filename": "extracto.pdf",
            "declared_mime_type": "application/pdf",
            "size_bytes": 200,
            "source": "upload",
        },
    )
    patch = derive_taskspec_patch_from_file_intake(file_intake)

    task_spec = assemble_service_1_taskspec_from_file_intake_patch(
        file_intake=file_intake,
        taskspec_patch=patch,
        task_id="task_pdf",
    )

    assert task_spec["task_type"] == "FILE_INTAKE_PDF"
    assert "Assembled only from FileIntakeResult and TaskSpecPatch." in task_spec["notes"]
    assert any("V1 acepta sólo XLSX" in note for note in task_spec["notes"])
    assert task_spec["runtime_authorized"] is False
