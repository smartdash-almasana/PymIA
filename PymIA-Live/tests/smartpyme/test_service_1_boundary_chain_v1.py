from __future__ import annotations

from pymia.smartpyme.file_intake_v1 import classify_file_intake
from pymia.smartpyme.service_1_boundary_chain_v1 import (
    FREEZE_REASON,
    FREEZE_STATUS,
    derive_service_1_boundary_chain_from_file_intake,
)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_boundary_chain_module_is_explicitly_frozen() -> None:
    assert FREEZE_STATUS == "EXPERIMENTAL_FROZEN"
    assert "do not expand before Service 1 product boundary" in FREEZE_REASON


def test_boundary_chain_supported_xlsx_stops_at_column_confirmation() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_xlsx",
        asset={
            "asset_id": "asset_xlsx",
            "filename": "ventas.xlsx",
            "declared_mime_type": XLSX_MIME,
            "size_bytes": 1024,
            "source": "upload",
        },
        source_channel="upload",
    )

    chain = derive_service_1_boundary_chain_from_file_intake(
        task_id="task_xlsx",
        owner_problem="Necesito revisar una planilla de ventas.",
        file_intake=file_intake,
    )

    task_spec = chain["task_spec"]
    decision = chain["fsm_decision_patch"]

    assert chain["service_name"] == "SERVICE_1"
    assert task_spec["service_name"] == "SERVICE_1"
    assert task_spec["input_assets"][0]["asset_id"] == "asset_xlsx"
    assert task_spec["evidence_received"][0]["evidence_status"] == "RECEIVED_SUPPORTED"
    assert task_spec["column_confirmation_required"] is True
    assert task_spec["runtime_authorized"] is False
    assert decision["next_state"] == "CONFIRMATION_REQUIRED"
    assert decision["decision_reason"] == "COLUMN_CONFIRMATION_REQUIRED"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_boundary_chain_unsupported_pdf_requests_xlsx_without_runtime() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_pdf",
        asset={
            "asset_id": "asset_pdf",
            "filename": "extracto.pdf",
            "declared_mime_type": "application/pdf",
            "size_bytes": 2048,
            "source": "upload",
        },
        source_channel="upload",
    )

    chain = derive_service_1_boundary_chain_from_file_intake(
        task_id="task_pdf",
        owner_problem="Necesito convertir un PDF a datos operativos.",
        file_intake=file_intake,
    )

    task_spec = chain["task_spec"]
    decision = chain["fsm_decision_patch"]

    assert task_spec["missing_evidence"] == ["xlsx_file"]
    assert task_spec["evidence_received"][0]["evidence_status"] == "REJECTED_UNSUPPORTED"
    assert task_spec["blocking_state"] == "BLOCKED_UNSUPPORTED_FILE_TYPE"
    assert task_spec["next_allowed_action"] == "ask_owner_to_upload_xlsx"
    assert task_spec["runtime_authorized"] is False
    assert decision["next_state"] == "EVIDENCE_REQUESTED"
    assert decision["decision_reason"] == "MISSING_EVIDENCE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False


def test_boundary_chain_unknown_file_requests_clearer_file_without_runtime() -> None:
    file_intake = classify_file_intake(
        file_intake_id="intake_unknown",
        asset={
            "asset_id": "asset_unknown",
            "filename": "archivo.dat",
            "declared_mime_type": None,
            "size_bytes": 512,
            "source": "upload",
        },
        source_channel="upload",
    )

    chain = derive_service_1_boundary_chain_from_file_intake(
        task_id="task_unknown",
        owner_problem="No sé qué archivo subí.",
        file_intake=file_intake,
    )

    task_spec = chain["task_spec"]
    decision = chain["fsm_decision_patch"]

    assert task_spec["missing_evidence"] == ["xlsx_file"]
    assert task_spec["evidence_received"][0]["evidence_status"] == "REJECTED_UNKNOWN"
    assert task_spec["blocking_state"] == "BLOCKED_UNKNOWN_FILE_TYPE"
    assert task_spec["next_allowed_action"] == "ask_owner_for_clearer_file"
    assert task_spec["runtime_authorized"] is False
    assert decision["next_state"] == "EVIDENCE_REQUESTED"
    assert decision["decision_reason"] == "MISSING_EVIDENCE"
    assert decision["runtime_authorized"] is False
    assert decision["allowed_to_process"] is False
