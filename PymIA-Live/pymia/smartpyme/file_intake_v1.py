from __future__ import annotations

from pathlib import PurePath
from typing import Any, Literal, TypedDict

DetectedFileType = Literal["xlsx", "csv", "pdf", "zip", "image", "text", "unknown"]
SupportStatus = Literal["SUPPORTED", "UNSUPPORTED_IN_V1", "UNKNOWN"]
CandidateIntakeEngine = Literal["document_ingestion_xlsx", "none"]
NextAllowedAction = Literal[
    "send_to_xlsx_document_ingestion",
    "ask_owner_to_upload_xlsx",
    "reject_unsupported_file_type",
    "ask_owner_for_clearer_file",
    "block_runtime_until_supported",
]
SourceChannel = Literal["cli", "chat", "upload", "api", "unknown"]
AssetSource = Literal["upload", "path", "message", "api", "unknown"]


class FileAsset(TypedDict, total=False):
    asset_id: str
    filename: str | None
    declared_mime_type: str | None
    size_bytes: int | None
    source: AssetSource


class FileIntakeSupport(TypedDict):
    status: SupportStatus
    reason_code: str
    owner_message: str


class FileIntakeRouting(TypedDict):
    candidate_intake_engine: CandidateIntakeEngine
    next_allowed_action: NextAllowedAction


class FileIntakeResult(TypedDict):
    file_intake_id: str
    schema_version: str
    service_name: str
    source_channel: SourceChannel
    asset: dict[str, Any]
    support: FileIntakeSupport
    routing: FileIntakeRouting
    risk_flags: list[str]
    curation_required: bool
    column_confirmation_expected: bool
    blocks_runtime: bool
    notes: list[str]


SCHEMA_VERSION = "1.0"
SERVICE_NAME = "SERVICE_1"

REASON_SUPPORTED_XLSX_V1 = "SUPPORTED_XLSX_V1"
REASON_UNSUPPORTED_CSV_V1 = "UNSUPPORTED_CSV_V1"
REASON_UNSUPPORTED_PDF_V1 = "UNSUPPORTED_PDF_V1"
REASON_UNSUPPORTED_ZIP_V1 = "UNSUPPORTED_ZIP_V1"
REASON_UNSUPPORTED_IMAGE_V1 = "UNSUPPORTED_IMAGE_V1"
REASON_UNSUPPORTED_TEXT_V1 = "UNSUPPORTED_TEXT_V1"
REASON_UNKNOWN_FILE_TYPE = "UNKNOWN_FILE_TYPE"
REASON_EMPTY_FILE = "EMPTY_FILE"
REASON_MIME_EXTENSION_MISMATCH = "MIME_EXTENSION_MISMATCH"
REASON_UNSAFE_FILENAME = "UNSAFE_FILENAME"

_SUPPORTED_XLSX_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroenabled.12",
}

_EXTENSION_TO_TYPE: dict[str, DetectedFileType] = {
    ".xlsx": "xlsx",
    ".xlsm": "xlsx",
    ".csv": "csv",
    ".pdf": "pdf",
    ".zip": "zip",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".txt": "text",
    ".md": "text",
}

_MIME_TO_TYPE: dict[str, DetectedFileType] = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel.sheet.macroenabled.12": "xlsx",
    "text/csv": "csv",
    "application/csv": "csv",
    "application/pdf": "pdf",
    "application/zip": "zip",
    "image/png": "image",
    "image/jpeg": "image",
    "image/webp": "image",
    "text/plain": "text",
    "text/markdown": "text",
}

_OWNER_MESSAGES = {
    REASON_SUPPORTED_XLSX_V1: (
        "Recibí el archivo Excel. Puedo revisarlo como evidencia operativa inicial. "
        "Antes de calcular o concluir algo, voy a identificar hojas, columnas y posibles campos que necesiten confirmación."
    ),
    REASON_UNSUPPORTED_CSV_V1: (
        "Recibí un CSV, pero esta versión del servicio todavía trabaja sólo con archivos Excel XLSX. "
        "Para avanzar, necesito que lo envíes como XLSX."
    ),
    REASON_UNSUPPORTED_PDF_V1: (
        "Recibí un PDF, pero esta versión todavía no procesa PDF como evidencia tabular. "
        "Para avanzar, necesito una planilla XLSX con los datos."
    ),
    REASON_UNSUPPORTED_ZIP_V1: (
        "Recibí un ZIP, pero esta versión todavía no procesa archivos comprimidos. "
        "Para avanzar, necesito un único archivo XLSX."
    ),
    REASON_UNSUPPORTED_IMAGE_V1: (
        "Recibí una imagen, pero esta versión todavía no procesa OCR ni capturas. "
        "Para avanzar, necesito una planilla XLSX."
    ),
    REASON_UNSUPPORTED_TEXT_V1: (
        "Recibí un archivo de texto, pero esta versión de File Intake trabaja sólo con XLSX. "
        "Para avanzar, necesito una planilla XLSX."
    ),
    REASON_UNKNOWN_FILE_TYPE: (
        "No pude identificar con seguridad el tipo de archivo. Para avanzar en esta versión, necesito un archivo XLSX."
    ),
    REASON_EMPTY_FILE: "El archivo parece estar vacío. Para avanzar, necesito un XLSX con datos.",
    REASON_MIME_EXTENSION_MISMATCH: (
        "El tipo declarado del archivo no coincide con su extensión. Para avanzar, necesito un XLSX claro y verificable."
    ),
    REASON_UNSAFE_FILENAME: (
        "El nombre del archivo no es seguro para procesarlo. Para avanzar, necesito reenviarlo con un nombre simple."
    ),
}


def classify_file_intake(
    *,
    file_intake_id: str,
    asset: FileAsset,
    source_channel: SourceChannel = "unknown",
) -> FileIntakeResult:
    """Classify a Service 1 file asset before evidence extraction.

    V1 is intentionally XLSX-first. It does not parse, calculate, diagnose, call LLMs,
    persist artifacts, or trigger pipeline/runtime wiring.
    """
    normalized_asset = _normalize_asset(asset)
    detected_type = _detect_file_type(
        filename=normalized_asset.get("filename"),
        declared_mime_type=normalized_asset.get("declared_mime_type"),
    )
    normalized_asset["detected_file_type"] = detected_type

    risk_flags: list[str] = []
    reason_code = _reason_for_detected_type(detected_type)

    if _is_empty_file(normalized_asset.get("size_bytes")):
        reason_code = REASON_EMPTY_FILE
        risk_flags.append("empty_file")
    elif _has_unsafe_filename(normalized_asset.get("filename")):
        reason_code = REASON_UNSAFE_FILENAME
        risk_flags.append("unsafe_filename")
    elif _has_mime_extension_mismatch(
        filename=normalized_asset.get("filename"),
        declared_mime_type=normalized_asset.get("declared_mime_type"),
    ):
        reason_code = REASON_MIME_EXTENSION_MISMATCH
        risk_flags.append("mime_extension_mismatch")

    if reason_code == REASON_SUPPORTED_XLSX_V1:
        support_status: SupportStatus = "SUPPORTED"
        routing: FileIntakeRouting = {
            "candidate_intake_engine": "document_ingestion_xlsx",
            "next_allowed_action": "send_to_xlsx_document_ingestion",
        }
        curation_required = True
        column_confirmation_expected = True
        risk_flags.append("requires_column_confirmation")
        notes = ["No calcular hasta completar curación y confirmación de columnas."]
    elif reason_code == REASON_UNKNOWN_FILE_TYPE:
        support_status = "UNKNOWN"
        routing = {
            "candidate_intake_engine": "none",
            "next_allowed_action": "ask_owner_for_clearer_file",
        }
        curation_required = False
        column_confirmation_expected = False
        risk_flags.append("ambiguous_file_type")
        notes = ["Tipo de archivo no identificado. V1 acepta sólo XLSX."]
    else:
        support_status = "UNSUPPORTED_IN_V1"
        routing = {
            "candidate_intake_engine": "none",
            "next_allowed_action": _unsupported_next_action(reason_code),
        }
        curation_required = False
        column_confirmation_expected = False
        if "unsupported_format" not in risk_flags and reason_code not in {REASON_EMPTY_FILE, REASON_UNSAFE_FILENAME, REASON_MIME_EXTENSION_MISMATCH}:
            risk_flags.append("unsupported_format")
        notes = ["Formato fuera de alcance para File Intake V1. V1 acepta sólo XLSX."]

    return {
        "file_intake_id": file_intake_id,
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "source_channel": source_channel,
        "asset": normalized_asset,
        "support": {
            "status": support_status,
            "reason_code": reason_code,
            "owner_message": _OWNER_MESSAGES[reason_code],
        },
        "routing": routing,
        "risk_flags": _dedupe(risk_flags),
        "curation_required": curation_required,
        "column_confirmation_expected": column_confirmation_expected,
        "blocks_runtime": True,
        "notes": notes,
    }


def _normalize_asset(asset: FileAsset) -> dict[str, Any]:
    return {
        "asset_id": asset.get("asset_id") or "unknown_asset",
        "filename": asset.get("filename"),
        "declared_mime_type": _normalize_mime(asset.get("declared_mime_type")),
        "size_bytes": asset.get("size_bytes"),
        "source": asset.get("source") or "unknown",
    }


def _detect_file_type(*, filename: str | None, declared_mime_type: str | None) -> DetectedFileType:
    by_extension = _detect_file_type_from_filename(filename)
    if by_extension != "unknown":
        return by_extension
    return _detect_file_type_from_mime(declared_mime_type)


def _detect_file_type_from_filename(filename: str | None) -> DetectedFileType:
    if not filename:
        return "unknown"
    suffix = PurePath(filename).suffix.lower()
    return _EXTENSION_TO_TYPE.get(suffix, "unknown")


def _detect_file_type_from_mime(declared_mime_type: str | None) -> DetectedFileType:
    if not declared_mime_type:
        return "unknown"
    return _MIME_TO_TYPE.get(declared_mime_type, "unknown")


def _reason_for_detected_type(detected_type: DetectedFileType) -> str:
    return {
        "xlsx": REASON_SUPPORTED_XLSX_V1,
        "csv": REASON_UNSUPPORTED_CSV_V1,
        "pdf": REASON_UNSUPPORTED_PDF_V1,
        "zip": REASON_UNSUPPORTED_ZIP_V1,
        "image": REASON_UNSUPPORTED_IMAGE_V1,
        "text": REASON_UNSUPPORTED_TEXT_V1,
        "unknown": REASON_UNKNOWN_FILE_TYPE,
    }[detected_type]


def _unsupported_next_action(reason_code: str) -> NextAllowedAction:
    if reason_code in {REASON_EMPTY_FILE, REASON_MIME_EXTENSION_MISMATCH, REASON_UNSAFE_FILENAME}:
        return "ask_owner_for_clearer_file"
    if reason_code == REASON_UNKNOWN_FILE_TYPE:
        return "ask_owner_for_clearer_file"
    return "ask_owner_to_upload_xlsx"


def _normalize_mime(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip().lower()
    return text or None


def _is_empty_file(size_bytes: Any) -> bool:
    return isinstance(size_bytes, int) and size_bytes <= 0


def _has_unsafe_filename(filename: str | None) -> bool:
    if not filename:
        return False
    normalized = filename.replace("\\", "/")
    path = PurePath(normalized)
    parts = set(path.parts)
    return ".." in parts or normalized.startswith("/") or ":" in normalized


def _has_mime_extension_mismatch(*, filename: str | None, declared_mime_type: str | None) -> bool:
    if not filename or not declared_mime_type:
        return False
    by_extension = _detect_file_type_from_filename(filename)
    by_mime = _detect_file_type_from_mime(declared_mime_type)
    if by_extension == "unknown" or by_mime == "unknown":
        return False
    return by_extension != by_mime


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
