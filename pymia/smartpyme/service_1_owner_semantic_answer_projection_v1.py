"""Servicio 1 — owner semantic answer projection V1.

ADR-029 / SEM-5. Projects an accepted SEM-4 dialogue response into canonical
owner evidence, reusing the existing column confirmation event and the separate
relationship confirmation event. Rejected, corrected or unresolved dialogue
states never create confirmatory owner evidence.
"""
from __future__ import annotations

from typing import Any, Final

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_owner_relationship_confirmation_event_v1,
)
from pymia.smartpyme.service_1_owner_semantic_dialogue_v1 import (
    ACTION_ACCEPT,
    RESPONSE_DECISION_CONFIRMED,
    RESPONSE_GROUP_CONFIRMED,
    RESPONSE_RELATIONSHIP_CONFIRMED,
    SCHEMA_VERSION as DIALOGUE_SCHEMA_VERSION,
)
from pymia.smartpyme.service_1_semantic_proposal_validator_v1 import (
    SCHEMA_VERSION as VALIDATOR_SCHEMA_VERSION,
    STATUS_READY as VALIDATOR_READY,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_OWNER_SEMANTIC_ANSWER_PROJECTION_V1"
STATUS_READY: Final[str] = "OWNER_SEMANTIC_EVIDENCE_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_DIALOGUE_RESPONSE_INVALID: Final[str] = "BLOCK_OWNER_SEMANTIC_DIALOGUE_RESPONSE_INVALID"
BLOCK_VALIDATED_PACKET_INVALID: Final[str] = "BLOCK_OWNER_SEMANTIC_VALIDATED_PACKET_INVALID"
BLOCK_CASE_MISMATCH: Final[str] = "BLOCK_OWNER_SEMANTIC_CASE_MISMATCH"
BLOCK_PROPOSAL_REF_NOT_FOUND: Final[str] = "BLOCK_OWNER_SEMANTIC_PROPOSAL_REF_NOT_FOUND"
BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED: Final[str] = "BLOCK_OWNER_SEMANTIC_ACCEPTED_SEMANTICS_UNRESOLVED"
BLOCK_RELATIONSHIP_INVALID: Final[str] = "BLOCK_OWNER_SEMANTIC_RELATIONSHIP_INVALID"
BLOCK_AUTHORITY_FORBIDDEN: Final[str] = "BLOCK_OWNER_SEMANTIC_AUTHORITY_FORBIDDEN"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
)
_ACCEPTED_STATUSES: Final[frozenset[str]] = frozenset(
    {RESPONSE_GROUP_CONFIRMED, RESPONSE_RELATIONSHIP_CONFIRMED, RESPONSE_DECISION_CONFIRMED}
)


def project_service_1_owner_semantic_answer_v1(
    *,
    dialogue_response: Any,
    validated_packet: Any,
    case_id: str,
    file_ref: str | None,
    owner_actor_id: str,
    owner_actor_role: str,
    owner_answer: str = "ACCEPT",
    timestamp: str | None = None,
) -> dict[str, Any]:
    if not _valid_dialogue_response(dialogue_response):
        return _blocked(BLOCK_DIALOGUE_RESPONSE_INVALID, case_id=case_id)
    if not _valid_validated_packet(validated_packet):
        return _blocked(BLOCK_VALIDATED_PACKET_INVALID, case_id=case_id)
    if any(bool(dialogue_response.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(BLOCK_AUTHORITY_FORBIDDEN, case_id=case_id)
    if any(bool(validated_packet.get(flag)) for flag in _AUTHORITY_FLAGS):
        return _blocked(BLOCK_AUTHORITY_FORBIDDEN, case_id=case_id)

    clean_case_id = str(case_id or "").strip()
    if not clean_case_id or str(validated_packet.get("case_id") or "").strip() != clean_case_id:
        return _blocked(BLOCK_CASE_MISMATCH, case_id=clean_case_id or None)

    decisions = {
        str(item.get("decision_id") or "").strip(): dict(item)
        for item in validated_packet.get("decisions") or []
        if isinstance(item, dict) and str(item.get("decision_id") or "").strip()
    }
    proposal_refs = [str(ref).strip() for ref in dialogue_response.get("proposal_refs") or [] if str(ref).strip()]
    missing = [ref for ref in proposal_refs if ref not in decisions]
    if missing:
        return _blocked(BLOCK_PROPOSAL_REF_NOT_FOUND, case_id=clean_case_id, detail=missing)

    provenance_base = {
        "producer": SCHEMA_VERSION,
        "source": "owner_semantic_dialogue",
        "owner_actor_id": str(owner_actor_id or "").strip(),
        "owner_actor_role": str(owner_actor_role or "").strip(),
        "dialogue_decision_id": str(dialogue_response.get("decision_id") or "").strip(),
    }
    if not provenance_base["owner_actor_id"] or not provenance_base["owner_actor_role"]:
        return _blocked(BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED, case_id=clean_case_id)

    column_events: list[dict[str, Any]] = []
    relationship_events: list[dict[str, Any]] = []

    for proposal_ref in proposal_refs:
        item = decisions[proposal_ref]
        source_kind = str(item.get("source_kind") or "").strip()
        if source_kind in {"CONCEPT", "DUPLICATE_SEMANTICS"}:
            semantic_role = str(item.get("semantic_role") or "").strip()
            variable_name = str(item.get("variable_name") or "").strip() or None
            targets = [str(ref).strip() for ref in item.get("target_refs") or [] if str(ref).strip()]
            if not semantic_role or not targets:
                return _blocked(
                    BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED,
                    case_id=clean_case_id,
                    detail=proposal_ref,
                )
            for target in targets:
                sheet_ref, column_ref = _split_column_ref(target)
                if not sheet_ref or not column_ref:
                    return _blocked(
                        BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED,
                        case_id=clean_case_id,
                        detail=target,
                    )
                event = build_service_1_owner_confirmation_event_v1(
                    case_id=clean_case_id,
                    file_ref=file_ref,
                    region_ref=None,
                    sheet_ref=sheet_ref,
                    column_ref=column_ref,
                    question_ref=str(dialogue_response.get("decision_id") or proposal_ref),
                    owner_answer=str(owner_answer or ACTION_ACCEPT).strip() or ACTION_ACCEPT,
                    confirmation_scope="SEMANTIC_ROLE",
                    proposed_role=semantic_role,
                    proposed_variable=variable_name,
                    confirmed_role=semantic_role,
                    timestamp=timestamp,
                    provenance={**provenance_base, "proposal_ref": proposal_ref},
                )
                column_events.append(event.to_dict())
            continue

        if source_kind == "RELATIONSHIP":
            targets = [str(ref).strip() for ref in item.get("target_refs") or [] if str(ref).strip()]
            relationship_kind = str(item.get("relationship_type") or "").strip()
            if len(targets) != 2 or not relationship_kind:
                return _blocked(BLOCK_RELATIONSHIP_INVALID, case_id=clean_case_id, detail=proposal_ref)
            left_sheet, left_column = _split_column_ref(targets[0])
            right_sheet, right_column = _split_column_ref(targets[1])
            if not all((left_sheet, left_column, right_sheet, right_column)):
                return _blocked(BLOCK_RELATIONSHIP_INVALID, case_id=clean_case_id, detail=targets)
            event = build_service_1_owner_relationship_confirmation_event_v1(
                case_id=clean_case_id,
                file_ref=file_ref,
                left_sheet_ref=left_sheet,
                left_column_ref=left_column,
                right_sheet_ref=right_sheet,
                right_column_ref=right_column,
                relationship_kind=relationship_kind,
                owner_answer=str(owner_answer or ACTION_ACCEPT).strip() or ACTION_ACCEPT,
                question_ref=str(dialogue_response.get("decision_id") or proposal_ref),
                timestamp=timestamp,
                provenance={**provenance_base, "proposal_ref": proposal_ref},
            )
            relationship_events.append(event.to_dict())
            continue

        return _blocked(
            BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED,
            case_id=clean_case_id,
            detail=proposal_ref,
        )

    if not column_events and not relationship_events:
        return _blocked(BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED, case_id=clean_case_id)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "detail": None,
        "case_id": clean_case_id,
        "owner_confirmation_events": column_events,
        "owner_relationship_confirmation_events": relationship_events,
        "owner_confirmation_event_count": len(column_events),
        "owner_relationship_confirmation_event_count": len(relationship_events),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _valid_dialogue_response(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema_version") == DIALOGUE_SCHEMA_VERSION
        and value.get("status") in _ACCEPTED_STATUSES
        and value.get("action") == ACTION_ACCEPT
        and isinstance(value.get("proposal_refs"), list)
    )


def _valid_validated_packet(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema_version") == VALIDATOR_SCHEMA_VERSION
        and value.get("status") == VALIDATOR_READY
        and isinstance(value.get("decisions"), list)
    )


def _split_column_ref(value: str) -> tuple[str, str]:
    text = str(value or "").strip()
    if "." not in text:
        return "", ""
    sheet, column = text.split(".", 1)
    return sheet.strip(), column.strip()


def _blocked(reason: str, *, case_id: str | None = None, detail: Any = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "case_id": case_id,
        "owner_confirmation_events": [],
        "owner_relationship_confirmation_events": [],
        "owner_confirmation_event_count": 0,
        "owner_relationship_confirmation_event_count": 0,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_DIALOGUE_RESPONSE_INVALID",
    "BLOCK_VALIDATED_PACKET_INVALID",
    "BLOCK_CASE_MISMATCH",
    "BLOCK_PROPOSAL_REF_NOT_FOUND",
    "BLOCK_ACCEPTED_SEMANTICS_UNRESOLVED",
    "BLOCK_RELATIONSHIP_INVALID",
    "BLOCK_AUTHORITY_FORBIDDEN",
    "project_service_1_owner_semantic_answer_v1",
]
