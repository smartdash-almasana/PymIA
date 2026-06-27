"""
Service 1 Column Confirmation Packet V1

Builds an owner-facing column confirmation packet from the detected XLSX
structure. Does not calculate, diagnose, or authorize runtime.
"""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "COLUMN_CONFIRMATION"
MAX_QUESTIONS = 12


def build_service_1_column_confirmation_packet_v1(
    detected_structure: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a column confirmation packet from detected XLSX structure.

    Args:
        detected_structure: Output from read_service_1_xlsx_structure_v1.

    Returns:
        Column confirmation packet with runtime_authorized=False.
    """
    questions: list[dict[str, Any]] = []
    warnings: list[str] = []

    workbook = detected_structure.get("workbook", {})
    sheets = workbook.get("sheets", []) or []

    question_counter = 0
    for sheet in sheets:
        sheet_name = sheet.get("name", "")
        headers = sheet.get("headers", []) or []

        for header in headers:
            if not header or not str(header).strip():
                continue

            question_counter += 1
            question_id = f"col_confirm_{question_counter:03d}"
            column_name = str(header).strip()

            questions.append(
                {
                    "question_id": question_id,
                    "sheet_name": sheet_name,
                    "column_name": column_name,
                    "question": (
                        f"\u00bfQu\u00e9 representa la columna "
                        f"'{column_name}' en la hoja '{sheet_name}'?"
                    ),
                    "answer_type": "owner_text",
                    "required": True,
                }
            )

            if question_counter >= MAX_QUESTIONS:
                break

        if question_counter >= MAX_QUESTIONS:
            break

    if not questions:
        warnings.append(
            "No se detectaron columnas con encabezados legibles en el archivo. "
            "Se requiere revisi\u00f3n manual antes de continuar."
        )
        status = "NO_COLUMNS_DETECTED"
    else:
        status = "NEEDS_OWNER_CONFIRMATION"

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "runtime_authorized": False,
        "status": status,
        "questions": questions,
        "warnings": warnings,
    }
