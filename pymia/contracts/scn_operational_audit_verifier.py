"""SCN OperationalAuditResult verifier (minimal implementation)."""

from __future__ import annotations

from typing import Any, Mapping


VALID_STATUSES = {"ok", "candidate", "blocked", "pending_data"}


class SCNVerificationError(ValueError):
    """Raised when OperationalAuditResult violates SCN minimum contract."""


def verify_operational_audit_result(result: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate minimal SCN contract for OperationalAuditResult.

    The function is fail-closed and returns the same mapping object when valid.
    """

    if not isinstance(result, Mapping):
        raise SCNVerificationError("OperationalAuditResult must be a mapping")

    required_fields = (
        "result_id",
        "tenant_id",
        "status",
        "sovereign_mark",
        "audit_trail_ref",
        "forbidden_inferences",
        "allowed_rendering",
    )
    for field in required_fields:
        if field not in result:
            raise SCNVerificationError(f"OperationalAuditResult missing {field}")

    status = result["status"]
    if status not in VALID_STATUSES:
        raise SCNVerificationError(f"OperationalAuditResult invalid status: {status}")

    sovereign_mark = result["sovereign_mark"]
    if sovereign_mark is None or (isinstance(sovereign_mark, str) and not sovereign_mark.strip()):
        raise SCNVerificationError("OperationalAuditResult missing sovereign_mark")

    forbidden_inferences = result["forbidden_inferences"]
    if not isinstance(forbidden_inferences, list):
        raise SCNVerificationError("OperationalAuditResult forbidden_inferences must be a list")

    allowed_rendering = result["allowed_rendering"]
    if not isinstance(allowed_rendering, Mapping):
        raise SCNVerificationError("OperationalAuditResult allowed_rendering must be a mapping")

    return result
