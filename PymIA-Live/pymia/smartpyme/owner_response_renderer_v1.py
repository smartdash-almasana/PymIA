from __future__ import annotations

from typing import Literal, TypedDict

from pymia.smartpyme.file_intake_taskspec_boundary_v1 import TaskSpecPatch
from pymia.smartpyme.file_intake_v1 import FileIntakeResult

OwnerResponseType = Literal["OWNER_RESPONSE_V1"]


class OwnerResponseV1(TypedDict):
    service_name: str
    response_type: OwnerResponseType
    owner_message: str
    what_we_received: str
    what_can_be_done_now: str
    what_is_missing: list[str]
    what_cannot_be_claimed: list[str]
    next_owner_action: str
    column_confirmation_required: bool
    runtime_authorized: bool
    notes: list[str]


_FORBIDDEN_CLAIMS = [
    "No es un diagnostico integral de la empresa.",
    "No calcula margenes, caja, stock ni conciliaciones.",
    "No confirma archivo normalizado ni lectura interna del XLSX.",
]


def render_owner_response_v1(
    file_intake: FileIntakeResult,
    taskspec_patch: TaskSpecPatch,
) -> OwnerResponseV1:
    return {
        "service_name": "SERVICE_1",
        "response_type": "OWNER_RESPONSE_V1",
        "owner_message": file_intake["support"]["owner_message"],
        "what_we_received": _what_we_received(file_intake),
        "what_can_be_done_now": _what_can_be_done_now(taskspec_patch),
        "what_is_missing": list(taskspec_patch["missing_evidence"]),
        "what_cannot_be_claimed": list(_FORBIDDEN_CLAIMS),
        "next_owner_action": _next_owner_action(taskspec_patch),
        "column_confirmation_required": taskspec_patch["column_confirmation_required"],
        "runtime_authorized": False,
        "notes": list(file_intake.get("notes", [])) + list(taskspec_patch.get("notes", [])),
    }


def _what_we_received(file_intake: FileIntakeResult) -> str:
    asset = file_intake["asset"]
    filename = asset.get("filename") or "archivo sin nombre"
    detected_type = asset.get("detected_file_type") or "unknown"
    support_status = file_intake["support"]["status"]
    return f"Recibimos {filename} como archivo {detected_type}. Estado inicial: {support_status}."


def _what_can_be_done_now(taskspec_patch: TaskSpecPatch) -> str:
    if taskspec_patch["column_confirmation_required"]:
        return "Podemos tratarlo como evidencia inicial y preparar la confirmacion de columnas antes de cualquier calculo."
    if taskspec_patch["blocking_state"] == "BLOCKED_UNSUPPORTED_FILE_TYPE":
        return "Por ahora no podemos procesar este formato en Servicio 1 V1; necesitamos una version XLSX."
    if taskspec_patch["blocking_state"] == "BLOCKED_UNKNOWN_FILE_TYPE":
        return "Por ahora no podemos identificar con seguridad el tipo de archivo; necesitamos un archivo mas claro."
    if taskspec_patch["blocking_state"] == "BLOCKED_UNSAFE_FILE":
        return "Por ahora no podemos avanzar porque el archivo tiene un riesgo o inconsistencia inicial."
    return "Podemos registrar la evidencia recibida y mantener el caso bloqueado hasta tener datos suficientes."


def _next_owner_action(taskspec_patch: TaskSpecPatch) -> str:
    action = taskspec_patch["next_allowed_action"]
    if action == "ask_owner_to_confirm_columns_after_curation":
        return "Confirmar columnas despues de la curacion inicial."
    if action == "ask_owner_to_upload_xlsx":
        return "Subir el archivo en formato XLSX."
    if action == "ask_owner_for_clearer_file":
        return "Subir un archivo claro, valido y verificable."
    return "Esperar hasta que el runtime sea autorizado por una frontera valida."
