from __future__ import annotations

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import TaskSpecPatch
from pymia.smartpyme.file_intake_v1 import FileIntakeResult
from pymia.smartpyme.service_1_taskspec_contract_v1 import (
    Service1TaskSpec,
    TaskSpecServiceDepth,
)

_SUPPORTED_XLSX_TASK_TYPE = "FILE_INTAKE_XLSX"
_UNSUPPORTED_CSV_TASK_TYPE = "FILE_INTAKE_CSV"
_UNSUPPORTED_PDF_TASK_TYPE = "FILE_INTAKE_PDF"

_FORBIDDEN_CLAIMS = (
    "diagnostico_integral_no_autorizado",
    "calculo_validado_no_autorizado",
    "archivo_normalizado_no_confirmado",
    "runtime_no_autorizado",
)


def assemble_service_1_taskspec_from_file_intake_patch(
    *,
    file_intake: FileIntakeResult,
    taskspec_patch: TaskSpecPatch,
    task_id: str,
    owner_problem: str | None = None,
    owner_requested_output: str | None = None,
    service_depth: TaskSpecServiceDepth = "UNKNOWN",
) -> Service1TaskSpec:
    """Assemble a conservative Service 1 TaskSpec from intake + patch only.

    V1 is intentionally narrow. It does not authorize runtime, infer diagnosis,
    connect pipeline/FSM, execute document ingestion, or choose a First Aid tool.
    """
    support_status = file_intake["support"]["status"]

    return {
        "task_id": task_id,
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "service_depth": service_depth,
        "task_type": _task_type_from_file_intake(file_intake),
        "owner_problem": owner_problem or _default_owner_problem(file_intake),
        "owner_requested_output": owner_requested_output,
        "source_channel": file_intake["source_channel"],
        "input_assets": list(taskspec_patch["input_assets"]),
        "candidate_capability": _candidate_capability_from_file_intake(file_intake),
        "candidate_tool_ref": None,
        "evidence_required": _evidence_required_from_patch(taskspec_patch),
        "evidence_received": list(taskspec_patch["evidence_received"]),
        "missing_evidence": list(taskspec_patch["missing_evidence"]),
        "column_confirmation_required": taskspec_patch["column_confirmation_required"],
        "column_confirmation_fields": list(taskspec_patch["column_confirmation_fields"]),
        "requested_formula_refs": [],
        "requested_claims": [],
        "forbidden_claims": list(_FORBIDDEN_CLAIMS),
        "blocking_state": taskspec_patch["blocking_state"],
        "next_allowed_action": taskspec_patch["next_allowed_action"],
        "expected_output": _expected_output_for_support_status(support_status),
        "runtime_authorized": False,
        "notes": [
            "Assembled only from FileIntakeResult and TaskSpecPatch.",
            *file_intake.get("notes", []),
            *taskspec_patch.get("notes", []),
        ],
    }


def _task_type_from_file_intake(file_intake: FileIntakeResult) -> str:
    detected_file_type = str(file_intake["asset"].get("detected_file_type") or "unknown")
    if detected_file_type == "xlsx":
        return _SUPPORTED_XLSX_TASK_TYPE
    if detected_file_type == "csv":
        return _UNSUPPORTED_CSV_TASK_TYPE
    if detected_file_type == "pdf":
        return _UNSUPPORTED_PDF_TASK_TYPE
    return "UNKNOWN"


def _candidate_capability_from_file_intake(file_intake: FileIntakeResult) -> str | None:
    task_type = _task_type_from_file_intake(file_intake)
    if task_type == "UNKNOWN":
        return None
    return task_type.lower()


def _evidence_required_from_patch(taskspec_patch: TaskSpecPatch) -> list[str]:
    if taskspec_patch["missing_evidence"]:
        return list(taskspec_patch["missing_evidence"])

    if taskspec_patch["column_confirmation_required"]:
        return ["xlsx_file"]

    return []


def _expected_output_for_support_status(support_status: str) -> dict[str, bool | str]:
    if support_status == "SUPPORTED":
        return {
            "output_type": "evidence_request",
            "downloadable_file_expected": False,
            "owner_facing_summary_expected": True,
            "technical_annex_expected": True,
            "limitations_required": True,
        }

    return {
        "output_type": "blocked_notice",
        "downloadable_file_expected": False,
        "owner_facing_summary_expected": True,
        "technical_annex_expected": True,
        "limitations_required": True,
    }


def _default_owner_problem(file_intake: FileIntakeResult) -> str:
    filename = file_intake["asset"].get("filename") or "archivo sin nombre"
    return f"Revisar el archivo {filename} dentro de Servicio 1."
