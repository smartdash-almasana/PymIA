"""
Service 1 Owner Confirmation -> Canonical Ingestion Output V1

Minimal, deterministic connector for the Servicio 1 assisted flow.

Flow implemented (connector only):

    owner_question_packet + owner_answers -> canonical ingestion_output

The owner_question_packet MUST come from
``service_1_web_column_confirmation_intake_boundary_v1``. This module turns the
owner's per-column confirmations into a canonical ``ingestion_output`` that is
directly consumable by the existing semantic chain starting at
``service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1``.

This module DOES NOT:
- authorize runtime, product or delivery,
- execute tools,
- create a delivery folder,
- re-read the XLSX (columns already travel inside the packet),
- parse XLSX or use openpyxl,
- touch the legacy CLI,
- implement any web UI.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    PACKET_TYPE as BOUNDARY_PACKET_TYPE,
    SCHEMA_VERSION as BOUNDARY_SCHEMA_VERSION,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_CONFIRMATION_TO_CANONICAL_INGESTION_OUTPUT_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "OWNER_CONFIRMATION_TO_CANONICAL_INGESTION_OUTPUT"

EXPECTED_INPUT_STATUS = "NEEDS_OWNER_CONFIRMATION"
STATUS_READY = "INGESTION_OUTPUT_READY"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_PACKET_NOT_DICT = "PACKET_NOT_DICT"
BLOCK_PACKET_WRONG_SCHEMA = "PACKET_WRONG_SCHEMA"
BLOCK_PACKET_WRONG_STATUS = "PACKET_WRONG_STATUS"
BLOCK_PACKET_FLAGS_FORBIDDEN = "PACKET_SAFETY_FLAGS_FORBIDDEN"
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_QUESTION_COUNT_INCONSISTENT = "QUESTION_COUNT_INCONSISTENT"
BLOCK_ANSWERS_NOT_DICT = "OWNER_ANSWERS_NOT_DICT"
BLOCK_MISSING_ANSWERS = "MISSING_ANSWERS"
BLOCK_UNKNOWN_COLUMNS = "UNKNOWN_COLUMNS"
BLOCK_DUPLICATE_COLUMNS = "DUPLICATE_COLUMNS"


def build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
    *,
    owner_question_packet: Any,
    owner_answers: Any,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    """Turn a validated owner confirmation into a canonical ingestion_output.

    Args:
        owner_question_packet: The packet produced by
            ``service_1_web_column_confirmation_intake_boundary_v1``.
        owner_answers: Mapping ``{column_name: owner_meaning_text}``. Every
            detected column must have a non-empty answer. Unknown or duplicate
            columns are blocking.
        runtime_authorized / product_ready / delivery_authorized: Must remain
            False. Passing any as True is itself a blocking condition, because
            this connector must stay observation-only.

    Returns:
        A canonical connector packet. On any blocking condition, status is
        ``BLOCKED`` with a ``blocked_reason``. On success, status is
        ``INGESTION_OUTPUT_READY`` and ``ingestion_output`` carries the shape
        consumed by the existing runtime-bridge adapter.
    """
    # Hard rule: this connector can never be invoked with runtime/delivery on.
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(owner_question_packet, dict):
        return _blocked(BLOCK_PACKET_NOT_DICT)

    packet = owner_question_packet

    # 1. Provenance: packet must come from the boundary module.
    if (
        packet.get("schema_version") != BOUNDARY_SCHEMA_VERSION
        or packet.get("packet_type") != BOUNDARY_PACKET_TYPE
    ):
        return _blocked(BLOCK_PACKET_WRONG_SCHEMA)

    # 2. Packet status must be NEEDS_OWNER_CONFIRMATION.
    if packet.get("status") != EXPECTED_INPUT_STATUS:
        return _blocked(BLOCK_PACKET_WRONG_STATUS)

    # 3. Packet safety flags must still be false.
    if (
        packet.get("runtime_authorized")
        or packet.get("product_ready")
        or packet.get("delivery_authorized")
    ):
        return _blocked(BLOCK_PACKET_FLAGS_FORBIDDEN)

    columns = list(packet.get("columns") or [])
    owner_questions = list(packet.get("owner_questions") or [])
    question_count = packet.get("question_count")

    # 7. question_count must match the packet's own detected reality.
    if question_count != len(columns) or question_count != len(owner_questions):
        return _blocked(
            BLOCK_QUESTION_COUNT_INCONSISTENT,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    if not isinstance(owner_answers, dict):
        return _blocked(
            BLOCK_ANSWERS_NOT_DICT,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    detected = [str(column).strip() for column in columns]

    # 5a. Duplicate detected columns are a blocking, unrecoverable ambiguity.
    duplicates = _duplicates(detected)
    if duplicates:
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=duplicates,
        )

    answer_keys = [str(key).strip() for key in owner_answers.keys()]
    detected_set = set(detected)

    # 5b. Unknown columns (answers for columns not detected) are blocking.
    unknown = [key for key in answer_keys if key not in detected_set]
    if unknown:
        return _blocked(
            BLOCK_UNKNOWN_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=sorted(set(unknown)),
        )

    # 4. Every detected column must have a non-empty owner answer.
    confirmed_columns: list[str] = []
    normalized_answers: dict[str, str] = {}
    missing: list[str] = []
    for column in detected:
        answer = _answer_for(owner_answers, column)
        if answer is None:
            missing.append(column)
            continue
        confirmed_columns.append(column)
        normalized_answers[column] = answer

    if missing:
        return _blocked(
            BLOCK_MISSING_ANSWERS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=missing,
        )

    case_id = packet.get("case_id")
    source_kind = packet.get("source_kind")
    filename = packet.get("filename")
    normalized_table = packet.get("normalized_table")
    column_evidence = _column_evidence(normalized_table, detected)
    selected_sheet_name = (
        normalized_table.get("sheet_name")
        if isinstance(normalized_table, dict)
        else None
    )

    # 6. Build ingestion_output in the shape the runtime-bridge adapter reads.
    ingestion_output: dict[str, Any] = {
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "source_file_ref": filename,
        "available_data_fields": list(confirmed_columns),
        "columns": list(confirmed_columns),
        "input_values": dict(normalized_answers),
        "normalized_values": dict(normalized_answers),
        "column_meaning_confirmations": list(confirmed_columns),
        "column_evidence": column_evidence,
        "sheet_name": selected_sheet_name,
        "declared_data_sources": [filename] if filename else [],
        "provenance": {
            "origin_schema_version": BOUNDARY_SCHEMA_VERSION,
            "case_id": case_id,
            "source_kind": source_kind,
            "filename": filename,
        },
        "runtime_authorized": False,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "columns": list(columns),
        "confirmed_columns": list(confirmed_columns),
        "owner_answers": dict(normalized_answers),
        "ingestion_output": ingestion_output,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _column_evidence(
    normalized_table: Any,
    detected_columns: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(normalized_table, dict):
        return {
            column: {"sample_values": [], "inferred_type": None}
            for column in detected_columns
        }

    headers = list(normalized_table.get("headers") or [])
    normalized_headers = list(normalized_table.get("normalized_headers") or [])
    rows = list(normalized_table.get("rows") or [])
    by_original: dict[str, dict[str, Any]] = {}

    for index, raw_column in enumerate(headers):
        column = str(raw_column).strip()
        normalized = (
            normalized_headers[index]
            if index < len(normalized_headers)
            else column
        )
        samples: list[Any] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            value = row.get(normalized, row.get(column))
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            samples.append(value)
            if len(samples) >= 5:
                break
        by_original[column] = {
            "sample_values": samples,
            "inferred_type": None,
        }

    return {
        column: by_original.get(
            column,
            {"sample_values": [], "inferred_type": None},
        )
        for column in detected_columns
    }


def _answer_for(owner_answers: dict[Any, Any], column: str) -> Optional[str]:
    for key, value in owner_answers.items():
        if str(key).strip() == column:
            text = "" if value is None else str(value).strip()
            return text or None
    return None


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen and value not in result:
            result.append(value)
        seen.add(value)
    return result


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
    columns: Optional[list[Any]] = None,
    detail: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "columns": list(columns or []),
        "confirmed_columns": [],
        "owner_answers": {},
        "ingestion_output": None,
        "detail": list(detail or []),
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "EXPECTED_INPUT_STATUS",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_PACKET_NOT_DICT",
    "BLOCK_PACKET_WRONG_SCHEMA",
    "BLOCK_PACKET_WRONG_STATUS",
    "BLOCK_PACKET_FLAGS_FORBIDDEN",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_QUESTION_COUNT_INCONSISTENT",
    "BLOCK_ANSWERS_NOT_DICT",
    "BLOCK_MISSING_ANSWERS",
    "BLOCK_UNKNOWN_COLUMNS",
    "BLOCK_DUPLICATE_COLUMNS",
    "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
]
