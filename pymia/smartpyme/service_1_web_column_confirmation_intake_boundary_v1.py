"""
Service 1 Web Column Confirmation Intake Boundary V1

Minimal, deterministic intake boundary for Servicio 1 assisted flow.

Flow implemented (boundary only):

    uploaded/local XLSX -> canonical reader -> owner question packet

This module DOES NOT:
- authorize runtime, product or delivery,
- execute tools,
- create delivery,
- parse XLSX by itself (it delegates to the canonical reader),
- use openpyxl directly,
- implement any web UI,
- resolve the full assisted flow.

It only turns an accepted XLSX source into a canonical owner question
packet asking the owner to confirm what each detected column means.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Literal, Optional

from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import (
    read_xlsx_to_normalized_table_v1,
)

SCHEMA_VERSION = "SERVICE_1_WEB_COLUMN_CONFIRMATION_INTAKE_BOUNDARY_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "WEB_COLUMN_CONFIRMATION_INTAKE"
MAX_QUESTIONS = 50

SourceKind = Literal["local_path", "uploaded_bytes"]

# Block reason constants (stable identifiers for tests and callers).
BLOCK_NO_SOURCE = "NO_SOURCE"
BLOCK_DUAL_SOURCE = "DUAL_SOURCE"
BLOCK_INVALID_EXTENSION = "INVALID_EXTENSION"
BLOCK_MISSING_FILENAME = "MISSING_FILENAME"
BLOCK_READER_FAILED = "CANONICAL_READER_FAILED"
BLOCK_RUNTIME_FLAG_FORBIDDEN = "RUNTIME_OR_DELIVERY_FLAG_FORBIDDEN"


def build_service_1_web_column_confirmation_intake_boundary_v1(
    *,
    local_xlsx_path: Optional[str | Path] = None,
    uploaded_xlsx_bytes: Optional[bytes] = None,
    uploaded_filename: Optional[str] = None,
    runtime_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
) -> dict[str, Any]:
    """Build a canonical owner question packet from a single XLSX source.

    Exactly one input source must be provided:
      1. ``local_xlsx_path``: a path to a local .xlsx file, or
      2. ``uploaded_xlsx_bytes`` + ``uploaded_filename``: uploaded content.

    The function never executes tools, never creates delivery and never
    authorizes runtime/product/delivery. Passing any of the runtime/product/
    delivery flags as ``True`` is itself a blocking condition, because this
    boundary must remain observation-only.

    Returns:
        A canonical intake packet dict. On any blocking condition the packet
        has ``status == "BLOCKED"`` and a ``blocked_reason``; otherwise
        ``status == "NEEDS_OWNER_CONFIRMATION"`` with ``owner_questions``.
    """
    # Hard rule: this boundary can never be invoked with runtime/delivery on.
    if runtime_authorized or product_ready or delivery_authorized:
        return _blocked(
            BLOCK_RUNTIME_FLAG_FORBIDDEN,
            source_kind=None,
            filename=None,
        )

    has_local = local_xlsx_path is not None
    has_uploaded = uploaded_xlsx_bytes is not None

    # Source arity: exactly one.
    if not has_local and not has_uploaded:
        return _blocked(BLOCK_NO_SOURCE, source_kind=None, filename=None)
    if has_local and has_uploaded:
        return _blocked(BLOCK_DUAL_SOURCE, source_kind=None, filename=None)

    if has_local:
        source_kind: SourceKind = "local_path"
        filename = os.path.basename(str(local_xlsx_path))
        if not _has_xlsx_extension(filename):
            return _blocked(
                BLOCK_INVALID_EXTENSION,
                source_kind=source_kind,
                filename=filename,
            )
        normalized_table = read_xlsx_to_normalized_table_v1(local_xlsx_path)
        case_id = _case_id(source_kind, filename)
    else:
        source_kind = "uploaded_bytes"
        if not uploaded_filename or not str(uploaded_filename).strip():
            return _blocked(
                BLOCK_MISSING_FILENAME,
                source_kind=source_kind,
                filename=None,
            )
        filename = os.path.basename(str(uploaded_filename).strip())
        if not _has_xlsx_extension(filename):
            return _blocked(
                BLOCK_INVALID_EXTENSION,
                source_kind=source_kind,
                filename=filename,
            )
        normalized_table = _read_uploaded_bytes_via_canonical_reader(
            uploaded_xlsx_bytes, filename
        )
        case_id = _case_id(source_kind, filename, uploaded_xlsx_bytes)

    if normalized_table.get("status") != "OK":
        return _blocked(
            BLOCK_READER_FAILED,
            source_kind=source_kind,
            filename=filename,
            case_id=case_id,
            reader_blocking_errors=list(normalized_table.get("blocking_errors", [])),
        )

    columns = list(normalized_table.get("headers", []))
    owner_questions = _build_owner_questions(columns)

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": "NEEDS_OWNER_CONFIRMATION",
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "columns": columns,
        "question_count": len(owner_questions),
        "owner_questions": owner_questions,
        "normalized_table": normalized_table,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def _read_uploaded_bytes_via_canonical_reader(
    uploaded_xlsx_bytes: bytes,
    filename: str,
) -> dict[str, Any]:
    """Persist uploaded bytes to a temp .xlsx and read via the canonical reader.

    This keeps XLSX parsing inside the single allowed reader; no openpyxl is
    used here directly and no parser is duplicated.
    """
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx", delete=False
        ) as tmp_file:
            tmp_file.write(uploaded_xlsx_bytes)
            tmp_path = tmp_file.name
        return read_xlsx_to_normalized_table_v1(tmp_path)
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _build_owner_questions(columns: list[str]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    counter = 0
    for column in columns:
        column_name = str(column).strip()
        if not column_name:
            continue
        counter += 1
        questions.append(
            {
                "question_id": f"col_confirm_{counter:03d}",
                "column_name": column_name,
                "question": (
                    f"\u00bfQu\u00e9 representa la columna '{column_name}' "
                    f"en este archivo?"
                ),
                "answer_type": "owner_text",
                "required": True,
            }
        )
        if counter >= MAX_QUESTIONS:
            break
    return questions


def _has_xlsx_extension(filename: str) -> bool:
    return filename.lower().endswith(".xlsx")


def _case_id(
    source_kind: str,
    filename: str,
    content: Optional[bytes] = None,
) -> str:
    hasher = hashlib.sha256()
    hasher.update(source_kind.encode("utf-8"))
    hasher.update(b"\x00")
    hasher.update(filename.encode("utf-8"))
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
        "columns": [],
        "question_count": 0,
        "owner_questions": [],
        "normalized_table": None,
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
    "build_service_1_web_column_confirmation_intake_boundary_v1",
]
