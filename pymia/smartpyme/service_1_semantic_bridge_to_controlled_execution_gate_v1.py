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

from pymia.smartpyme.service_1_column_understanding_owner_question_adapter_v1 import (
    Service1ColumnOwnerQuestionViewV1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)
from pymia.smartpyme.service_1_p6_approval_decision_v1 import (
    STATUS_AMBIGUOUS as P6_STATUS_AMBIGUOUS,
    STATUS_APPROVED as P6_STATUS_APPROVED,
    STATUS_BLOCKED as P6_STATUS_BLOCKED,
    STATUS_NEEDS_OWNER_CONFIRMATION as P6_STATUS_NEEDS_OWNER_CONFIRMATION,
    build_service_1_p6_approval_decisions_v1,
)
from pymia.smartpyme.service_1_variable_family_bindings_v1 import (
    build_service_1_requirement_matches_v1,
    project_service_1_requirement_matches_to_variable_family_bindings_v1,
    ready_service_1_requirement_family_ids_v1,
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
BLOCK_NO_ACTIVE_CANDIDATES = "NO_ACTIVE_SEMANTIC_CANDIDATES"
BLOCK_INVALID_CANDIDATE = "INVALID_CANDIDATE_OBJECT"
BLOCK_CANDIDATE_FLAGS_FORBIDDEN = "CANDIDATE_SAFETY_FLAGS_FORBIDDEN"
BLOCK_OWNER_QUESTION_VIEW_MISSING = "OWNER_QUESTION_VIEW_MISSING"
BLOCK_OWNER_QUESTION_VIEW_INVALID = "OWNER_QUESTION_VIEW_INVALID"
BLOCK_OWNER_QUESTION_SURFACE_UNSAFE = "OWNER_QUESTION_SURFACE_UNSAFE"

OWNER_OPTION_OTHER = "OTHER"
OWNER_OPTION_IGNORE = "IGNORE"

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
    if not active_candidates:
        return _blocked(
            BLOCK_NO_ACTIVE_CANDIDATES,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )
    candidate_roles = _collect_roles(active_candidates)
    owner_confirmation_events = tuple(packet.get("owner_confirmation_events") or ())
    p6_decisions = build_service_1_p6_approval_decisions_v1(
        case_id=str(case_id or "").strip(),
        candidates=active_candidates,
        owner_confirmation_events=owner_confirmation_events,
    )
    decisions_by_ref = {
        decision.provenance["candidate_ref"]: decision for decision in p6_decisions
    }
    blocked_p6 = [decision for decision in p6_decisions if decision.status == P6_STATUS_BLOCKED]
    if blocked_p6:
        return _blocked(
            f"P6_BLOCKED:{blocked_p6[0].reason}",
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )

    # Rule 8: owner clarification is driven by canonical P6 decisions, not by
    # this compatibility gate reinterpreting candidate state independently.
    needs_confirmation = [
        candidate
        for candidate in active_candidates
        if decisions_by_ref[_candidate_ref_id(candidate)].status
        in {P6_STATUS_NEEDS_OWNER_CONFIRMATION, P6_STATUS_AMBIGUOUS}
    ]

    if needs_confirmation:
        owner_questions, owner_answer_bindings, owner_question_error = _owner_questions(
            semantic_bridge_packet=packet,
            candidates=needs_confirmation,
        )
        if owner_question_error is not None:
            return _blocked(
                owner_question_error,
                case_id=case_id,
                source_kind=source_kind,
                filename=filename,
            )
        return _packet(
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
            candidate_count=len(candidate_list),
            candidate_roles=candidate_roles,
            variable_family_bindings=(),
            ready_variable_family_ids=(),
            controlled_execution_candidate=None,
            owner_questions=owner_questions,
            owner_answer_bindings=owner_answer_bindings,
            p6_decisions=p6_decisions,
        )

    # P7-adjacent family matching is allowed only after every active semantic
    # candidate has passed canonical P6 approval.
    if any(decision.status != P6_STATUS_APPROVED for decision in p6_decisions):
        return _blocked(
            "P6_APPROVAL_REQUIRED_BEFORE_REQUIREMENT_MATCHING",
            case_id=case_id,
            source_kind=source_kind,
            filename=filename,
        )
    requirement_matches = build_service_1_requirement_matches_v1(p6_decisions)
    variable_family_bindings = (
        project_service_1_requirement_matches_to_variable_family_bindings_v1(
            requirement_matches
        )
    )
    ready_variable_family_ids = ready_service_1_requirement_family_ids_v1(
        requirement_matches
    )

    # Rule 9: all safe and P6-approved -> READY (still no execution).
    controlled_execution_candidate = {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "source_kind": source_kind,
        "filename": filename,
        "candidate_columns": [c.source_column_name for c in active_candidates],
        "candidate_refs": [_candidate_ref_id(c) for c in active_candidates],
        "candidate_roles": candidate_roles,
        "candidate_count": len(candidate_list),
        "requirement_matches": [match.to_dict() for match in requirement_matches],
        "variable_family_bindings": variable_family_bindings,
        "ready_variable_family_ids": list(ready_variable_family_ids),
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
        variable_family_bindings=variable_family_bindings,
        ready_variable_family_ids=ready_variable_family_ids,
        controlled_execution_candidate=controlled_execution_candidate,
        owner_questions=[],
        owner_answer_bindings={},
        p6_decisions=p6_decisions,
        requirement_matches=requirement_matches,
    )


def _collect_roles(candidates: list[Any]) -> list[str]:
    roles: list[str] = []
    for candidate in candidates:
        for role in getattr(candidate, "candidate_semantic_roles", ()) or ():
            role_text = str(role).strip()
            if role_text and role_text not in roles:
                roles.append(role_text)
    return roles


def _owner_questions(
    *,
    semantic_bridge_packet: dict[str, Any],
    candidates: list[Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]], str | None]:
    raw_views = semantic_bridge_packet.get("owner_question_views")
    if not isinstance(raw_views, (list, tuple)):
        return [], {}, BLOCK_OWNER_QUESTION_VIEW_MISSING

    views_by_identity: dict[tuple[str, str], Service1ColumnOwnerQuestionViewV1] = {}
    for view in raw_views:
        if not isinstance(view, Service1ColumnOwnerQuestionViewV1):
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        if view.question_required:
            identity = (str(view.sheet_name).strip(), str(view.column_name).strip())
            if identity in views_by_identity:
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            views_by_identity[identity] = view

    questions: list[dict[str, Any]] = []
    bindings_by_ref: dict[str, dict[str, str]] = {}
    for candidate in candidates:
        column = str(getattr(candidate, "source_column_name", "") or "").strip()
        sheet = str(getattr(candidate, "sheet_name", "") or "").strip()
        ref_id = _candidate_ref_id(candidate)
        if not ref_id:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        view = views_by_identity.get((sheet, column))
        if view is None or not view.question or not view.options:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_MISSING

        metadata = dict(getattr(candidate, "metadata", {}) or {})
        raw_options = metadata.get("allowed_owner_answers")
        if not isinstance(raw_options, list):
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID

        internal_bindings: dict[str, str] = {}
        for option in raw_options:
            if not isinstance(option, dict):
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            option_id = str(option.get("option_id") or "").strip()
            linked = option.get("linked_hypothesis")
            if option_id == OWNER_OPTION_OTHER:
                continue
            if not option_id or not isinstance(linked, dict):
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            semantic_role = str(linked.get("semantic_role") or "").strip()
            if not semantic_role:
                return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
            if semantic_role == "unknown":
                continue
            internal_bindings[option_id] = semantic_role

        safe_options = [
            option.to_dict()
            for option in view.options
            if option.option_id in internal_bindings
            or option.option_id == OWNER_OPTION_OTHER
        ]
        safe_options.append(
            {
                "option_id": OWNER_OPTION_IGNORE,
                "label": "No usar esta columna",
                "description": (
                    "La columna no es necesaria para este análisis y queda fuera "
                    "sin modificar el archivo original."
                ),
            }
        )
        question = {
            "question_id": ref_id,
            "field_id": ref_id,
            "column_name": column,
            "sheet_name": view.sheet_name,
            "title": view.title,
            "context": view.context,
            "question": view.question,
            "options": safe_options,
            "allowed_option_ids": [item["option_id"] for item in safe_options],
            "free_text_option_id": OWNER_OPTION_OTHER,
            "risk_note": view.risk_note,
            "confidence_note": view.confidence_note,
            "answer_type": "select_owner_option_id",
            "required": True,
        }
        if not _owner_question_surface_is_safe(question, candidate):
            return [], {}, BLOCK_OWNER_QUESTION_SURFACE_UNSAFE

        internal_bindings[OWNER_OPTION_IGNORE] = "IGNORED_NOT_RELEVANT"
        questions.append(question)
        if ref_id in bindings_by_ref:
            return [], {}, BLOCK_OWNER_QUESTION_VIEW_INVALID
        bindings_by_ref[ref_id] = internal_bindings

    return questions, bindings_by_ref, None


def _candidate_ref_id(candidate: Any) -> str:
    metadata = dict(getattr(candidate, "metadata", {}) or {})
    return str(
        metadata.get("column_ref_id")
        or metadata.get("question_id")
        or getattr(candidate, "source_column_name", "")
        or ""
    ).strip()


def _owner_question_surface_is_safe(
    question: dict[str, Any], candidate: Any
) -> bool:
    generated_surface = {
        "options": question.get("options", []),
        "answer_type": question.get("answer_type"),
        "free_text_option_id": question.get("free_text_option_id"),
    }
    rendered = str(generated_surface).lower()
    internal_tokens = {
        str(role).strip().lower()
        for role in (getattr(candidate, "candidate_semantic_roles", ()) or ())
        if str(role).strip()
    }
    internal_tokens.update(
        {
            "ignored_not_relevant",
            "owner_rectified_function",
            "computed_variables",
        }
    )
    return not any(token in rendered for token in internal_tokens)


def _packet(
    *,
    status: str,
    case_id: Optional[str],
    source_kind: Optional[str],
    filename: Optional[str],
    candidate_count: int,
    candidate_roles: list[str],
    variable_family_bindings: tuple[Any, ...],
    ready_variable_family_ids: tuple[str, ...],
    controlled_execution_candidate: Optional[dict[str, Any]],
    owner_questions: list[dict[str, Any]],
    owner_answer_bindings: dict[str, dict[str, str]],
    p6_decisions: tuple[Any, ...] = (),
    requirement_matches: tuple[Any, ...] = (),
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
        "variable_family_count": len(variable_family_bindings),
        "variable_family_bindings": variable_family_bindings,
        "ready_variable_family_ids": list(ready_variable_family_ids),
        "controlled_execution_candidate": controlled_execution_candidate,
        "owner_questions": owner_questions,
        "owner_answer_bindings": {
            column: dict(bindings)
            for column, bindings in owner_answer_bindings.items()
        },
        "p6_decisions": [decision.to_dict() for decision in p6_decisions],
        "requirement_matches": [match.to_dict() for match in requirement_matches],
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
        "variable_family_count": 0,
        "variable_family_bindings": (),
        "ready_variable_family_ids": [],
        "controlled_execution_candidate": None,
        "owner_questions": [],
        "owner_answer_bindings": {},
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
    "BLOCK_NO_ACTIVE_CANDIDATES",
    "BLOCK_INVALID_CANDIDATE",
    "BLOCK_CANDIDATE_FLAGS_FORBIDDEN",
    "BLOCK_OWNER_QUESTION_VIEW_MISSING",
    "BLOCK_OWNER_QUESTION_VIEW_INVALID",
    "BLOCK_OWNER_QUESTION_SURFACE_UNSAFE",
    "OWNER_OPTION_OTHER",
    "OWNER_OPTION_IGNORE",
    "build_service_1_controlled_execution_gate_from_semantic_bridge_v1",
]

