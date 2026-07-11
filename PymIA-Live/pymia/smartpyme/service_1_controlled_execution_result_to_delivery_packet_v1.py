"""
Service 1 Controlled Execution Result -> Delivery Packet V1

Fail-closed delivery packet builder for the Servicio 1 assisted flow.

Flow position:

    controlled_execution_result (READY) -> DELIVERY packet (this module)

Only when the owner has explicitly authorized delivery (``delivery_authorized=True``
passed in the request) does this module materialize a minimal delivery on disk:

    README.md
    manifest.json
    execution_result.json
    hashes.json

The delivery is written ONLY under the explicitly provided ``output_dir``; no
other paths are touched. The output is fail-closed: any missing precondition,
invalid input, forbidden flag, or absent authorization blocks creation.

Output flags:
- delivery_created=True / product_ready=True / delivery_authorized=True
- execution_executed=True (carried from the execution result)
- diagnosis_generated=False / runtime_authorized=False / tool_execution_authorized=False
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from pymia.smartpyme.service_1_owner_validated_dry_run_to_controlled_execution_result_v1 import (
    STATUS_READY as EXECUTION_STATUS_READY,
)

SCHEMA_VERSION = "SERVICE_1_CONTROLLED_EXECUTION_RESULT_TO_DELIVERY_PACKET_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "CONTROLLED_EXECUTION_RESULT_TO_DELIVERY_PACKET"

STATUS_READY = "DELIVERY_PACKET_READY"
STATUS_BLOCKED = "BLOCKED"

# Deliverable file names (written only under output_dir).
_README_NAME = "README.md"
_MANIFEST_NAME = "manifest.json"
_RESULT_NAME = "execution_result.json"
_HASHES_NAME = "hashes.json"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_INPUT_NOT_DICT = "EXECUTION_RESULT_NOT_DICT"
BLOCK_INPUT_FLAGS_FORBIDDEN = "EXECUTION_RESULT_SAFETY_FLAGS_FORBIDDEN"
BLOCK_WRONG_STATUS = "EXECUTION_RESULT_WRONG_STATUS"
BLOCK_MISSING_EXECUTION = "MISSING_EXECUTION"
BLOCK_MISSING_RESULTS = "MISSING_RESULTS"
BLOCK_DELIVERY_NOT_AUTHORIZED = "DELIVERY_NOT_AUTHORIZED"
BLOCK_MISSING_OUTPUT_DIR = "MISSING_OUTPUT_DIR"

_REQUEST_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "diagnosis_generated",
)

_INPUT_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_controlled_execution_result_to_delivery_packet_v1(
    *,
    controlled_execution_result_packet: Any,
    output_dir: Any,
    delivery_authorized: bool = False,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Materialize a minimal delivery packet from a READY execution result.

    Args:
        controlled_execution_result_packet: The execution result (status
            CONTROLLED_EXECUTION_RESULT_READY).
        output_dir: Directory (path-like/str) where the 4 deliverables are written.
        delivery_authorized: MUST be True (explicit owner authorization). Otherwise
            the build is BLOCKED and nothing is written.

    Returns:
        A delivery packet dict. Status is DELIVERY_PACKET_READY (with
        ``deliverables`` listing written files + hashes) or BLOCKED.
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(controlled_execution_result_packet, dict) or not controlled_execution_result_packet:
        return _blocked(BLOCK_INPUT_NOT_DICT)

    if any(controlled_execution_result_packet.get(flag) for flag in _INPUT_FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_INPUT_FLAGS_FORBIDDEN,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    if controlled_execution_result_packet.get("status") != EXECUTION_STATUS_READY:
        return _blocked(
            BLOCK_WRONG_STATUS,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    # The execution must have actually run.
    if not controlled_execution_result_packet.get("execution_executed"):
        return _blocked(
            BLOCK_MISSING_EXECUTION,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    results = controlled_execution_result_packet.get("results")
    if not isinstance(results, (list, tuple)) or not results:
        return _blocked(
            BLOCK_MISSING_RESULTS,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    # Explicit delivery authorization is mandatory.
    if not delivery_authorized:
        return _blocked(
            BLOCK_DELIVERY_NOT_AUTHORIZED,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    if output_dir is None:
        return _blocked(
            BLOCK_MISSING_OUTPUT_DIR,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )
    out_path = Path(output_dir)
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path
    try:
        out_path.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError) as exc:  # pragma: no cover - filesystem edge
        return _blocked(
            BLOCK_MISSING_OUTPUT_DIR,
            case_id=controlled_execution_result_packet.get("case_id"),
            source_kind=controlled_execution_result_packet.get("source_kind"),
            filename=controlled_execution_result_packet.get("filename"),
        )

    deliverables = _write_deliverables(
        out_path=out_path,
        case_id=controlled_execution_result_packet.get("case_id"),
        source_kind=controlled_execution_result_packet.get("source_kind"),
        filename=controlled_execution_result_packet.get("filename"),
        roles=list(controlled_execution_result_packet.get("roles") or []),
        results=list(results),
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": controlled_execution_result_packet.get("case_id"),
        "source_kind": controlled_execution_result_packet.get("source_kind"),
        "filename": controlled_execution_result_packet.get("filename"),
        "output_dir": str(out_path),
        "deliverables": deliverables,
        "delivery_created": True,
        "product_ready": True,
        "delivery_authorized": True,
        "execution_executed": True,
        "diagnosis_generated": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
    }


def _write_deliverables(
    *,
    out_path: Path,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    roles: list[str],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Write exactly the 4 deliverables under out_path and return their manifest."""
    readme = _build_readme(case_id=case_id, filename=filename, roles=roles)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "roles": roles,
        "files": [
            _README_NAME,
            _MANIFEST_NAME,
            _RESULT_NAME,
            _HASHES_NAME,
        ],
    }
    result_payload = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "result_count": len(results),
        "results": results,
    }

    files_content = {
        _README_NAME: readme,
        _MANIFEST_NAME: json.dumps(manifest, indent=2, ensure_ascii=False),
        _RESULT_NAME: json.dumps(result_payload, indent=2, ensure_ascii=False),
    }

    written: list[dict[str, Any]] = []
    for name, content in files_content.items():
        path = out_path / name
        path.write_text(content, encoding="utf-8")
        written.append({"name": name, "path": str(path), "bytes": len(content.encode("utf-8"))})

    # hashes.json covers the 3 written data files (deterministic SHA-256).
    hashes = {
        "schema_version": SCHEMA_VERSION,
        "algorithm": "sha256",
        "files": {
            name: _sha256(content)
            for name, content in files_content.items()
        },
    }
    hash_path = out_path / _HASHES_NAME
    hash_path.write_text(json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8")
    written.append(
        {"name": _HASHES_NAME, "path": str(hash_path), "bytes": hash_path.stat().st_size}
    )

    return written


def _build_readme(
    *,
    case_id: Optional[str],
    filename: Optional[str],
    roles: list[str],
) -> str:
    return (
        "# Controlled Execution Delivery\n"
        "\n"
        f"- case_id: {case_id}\n"
        f"- source: {filename}\n"
        f"- semantic roles: {', '.join(roles) if roles else '(none)'}\n"
        "\n"
        "## Files\n"
        f"- `{_MANIFEST_NAME}`: manifest of delivered files.\n"
        f"- `{_RESULT_NAME}`: execution result payload.\n"
        f"- `{_HASHES_NAME}`: SHA-256 hashes of the delivered files.\n"
        "\n"
        "This delivery was produced under explicit owner authorization. "
        "No external tools were executed and no diagnosis was generated.\n"
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
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
        "output_dir": None,
        "deliverables": [],
        "delivery_created": False,
        "product_ready": False,
        "delivery_authorized": False,
        "execution_executed": False,
        "diagnosis_generated": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_INPUT_NOT_DICT",
    "BLOCK_INPUT_FLAGS_FORBIDDEN",
    "BLOCK_WRONG_STATUS",
    "BLOCK_MISSING_EXECUTION",
    "BLOCK_MISSING_RESULTS",
    "BLOCK_DELIVERY_NOT_AUTHORIZED",
    "BLOCK_MISSING_OUTPUT_DIR",
    "build_service_1_controlled_execution_result_to_delivery_packet_v1",
]
