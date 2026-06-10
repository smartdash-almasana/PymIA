from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pymia.contracts.owner_semantic_confirmation import OwnerSemanticConfirmationGate
from pymia.contracts.owner_semantic_evidence_requests import OwnerSemanticEvidenceRequest
from pymia.smartpyme.owner_semantic_evidence_request_builder import (
    build_owner_semantic_evidence_request,
)

OwnerConfirmedSemanticRequestFlowStatus = Literal[
    "BLOCKED_ACTIONABLE",
    "PENDING_OWNER_CONFIRMATION",
    "NEEDS_REINTERPRETATION",
]


@dataclass(frozen=True)
class OwnerConfirmedSemanticRequestFlowResult:
    flow_status: OwnerConfirmedSemanticRequestFlowStatus
    semantic_evidence_requests: tuple[OwnerSemanticEvidenceRequest, ...] = field(default_factory=tuple)
    reason: str = ""
    unsupported_missing_keys: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_blocked_actionable(self) -> bool:
        return self.flow_status == "BLOCKED_ACTIONABLE"


def _normalize_missing_keys(values: list[str] | tuple[str, ...] | None) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values or []:
        key = str(value or "").strip()
        if key and key not in seen:
            seen.add(key)
            normalized.append(key)
    return normalized


def build_owner_confirmed_semantic_request_flow(
    *,
    confirmation_gate: OwnerSemanticConfirmationGate,
    missing_keys: list[str] | tuple[str, ...],
    source_ref: str,
    metadata: dict[str, Any] | None = None,
) -> OwnerConfirmedSemanticRequestFlowResult:
    """Conecta gate semántico confirmado/corregido con pedidos accionables.

    Función pura, sin side effects. No computa, no diagnostica y no promueve
    narrativa del dueño a evidencia dura.
    """

    source_ref_text = str(source_ref or "").strip()
    if not source_ref_text:
        raise ValueError("source_ref must be non-empty")

    normalized_missing_keys = _normalize_missing_keys(missing_keys)
    base_metadata = dict(metadata or {})
    base_metadata.update(
        {
            "confirmation_gate_id": confirmation_gate.gate_id,
            "confirmation_status": confirmation_gate.status,
            "confirmation_target_type": confirmation_gate.target_type,
            "does_resolve_structural_input": False,
            "produces_findings": False,
        }
    )

    if confirmation_gate.status == "PENDING_OWNER_CONFIRMATION":
        return OwnerConfirmedSemanticRequestFlowResult(
            flow_status="PENDING_OWNER_CONFIRMATION",
            semantic_evidence_requests=(),
            reason="semantic axis is pending explicit owner confirmation",
            metadata=base_metadata,
        )

    if confirmation_gate.status == "REJECTED_BY_OWNER":
        return OwnerConfirmedSemanticRequestFlowResult(
            flow_status="NEEDS_REINTERPRETATION",
            semantic_evidence_requests=(),
            reason="owner rejected the proposed semantic axis; a new interpretation is required",
            metadata=base_metadata,
        )

    if confirmation_gate.status == "CORRECTED_BY_OWNER":
        owner_answer_text = confirmation_gate.corrected_interpretation or confirmation_gate.owner_response_text or ""
    else:
        owner_answer_text = confirmation_gate.owner_response_text or confirmation_gate.proposed_interpretation

    requests: list[OwnerSemanticEvidenceRequest] = []
    unsupported: list[str] = []

    for missing_key in normalized_missing_keys:
        try:
            requests.append(
                build_owner_semantic_evidence_request(
                    missing_key=missing_key,
                    owner_answer_text=owner_answer_text,
                    source_ref=source_ref_text,
                    metadata={**base_metadata, "flow_status": "BLOCKED_ACTIONABLE"},
                )
            )
        except ValueError:
            unsupported.append(missing_key)

    return OwnerConfirmedSemanticRequestFlowResult(
        flow_status="BLOCKED_ACTIONABLE",
        semantic_evidence_requests=tuple(requests),
        reason="owner-confirmed semantic axis produced actionable evidence requests; structural evidence is still required",
        unsupported_missing_keys=tuple(unsupported),
        metadata=base_metadata,
    )
