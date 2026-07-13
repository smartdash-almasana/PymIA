from __future__ import annotations

from typing import Final, Literal, NotRequired, TypedDict

from pymia.smartpyme.service_1_xlsx_delivery_v1 import Service1XlsxDeliveryInputV1

SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
CAPABILITY_REF: Final[str] = "excel_treatment_lab_v1"

ExcelTreatmentLabV1Status = Literal[
    "OK",
    "MISSING_INPUTS",
    "MISSING_CONFIRMATION",
    "INVALID_INPUT",
]

ALLOWED_STATUSES: Final[tuple[ExcelTreatmentLabV1Status, ...]] = (
    "OK",
    "MISSING_INPUTS",
    "MISSING_CONFIRMATION",
    "INVALID_INPUT",
)

DEFAULT_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No se puede afirmar un diagnóstico todavía.",
    "No se puede afirmar un cálculo validado todavía.",
    "No se puede afirmar que el archivo ya quedó normalizado.",
)

DEFAULT_TECHNICAL_NOTES: Final[tuple[str, ...]] = (
    "Pure deterministic packaging over declared Excel Treatment Lab facts.",
    "No file IO or external runtime integrations were executed.",
)


class ExcelTreatmentLabDetectedColumnV1(TypedDict):
    original_column_name: str
    suggested_semantic_role: NotRequired[str]
    confidence: NotRequired[str]


class ExcelTreatmentLabConfirmedColumnV1(TypedDict):
    original_column_name: str
    confirmed_semantic_role: str


class ExcelTreatmentLabInputV1(TypedDict):
    source_file: str | None
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1]
    confirmed_columns: list[ExcelTreatmentLabConfirmedColumnV1]
    rows_processed: int
    warnings: list[str]
    missing_inputs: NotRequired[list[str]]
    limitations: NotRequired[list[str]]
    forbidden_claims: NotRequired[list[str]]
    owner_summary: NotRequired[str]
    technical_notes: NotRequired[list[str]]


class ExcelTreatmentLabV1Result(Service1XlsxDeliveryInputV1):
    schema_version: Literal["1.0"]
    capability_ref: Literal["excel_treatment_lab_v1"]
    status: ExcelTreatmentLabV1Status
    source_file: str | None
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1]
    confirmed_columns: list[ExcelTreatmentLabConfirmedColumnV1]
    rows_processed: int
    warnings: list[str]


def build_excel_treatment_lab_v1(
    *,
    lab_input: ExcelTreatmentLabInputV1,
) -> ExcelTreatmentLabV1Result:
    source_file = _normalize_optional_text(lab_input.get("source_file"))
    detected_columns = _normalize_detected_columns(lab_input.get("detected_columns", []))
    confirmed_columns = _normalize_confirmed_columns(lab_input.get("confirmed_columns", []))
    warnings = _normalize_text_list(lab_input.get("warnings", []))
    limitations = _normalize_text_list(lab_input.get("limitations", []))
    technical_notes = _merge_technical_notes(lab_input.get("technical_notes"))
    rows_processed = lab_input["rows_processed"]

    if rows_processed < 0:
        status: ExcelTreatmentLabV1Status = "INVALID_INPUT"
    else:
        status = _infer_status(
            source_file=source_file,
            detected_columns=detected_columns,
            confirmed_columns=confirmed_columns,
        )

    missing_inputs = _merge_missing_inputs(
        declared_missing_inputs=lab_input.get("missing_inputs"),
        source_file=source_file,
        detected_columns=detected_columns,
    )
    pending_confirmation_columns = _pending_confirmation_columns(
        detected_columns=detected_columns,
        confirmed_columns=confirmed_columns,
    )

    owner_summary = _build_owner_summary(
        status=status,
        owner_summary=lab_input.get("owner_summary"),
        missing_inputs=missing_inputs,
        pending_confirmation_columns=pending_confirmation_columns,
    )

    computed_results: dict[str, object] = {
        "rows_processed": rows_processed,
        "detected_columns_count": len(detected_columns),
        "confirmed_columns_count": len(confirmed_columns),
        "pending_confirmation_columns": pending_confirmation_columns,
        "warnings": warnings,
    }

    inputs_used: dict[str, object] = {
        "source_file": source_file,
        "detected_columns": detected_columns,
        "confirmed_columns": confirmed_columns,
    }

    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "capability_ref": "excel_treatment_lab_v1",
        "status": status,
        "owner_summary": owner_summary,
        "inputs_used": inputs_used,
        "computed_results": computed_results,
        "missing_inputs": missing_inputs,
        "limitations": limitations,
        "forbidden_claims": _merge_forbidden_claims(lab_input.get("forbidden_claims")),
        "technical_notes": technical_notes,
        "runtime_authorized": False,
        "source_file": source_file,
        "detected_columns": detected_columns,
        "confirmed_columns": confirmed_columns,
        "rows_processed": rows_processed,
        "warnings": warnings,
    }


def _infer_status(
    *,
    source_file: str | None,
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1],
    confirmed_columns: list[ExcelTreatmentLabConfirmedColumnV1],
) -> ExcelTreatmentLabV1Status:
    if not source_file or not detected_columns:
        return "MISSING_INPUTS"
    if _pending_confirmation_columns(
        detected_columns=detected_columns,
        confirmed_columns=confirmed_columns,
    ):
        return "MISSING_CONFIRMATION"
    return "OK"


def _pending_confirmation_columns(
    *,
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1],
    confirmed_columns: list[ExcelTreatmentLabConfirmedColumnV1],
) -> list[str]:
    confirmed_names = {
        entry["original_column_name"].strip()
        for entry in confirmed_columns
        if entry["original_column_name"].strip()
    }
    return [
        entry["original_column_name"]
        for entry in detected_columns
        if entry["original_column_name"] not in confirmed_names
    ]


def _merge_missing_inputs(
    *,
    declared_missing_inputs: list[str] | None,
    source_file: str | None,
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1],
) -> list[str]:
    merged = _normalize_text_list(declared_missing_inputs or [])
    if not source_file and "source_file" not in merged:
        merged.append("source_file")
    if not detected_columns and "detected_columns" not in merged:
        merged.append("detected_columns")
    return merged


def _merge_forbidden_claims(forbidden_claims: list[str] | None) -> list[str]:
    merged = list(DEFAULT_FORBIDDEN_CLAIMS)
    for claim in _normalize_text_list(forbidden_claims or []):
        if claim not in merged:
            merged.append(claim)
    return merged


def _merge_technical_notes(technical_notes: list[str] | None) -> list[str]:
    merged = list(DEFAULT_TECHNICAL_NOTES)
    for note in _normalize_text_list(technical_notes or []):
        if note not in merged:
            merged.append(note)
    return merged


def _build_owner_summary(
    *,
    status: ExcelTreatmentLabV1Status,
    owner_summary: str | None,
    missing_inputs: list[str],
    pending_confirmation_columns: list[str],
) -> str:
    normalized_summary = _normalize_optional_text(owner_summary)
    if normalized_summary:
        return normalized_summary

    if status == "OK":
        return "La preparación lógica del Laboratorio Excel quedó lista para el delivery XLSX de Servicio 1."
    if status == "MISSING_CONFIRMATION":
        pending_preview = ", ".join(pending_confirmation_columns[:3]) or "columnas detectadas"
        return (
            "Hay columnas detectadas sin confirmación del dueño "
            f"({pending_preview}); no corresponde afirmar normalización cerrada todavía."
        )
    if status == "INVALID_INPUT":
        return "El input estructurado del Laboratorio Excel es inválido y debe corregirse antes de continuar."
    if missing_inputs:
        return (
            "Faltan datos mínimos para preparar la curación lógica del Laboratorio Excel: "
            + ", ".join(missing_inputs)
            + "."
        )
    return "Faltan datos mínimos para preparar la curación lógica del Laboratorio Excel."


def _normalize_detected_columns(
    detected_columns: list[ExcelTreatmentLabDetectedColumnV1],
) -> list[ExcelTreatmentLabDetectedColumnV1]:
    normalized: list[ExcelTreatmentLabDetectedColumnV1] = []
    for entry in detected_columns:
        column_name = _normalize_optional_text(entry.get("original_column_name"))
        if not column_name:
            continue

        payload: ExcelTreatmentLabDetectedColumnV1 = {
            "original_column_name": column_name,
        }
        suggested_role = _normalize_optional_text(entry.get("suggested_semantic_role"))
        if suggested_role:
            payload["suggested_semantic_role"] = suggested_role
        confidence = _normalize_optional_text(entry.get("confidence"))
        if confidence:
            payload["confidence"] = confidence
        normalized.append(payload)
    return normalized


def _normalize_confirmed_columns(
    confirmed_columns: list[ExcelTreatmentLabConfirmedColumnV1],
) -> list[ExcelTreatmentLabConfirmedColumnV1]:
    normalized: list[ExcelTreatmentLabConfirmedColumnV1] = []
    seen: set[tuple[str, str]] = set()
    for entry in confirmed_columns:
        column_name = _normalize_optional_text(entry.get("original_column_name"))
        confirmed_role = _normalize_optional_text(entry.get("confirmed_semantic_role"))
        if not column_name or not confirmed_role:
            continue
        fingerprint = (column_name, confirmed_role)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        normalized.append(
            {
                "original_column_name": column_name,
                "confirmed_semantic_role": confirmed_role,
            }
        )
    return normalized


def _normalize_text_list(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        text = _normalize_optional_text(value)
        if text:
            normalized.append(text)
    return normalized


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
