"""Servicio 1 — SEM-5 owner evidence -> existing semantic reinjection/P6 V1.

ADR-029 / SEM-6. This is a compatibility adapter, not a second semantic gate.
It maps canonical owner evidence produced by SEM-5 onto the legacy reinjection
packet shape, invokes the existing owner-confirmation reinjector, and preserves
relationship evidence as a separate confirmed-evidence channel.

No LLM calls, parsing, persistence, calculation, runtime permission or
product/delivery authority live here.
"""
from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as BRIDGE_READY,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
)
from pymia.smartpyme.service_1_owner_confirmation_reinjection_to_semantic_gate_v1 import (
    STATUS_NEEDS_OWNER_CONFIRMATION as REINJECTION_NEEDS_OWNER,
    STATUS_READY as REINJECTION_READY,
    build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1,
)
from pymia.smartpyme.service_1_owner_semantic_answer_projection_v1 import (
    SCHEMA_VERSION as SEM5_SCHEMA_VERSION,
    STATUS_READY as SEM5_READY,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_OWNER_SEMANTIC_EVIDENCE_REENTRY_V1"
STATUS_READY: Final[str] = "OWNER_SEMANTIC_EVIDENCE_REENTRY_READY"
STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_BRIDGE_INVALID: Final[str] = "BLOCK_SEM6_BRIDGE_INVALID"
BLOCK_EVIDENCE_PACKET_INVALID: Final[str] = "BLOCK_SEM6_EVIDENCE_PACKET_INVALID"
BLOCK_CASE_MISMATCH: Final[str] = "BLOCK_SEM6_CASE_MISMATCH"
BLOCK_AUTHORITY_FORBIDDEN: Final[str] = "BLOCK_SEM6_AUTHORITY_FORBIDDEN"
BLOCK_CANDIDATE_IDENTITY_INVALID: Final[str] = "BLOCK_SEM6_CANDIDATE_IDENTITY_INVALID"
BLOCK_OWNER_EVENT_INVALID: Final[str] = "BLOCK_SEM6_OWNER_EVENT_INVALID"
BLOCK_OWNER_EVENT_TARGET_NOT_FOUND: Final[str] = "BLOCK_SEM6_OWNER_EVENT_TARGET_NOT_FOUND"
BLOCK_OWNER_EVENT_ROLE_NOT_AVAILABLE: Final[str] = "BLOCK_SEM6_OWNER_EVENT_ROLE_NOT_AVAILABLE"
BLOCK_DUPLICATE_OWNER_EVENT: Final[str] = "BLOCK_SEM6_DUPLICATE_OWNER_EVENT"
BLOCK_IRRELEVANT_REF_NOT_FOUND: Final[str] = "BLOCK_SEM6_IRRELEVANT_REF_NOT_FOUND"
BLOCK_CONFIRMATION_AND_EXCLUSION_CONFLICT: Final[str] = "BLOCK_SEM6_CONFIRMATION_AND_EXCLUSION_CONFLICT"
BLOCK_REENTRY_EVIDENCE_INCOMPLETE: Final[str] = "BLOCK_SEM6_REENTRY_EVIDENCE_INCOMPLETE"
BLOCK_RELATIONSHIP_EVENT_INVALID: Final[str] = "BLOCK_SEM6_RELATIONSHIP_EVENT_INVALID"
BLOCK_RELATIONSHIP_ENDPOINT_NOT_FOUND: Final[str] = "BLOCK_SEM6_RELATIONSHIP_ENDPOINT_NOT_FOUND"
BLOCK_REINJECTION_FAILED: Final[str] = "BLOCK_SEM6_REINJECTION_FAILED"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)


def build_service_1_owner_semantic_evidence_reentry_v1(
    *,
    semantic_bridge_packet: Any,
    owner_semantic_evidence_packet: Any,
    suppressed_irrelevant_refs: Any = (),
) -> dict[str, Any]:
    """Re-enter SEM-5 owner evidence through the existing reinjection + P6 path."""
    if not _valid_bridge(semantic_bridge_packet):
        return _blocked(BLOCK_BRIDGE_INVALID)
    if not _valid_sem5_packet(owner_semantic_evidence_packet):
        return _blocked(
            BLOCK_EVIDENCE_PACKET_INVALID,
            case_id=semantic_bridge_packet.get("case_id"),
        )
    if any(bool(semantic_bridge_packet.get(flag)) for flag in _AUTHORITY_FLAGS) or any(
        bool(owner_semantic_evidence_packet.get(flag)) for flag in _AUTHORITY_FLAGS
    ):
        return _blocked(
            BLOCK_AUTHORITY_FORBIDDEN,
            case_id=semantic_bridge_packet.get("case_id"),
        )

    case_id = str(semantic_bridge_packet.get("case_id") or "").strip()
    evidence_case_id = str(owner_semantic_evidence_packet.get("case_id") or "").strip()
    if not case_id or evidence_case_id != case_id:
        return _blocked(BLOCK_CASE_MISMATCH, case_id=case_id or None)

    candidate_list = list(semantic_bridge_packet.get("column_candidates") or ())
    identity_to_ref, ref_to_candidate = _candidate_maps(candidate_list)
    if identity_to_ref is None or ref_to_candidate is None:
        return _blocked(BLOCK_CANDIDATE_IDENTITY_INVALID, case_id=case_id)

    confirmed_answers: dict[str, str] = {}
    column_events = list(owner_semantic_evidence_packet.get("owner_confirmation_events") or [])
    for event in column_events:
        event_error = _validate_owner_event(event, case_id=case_id)
        if event_error is not None:
            return _blocked(BLOCK_OWNER_EVENT_INVALID, case_id=case_id, detail=event_error)
        identity = (
            str(event.get("sheet_ref") or "").strip(),
            str(event.get("column_ref") or "").strip(),
        )
        ref_id = identity_to_ref.get(identity)
        if not ref_id:
            return _blocked(
                BLOCK_OWNER_EVENT_TARGET_NOT_FOUND,
                case_id=case_id,
                detail=[f"{identity[0]}.{identity[1]}"],
            )
        if ref_id in confirmed_answers:
            return _blocked(BLOCK_DUPLICATE_OWNER_EVENT, case_id=case_id, detail=[ref_id])
        confirmed_role = str(event.get("confirmed_role") or "").strip()
        candidate = ref_to_candidate[ref_id]
        if confirmed_role not in tuple(candidate.candidate_semantic_roles or ()):
            return _blocked(
                BLOCK_OWNER_EVENT_ROLE_NOT_AVAILABLE,
                case_id=case_id,
                detail=[f"{ref_id}:{confirmed_role}"],
            )
        confirmed_answers[ref_id] = confirmed_role

    exclusions: set[str] = set()
    if not isinstance(suppressed_irrelevant_refs, (list, tuple, set, frozenset)):
        return _blocked(BLOCK_IRRELEVANT_REF_NOT_FOUND, case_id=case_id)
    for raw_ref in suppressed_irrelevant_refs:
        identity = _split_qualified_ref(raw_ref)
        if identity is None or identity not in identity_to_ref:
            return _blocked(
                BLOCK_IRRELEVANT_REF_NOT_FOUND,
                case_id=case_id,
                detail=[str(raw_ref)],
            )
        ref_id = identity_to_ref[identity]
        if ref_id in confirmed_answers:
            return _blocked(
                BLOCK_CONFIRMATION_AND_EXCLUSION_CONFLICT,
                case_id=case_id,
                detail=[ref_id],
            )
        exclusions.add(ref_id)

    covered = set(confirmed_answers) | exclusions
    missing = sorted(set(ref_to_candidate) - covered)
    if missing:
        return _blocked(
            BLOCK_REENTRY_EVIDENCE_INCOMPLETE,
            case_id=case_id,
            detail=missing,
        )

    relationship_events = list(
        owner_semantic_evidence_packet.get("owner_relationship_confirmation_events") or []
    )
    for event in relationship_events:
        relation_error = _validate_relationship_event(
            event,
            case_id=case_id,
            identity_to_ref=identity_to_ref,
        )
        if relation_error is not None:
            reason = (
                BLOCK_RELATIONSHIP_ENDPOINT_NOT_FOUND
                if relation_error.startswith("endpoint_not_found:")
                else BLOCK_RELATIONSHIP_EVENT_INVALID
            )
            return _blocked(reason, case_id=case_id, detail=[relation_error])

    compatibility_loop_packet = {
        "status": STATUS_OWNER_CONFIRMATION_RECHECK_READY,
        "case_id": case_id,
        "source_kind": semantic_bridge_packet.get("source_kind"),
        "filename": semantic_bridge_packet.get("filename"),
        "confirmed_answers": dict(confirmed_answers),
        "system_scope_exclusions": sorted(exclusions),
        # Preserve canonical SEM-5 events unchanged. The existing reinjector is
        # identity-aware and P6 itself matches by physical column identity.
        "owner_confirmation_events": [dict(item) for item in column_events],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }

    reentry = build_service_1_owner_confirmation_reinjection_to_semantic_gate_v1(
        semantic_bridge_packet=semantic_bridge_packet,
        owner_confirmation_loop_packet=compatibility_loop_packet,
    )
    if reentry.get("status") == REINJECTION_NEEDS_OWNER:
        return _packet(
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            blocked_reason=None,
            case_id=case_id,
            reentry_packet=reentry,
            column_events=column_events,
            relationship_events=relationship_events,
            exclusions=exclusions,
        )
    if reentry.get("status") != REINJECTION_READY:
        return _blocked(
            BLOCK_REINJECTION_FAILED,
            case_id=case_id,
            detail=[str(reentry.get("blocked_reason") or "UNKNOWN_REINJECTION_FAILURE")],
            reentry_packet=reentry,
        )

    return _packet(
        status=STATUS_READY,
        blocked_reason=None,
        case_id=case_id,
        reentry_packet=reentry,
        column_events=column_events,
        relationship_events=relationship_events,
        exclusions=exclusions,
    )


def _valid_bridge(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("status") == BRIDGE_READY
        and isinstance(value.get("column_candidates"), (list, tuple))
        and bool(value.get("column_candidates"))
    )


def _valid_sem5_packet(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema_version") == SEM5_SCHEMA_VERSION
        and value.get("status") == SEM5_READY
        and isinstance(value.get("owner_confirmation_events"), list)
        and isinstance(value.get("owner_relationship_confirmation_events"), list)
    )


def _candidate_maps(
    candidate_list: list[Any],
) -> tuple[
    dict[tuple[str, str], str] | None,
    dict[str, Service1ColumnSemanticCandidateV1] | None,
]:
    identity_to_ref: dict[tuple[str, str], str] = {}
    ref_to_candidate: dict[str, Service1ColumnSemanticCandidateV1] = {}
    for candidate in candidate_list:
        if not isinstance(candidate, Service1ColumnSemanticCandidateV1):
            return None, None
        metadata = dict(candidate.metadata or {})
        ref_id = str(
            metadata.get("column_ref_id")
            or metadata.get("question_id")
            or candidate.source_column_name
            or ""
        ).strip()
        identity = (
            str(candidate.sheet_name or "").strip(),
            str(candidate.source_column_name or "").strip(),
        )
        if not ref_id or not all(identity) or ref_id in ref_to_candidate or identity in identity_to_ref:
            return None, None
        ref_to_candidate[ref_id] = candidate
        identity_to_ref[identity] = ref_id
    return identity_to_ref, ref_to_candidate


def _validate_owner_event(event: Any, *, case_id: str) -> list[str] | None:
    if not isinstance(event, dict):
        return ["event_not_dict"]
    if str(event.get("case_id") or "").strip() != case_id:
        return ["event_case_mismatch"]
    if event.get("confirmed_by_owner") is not True:
        return ["event_not_owner_confirmed"]
    if str(event.get("confirmation_scope") or "").strip() != "SEMANTIC_ROLE":
        return ["event_scope_not_semantic_role"]
    if not str(event.get("sheet_ref") or "").strip() or not str(event.get("column_ref") or "").strip():
        return ["event_identity_missing"]
    if not str(event.get("confirmed_role") or "").strip():
        return ["event_confirmed_role_missing"]
    if any(bool(event.get(flag)) for flag in _AUTHORITY_FLAGS):
        return ["event_authority_forbidden"]
    return None


def _validate_relationship_event(
    event: Any,
    *,
    case_id: str,
    identity_to_ref: dict[tuple[str, str], str],
) -> str | None:
    if not isinstance(event, dict):
        return "relationship_event_not_dict"
    if str(event.get("case_id") or "").strip() != case_id:
        return "relationship_event_case_mismatch"
    if event.get("confirmed_by_owner") is not True:
        return "relationship_event_not_owner_confirmed"
    if not str(event.get("relationship_kind") or "").strip():
        return "relationship_kind_missing"
    if any(bool(event.get(flag)) for flag in _AUTHORITY_FLAGS):
        return "relationship_event_authority_forbidden"
    left = (
        str(event.get("left_sheet_ref") or "").strip(),
        str(event.get("left_column_ref") or "").strip(),
    )
    right = (
        str(event.get("right_sheet_ref") or "").strip(),
        str(event.get("right_column_ref") or "").strip(),
    )
    if not all(left) or not all(right) or left == right:
        return "relationship_identity_invalid"
    if left not in identity_to_ref:
        return f"endpoint_not_found:{left[0]}.{left[1]}"
    if right not in identity_to_ref:
        return f"endpoint_not_found:{right[0]}.{right[1]}"
    return None


def _split_qualified_ref(value: Any) -> tuple[str, str] | None:
    text = str(value or "").strip()
    if "." not in text:
        return None
    sheet, column = text.split(".", 1)
    sheet = sheet.strip()
    column = column.strip()
    return (sheet, column) if sheet and column else None


def _packet(
    *,
    status: str,
    blocked_reason: str | None,
    case_id: str,
    reentry_packet: dict[str, Any],
    column_events: list[dict[str, Any]],
    relationship_events: list[dict[str, Any]],
    exclusions: set[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "blocked_reason": blocked_reason,
        "detail": None,
        "case_id": case_id,
        "reentry_packet": reentry_packet,
        "confirmed_candidate": reentry_packet.get("controlled_execution_candidate"),
        "p6_decisions": list(reentry_packet.get("p6_decisions") or []),
        "requirement_matches": list(reentry_packet.get("requirement_matches") or []),
        "owner_confirmation_events": [dict(item) for item in column_events],
        "confirmed_relationships": [dict(item) for item in relationship_events],
        "system_scope_exclusions": sorted(exclusions),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(
    reason: str,
    *,
    case_id: str | None = None,
    detail: list[str] | None = None,
    reentry_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": list(detail or []),
        "case_id": case_id,
        "reentry_packet": reentry_packet,
        "confirmed_candidate": None,
        "p6_decisions": [],
        "requirement_matches": [],
        "owner_confirmation_events": [],
        "confirmed_relationships": [],
        "system_scope_exclusions": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_BLOCKED",
    "BLOCK_BRIDGE_INVALID",
    "BLOCK_EVIDENCE_PACKET_INVALID",
    "BLOCK_CASE_MISMATCH",
    "BLOCK_AUTHORITY_FORBIDDEN",
    "BLOCK_CANDIDATE_IDENTITY_INVALID",
    "BLOCK_OWNER_EVENT_INVALID",
    "BLOCK_OWNER_EVENT_TARGET_NOT_FOUND",
    "BLOCK_OWNER_EVENT_ROLE_NOT_AVAILABLE",
    "BLOCK_DUPLICATE_OWNER_EVENT",
    "BLOCK_IRRELEVANT_REF_NOT_FOUND",
    "BLOCK_CONFIRMATION_AND_EXCLUSION_CONFLICT",
    "BLOCK_REENTRY_EVIDENCE_INCOMPLETE",
    "BLOCK_RELATIONSHIP_EVENT_INVALID",
    "BLOCK_RELATIONSHIP_ENDPOINT_NOT_FOUND",
    "BLOCK_REINJECTION_FAILED",
    "build_service_1_owner_semantic_evidence_reentry_v1",
]
