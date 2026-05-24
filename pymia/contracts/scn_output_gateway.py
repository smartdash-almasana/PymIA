"""SCN output gateway.

Minimal PymIA -> Hermes boundary wrapper:
verify OperationalAuditResult, then build a RenderContract.

No Hermes execution, no Telegram, no MCP, no network, no production side effects.
"""

from __future__ import annotations

from typing import Any, Mapping

from .scn_operational_audit_verifier import (
    SCNVerificationError,
    verify_operational_audit_result,
)
from .scn_render_contract import SCNBoundaryError, build_render_contract


def build_render_contract_from_operational_audit_result(
    operational_audit_result: Mapping[str, Any],
    *,
    render_id: str | None = None,
    created_at: str | None = None,
    allowed_tone: str = "neutral_operational",
) -> dict[str, Any]:
    """Verify a sovereign OperationalAuditResult and return a RenderContract."""

    verified = verify_operational_audit_result(operational_audit_result)
    return build_render_contract(
        verified,
        render_id=render_id,
        created_at=created_at,
        allowed_tone=allowed_tone,
    )
