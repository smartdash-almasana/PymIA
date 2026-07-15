"""Canonical XLSX intake boundary for Servicio 1.

Reads one or every non-empty worksheet through the canonical XLSX reader and
builds sheet-qualified owner questions. No runtime, tool or delivery authority
is granted here.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Literal, Optional

from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import (
    read_xlsx_to_normalized_table_v1,
    read_xlsx_to_normalized_tables_v1,
)

SCHEMA_VERSION = "SERVICE_1_WEB_COLUMN_CONFIRMATION_INTAKE_BOUNDARY_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "WEB_COLUMN_CONFIRMATION_INTAKE"
MAX_QUESTIONS = 50

SourceKind = Literal["local_path", "uploaded_bytes"]

BLOCK_NO_SOURCE = "NO_SOURCE"
BLOCK_DUAL_SOURCE = "DUAL_SOURCE"
BLOCK_INVALID_EXTENSION = "INVALID_EXTENSION"
BLOCK_MISSING_FILENAME = "MISSING_FILENAME"
BLOCK_READER_FAILED = "CANONICAL_READER_FAILED"
BLOCK_RUNTIME_FLAG_FORBIDDEN = "RUNTIME_OR_DELIVERY_FLAG_FORBIDDEN"
BLOCK_SHEET_SELECTION_CONFLICT = "SHEET_SELECTION_CONFLICT"
BLOCK_INVALID_SHEET_SELECTION = "INVALID_SHEET_SELECTION"
BLOCK_TOO_MANY_COLUMNS = "TOO_MANY_COLUMNS"


def build_service_1_web_column_confirmation_intake_boundary_v1(
    *,
    local_xlsx_path: Optional[str | Path] = None,
    uploaded_xlsx_bytes: Optional[bytes] = None,
    uploaded_filename: Optional[str] = None,
    sheet_name: Optional[str] = None,
    sheet_names: Optional[list[str] | tuple[str, ...]] = None,
    include_all_sheets: bool = False,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    """Build sheet-qualified owner questions from one canonical XLSX source.

    With no sheet selection, the historical first non-empty worksheet is used.
    A single ``sheet_name``, ordered ``sheet_names`` selection, or explicit
    ``include_all_sheets=True`` may be supplied. These modes are exclusive.
    """
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(BLOCK_RUNTIME_FLAG_FORBIDDEN, source_kind=None, filename=None)

    selected_sheets, selection_error = _sheet_selection(
        sheet_name=sheet_name,
        sheet_names=sheet_names,
        include_all_sheets=include_all_sheets,
    )
    if selection_error is not None:
        return _blocked(selection_error, source_kind=None, filename=None)

    has_local = local_xlsx_path is not None
    has_uploaded = uploaded_xlsx_bytes is not None
    if not has_local and not has_uploaded:
        return _blocked(BLOCK_NO_SOURCE, source_kind=None, filename=None)
    if has_local and has_uploaded:
        return _blocked(BLOCK_DUAL_SOURCE, source_kind=None, filename=None)

    if has_local:
        source_kind: SourceKind = "local_path"
        filename = os.path.basename(str(local_xlsx_path))
        if not _has_xlsx_extension(filename):
            return _blocked(BLOCK_INVALID_EXTENSION, source_kind=source_kind, filename=filename)
        normalized_tables = _read_local_source(
            local_xlsx_path,
            selected_sheets=selected_sheets,
            include_all_sheets=include_all_sheets,
        )
        case_id = _case_id(
            source_kind,
            filename,
            selected_sheets=selected_sheets,
            include_all_sheets=include_all_sheets,
        )
    else:
        source_kind = "uploaded_bytes"
        if not uploaded_filename or not str(uploaded_filename).strip():
            return _blocked(BLOCK_MISSING_FILENAME, source_kind=source_kind, filename=None)
        filename = os.path.basename(str(uploaded_filename).strip())
        if not _has_xlsx_extension(filename):
            return _blocked(BLOCK_INVALID_EXTENSION, source_kind=source_kind, filename=filename)
        normalized_tables = _read_uploaded_bytes_via_canonical_reader(
            uploaded_xlsx_bytes,
            sheet_names=selected_sheets,
            include_all_sheets=include_all_sheets,
        )
        case_id = _case_id(
            source_kind,
            filename,
            uploaded_xlsx_bytes,
            selected_sheets=selected_sheets,
            include_all_sheets=include_all_sheets,
        )

    blocked_tables = [table for table in normalized_tables if table.get("status") != "OK"]
    if blocked_tables:
        errors: list[str] = []
        for table in blocked_tables:
            label = str(table.get("sheet_name") or "workbook")
            for error in table.get("blocking_errors", []):
                errors.append(f"{label}: {error}")
        return _blocked(
            BLOCK_READER_FAILED,
            source_kind=source_kind,
            filename=filename,
            case_id=case_id,
            reader_blocking_errors=errors,
        )

    column_refs, owner_questions = _build_owner_questions(normalized_tables)
    if len(column_refs) > MAX_QUESTIONS:
        return _blocked(
            BLOCK_TOO_MANY_COLUMNS,
            source_kind=source_kind,
            filename=filename,
            case_id=case_id,
            reader_blocking_errors=[
                f"Detected {len(column_refs)} columns; maximum is {MAX_QUESTIONS}."
            ],
        )

    workbook_sheet_names = [str(table.get("sheet_name") or "").strip() for table in normalized_tables]
    columns = [ref["column_name"] for ref in column_refs]
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": "NEEDS_OWNER_CONFIRMATION",
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "sheet_names": workbook_sheet_names,
        "columns": columns,
        "column_refs": column_refs,
        "question_count": len(owner_questions),
        "owner_questions": owner_questions,
        "normalized_table": normalized_tables[0] if len(normalized_tables) == 1 else None,
        "normalized_tables": normalized_tables,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _sheet_selection(
    *,
    sheet_name: str | None,
    sheet_names: list[str] | tuple[str, ...] | None,
    include_all_sheets: bool,
) -> tuple[tuple[str, ...] | None, str | None]:
    selection_modes = sum(
        (
            sheet_name is not None,
            sheet_names is not None,
            bool(include_all_sheets),
        )
    )
    if selection_modes > 1:
        return None, BLOCK_SHEET_SELECTION_CONFLICT
    if sheet_name is not None:
        selected = str(sheet_name).strip()
        return ((selected,), None) if selected else (None, BLOCK_INVALID_SHEET_SELECTION)
    if sheet_names is None:
        return None, None
    if not isinstance(sheet_names, (list, tuple)):
        return None, BLOCK_INVALID_SHEET_SELECTION
    cleaned = tuple(str(item).strip() for item in sheet_names if str(item).strip())
    if not cleaned or len(cleaned) != len(sheet_names) or len(set(cleaned)) != len(cleaned):
        return None, BLOCK_INVALID_SHEET_SELECTION
    return cleaned, None


def _read_local_source(
    xlsx_path: str | Path,
    *,
    selected_sheets: tuple[str, ...] | None,
    include_all_sheets: bool,
) -> list[dict[str, Any]]:
    if selected_sheets is not None:
        return read_xlsx_to_normalized_tables_v1(
            xlsx_path, sheet_names=selected_sheets
        )
    if include_all_sheets:
        return read_xlsx_to_normalized_tables_v1(xlsx_path)
    return [read_xlsx_to_normalized_table_v1(xlsx_path)]


def _read_uploaded_bytes_via_canonical_reader(
    uploaded_xlsx_bytes: bytes,
    *,
    sheet_names: tuple[str, ...] | None,
    include_all_sheets: bool,
) -> list[dict[str, Any]]:
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_file.write(uploaded_xlsx_bytes)
            tmp_path = tmp_file.name
        return _read_local_source(
            tmp_path,
            selected_sheets=sheet_names,
            include_all_sheets=include_all_sheets,
        )
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _build_owner_questions(
    normalized_tables: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    raw_refs: list[dict[str, str]] = []
    counter = 0
    for table in normalized_tables:
        sheet = str(table.get("sheet_name") or "").strip()
        headers = list(table.get("headers") or [])
        normalized_headers = list(table.get("normalized_headers") or [])
        for index, raw_column in enumerate(headers):
            column = str(raw_column).strip()
            if not column:
                continue
            counter += 1
            question_id = f"col_confirm_{counter:03d}"
            normalized_column = (
                str(normalized_headers[index]).strip()
                if index < len(normalized_headers)
                else column
            )
            raw_refs.append(
                {
                    "question_id": question_id,
                    "sheet_name": sheet,
                    "column_name": column,
                    "normalized_column_name": normalized_column,
                }
            )

    multisheet = len({ref["sheet_name"] for ref in raw_refs}) > 1
    column_refs: list[dict[str, str]] = []
    owner_questions: list[dict[str, Any]] = []
    for ref in raw_refs:
        field_id = ref["question_id"] if multisheet else ref["column_name"]
        complete_ref = {**ref, "field_id": field_id}
        column_refs.append(complete_ref)
        owner_questions.append(
            {
                **complete_ref,
                "question": (
                    f"En la hoja '{ref['sheet_name']}', ¿qué representa la columna "
                    f"'{ref['column_name']}'?"
                ),
                "answer_type": "owner_text",
                "required": True,
            }
        )
    return column_refs, owner_questions


def _has_xlsx_extension(filename: str) -> bool:
    return filename.lower().endswith(".xlsx")


def _case_id(
    source_kind: str,
    filename: str,
    content: Optional[bytes] = None,
    *,
    selected_sheets: tuple[str, ...] | None = None,
    include_all_sheets: bool = False,
) -> str:
    hasher = hashlib.sha256()
    hasher.update(source_kind.encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(filename.encode("utf-8"))
    hasher.update(b"\x00")
    if include_all_sheets:
        hasher.update(b"ALL_SHEETS")
    elif selected_sheets:
        hasher.update("\x1f".join(selected_sheets).encode("utf-8"))
    else:
        hasher.update(b"DEFAULT_SHEET")
    if content is not None:
        hasher.update(b"\x00")
        hasher.update(content)
    return "case_" + hasher.hexdigest()[:16]


def _blocked(
    reason: str,
    *,
    source_kind: Optional[str],
    filename: Optional[str],
    case_id: Optional[str] = None,
    reader_blocking_errors: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": "BLOCKED",
        "blocked_reason": reason,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "sheet_names": [],
        "columns": [],
        "column_refs": [],
        "question_count": 0,
        "owner_questions": [],
        "normalized_table": None,
        "normalized_tables": [],
        "reader_blocking_errors": list(reader_blocking_errors or []),
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "MAX_QUESTIONS",
    "BLOCK_NO_SOURCE",
    "BLOCK_DUAL_SOURCE",
    "BLOCK_INVALID_EXTENSION",
    "BLOCK_MISSING_FILENAME",
    "BLOCK_READER_FAILED",
    "BLOCK_RUNTIME_FLAG_FORBIDDEN",
    "BLOCK_SHEET_SELECTION_CONFLICT",
    "BLOCK_INVALID_SHEET_SELECTION",
    "BLOCK_TOO_MANY_COLUMNS",
    "build_service_1_web_column_confirmation_intake_boundary_v1",
]
