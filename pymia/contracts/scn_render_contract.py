"""SCN RenderContract boundary helpers.

This module is intentionally small and dependency-light. It does not call Hermes,
Telegram, MCP, network services, or runtime gateways. It only converts a sovereign
OperationalAuditResult-like mapping into a RenderContract-like mapping that Hermes
may render without reinterpretation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


FAIL_CLOSED_STATUSES = {"blocked", "pending_data"}


class SCNBoundaryError(ValueError):
    """Raised when an SCN boundary contract cannot be satisfied."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _require_mapping(value: Mapping[str, Any] | dict[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SCNBoundaryError("OperationalAuditResult must be a mapping")
    return value


def build_render_contract(
    operational_audit_result: Mapping[str, Any],
    *,
    render_id: str | None = None,
    created_at: str | None = None,
    allowed_tone: str = "neutral_operational",
) -> dict[str, Any]:
    """Build the minimal RenderContract Hermes is allowed to render.

    Required sovereign controls:
    - result_id
    - tenant_id
    - status
    - sovereign_mark

    Preserved safety controls:
    - forbidden_inferences
    - missing_evidence as next_questions when pending/blocked
    - blocked_message when fail-closed status is present

    The returned contract intentionally excludes findings. Hermes renders; Hermes
    does not reinterpret or complete findings.
    """

    result = _require_mapping(operational_audit_result)

    result_id = result.get("result_id")
    tenant_id = result.get("tenant_id")
    status = result.get("status")
    sovereign_mark = result.get("sovereign_mark")

    missing = [str(item) for item in _as_list(result.get("missing_evidence"))]
    forbidden = [str(item) for item in _as_list(result.get("forbidden_inferences"))]
    allowed_rendering = result.get("allowed_rendering") or {}

    if not result_id:
        raise SCNBoundaryError("OperationalAuditResult missing result_id")
    if not tenant_id:
        raise SCNBoundaryError("OperationalAuditResult missing tenant_id")
    if not status:
        raise SCNBoundaryError("OperationalAuditResult missing status")
    if not sovereign_mark:
        raise SCNBoundaryError("OperationalAuditResult missing sovereign_mark")
    if not isinstance(allowed_rendering, Mapping):
        raise SCNBoundaryError("allowed_rendering must be a mapping")

    summary = str(allowed_rendering.get("summary") or "")
    next_questions = [str(item) for item in _as_list(allowed_rendering.get("next_questions"))]
    next_steps = [str(item) for item in _as_list(allowed_rendering.get("next_steps"))]
    references = [str(item) for item in _as_list(allowed_rendering.get("references"))]

    blocked_message = str(allowed_rendering.get("blocked_message") or "")
    if status in FAIL_CLOSED_STATUSES:
        if missing and not next_questions:
            next_questions = missing
        if not blocked_message:
            blocked_message = "PymIA cannot complete this result without additional evidence."
        next_steps = []

    return {
        "schema_version": "scn.render_contract.v1",
        "render_id": render_id or f"render_{uuid4().hex}",
        "result_ref": str(result_id),
        "tenant_id": str(tenant_id),
        "summary": summary,
        "next_questions": next_questions,
        "next_steps": next_steps,
        "blocked_message": blocked_message,
        "forbidden_inferences": forbidden,
        "references": references,
        "allowed_tone": allowed_tone,
        "created_at": created_at or _utc_now_iso(),
    }
