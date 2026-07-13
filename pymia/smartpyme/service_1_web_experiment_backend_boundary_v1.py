"""
Service 1 Web Experiment Backend Boundary V1

Experimental backend boundary for web upload that delegates to the REAL
``service_1_assisted_flow_orchestrator_v1`` (the authority for the closed
Servicio 1 assisted flow).

This module is a thin transport boundary. It does NOT:
- parse XLSX itself (no SheetJS, no openpyxl, no duplicated parser);
- generate fake owner questions;
- run an LLM;
- touch the legacy CLI;
- call external APIs.

It accepts exactly ONE source of the workbook:
- ``local_xlsx_path`` (a path on disk), OR
- ``uploaded_xlsx_bytes`` + ``uploaded_filename`` (raw upload content).

When the source is uploaded bytes, the bytes are persisted to a temporary
``.xlsx`` file and that path is handed to the orchestrator. The temp file is
always removed afterwards (best-effort). No XLSX parsing happens here — the
orchestrator (via its boundary) reads the file through the canonical reader.

All decisions (authorization, validation, delivery) and the delivery artifact
come straight from the orchestrator. If the orchestrator blocks (missing
answers, rejected auth/validation, no delivery authorization) this boundary
returns the orchestrator's packet unchanged (status/trace/delivery_packet).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Optional

from pymia.smartpyme.service_1_assisted_flow_orchestrator_v1 import (
    STATUS_READY as ORCHESTRATOR_READY,
    build_service_1_assisted_flow_orchestrator_v1 as run_orchestrator,
)

SCHEMA_VERSION = "SERVICE_1_WEB_EXPERIMENT_BACKEND_BOUNDARY_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "WEB_EXPERIMENT_BACKEND_BOUNDARY"

STATUS_READY = "WEB_BACKEND_DELIVERY_READY"
STATUS_BLOCKED = "BLOCKED"

# Stable block reasons local to this boundary (transport-layer rejections).
BLOCK_NO_SOURCE = "NO_SOURCE_PROVIDED"
BLOCK_DUAL_SOURCE = "DUAL_SOURCE_PROVIDED"
BLOCK_INVALID_EXTENSION = "INVALID_FILE_EXTENSION"

_REQUIRED_EXTENSION = ".xlsx"


def build_service_1_web_experiment_backend_boundary_v1(
    *,
    local_xlsx_path: Any = None,
    uploaded_xlsx_bytes: Optional[bytes] = None,
    uploaded_filename: Optional[str] = None,
    owner_column_answers: Any,
    semantic_owner_answers: Any,
    owner_authorization: str = "accept",
    owner_validation: str = "accept",
    delivery_authorized: bool = False,
    output_dir: Any = None,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Run the assisted flow for a web upload, via the real orchestrator.

    Args:
        local_xlsx_path: Path to a local .xlsx file (exactly one source).
        uploaded_xlsx_bytes: Raw bytes of an uploaded .xlsx (exactly one source).
        uploaded_filename: Filename for the upload (used for extension check + name).
        owner_column_answers / semantic_owner_answers / owner_authorization /
        owner_validation / delivery_authorized / output_dir: forwarded verbatim to
        the orchestrator.

    Returns:
        A packet. On success (orchestrator ASSISTED_FLOW_DELIVERY_READY) status is
        WEB_BACKEND_DELIVERY_READY wrapping the orchestrator output. On any
        transport rejection (no/dual/invalid source) status is BLOCKED. Otherwise
        the orchestrator's own BLOCKED packet is propagated unchanged.
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, diagnosis_generated)):
        return _blocked(BLOCK_DUAL_SOURCE)  # treat forbidden flags as a bad request

    has_local = local_xlsx_path is not None
    has_uploaded = uploaded_xlsx_bytes is not None

    if not has_local and not has_uploaded:
        return _blocked(BLOCK_NO_SOURCE)
    if has_local and has_uploaded:
        return _blocked(BLOCK_DUAL_SOURCE)

    resolved_path: Optional[str] = None
    temp_path: Optional[Path] = None
    try:
        if has_local:
            resolved_path = str(local_xlsx_path)
        else:
            # Persist uploaded bytes to a temp .xlsx, then hand the path to the
            # orchestrator. No parsing happens here.
            name = _safe_upload_name(uploaded_filename)
            if not name.lower().endswith(_REQUIRED_EXTENSION):
                return _blocked(BLOCK_INVALID_EXTENSION)
            fd, temp_str = tempfile.mkstemp(suffix=_REQUIRED_EXTENSION, prefix="s1_upload_")
            os.close(fd)
            temp_path = Path(temp_str)
            temp_path.write_bytes(uploaded_xlsx_bytes)
            resolved_path = str(temp_path)

        orch = run_orchestrator(
            local_xlsx_path=resolved_path,
            owner_column_answers=owner_column_answers,
            semantic_owner_answers=semantic_owner_answers,
            owner_authorization=owner_authorization,
            owner_validation=owner_validation,
            delivery_authorized=delivery_authorized,
            output_dir=output_dir,
        )

        if orch.get("status") == ORCHESTRATOR_READY:
            return {
                "schema_version": SCHEMA_VERSION,
                "service_name": SERVICE_NAME,
                "packet_type": PACKET_TYPE,
                "status": STATUS_READY,
                "blocked_reason": None,
                "orchestrator_status": orch.get("status"),
                "trace": orch.get("trace", {}),
                "delivery_packet": orch.get("delivery_packet"),
                "delivery_created": bool(orch.get("delivery_created")),
                "delivery_authorized": bool(orch.get("delivery_authorized")),
                "product_ready": bool(orch.get("product_ready")),
                "runtime_authorized": False,
                "tool_execution_authorized": False,
                "diagnosis_generated": False,
            }

        # Orchestrator blocked or produced a non-ready status: propagate as-is.
        return {
            "schema_version": SCHEMA_VERSION,
            "service_name": SERVICE_NAME,
            "packet_type": PACKET_TYPE,
            "status": orch.get("status", STATUS_BLOCKED),
            "blocked_reason": orch.get("blocked_reason"),
            "orchestrator_status": orch.get("status"),
            "trace": orch.get("trace", {}),
            "delivery_packet": orch.get("delivery_packet"),
            "delivery_created": bool(orch.get("delivery_created")),
            "delivery_authorized": bool(orch.get("delivery_authorized")),
            "product_ready": bool(orch.get("product_ready")),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "diagnosis_generated": False,
        }
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _safe_upload_name(filename: Optional[str]) -> str:
    name = str(filename or "").strip()
    if not name:
        return "upload.xlsx"
    # Keep only the basename to avoid path traversal via uploaded_filename.
    return os.path.basename(name) or "upload.xlsx"


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "orchestrator_status": None,
        "trace": {},
        "delivery_packet": None,
        "delivery_created": False,
        "delivery_authorized": False,
        "product_ready": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_NO_SOURCE",
    "BLOCK_DUAL_SOURCE",
    "BLOCK_INVALID_EXTENSION",
    "build_service_1_web_experiment_backend_boundary_v1",
]
