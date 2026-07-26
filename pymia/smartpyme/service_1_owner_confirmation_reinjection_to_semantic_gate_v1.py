"""
Service 1 Owner Confirmation Reinjection -> Semantic Gate V1

Fail-closed connector that closes the owner-confirmation loop for the Servicio 1
assisted flow.

Flow position:

    semantic_bridge_packet + owner_confirmation_loop_packet (RECHECK_READY)
        -> reapply owner answers onto ambiguous candidates
        -> re-run controlled execution gate

The connector:

1. Reads the original ``semantic_bridge_packet`` (status must be
   SEMANTIC_CANDIDATES_READY) and the loop packet (status must be
   OWNER_CONFIRMATION_RECHECK_READY with a non-empty ``confirmed_answers`` map).
2. Builds NEW candidate objects (never mutates the inputs) marking the answered
   columns as ``owner_confirmation_required=False`` and recording the owner
   answer in ``metadata`` (``owner_confirmed=True``, ``owner_confirmation_answer``).
   Roles/variables are NOT changed unless they already existed on the candidate.
3. Re-packs a bridge packet with the re-injected candidates and re-runs the
   existing controlled execution gate.

The connector NEVER executes tools, NEVER creates delivery, and NEVER authorizes
runtime/product/delivery/diagnosis.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as EXPECTED_BRIDGE_STATUS,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY as EXPECTED_LOOP_STATUS,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_READY as GATE_STATUS_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_CONFIRMATION_REINJECTION_TO_SEMANTIC_GATE_V1"
SERVICE_NAME = "SERVICE_1"
PACKET_TYPE = "OWNER_CONFIRMATION_REINJECTION_TO_SEMANTIC_GATE"

STATUS_READY = "CONTROLLED_EXECUTION_CANDIDATE_READY"
STATUS_NEEDS_OWNER_CONFIRMATION = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED = "BLOCKED"

# Block reason constants (stable identifiers for tests and callers).
BLOCK_REQUEST_FLAGS_FORBIDDEN = "REQUEST_SAFETY_FLAGS_FORBIDDEN"
BLOCK_BRIDGE_NOT_DICT = "BRIDGE_PACKET_NOT_DICT"
BLOCK_LOOP_NOT_DICT = "LOOP_PACKET_NOT_DICT"
BLOCK_BRIDGE_FLAGS_FORBIDDEN = "BRIDGE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_LOOP_FLAGS_FORBIDDEN = "LOOP_SAFETY_FLAGS_FORBIDDEN"
BLOCK_BRIDGE_WRONG_STATUS = "BRIDGE_WRONG_STATUS"
BLOCK_LOOP_WRONG_STATUS = "LOOP_WRONG_STATUS"
BLOCK_LOOP_NO_ANSWERS = "LOOP_NO_CONFIRMED_ANSWERS"
BLOCK_MISSING_ANSWERS = "MISSING_ANSWERS"
BLOCK_UNKNOWN_ANSWERS = "UNKNOWN_ANSWERS"
BLOCK_EMPTY_ANSWERS = "EMPTY_ANSWERS"
BLOCK_EVENT_PROJECTION_MISMATCH = "OWNER_CONFIRMATION_EVENT_PROJECTION_MISMATCH"

_FORBIDDEN_FLAGS = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1(
    *,
    semantic_bridge_packet: Any,
    owner_confirmation_loop_packet: Any,
    runtime_authorized: bool = False,
    tool_execution_authorized: bool = False,
    product_ready: bool = False,
    delivery_authorized: bool = False,
    diagnosis_generated: bool = False,
) -> dict[str, Any]:
    """Reapply owner confirmations and re-run the controlled execution gate.

    Returns:
        A packet mirroring the gate output (CONTROLLED_EXECUTION_CANDIDATE_READY
        or NEEDS_OWNER_CONFIRMATION), or BLOCKED with a ``blocked_reason``.
    """
    if any((runtime_authorized, tool_execution_authorized, product_ready, delivery_authorized, diagnosis_generated)):
        return _blocked(BLOCK_REQUEST_FLAGS_FORBIDDEN)

    if not isinstance(semantic_bridge_packet, dict) or not semantic_bridge_packet:
        return _blocked(BLOCK_BRIDGE_NOT_DICT)
    if not isinstance(owner_confirmation_loop_packet, dict) or not owner_confirmation_loop_packet:
        return _blocked(BLOCK_LOOP_NOT_DICT)

    if any(semantic_bridge_packet.get(flag) for flag in _FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_BRIDGE_FLAGS_FORBIDDEN,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )
    if any(owner_confirmation_loop_packet.get(flag) for flag in _FORBIDDEN_FLAGS):
        return _blocked(
            BLOCK_LOOP_FLAGS_FORBIDDEN,
            case_id=owner_confirmation_loop_packet.get("case_id"),
            source_kind=owner_confirmation_loop_packet.get("source_kind"),
            filename=owner_confirmation_loop_packet.get("filename"),
        )

    if semantic_bridge_packet.get("status") != EXPECTED_BRIDGE_STATUS:
        return _blocked(
            BLOCK_BRIDGE_WRONG_STATUS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )
    if owner_confirmation_loop_packet.get("status") != EXPECTED_LOOP_STATUS:
        return _blocked(
            BLOCK_LOOP_WRONG_STATUS,
            case_id=owner_confirmation_loop_packet.get("case_id"),
            source_kind=owner_confirmation_loop_packet.get("source_kind"),
            filename=owner_confirmation_loop_packet.get("filename"),
        )

    raw_events = owner_confirmation_loop_packet.get("owner_confirmation_events") or []
    if not isinstance(raw_events, list):
        return _blocked(
            BLOCK_LOOP_NO_ANSWERS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )
    event_answers = {
        str(event.get("question_ref") or "").strip(): (
            "IGNORED_NOT_RELEVANT"
            if event.get("confirmation_scope") == "COLUMN_EXCLUSION"
            else str(event.get("confirmed_role") or "").strip()
        )
        for event in raw_events
        if isinstance(event, dict)
        and event.get("confirmed_by_owner") is True
        and event.get("confirmation_scope") in {"SEMANTIC_ROLE", "COLUMN_EXCLUSION"}
    }
    event_answers = {key: value for key, value in event_answers.items() if key and value}

    # During Package 2 migration the legacy map remains a compatibility
    # projection/checksum. Events are the canonical evidence source, but a
    # malformed legacy projection still fails closed until its callers migrate.
    confirmed_answers = owner_confirmation_loop_packet.get("confirmed_answers") or {}
    if not isinstance(confirmed_answers, dict) or not confirmed_answers:
        return _blocked(
            BLOCK_LOOP_NO_ANSWERS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )

    candidates = semantic_bridge_packet.get("column_candidates")
    candidate_list = list(candidates) if isinstance(candidates, (list, tuple)) else []
    if not candidate_list:
        return _blocked(
            BLOCK_BRIDGE_WRONG_STATUS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )

    candidate_refs = {_candidate_ref_id(c) for c in candidate_list}
    if "" in candidate_refs or len(candidate_refs) != len(candidate_list):
        return _blocked(
            BLOCK_BRIDGE_WRONG_STATUS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
        )
    pending_refs = {
        _candidate_ref_id(c)
        for c in candidate_list
        if getattr(c, "owner_confirmation_required", False)
    }

    unknown = sorted(set(str(k).strip() for k in confirmed_answers.keys()) - candidate_refs)
    if unknown:
        return _blocked(
            BLOCK_UNKNOWN_ANSWERS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
            detail=unknown,
        )

    cleaned: dict[str, str] = {}
    missing: list[str] = []
    empty: list[str] = []
    for ref_id in sorted(pending_refs):
        if ref_id not in confirmed_answers:
            # Answer key entirely absent -> missing.
            missing.append(ref_id)
            continue
        raw = confirmed_answers.get(ref_id)
        text = "" if raw is None else str(raw)
        if not text.strip():
            # Key present but blank/whitespace -> empty.
            empty.append(ref_id)
            continue
        cleaned[ref_id] = text.strip()

    if missing:
        return _blocked(
            BLOCK_MISSING_ANSWERS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
            detail=missing,
        )
    if empty:
        return _blocked(
            BLOCK_EMPTY_ANSWERS,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
            detail=empty,
        )

    if event_answers and cleaned != event_answers:
        return _blocked(
            BLOCK_EVENT_PROJECTION_MISMATCH,
            case_id=semantic_bridge_packet.get("case_id"),
            source_kind=semantic_bridge_packet.get("source_kind"),
            filename=semantic_bridge_packet.get("filename"),
            detail=sorted(set(cleaned) ^ set(event_answers)),
        )
    canonical_answers = event_answers or cleaned
    reinjected = _reinject(candidate_list, canonical_answers)

    # Re-pack a bridge packet WITHOUT mutating the original input.
    re_packed_bridge = {
        "schema_version": semantic_bridge_packet.get("schema_version"),
        "service_name": semantic_bridge_packet.get("service_name"),
        "packet_type": semantic_bridge_packet.get("packet_type"),
        "status": EXPECTED_BRIDGE_STATUS,
        "case_id": semantic_bridge_packet.get("case_id"),
        "source_kind": semantic_bridge_packet.get("source_kind"),
        "filename": semantic_bridge_packet.get("filename"),
        "column_candidates": tuple(reinjected),
        "semantic_candidate_count": len(reinjected),
        "column_refs": semantic_bridge_packet.get("column_refs", []),
        "column_understandings": semantic_bridge_packet.get("column_understandings", ()),
        "owner_question_views": semantic_bridge_packet.get("owner_question_views", ()),
        "owner_confirmation_events": [dict(item) for item in raw_events],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }

    gate_out = build_gate(semantic_bridge_packet=re_packed_bridge)

    # Mirror the gate status into this connector's vocabulary.
    if gate_out.get("status") == GATE_STATUS_READY:
        status = STATUS_READY
    elif gate_out.get("status") == "NEEDS_OWNER_CONFIRMATION":
        status = STATUS_NEEDS_OWNER_CONFIRMATION
    else:
        return _blocked(
            gate_out.get("blocked_reason", "GATE_BLOCKED"),
            case_id=gate_out.get("case_id"),
            source_kind=gate_out.get("source_kind"),
            filename=gate_out.get("filename"),
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "packet_type": PACKET_TYPE,
        "status": status,
        "blocked_reason": None,
        "case_id": gate_out.get("case_id"),
        "source_kind": gate_out.get("source_kind"),
        "filename": gate_out.get("filename"),
        "semantic_candidate_count": gate_out.get("semantic_candidate_count"),
        "column_candidates": tuple(reinjected),
        "candidate_roles": gate_out.get("candidate_roles", []),
        "variable_family_count": gate_out.get("variable_family_count", 0),
        "variable_family_bindings": gate_out.get("variable_family_bindings", ()),
        "ready_variable_family_ids": gate_out.get("ready_variable_family_ids", []),
        "reinjected_columns": sorted(canonical_answers.keys()),
        "owner_confirmation_events": [dict(item) for item in raw_events],
        "controlled_execution_candidate": gate_out.get("controlled_execution_candidate"),
        "owner_questions": gate_out.get("owner_questions", []),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _candidate_ref_id(candidate: Service1ColumnSemanticCandidateV1) -> str:
    metadata = dict(candidate.metadata or {})
    return str(
        metadata.get("column_ref_id")
        or metadata.get("question_id")
        or candidate.source_column_name
        or ""
    ).strip()


def _reinject(
    candidate_list: list[Service1ColumnSemanticCandidateV1],
    cleaned: dict[str, str],
) -> list[Service1ColumnSemanticCandidateV1]:
    """Return NEW candidate objects with owner answers applied (no mutation)."""
    result: list[Service1ColumnSemanticCandidateV1] = []
    for candidate in candidate_list:
        ref_id = _candidate_ref_id(candidate)
        if ref_id in cleaned:
            answer = cleaned[ref_id]
            new_metadata = dict(candidate.metadata or {})
            new_metadata["owner_confirmed"] = True
            new_metadata["owner_confirmation_answer"] = answer

            if answer == "IGNORED_NOT_RELEVANT":
                new_metadata["owner_ignored_not_relevant"] = True
                result.append(
                    replace(
                        candidate,
                        candidate_semantic_roles=(),
                        candidate_variable_names=(),
                        owner_confirmation_required=False,
                        ambiguity_reason=None,
                        metadata=new_metadata,
                    )
                )
            else:
                roles = tuple(candidate.candidate_semantic_roles or ())
                variables = tuple(candidate.candidate_variable_names or ())
                index = roles.index(answer)
                variable = variables[index] if index < len(variables) else "unknown"
                result.append(
                    replace(
                        candidate,
                        candidate_semantic_roles=(answer,),
                        candidate_variable_names=(variable,),
                        owner_confirmation_required=False,
                        ambiguity_reason=None,
                        metadata=new_metadata,
                    )
                )
        else:
            result.append(candidate)
    return result


def _blocked(
    reason: str,
    *,
    case_id: Optional[str] = None,
    source_kind: Optional[str] = None,
    filename: Optional[str] = None,
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
        "semantic_candidate_count": 0,
        "column_candidates": (),
        "candidate_roles": [],
        "variable_family_count": 0,
        "variable_family_bindings": (),
        "ready_variable_family_ids": [],
        "reinjected_columns": [],
        "controlled_execution_candidate": None,
        "owner_questions": [],
        "detail": list(detail or []),
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
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_BLOCKED",
    "BLOCK_REQUEST_FLAGS_FORBIDDEN",
    "BLOCK_BRIDGE_NOT_DICT",
    "BLOCK_LOOP_NOT_DICT",
    "BLOCK_BRIDGE_FLAGS_FORBIDDEN",
    "BLOCK_LOOP_FLAGS_FORBIDDEN",
    "BLOCK_BRIDGE_WRONG_STATUS",
    "BLOCK_LOOP_WRONG_STATUS",
    "BLOCK_LOOP_NO_ANSWERS",
    "BLOCK_MISSING_ANSWERS",
    "BLOCK_UNKNOWN_ANSWERS",
    "BLOCK_EMPTY_ANSWERS",
    "BLOCK_EVENT_PROJECTION_MISMATCH",
    "build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1",
]
