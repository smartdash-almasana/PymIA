from __future__ import annotations

from typing import Any, TypedDict

from pymia.smartpyme.file_intake_v1 import FileIntakeResult
from pymia.smartpyme.service_1_taskspec_vocabulary_v1 import (
    EvidenceAssetStatus,
    TaskSpecBlockingState,
    TaskSpecNextAllowedAction,
)


class TaskSpecAssetRef(TypedDict):
    asset_id: str
    file_intake_id: str
    filename: str | None
    detected_file_type: str
    support_status: str
    reason_code: str
    risk_flags: list[str]


class TaskSpecEvidenceRef(TaskSpecAssetRef):
    evidence_status: EvidenceAssetStatus


class TaskSpecPatch(TypedDict):
    service_name: str
    input_assets: list[TaskSpecAssetRef]
    evidence_received: list[TaskSpecEvidenceRef]
    missing_evidence: list[str]
    blocking_state: TaskSpecBlockingState
    next_allowed_action: TaskSpecNextAllowedAction
    column_confirmation_required: bool
    column_confirmation_fields: list[str]
    runtime_authorized: bool
    notes: list[str]


_UNSAFE_REASON_CODES = {
    "EMPTY_FILE",
    "MIME_EXTENSION_MISMATCH",
    "UNSAFE_FILENAME",
}


def derive_taskspec_patch_from_file_intake(file_intake: FileIntakeResult) -> TaskSpecPatch:
    """Derive a minimal TaskSpec patch from a FileIntakeResult.

    This boundary is pure and intentionally narrow. It does not create a full TaskSpec,
    persist state, call document ingestion, call LLMs, run pipeline, or authorize runtime.
    """
    asset_ref = _asset_ref(file_intake)
    support_status = file_intake["support"]["status"]
    reason_code = file_intake["support"]["reason_code"]

    if support_status == "SUPPORTED":
        return {
            "service_name": "SERVICE_1",
            "input_assets": [asset_ref],
            "evidence_received": [{**asset_ref, "evidence_status": "RECEIVED_SUPPORTED"}],
            "missing_evidence": [],
            "blocking_state": "BLOCKED_COLUMN_CONFIRMATION",
            "next_allowed_action": "ask_owner_to_confirm_columns_after_curation",
            "column_confirmation_required": True,
            "column_confirmation_fields": [],
            "runtime_authorized": False,
            "notes": [
                "Archivo XLSX aceptado como evidencia inicial.",
                "No calcular hasta completar curación y confirmación de columnas.",
            ],
        }

    if support_status == "UNKNOWN":
        return {
            "service_name": "SERVICE_1",
            "input_assets": [asset_ref],
            "evidence_received": [{**asset_ref, "evidence_status": "REJECTED_UNKNOWN"}],
            "missing_evidence": ["xlsx_file"],
            "blocking_state": "BLOCKED_UNKNOWN_FILE_TYPE",
            "next_allowed_action": "ask_owner_for_clearer_file",
            "column_confirmation_required": False,
            "column_confirmation_fields": [],
            "runtime_authorized": False,
            "notes": ["Tipo de archivo no identificado. V1 acepta sólo XLSX."],
        }

    if reason_code in _UNSAFE_REASON_CODES:
        return {
            "service_name": "SERVICE_1",
            "input_assets": [asset_ref],
            "evidence_received": [{**asset_ref, "evidence_status": "REJECTED_UNSAFE"}],
            "missing_evidence": ["valid_xlsx_file"],
            "blocking_state": "BLOCKED_UNSAFE_FILE",
            "next_allowed_action": "ask_owner_for_clearer_file",
            "column_confirmation_required": False,
            "column_confirmation_fields": [],
            "runtime_authorized": False,
            "notes": ["Archivo rechazado antes de curación por riesgo o inconsistencia inicial."],
        }

    return {
        "service_name": "SERVICE_1",
        "input_assets": [asset_ref],
        "evidence_received": [{**asset_ref, "evidence_status": "REJECTED_UNSUPPORTED"}],
        "missing_evidence": ["xlsx_file"],
        "blocking_state": "BLOCKED_UNSUPPORTED_FILE_TYPE",
        "next_allowed_action": "ask_owner_to_upload_xlsx",
        "column_confirmation_required": False,
        "column_confirmation_fields": [],
        "runtime_authorized": False,
        "notes": ["Formato fuera de alcance para File Intake V1. V1 acepta sólo XLSX."],
    }


def _asset_ref(file_intake: FileIntakeResult) -> TaskSpecAssetRef:
    asset: dict[str, Any] = file_intake["asset"]
    return {
        "asset_id": str(asset.get("asset_id") or "unknown_asset"),
        "file_intake_id": file_intake["file_intake_id"],
        "filename": asset.get("filename"),
        "detected_file_type": str(asset.get("detected_file_type") or "unknown"),
        "support_status": file_intake["support"]["status"],
        "reason_code": file_intake["support"]["reason_code"],
        "risk_flags": list(file_intake.get("risk_flags", [])),
    }
