"""Owner confirmation -> canonical multisheet ingestion output V1."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Optional

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    PACKET_TYPE as BOUNDARY_PACKET_TYPE,
    SCHEMA_VERSION as BOUNDARY_SCHEMA_VERSION,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_CONFIRMATION_TO_CANONICAL_INGESTION_OUTPUT_V1"
CANONICAL_INGESTION_SCHEMA_VERSION = "SERVICE_1_CANONICAL_INGESTION_OUTPUT_V2"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "OWNER_CONFIRMATION_TO_CANONICAL_INGESTION_OUTPUT"
EXPECTED_INPUT_STATUS = "NEEDS_OWNER_CONFIRMATION"
STATUS_READY = "INGESTION_OUTPUT_READY"
STATUS_UNCONFIRMED_READY = "UNCONFIRMED_INGESTION_OUTPUT_READY"
STATUS_BLOCKED = "BLOCKED"
REQUEST_KIND_WORKBOOK = "WORKBOOK"

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
BLOCK_DUPLICATE_ANSWERS = "DUPLICATE_ANSWERS"
BLOCK_INVALID_COLUMN_REFS = "INVALID_COLUMN_REFS"
BLOCK_WORKBOOK_CONTEXT_REQUIRED = "WORKBOOK_CONTEXT_REQUIRED"

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T].*)?$")
_SLASH_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")


def _workbook_context(packet: dict[str, Any]) -> dict[str, Any] | None:
    case_id = str(packet.get("case_id") or "").strip()
    workbook_ref = str(packet.get("workbook_ref") or "").strip()
    source_artifact_ref = str(packet.get("source_artifact_ref") or "").strip()
    ingestion_scope = str(packet.get("ingestion_scope") or "").strip()
    if not case_id or not workbook_ref or not source_artifact_ref or not ingestion_scope:
        return None
    source_system_ref = str(
        packet.get("source_system_ref") or packet.get("source_kind") or ""
    ).strip() or None
    source_context_ref = str(packet.get("source_context_ref") or "").strip() or None
    return {
        "case_id": case_id,
        "source_artifact_ref": source_artifact_ref,
        "workbook_ref": workbook_ref,
        "ingestion_scope": ingestion_scope,
        "canonical_reader_schema_version": str(
            packet.get("canonical_reader_schema_version")
            or "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1"
        ).strip(),
        "source_system_ref": source_system_ref,
        "source_context_ref": source_context_ref,
    }


def _physical_lineage(
    normalized_tables: list[dict[str, Any]],
    *,
    workbook_ref: str,
) -> list[dict[str, Any]]:
    lineage: list[dict[str, Any]] = []
    for table in normalized_tables:
        sheet_name = str(table.get("sheet_name") or "").strip()
        if not sheet_name:
            continue
        lineage.append(
            {
                "sheet_name": sheet_name,
                "sheet_ref": _packet_sheet_ref(
                    {"workbook_ref": workbook_ref},
                    sheet_name,
                ),
                "source_kind": str(table.get("source_kind") or "").strip() or None,
                "source_path": str(table.get("source_path") or "").strip() or None,
                "header_row_number": table.get("header_row_number"),
                "source_row_numbers": list(table.get("source_row_numbers") or []),
                "physical_max_column": int(table.get("physical_max_column") or 0),
                "physical_max_row": int(table.get("physical_max_row") or 0),
            }
        )
    return lineage


def _canonical_ingestion_envelope(
    *,
    packet: dict[str, Any],
    normalized_tables: list[dict[str, Any]],
    column_refs: list[dict[str, Any]],
    sheet_names: list[str],
) -> dict[str, Any] | None:
    workbook_context = _workbook_context(packet)
    if workbook_context is None:
        return None
    filename = packet.get("filename")
    source_artifact_ref = workbook_context["source_artifact_ref"]
    workbook_ref = workbook_context["workbook_ref"]
    sheet_refs = [
        dict(item)
        for item in packet.get("sheet_refs") or ()
        if isinstance(item, dict)
    ]
    return {
        "schema_version": CANONICAL_INGESTION_SCHEMA_VERSION,
        "request_kind": REQUEST_KIND_WORKBOOK,
        "workbook_context": workbook_context,
        "normalized_tables": normalized_tables,
        "column_refs": column_refs,
        "physical_lineage": _physical_lineage(
            normalized_tables,
            workbook_ref=workbook_ref,
        ),
        "provenance": {
            "origin_schema_version": BOUNDARY_SCHEMA_VERSION,
            "source_kind": packet.get("source_kind"),
            "source_artifact_ref": source_artifact_ref,
            "source_file_ref": workbook_ref,
            "workbook_ref": workbook_ref,
            "ingestion_scope": workbook_context["ingestion_scope"],
            "canonical_reader_schema_version": workbook_context[
                "canonical_reader_schema_version"
            ],
            "filename": filename,
            "sheet_names": sheet_names,
            "sheet_refs": sheet_refs,
        },
        "safety_flags": {
            "runtime_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
        },
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def build_service_1_unconfirmed_canonical_ingestion_output_v1(
    *,
    owner_question_packet: Any,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    """Create canonical ingestion evidence before any owner confirmation."""
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)
    if not isinstance(owner_question_packet, dict):
        return _blocked(BLOCK_PACKET_NOT_DICT)

    packet = owner_question_packet
    if (
        packet.get("schema_version") != BOUNDARY_SCHEMA_VERSION
        or packet.get("packet_type") != BOUNDARY_PACKET_TYPE
    ):
        return _blocked(BLOCK_PACKET_WRONG_SCHEMA)
    if packet.get("status") != EXPECTED_INPUT_STATUS:
        return _blocked(BLOCK_PACKET_WRONG_STATUS)
    if (
        packet.get("runtime_authorized")
        or packet.get("product_ready")
        or packet.get("delivery_authorized")
    ):
        return _blocked(BLOCK_PACKET_FLAGS_FORBIDDEN)

    columns = [str(item).strip() for item in list(packet.get("columns") or [])]
    owner_questions = list(packet.get("owner_questions") or [])
    column_refs = _column_refs(
        packet,
        columns=columns,
        owner_questions=owner_questions,
    )
    if column_refs is None:
        return _blocked(
            BLOCK_INVALID_COLUMN_REFS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )
    if (
        packet.get("question_count") != len(columns)
        or packet.get("question_count") != len(owner_questions)
        or packet.get("question_count") != len(column_refs)
    ):
        return _blocked(
            BLOCK_QUESTION_COUNT_INCONSISTENT,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    sheet_names = _ordered_unique(ref["sheet_name"] for ref in column_refs)
    identities = [
        f"{ref['sheet_name']}\x00{ref['column_name']}" for ref in column_refs
    ]
    field_ids = [ref["field_id"] for ref in column_refs]
    question_ids = [ref["question_id"] for ref in column_refs]
    if (
        (len(sheet_names) <= 1 and _duplicates(columns))
        or _duplicates(identities)
        or _duplicates(field_ids)
        or _duplicates(question_ids)
    ):
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    case_id = packet.get("case_id")
    source_kind = packet.get("source_kind")
    filename = packet.get("filename")
    normalized_tables = _normalized_tables(packet)
    unconfirmed_refs = [dict(ref) for ref in column_refs]
    ingestion_output = _canonical_ingestion_envelope(
        packet=packet,
        normalized_tables=normalized_tables,
        column_refs=unconfirmed_refs,
        sheet_names=sheet_names,
    )
    if ingestion_output is None:
        return _blocked(
            BLOCK_WORKBOOK_CONTEXT_REQUIRED,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_UNCONFIRMED_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "source_artifact_ref": packet.get("source_artifact_ref"),
        "workbook_ref": packet.get("workbook_ref"),
        "ingestion_scope": packet.get("ingestion_scope"),
        "source_kind": source_kind,
        "filename": filename,
        "sheet_names": sheet_names,
        "sheet_refs": list(packet.get("sheet_refs") or ()),
        "columns": list(columns),
        "column_refs": unconfirmed_refs,
        "confirmed_columns": [],
        "ingestion_output": ingestion_output,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
    *,
    owner_question_packet: Any,
    owner_answers: Any,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)
    if not isinstance(owner_question_packet, dict):
        return _blocked(BLOCK_PACKET_NOT_DICT)

    packet = owner_question_packet
    if (
        packet.get("schema_version") != BOUNDARY_SCHEMA_VERSION
        or packet.get("packet_type") != BOUNDARY_PACKET_TYPE
    ):
        return _blocked(BLOCK_PACKET_WRONG_SCHEMA)
    if packet.get("status") != EXPECTED_INPUT_STATUS:
        return _blocked(BLOCK_PACKET_WRONG_STATUS)
    if (
        packet.get("runtime_authorized")
        or packet.get("product_ready")
        or packet.get("delivery_authorized")
    ):
        return _blocked(BLOCK_PACKET_FLAGS_FORBIDDEN)

    columns = [str(item).strip() for item in list(packet.get("columns") or [])]
    owner_questions = list(packet.get("owner_questions") or [])
    question_count = packet.get("question_count")
    packet_sheet_names = _ordered_unique(packet.get("sheet_names") or ())
    if not packet_sheet_names and isinstance(packet.get("column_refs"), list):
        packet_sheet_names = _ordered_unique(
            raw.get("sheet_name")
            for raw in packet["column_refs"]
            if isinstance(raw, dict)
        )
    if len(packet_sheet_names) <= 1 and _duplicates(columns):
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=_duplicates(columns),
        )
    column_refs = _column_refs(packet, columns=columns, owner_questions=owner_questions)

    if column_refs is None:
        return _blocked(
            BLOCK_INVALID_COLUMN_REFS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )
    if (
        question_count != len(columns)
        or question_count != len(owner_questions)
        or question_count != len(column_refs)
    ):
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

    sheet_names = _ordered_unique(ref["sheet_name"] for ref in column_refs)
    multisheet = len(sheet_names) > 1
    if not multisheet and _duplicates(columns):
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=_duplicates(columns),
        )

    identity_keys = [f"{ref['sheet_name']}\x00{ref['column_name']}" for ref in column_refs]
    field_ids = [ref["field_id"] for ref in column_refs]
    question_ids = [ref["question_id"] for ref in column_refs]
    if _duplicates(identity_keys) or _duplicates(field_ids) or _duplicates(question_ids):
        return _blocked(
            BLOCK_DUPLICATE_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    aliases: dict[str, str] = {}
    for ref in column_refs:
        aliases[ref["question_id"]] = ref["field_id"]
        if not multisheet:
            aliases[ref["column_name"]] = ref["field_id"]

    unknown = [str(key).strip() for key in owner_answers if str(key).strip() not in aliases]
    if unknown:
        return _blocked(
            BLOCK_UNKNOWN_COLUMNS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=sorted(set(unknown)),
        )

    normalized_answers: dict[str, str] = {}
    duplicate_answer_fields: list[str] = []
    for raw_key, raw_value in owner_answers.items():
        key = str(raw_key).strip()
        field_id = aliases[key]
        text = "" if raw_value is None else str(raw_value).strip()
        if field_id in normalized_answers:
            duplicate_answer_fields.append(field_id)
            continue
        if text:
            normalized_answers[field_id] = text
    if duplicate_answer_fields:
        return _blocked(
            BLOCK_DUPLICATE_ANSWERS,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
            detail=sorted(set(duplicate_answer_fields)),
        )

    missing = [ref["field_id"] for ref in column_refs if ref["field_id"] not in normalized_answers]
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
    normalized_tables = _normalized_tables(packet)
    confirmed_refs = [
        {**ref, "owner_meaning": normalized_answers[ref["field_id"]]}
        for ref in column_refs
    ]
    available_fields = [ref["field_id"] for ref in column_refs]

    ingestion_output = _canonical_ingestion_envelope(
        packet=packet,
        normalized_tables=normalized_tables,
        column_refs=confirmed_refs,
        sheet_names=sheet_names,
    )
    if ingestion_output is None:
        return _blocked(
            BLOCK_WORKBOOK_CONTEXT_REQUIRED,
            case_id=packet.get("case_id"),
            source_kind=packet.get("source_kind"),
            filename=packet.get("filename"),
            columns=columns,
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "source_artifact_ref": packet.get("source_artifact_ref"),
        "workbook_ref": packet.get("workbook_ref"),
        "ingestion_scope": packet.get("ingestion_scope"),
        "source_kind": source_kind,
        "filename": filename,
        "sheet_names": sheet_names,
        "sheet_refs": list(packet.get("sheet_refs") or ()),
        "columns": list(columns),
        "column_refs": confirmed_refs,
        "confirmed_columns": available_fields,
        "ingestion_output": ingestion_output,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _column_refs(
    packet: dict[str, Any],
    *,
    columns: list[str],
    owner_questions: list[Any],
) -> list[dict[str, str]] | None:
    raw_refs = packet.get("column_refs")
    if isinstance(raw_refs, list) and raw_refs:
        refs: list[dict[str, str]] = []
        for raw in raw_refs:
            if not isinstance(raw, dict):
                return None
            ref = {
                "question_id": str(raw.get("question_id") or "").strip(),
                "field_id": str(raw.get("field_id") or "").strip(),
                "sheet_name": str(raw.get("sheet_name") or "").strip(),
                "sheet_ref": str(raw.get("sheet_ref") or "").strip(),
                "column_name": str(raw.get("column_name") or "").strip(),
                "normalized_column_name": str(
                    raw.get("normalized_column_name") or raw.get("column_name") or ""
                ).strip(),
            }
            if not ref["sheet_ref"]:
                ref["sheet_ref"] = _packet_sheet_ref(packet, ref["sheet_name"])
            if any(not ref[key] for key in ("question_id", "field_id", "sheet_name", "sheet_ref", "column_name")):
                return None
            refs.append(ref)
        if [ref["column_name"] for ref in refs] != columns:
            return None
        return refs

    table = packet.get("normalized_table")
    if not isinstance(table, dict):
        return None
    sheet = str(table.get("sheet_name") or "").strip()
    if not sheet:
        return None
    sheet_ref = _packet_sheet_ref(packet, sheet)
    if not sheet_ref:
        return None
    refs = []
    for index, column in enumerate(columns):
        question = owner_questions[index] if index < len(owner_questions) else {}
        question_id = (
            str(question.get("question_id") or "").strip()
            if isinstance(question, dict)
            else ""
        ) or f"col_confirm_{index + 1:03d}"
        refs.append(
            {
                "question_id": question_id,
                "field_id": column,
                "sheet_name": sheet,
                "sheet_ref": sheet_ref,
                "column_name": column,
                "normalized_column_name": column,
            }
        )
    return refs


def _normalized_tables(packet: dict[str, Any]) -> list[dict[str, Any]]:
    tables = packet.get("normalized_tables")
    if isinstance(tables, list) and tables:
        return [table for table in tables if isinstance(table, dict)]
    table = packet.get("normalized_table")
    return [table] if isinstance(table, dict) else []


def _column_evidence(
    normalized_tables: list[dict[str, Any]],
    column_refs: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    tables_by_sheet = {
        str(table.get("sheet_name") or "").strip(): table
        for table in normalized_tables
    }
    result: dict[str, dict[str, Any]] = {}
    for ref in column_refs:
        table = tables_by_sheet.get(ref["sheet_name"], {})
        headers = list(table.get("headers") or [])
        normalized_headers = list(table.get("normalized_headers") or [])
        rows = list(table.get("rows") or [])
        try:
            index = [str(header).strip() for header in headers].index(ref["column_name"])
        except ValueError:
            index = -1
        normalized = (
            str(normalized_headers[index]).strip()
            if index >= 0 and index < len(normalized_headers)
            else ref["normalized_column_name"]
        )
        samples: list[Any] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            value = row.get(normalized, row.get(ref["column_name"]))
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            samples.append(value)
            if len(samples) >= 5:
                break
        result[ref["field_id"]] = {
            "sheet_name": ref["sheet_name"],
            "sheet_ref": ref["sheet_ref"],
            "column_name": ref["column_name"],
            "sample_values": samples,
            "inferred_type": _infer_type(samples),
        }
    return result


def _packet_sheet_ref(packet: dict[str, Any], sheet_name: str) -> str:
    sheet = str(sheet_name or "").strip()
    workbook_ref = str(packet.get("workbook_ref") or "").strip()
    for raw in packet.get("sheet_refs") or ():
        if isinstance(raw, dict) and str(raw.get("sheet_name") or "").strip() == sheet:
            value = str(raw.get("sheet_ref") or "").strip()
            if value:
                return value
    if not workbook_ref or not sheet:
        return ""
    return "sheet:sha256:" + hashlib.sha256(
        f"{workbook_ref}\x00{sheet}".encode("utf-8")
    ).hexdigest()


def _infer_type(values: list[Any]) -> str:
    if not values:
        return "empty"
    kinds: set[str] = set()
    for value in values:
        text = str(value).strip()
        if _DATE_RE.match(text) or _SLASH_DATE_RE.match(text):
            kinds.add("date")
            continue
        try:
            float(text)
        except (TypeError, ValueError):
            kinds.add("text")
        else:
            kinds.add("number")
    return next(iter(kinds)) if len(kinds) == 1 else "mixed"


def _ordered_unique(values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result


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
        "sheet_names": [],
        "columns": list(columns or []),
        "column_refs": [],
        "confirmed_columns": [],
        "ingestion_output": None,
        "detail": list(detail or []),
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "CANONICAL_INGESTION_SCHEMA_VERSION",
    "REQUEST_KIND_WORKBOOK",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "EXPECTED_INPUT_STATUS",
    "STATUS_READY",
    "STATUS_UNCONFIRMED_READY",
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
    "BLOCK_DUPLICATE_ANSWERS",
    "BLOCK_INVALID_COLUMN_REFS",
    "BLOCK_WORKBOOK_CONTEXT_REQUIRED",
    "build_service_1_unconfirmed_canonical_ingestion_output_v1",
    "build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
]
