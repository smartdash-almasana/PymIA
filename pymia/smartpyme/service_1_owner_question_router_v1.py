from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_OWNER_QUESTION_ROUTER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
ROUTER_KIND: Final[str] = "OWNER_QUESTION_ROUTE_CANDIDATE"
SOURCE_BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"
SOURCE_GUARDED_KIND: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE"

ROUTE_STATUS_EXPLANATION: Final[str] = "ROUTE_STATUS_EXPLANATION"
ROUTE_STATE_EXPLANATION: Final[str] = "ROUTE_STATE_EXPLANATION"
ROUTE_OWNER_CLARIFICATION_CAPTURE: Final[str] = "ROUTE_OWNER_CLARIFICATION_CAPTURE"
ROUTE_OWNER_CORRECTION_CAPTURE: Final[str] = "ROUTE_OWNER_CORRECTION_CAPTURE"
ROUTE_RERUN_REQUEST_CAPTURE: Final[str] = "ROUTE_RERUN_REQUEST_CAPTURE"
ROUTE_NEXT_STEP_EXPLANATION: Final[str] = "ROUTE_NEXT_STEP_EXPLANATION"
ROUTE_DELIVERY_SUMMARY_EXPLANATION: Final[str] = "ROUTE_DELIVERY_SUMMARY_EXPLANATION"
ROUTE_MISSING_EVIDENCE_REQUEST: Final[str] = "ROUTE_MISSING_EVIDENCE_REQUEST"
ROUTE_BLOCK_UNSUPPORTED_MESSAGE: Final[str] = "ROUTE_BLOCK_UNSUPPORTED_MESSAGE"

FAMILY_EXPLANATION: Final[str] = "EXPLANATION"
FAMILY_CAPTURE: Final[str] = "CAPTURE"
FAMILY_REQUEST: Final[str] = "REQUEST"
FAMILY_BLOCK: Final[str] = "BLOCK"

ALWAYS_FALSE_FLAG_NAMES: Final[tuple[str, ...]] = (
    "llm_authorized",
    "pydantic_ai_authorized",
    "prompt_runtime_authorized",
    "chatbot_authorized",
    "tool_authorized",
    "pipeline_authorized",
    "runner_authorized",
    "mutation_authorized",
    "runtime_authorized",
    "api_exposed",
)

GUARDED_ALWAYS_FALSE_FLAG_NAMES: Final[tuple[str, ...]] = (
    "client_delivery_authorized",
    "llm_authorized",
    "pydantic_ai_authorized",
    "prompt_runtime_authorized",
    "chatbot_authorized",
    "tool_authorized",
    "pipeline_authorized",
    "runner_authorized",
    "mutation_authorized",
    "runtime_authorized",
    "api_exposed",
)

ROUTE_FAMILY_BY_ROUTE: Final[dict[str, str]] = {
    ROUTE_STATUS_EXPLANATION: FAMILY_EXPLANATION,
    ROUTE_STATE_EXPLANATION: FAMILY_EXPLANATION,
    ROUTE_NEXT_STEP_EXPLANATION: FAMILY_EXPLANATION,
    ROUTE_DELIVERY_SUMMARY_EXPLANATION: FAMILY_EXPLANATION,
    ROUTE_OWNER_CLARIFICATION_CAPTURE: FAMILY_CAPTURE,
    ROUTE_OWNER_CORRECTION_CAPTURE: FAMILY_CAPTURE,
    ROUTE_RERUN_REQUEST_CAPTURE: FAMILY_REQUEST,
    ROUTE_MISSING_EVIDENCE_REQUEST: FAMILY_REQUEST,
    ROUTE_BLOCK_UNSUPPORTED_MESSAGE: FAMILY_BLOCK,
}

OwnerQuestionRouterStatusV1 = Literal[
    "OWNER_QUESTION_ROUTE_CANDIDATE_READY",
    "BLOCKED_MISSING_BRIDGE",
    "BLOCKED_INVALID_BRIDGE",
    "BLOCKED_MISSING_GUARDED_CANDIDATE",
    "BLOCKED_INVALID_GUARDED_CANDIDATE",
    "BLOCKED_IDENTITY_MISMATCH",
    "BLOCKED_ROUTE_NOT_ALLOWED",
    "BLOCKED_NEXT_ACTION_MISMATCH",
    "BLOCKED_UNSAFE_FLAGS",
    "UNKNOWN",
]


class Service1OwnerQuestionRouterInputV1(TypedDict):
    conversational_owner_bridge_candidate: dict[str, object] | None
    guarded_llm_response_candidate: dict[str, object] | None
    notes: list[str]


class Service1OwnerQuestionRouteCandidateV1(TypedDict):
    router_kind: Literal["OWNER_QUESTION_ROUTE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    owner_intent: str
    next_conversational_action: str
    selected_route: str
    route_family: str
    route_reason: str
    route_response_text_candidate: str
    route_follow_up_question_candidates: list[str]
    route_missing_evidence_request_candidates: list[str]
    route_clarification_capture_candidates: list[str]
    route_correction_capture_candidates: list[str]
    route_owner_visible_disclaimer_candidates: list[str]
    cited_safe_context_refs: dict[str, str]
    allowed_response_scope: list[str]
    forbidden_response_scope: list[str]
    client_delivery_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1OwnerQuestionRouterResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: OwnerQuestionRouterStatusV1
    owner_question_route_candidate: Service1OwnerQuestionRouteCandidateV1 | None
    blocked_reason: str | None
    client_delivery_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    prompt_runtime_authorized: Literal[False]
    chatbot_authorized: Literal[False]
    tool_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_owner_question_router_v1(
    router_input: Service1OwnerQuestionRouterInputV1,
) -> Service1OwnerQuestionRouterResultV1:
    """Route a validated conversational interaction into one safe route candidate.

    This router is pure and deterministic. It consumes the E.1 bridge and E.2
    guarded response candidate and emits one allowed route candidate, without
    granting runtime, mutation, tool, or delivery authority.
    """
    bridge_candidate = router_input.get("conversational_owner_bridge_candidate")
    if bridge_candidate is None:
        return _result(
            status="BLOCKED_MISSING_BRIDGE",
            blocked_reason="conversational_owner_bridge_candidate_required",
            notes=_notes(router_input.get("notes"), "Owner question router requires a conversational owner bridge candidate."),
        )
    if not isinstance(bridge_candidate, dict) or not bridge_candidate:
        return _result(
            status="BLOCKED_INVALID_BRIDGE",
            blocked_reason="conversational_owner_bridge_candidate_invalid",
            notes=_notes(router_input.get("notes"), "Conversational owner bridge candidate is invalid."),
        )

    bridge_validation_reason = _validate_bridge_candidate(bridge_candidate)
    if bridge_validation_reason is not None:
        status = "BLOCKED_UNSAFE_FLAGS" if bridge_validation_reason == "bridge_flags_must_be_false" else "BLOCKED_INVALID_BRIDGE"
        return _result(
            status=status,
            blocked_reason=bridge_validation_reason,
            notes=_notes(router_input.get("notes"), "Conversational owner bridge candidate failed router validation."),
        )

    guarded_candidate = router_input.get("guarded_llm_response_candidate")
    if guarded_candidate is None:
        return _result(
            status="BLOCKED_MISSING_GUARDED_CANDIDATE",
            blocked_reason="guarded_llm_response_candidate_required",
            notes=_notes(router_input.get("notes"), "Owner question router requires a guarded LLM response candidate."),
        )
    if not isinstance(guarded_candidate, dict) or not guarded_candidate:
        return _result(
            status="BLOCKED_INVALID_GUARDED_CANDIDATE",
            blocked_reason="guarded_llm_response_candidate_invalid",
            notes=_notes(router_input.get("notes"), "Guarded LLM response candidate is invalid."),
        )

    guarded_validation_reason = _validate_guarded_candidate(guarded_candidate)
    if guarded_validation_reason is not None:
        status = "BLOCKED_UNSAFE_FLAGS" if guarded_validation_reason == "guarded_candidate_flags_must_be_false" else "BLOCKED_INVALID_GUARDED_CANDIDATE"
        return _result(
            status=status,
            blocked_reason=guarded_validation_reason,
            notes=_notes(router_input.get("notes"), "Guarded LLM response candidate failed router validation."),
        )

    bridge_owner_ref = str(bridge_candidate["owner_ref"]).strip()
    guarded_owner_ref = str(guarded_candidate["owner_ref"]).strip()
    if guarded_owner_ref != bridge_owner_ref:
        return _result(
            status="BLOCKED_IDENTITY_MISMATCH",
            blocked_reason="owner_ref_must_match_between_bridge_and_guarded_candidate",
            notes=_notes(router_input.get("notes"), "Bridge and guarded candidate owner_ref must match."),
        )

    bridge_case_ref = str(bridge_candidate["case_ref"]).strip()
    guarded_case_ref = str(guarded_candidate["case_ref"]).strip()
    if guarded_case_ref != bridge_case_ref:
        return _result(
            status="BLOCKED_IDENTITY_MISMATCH",
            blocked_reason="case_ref_must_match_between_bridge_and_guarded_candidate",
            notes=_notes(router_input.get("notes"), "Bridge and guarded candidate case_ref must match."),
        )

    bridge_source_session_ref = str(bridge_candidate["source_session_ref"]).strip()
    guarded_source_session_ref = str(guarded_candidate["source_session_ref"]).strip()
    if guarded_source_session_ref != bridge_source_session_ref:
        return _result(
            status="BLOCKED_IDENTITY_MISMATCH",
            blocked_reason="source_session_ref_must_match_between_bridge_and_guarded_candidate",
            notes=_notes(router_input.get("notes"), "Bridge and guarded candidate source_session_ref must match."),
        )

    bridge_next_action = str(bridge_candidate["next_conversational_action"]).strip()
    guarded_next_action = _clean_required_ref(guarded_candidate.get("next_conversational_action"))
    if guarded_next_action != bridge_next_action:
        return _result(
            status="BLOCKED_NEXT_ACTION_MISMATCH",
            blocked_reason="next_conversational_action_must_match_between_bridge_and_guarded_candidate",
            notes=_notes(router_input.get("notes"), "Bridge and guarded candidate next_conversational_action must match."),
        )

    owner_intent = str(bridge_candidate["owner_intent"]).strip()
    applied_response_scope = _clean_str_list(guarded_candidate.get("applied_response_scope"))
    selected_route_info = _select_route(
        owner_intent=owner_intent,
        next_conversational_action=bridge_next_action,
        applied_response_scope=applied_response_scope,
    )
    if selected_route_info is None:
        return _result(
            status="BLOCKED_ROUTE_NOT_ALLOWED",
            blocked_reason="selected_route_not_allowed_for_guarded_scope",
            notes=_notes(router_input.get("notes"), "No safe route could be selected from bridge intent/action and guarded applied scope."),
        )

    selected_route, route_reason = selected_route_info
    if selected_route not in ROUTE_FAMILY_BY_ROUTE:
        return _result(
            status="BLOCKED_ROUTE_NOT_ALLOWED",
            blocked_reason="blocked_route_family_detected",
            notes=_notes(router_input.get("notes"), "Selected route is not part of the allowed route families."),
        )

    route_candidate: Service1OwnerQuestionRouteCandidateV1 = {
        "router_kind": ROUTER_KIND,
        "owner_ref": bridge_owner_ref,
        "case_ref": bridge_case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": bridge_source_session_ref,
        "owner_intent": owner_intent,
        "next_conversational_action": bridge_next_action,
        "selected_route": selected_route,
        "route_family": ROUTE_FAMILY_BY_ROUTE[selected_route],
        "route_reason": route_reason,
        "route_response_text_candidate": str(guarded_candidate["response_text_candidate"]),
        "route_follow_up_question_candidates": _clean_str_list(guarded_candidate.get("follow_up_question_candidates")),
        "route_missing_evidence_request_candidates": _clean_str_list(guarded_candidate.get("missing_evidence_request_candidates")),
        "route_clarification_capture_candidates": _clean_str_list(guarded_candidate.get("clarification_capture_candidates")),
        "route_correction_capture_candidates": _clean_str_list(guarded_candidate.get("correction_capture_candidates")),
        "route_owner_visible_disclaimer_candidates": _clean_str_list(guarded_candidate.get("owner_visible_disclaimer_candidates")),
        "cited_safe_context_refs": _clean_refs_map(guarded_candidate.get("cited_safe_context_refs")),
        "allowed_response_scope": _clean_str_list(bridge_candidate.get("allowed_response_scope")),
        "forbidden_response_scope": _clean_str_list(bridge_candidate.get("forbidden_response_scope")),
        "client_delivery_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "prompt_runtime_authorized": False,
        "chatbot_authorized": False,
        "tool_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="OWNER_QUESTION_ROUTE_CANDIDATE_READY",
        owner_question_route_candidate=route_candidate,
        notes=_notes(router_input.get("notes"), "Owner question route candidate selected without runtime, mutation, tool, or delivery authority."),
    )


def _validate_bridge_candidate(bridge_candidate: dict[str, object]) -> str | None:
    if bridge_candidate.get("bridge_kind") != SOURCE_BRIDGE_KIND:
        return "bridge_kind_must_be_conversational_owner_bridge_candidate"
    if bridge_candidate.get("service_name") != SERVICE_NAME:
        return "bridge_service_name_must_be_service_1"
    if _clean_required_ref(bridge_candidate.get("owner_ref")) is None:
        return "bridge_owner_ref_required"
    if _clean_required_ref(bridge_candidate.get("case_ref")) is None:
        return "bridge_case_ref_required"
    if _clean_required_ref(bridge_candidate.get("next_conversational_action")) is None:
        return "bridge_next_conversational_action_required"
    if _flags_are_unsafe(bridge_candidate, ALWAYS_FALSE_FLAG_NAMES):
        return "bridge_flags_must_be_false"
    return None


def _validate_guarded_candidate(guarded_candidate: dict[str, object]) -> str | None:
    if guarded_candidate.get("gate_kind") != SOURCE_GUARDED_KIND:
        return "guarded_candidate_kind_must_be_guarded_llm_response_candidate"
    if guarded_candidate.get("service_name") != SERVICE_NAME:
        return "guarded_candidate_service_name_must_be_service_1"
    if _clean_required_ref(guarded_candidate.get("owner_ref")) is None:
        return "guarded_candidate_owner_ref_required"
    if _clean_required_ref(guarded_candidate.get("case_ref")) is None:
        return "guarded_candidate_case_ref_required"
    if not _clean_str_list(guarded_candidate.get("applied_response_scope")):
        return "guarded_candidate_applied_response_scope_required"
    if _flags_are_unsafe(guarded_candidate, GUARDED_ALWAYS_FALSE_FLAG_NAMES):
        return "guarded_candidate_flags_must_be_false"
    return None


def _select_route(
    *,
    owner_intent: str,
    next_conversational_action: str,
    applied_response_scope: list[str],
) -> tuple[str, str] | None:
    if owner_intent in {"OWNER_PROVIDES_UNSUPPORTED_MESSAGE", "UNKNOWN"} and next_conversational_action == "BLOCK_UNSUPPORTED_MESSAGE":
        return (ROUTE_BLOCK_UNSUPPORTED_MESSAGE, "blocked_unsupported_or_unknown_owner_intent")
    if "ask_for_missing_evidence" in applied_response_scope:
        return (ROUTE_MISSING_EVIDENCE_REQUEST, "guarded_scope_requests_missing_evidence")

    route_mapping: dict[tuple[str, str], tuple[str, str, tuple[str, ...]]] = {
        ("OWNER_ASKS_STATUS", "PREPARE_STATUS_EXPLANATION_CANDIDATE"): (
            ROUTE_STATUS_EXPLANATION,
            "status_intent_and_action_match",
            ("explain_existing_state",),
        ),
        ("OWNER_ASKS_EXPLANATION", "PREPARE_STATE_EXPLANATION_CANDIDATE"): (
            ROUTE_STATE_EXPLANATION,
            "explanation_intent_and_action_match",
            ("explain_existing_state",),
        ),
        ("OWNER_PROVIDES_CLARIFICATION", "PREPARE_OWNER_CLARIFICATION_CAPTURE_CANDIDATE"): (
            ROUTE_OWNER_CLARIFICATION_CAPTURE,
            "clarification_intent_and_action_match",
            ("capture_owner_clarification",),
        ),
        ("OWNER_PROVIDES_CORRECTION", "PREPARE_OWNER_CORRECTION_CAPTURE_CANDIDATE"): (
            ROUTE_OWNER_CORRECTION_CAPTURE,
            "correction_intent_and_action_match",
            ("capture_owner_correction",),
        ),
        ("OWNER_REQUESTS_RERUN", "PREPARE_RERUN_REQUEST_CANDIDATE"): (
            ROUTE_RERUN_REQUEST_CAPTURE,
            "rerun_request_intent_and_action_match",
            ("explain_next_safe_step",),
        ),
        ("OWNER_ASKS_NEXT_STEP", "PREPARE_NEXT_STEP_EXPLANATION_CANDIDATE"): (
            ROUTE_NEXT_STEP_EXPLANATION,
            "next_step_intent_and_action_match",
            ("explain_next_safe_step",),
        ),
        ("OWNER_ASKS_DELIVERY_SUMMARY", "PREPARE_DELIVERY_SUMMARY_CANDIDATE"): (
            ROUTE_DELIVERY_SUMMARY_EXPLANATION,
            "delivery_summary_intent_and_action_match",
            ("summarize_existing_delivery_candidate",),
        ),
    }
    mapping = route_mapping.get((owner_intent, next_conversational_action))
    if mapping is None:
        return None
    selected_route, route_reason, required_scopes = mapping
    if not any(required_scope in applied_response_scope for required_scope in required_scopes):
        return None
    return (selected_route, route_reason)


def _flags_are_unsafe(candidate: dict[str, object], flag_names: tuple[str, ...]) -> bool:
    return any(candidate.get(flag_name) is not False for flag_name in flag_names)


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _clean_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    clean: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if not stripped:
            continue
        clean.append(stripped)
    return clean


def _clean_refs_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    clean: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            continue
        if not isinstance(item, str) or not item.strip():
            continue
        clean[key] = item
    return clean


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: OwnerQuestionRouterStatusV1,
    owner_question_route_candidate: Service1OwnerQuestionRouteCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1OwnerQuestionRouterResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "owner_question_route_candidate": owner_question_route_candidate,
        "blocked_reason": blocked_reason,
        "client_delivery_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "prompt_runtime_authorized": False,
        "chatbot_authorized": False,
        "tool_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "ROUTER_KIND",
    "SOURCE_BRIDGE_KIND",
    "SOURCE_GUARDED_KIND",
    "ROUTE_STATUS_EXPLANATION",
    "ROUTE_STATE_EXPLANATION",
    "ROUTE_OWNER_CLARIFICATION_CAPTURE",
    "ROUTE_OWNER_CORRECTION_CAPTURE",
    "ROUTE_RERUN_REQUEST_CAPTURE",
    "ROUTE_NEXT_STEP_EXPLANATION",
    "ROUTE_DELIVERY_SUMMARY_EXPLANATION",
    "ROUTE_MISSING_EVIDENCE_REQUEST",
    "ROUTE_BLOCK_UNSUPPORTED_MESSAGE",
    "Service1OwnerQuestionRouterInputV1",
    "Service1OwnerQuestionRouteCandidateV1",
    "Service1OwnerQuestionRouterResultV1",
    "build_service_1_owner_question_router_v1",
]
