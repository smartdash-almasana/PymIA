from __future__ import annotations

from typing import Literal, TypedDict

from pymia.smartpyme.file_intake_v1 import FileIntakeResult
from pymia.smartpyme.file_intake_taskspec_boundary_v1 import TaskSpecPatch

Service1ExcelTriageReportType = Literal["EXCEL_TRIAGE_REPORT"]


class Service1ExcelTriageAssetSummary(TypedDict):
    asset_id: str
    file_intake_id: str
    filename: str | None
    source: str


class Service1ExcelTriageReport(TypedDict):
    report_id: str
    service_name: str
    report_type: Service1ExcelTriageReportType
    received_asset: Service1ExcelTriageAssetSummary
    support_status: str
    detected_file_type: str
    risk_flags: list[str]
    owner_summary: str
    what_we_received: list[str]
    what_can_be_done_now: list[str]
    what_cannot_be_claimed: list[str]
    missing_evidence: list[str]
    column_confirmation_required: bool
    owner_next_action: str
    runtime_authorized: bool
    notes: list[str]


def build_service_1_excel_triage_report_from_taskspec_patch(
    *,
    file_intake: FileIntakeResult,
    taskspec_patch: TaskSpecPatch,
) -> Service1ExcelTriageReport:
    asset = file_intake["asset"]
    support_status = file_intake["support"]["status"]
    detected_file_type = str(asset.get("detected_file_type") or "unknown")
    owner_next_action = _owner_next_action(taskspec_patch["next_allowed_action"])

    return {
        "report_id": f"excel_triage_report::{file_intake['file_intake_id']}",
        "service_name": "SERVICE_1",
        "report_type": "EXCEL_TRIAGE_REPORT",
        "received_asset": {
            "asset_id": str(asset.get("asset_id") or "unknown_asset"),
            "file_intake_id": file_intake["file_intake_id"],
            "filename": asset.get("filename"),
            "source": str(asset.get("source") or "unknown"),
        },
        "support_status": support_status,
        "detected_file_type": detected_file_type,
        "risk_flags": list(file_intake.get("risk_flags", [])),
        "owner_summary": file_intake["support"]["owner_message"],
        "what_we_received": _what_we_received(asset.get("filename"), detected_file_type, support_status),
        "what_can_be_done_now": _what_can_be_done_now(support_status, taskspec_patch["column_confirmation_required"]),
        "what_cannot_be_claimed": _what_cannot_be_claimed(),
        "missing_evidence": list(taskspec_patch.get("missing_evidence", [])),
        "column_confirmation_required": taskspec_patch["column_confirmation_required"],
        "owner_next_action": owner_next_action,
        "runtime_authorized": False,
        "notes": list(taskspec_patch.get("notes", [])),
    }


def _what_we_received(filename: str | None, detected_file_type: str, support_status: str) -> list[str]:
    visible_name = filename or "archivo sin nombre"
    return [
        f"Recibimos: {visible_name}.",
        f"Tipo detectado: {detected_file_type}.",
        f"Estado de soporte actual: {support_status}.",
    ]


def _what_can_be_done_now(support_status: str, column_confirmation_required: bool) -> list[str]:
    if support_status == "SUPPORTED":
        items = ["Podemos hacer una revisión inicial prudente del archivo como evidencia operativa."]
        if column_confirmation_required:
            items.append("Antes de calcular o concluir algo, hay que confirmar columnas después de la curación inicial.")
        return items

    if support_status == "UNKNOWN":
        return ["Podemos pedir un archivo más claro para decidir si entra o no en esta versión del servicio."]

    return ["Podemos indicar el formato aceptado en esta versión y pedir un XLSX válido para continuar."]


def _what_cannot_be_claimed() -> list[str]:
    return [
        "No se puede afirmar un diagnóstico todavía.",
        "No se puede afirmar un cálculo validado todavía.",
        "No se puede afirmar que el archivo ya quedó normalizado.",
    ]


def _owner_next_action(next_allowed_action: str) -> str:
    if next_allowed_action == "ask_owner_to_confirm_columns_after_curation":
        return "Cuando te mostremos la curación inicial, confirmá las columnas necesarias para seguir."
    if next_allowed_action == "ask_owner_to_upload_xlsx":
        return "Para seguir en esta versión del servicio, enviá el archivo en formato XLSX."
    if next_allowed_action == "ask_owner_for_clearer_file":
        return "Para seguir, reenviá un archivo más claro y válido."
    return "Por ahora el runtime sigue bloqueado; todavía no corresponde procesamiento automático."

