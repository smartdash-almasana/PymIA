"""
Service 1 Semantic Bridge -> Controlled Execution Gate V1

Fail-closed gate for the Servicio 1 assisted flow.

Flow position:

    semantic bridge output -> controlled execution GATE (this module)

The gate receives the output of
``build_service_1_semantic_bridge_from_canonical_ingestion_output_v1`` and
decides whether a controlled execution *candidate* may be prepared. It NEVER
executes tools, NEVER authorizes runtime/product/delivery, NEVER generates a
diagnosis. It only emits a controlled execution gate packet.

Fail-closed principle: any ambiguity, any missing owner confirmation, any
forbidden flag, or any malformed candidate results in a non-ready status
(BLOCKED or NEEDS_OWNER_CONFIRMATION). Readiness is never forced.
"""

from __future__ import annotations

from typing import Any, Optional

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)

SCHEMA_VERSION = "SERVICE_1_SEMANTIC_BRIDGE_TO_CONTROLLED_EXECUTION_GATE_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "SEMANTIC_BRIDGE_TO_CONTROLLED_EXECUTION_GATE"

# Expected upstream status from the semantic bridge.
EXPECTED_BRIDGE_STATUS = "SEMANTIC_CANDIDATES_READY"

STATUS_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"
STATUS_NEEDS_OWNER_CONFIRMATION = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_BRIDGE_NOT_DICT = "BRIDGE_PACKET_NOT_DICT"
BLOCK_BRIDGE_WRONG_STATUS = "BRIDGE_WRONG_STATUS"
BLOCK_BRIDGE_FLAGS_FORBIDDEN = "BRIDGE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_NO_CANDIDATES = "NO_SEMANTIC_CANDIDATES"
BLOCK_INVALID_CANDIDATE = "INVALID_CANDIDATE_OBJECT"
BLOCK_CANDIDATE_FLAGS_FORBIDDEN = "CANDIDATE_SAFETY_FLAGS_FORBIDDEN"

_CANDIDATE_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_controlled_execution_gate_from_semantic_bridge_v1(
    *,
    semantic_bridge_packet: Any,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Decide whether a controlled execution candidate may be prepared.

    The gate is fail-closed: it never executes tools and never authorizes any
    runtime/product/delivery/diagnosis action. It only classifies the input.

    Returns:
        A controlled execution gate packet dict. Status is one of:
          - CONTROLLED_EXECUTION_CANDIDATE_READY: all candidates safe and no
            owner confirmation required (still no execution/authorization),
          - NEEDS_OWNER_CONFIRMATION: at least one candidate needs owner input,
          - BLOCKED: with a ``blocked_reason``.
    """
    # Rule 1: request flags true -> BLOCKED.
    if (
        runtime_authorized
        or tool_execution_authorized
        or product_ready
        or delivery_authorized
        or diagnosis_generated
    ):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    # Rule 2: bridge packet not dict -> BLOCKED.
    if not isinstance(semantic_bridge_packet, dict) or not semantic_bridge_packet:
        return _blocked(BLOCK_BRIDGE_NOT_DICT)

    packet = semantic_bridge_packet
    case_id = packet.get("case_id")
    source_kind = packet.get("source_kind")
    filename = packet.get("filename")

    # Rule 3: bridge status must be SEMANTIC_CANDIDATES_READY.
    if packet.get("status") != EXPECTED_BRIDGE_STATUS:
        return _blocked(
            BLOCK_BRIDGE_WRONG_STATUS,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    # Rule 4: bridge must not carry any forbidden flag true.
    if (
        packet.get("runtime_authorized")
        or packet.get("tool_execution_authorized")
        or packet.get("product_ready")
        or packet.get("delivery_authorized")
        or packet.get("diagnosis_generated")
    ):
        return _blocked(
            BLOCK_BRIDGE_FLAGS_FORBIDDEN,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    candidates = packet.get("column_candidates")
    candidate_list = list(candidates) if isinstance(candidates, (list, tuple)) else []

    # Rule 5: no column_candidates -> BLOCKED.
    if not candidate_list:
        return _blocked(
            BLOCK_NO_CANDIDATES,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    # Rule 6: every candidate must be a Service1ColumnSemanticCandidateV1.
    for candidate in candidate_list:
        if not isinstance(candidate, Service1ColumnSemanticCandidateV1):
            return _blocked(
                BLOCK_INVALID_CANDIDATE,
                case_id=case_id,
                source_kind=source_kind,
                filename=filename,
            )

    # Rule 7: no candidate may carry a forbidden flag true.
    for candidate in candidate_list:
        if any(getattr(candidate, flag, False) for flag in _CANDIDATE_FORBIDDEN_FLAGS):
            return _blocked(
                BLOCK_CANDIDATE_FLAGS_FORBIDDEN,
                case_id=case_id,
                source_kind=source_kind,
                filename=filename,
            )

    active_candidates = [
        candidate
        for candidate in candidate_list
        if not bool(
            (getattr(candidate, "metadata", {}) or {}).get(
                "owner_ignored_not_relevant"
            )
        )
    ]
    candidate_roles = _collect_roles(active_candidates)

    # Rule 8: any active candidate requiring owner confirmation or still
    # carrying only an unknown role remains fail-closed.
    needs_confirmation = [
        candidate
        for candidate in active_candidates
        if getattr(candidate, "owner_confirmation_required", False)
        or not tuple(getattr(candidate, "candidate_semantic_roles", ()) or ())
        or "unknown"
        in tuple(getattr(candidate, "candidate_semantic_roles", ()) or ())
    ]

    if needs_confirmation:
        owner_questions = _owner_questions(needs_confirmation)
        return _packet(
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            candidate_count=len(candidate_list),
            candidate_roles=candidate_roles,
            controlled_execution_candidate=None,
            owner_questions=owner_questions,
        )

    # Rule 9: all safe and no confirmation required -> READY (still no execution).
    controlled_execution_candidate = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "candidate_columns": [c.source_column_name for c in active_candidates],
        "candidate_roles": candidate_roles,
        "candidate_count": len(candidate_list),
        # Rule 10: candidate is a proposal only, never an execution authorization.
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return _packet(
        status=STATUS_READY,
        case_id=case_id,
        source_kind=source_kind,
        filename=filename,
        candidate_count=len(candidate_list),
        candidate_roles=candidate_roles,
        controlled_execution_candidate=controlled_execution_candidate,
        owner_questions=[],
    )


def _collect_roles(candidates: list[Any]) -> list[str]:
    roles: list[str] = []
    for candidate in candidates:
        for role in getattr(candidate, "candidate_semantic_roles", ()) or ():
            role_text = str(role).strip()
            if role_text and role_text not in roles:
                roles.append(role_text)
    return roles


def _owner_questions(candidates: list[Any]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for candidate in candidates:
        column = getattr(candidate, "source_column_name", "")
        roles = [
            role
            for role in (getattr(candidate, "candidate_semantic_roles", ()) or ())
            if role != "unknown"
        ]
        metadata = dict(getattr(candidate, "metadata", {}) or {})
        questions.append(
            {
                "column_name": column,
                "candidate_roles": roles,
                "allowed_answers": roles + ["IGNORED_NOT_RELEVANT"],
                "ambiguity_reason": getattr(candidate, "ambiguity_reason", None),
                "question": metadata.get("owner_question_text")
                or f"¿Qué función cumple la columna '{column}' en tu negocio?",
                "answer_type": "select_canonical_semantic_role_or_ignore",
                "required": True,
            }
        )
    return questions


def _packet(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    candidate_count: int,
    candidate_roles: list[str],
    controlled_execution_candidate: Optional[dict[str, Any]],
    owner_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "blocked_reason": None,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "semantic_candidate_count": candidate_count,
        "candidate_roles": candidate_roles,
        "controlled_execution_candidate": controlled_execution_candidate,
        "owner_questions": owner_questions,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


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
        "semantic_candidate_count": 0,
        "candidate_roles": [],
        "controlled_execution_candidate": None,
        "owner_questions": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "PACKET_TYPE",
    "EXPECTED_BRIDGE_STATUS",
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_BRIDGE_NOT_DICT",
    "BLOCK_BRIDGE_WRONG_STATUS",
    "BLOCK_BRIDGE_FLAGS_FORBIDDEN",
    "BLOCK_NO_CANDIDATES",
    "BLOCK_INVALID_CANDIDATE",
    "BLOCK_CANDIDATE_FLAGS_FORBIDDEN",
    "build_service_1_controlled_execution_gate_from_semantic_bridge_v1",
]
