from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_LLM_GUARDED_RESPONSE_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
GATE_KIND: Final[str] = "GUARDED_LLM_RESPONSE_CANDIDATE"
SOURCE_BRIDGE_KIND: Final[str] = "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE"

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

RESPONSE_CANDIDATE_ALWAYS_FALSE_FLAG_NAMES: Final[tuple[str, ...]] = (
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

LlmGuardedResponseGateStatusV1 = Literal[
    "GUARDED_LLM_RESPONSE_CANDIDATE_READY",
    "BLOCKED_MISSING_BRIDGE",
    "BLOCKED_INVALID_BRIDGE",
    "BLOCKED_MISSING_LLM_RESPONSE_CANDIDATE",
    "BLOCKED_EMPTY_RESPONSE_TEXT",
    "BLOCKED_SCOPE_NOT_ALLOWED",
    "BLOCKED_FORBIDDEN_SCOPE",
    "BLOCKED_UNSAFE_CONTEXT_REF",
    "BLOCKED_NEXT_ACTION_MISMATCH",
    "BLOCKED_UNSAFE_FLAGS",
    "UNKNOWN",
]


class Service1LlmGuardedResponseGateInputV1(TypedDict):
    conversational_owner_bridge_candidate: dict[str, object] | None
    llm_response_candidate: dict[str, object] | None
    notes: list[str]


class Service1FutureLlmResponseCandidateV1(TypedDict):
    response_text_candidate: str
    declared_response_scope: list[str]
    cited_safe_context_ref_keys: list[str]
    declared_next_conversational_action: str
    follow_up_question_candidates: list[str]
    missing_evidence_request_candidates: list[str]
    clarification_capture_candidates: list[str]
    correction_capture_candidates: list[str]
    owner_visible_disclaimer_candidates: list[str]
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


class Service1LlmGuardedResponseCandidateV1(TypedDict):
    gate_kind: Literal["GUARDED_LLM_RESPONSE_CANDIDATE"]
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    source_bridge_ref_candidate: str | None
    source_owner_message_ref_candidate: str | None
    owner_intent: str
    next_conversational_action: str
    response_text_candidate: str
    allowed_response_scope: list[str]
    forbidden_response_scope: list[str]
    applied_response_scope: list[str]
    cited_safe_context_refs: dict[str, str]
    follow_up_question_candidates: list[str]
    missing_evidence_request_candidates: list[str]
    clarification_capture_candidates: list[str]
    correction_capture_candidates: list[str]
    owner_visible_disclaimer_candidates: list[str]
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


class Service1LlmGuardedResponseGateResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: LlmGuardedResponseGateStatusV1
    guarded_llm_response_candidate: Service1LlmGuardedResponseCandidateV1 | None
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


def build_service_1_llm_guarded_response_gate_v1(
    gate_input: Service1LlmGuardedResponseGateInputV1,
) -> Service1LlmGuardedResponseGateResultV1:
    """Validate a structured future-LLM response candidate against the E.1 bridge.

    This gate is pure and deterministic. It does not call LLMs, APIs, tools,
    pipelines, runners, storage, or runtime layers. It only validates whether
    the proposed response candidate remains inside the bridge's safe scope.
    """
    bridge_candidate = gate_input.get("conversational_owner_bridge_candidate")
    if bridge_candidate is None:
        return _result(
            status="BLOCKED_MISSING_BRIDGE",
            blocked_reason="conversational_owner_bridge_candidate_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response gate requires a conversational owner bridge candidate."),
        )
    if not isinstance(bridge_candidate, dict) or not bridge_candidate:
        return _result(
            status="BLOCKED_INVALID_BRIDGE",
            blocked_reason="conversational_owner_bridge_candidate_invalid",
            notes=_notes(gate_input.get("notes"), "Conversational owner bridge candidate is invalid."),
        )

    bridge_validation_reason = _validate_bridge_candidate(bridge_candidate)
    if bridge_validation_reason is not None:
        status = "BLOCKED_UNSAFE_FLAGS" if bridge_validation_reason == "bridge_flags_must_be_false" else "BLOCKED_INVALID_BRIDGE"
        return _result(
            status=status,
            blocked_reason=bridge_validation_reason,
            notes=_notes(gate_input.get("notes"), "Conversational owner bridge candidate failed guarded response gate validation."),
        )

    response_candidate = gate_input.get("llm_response_candidate")
    if not isinstance(response_candidate, dict) or not response_candidate:
        return _result(
            status="BLOCKED_MISSING_LLM_RESPONSE_CANDIDATE",
            blocked_reason="llm_response_candidate_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response gate requires a structured future-LLM response candidate."),
        )

    if _flags_are_unsafe(response_candidate, RESPONSE_CANDIDATE_ALWAYS_FALSE_FLAG_NAMES):
        return _result(
            status="BLOCKED_UNSAFE_FLAGS",
            blocked_reason="llm_response_candidate_flags_must_be_false",
            notes=_notes(gate_input.get("notes"), "Future-LLM response candidate attempted unsafe authorization."),
        )

    response_text_candidate = _normalize_text(response_candidate.get("response_text_candidate"))
    if response_text_candidate is None:
        return _result(
            status="BLOCKED_EMPTY_RESPONSE_TEXT",
            blocked_reason="response_text_candidate_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response candidate requires non-empty response_text_candidate."),
        )

    allowed_response_scope = _clean_str_list(bridge_candidate.get("allowed_response_scope"))
    forbidden_response_scope = _clean_str_list(bridge_candidate.get("forbidden_response_scope"))
    declared_response_scope = _clean_str_list(response_candidate.get("declared_response_scope"))
    if not declared_response_scope:
        return _result(
            status="BLOCKED_SCOPE_NOT_ALLOWED",
            blocked_reason="declared_response_scope_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response candidate requires declared_response_scope."),
        )
    if any(scope not in allowed_response_scope for scope in declared_response_scope):
        return _result(
            status="BLOCKED_SCOPE_NOT_ALLOWED",
            blocked_reason="declared_response_scope_not_allowed",
            notes=_notes(gate_input.get("notes"), "Declared response scope must remain inside bridge allowed_response_scope."),
        )
    if any(scope in forbidden_response_scope for scope in declared_response_scope):
        return _result(
            status="BLOCKED_FORBIDDEN_SCOPE",
            blocked_reason="declared_response_scope_contains_forbidden_scope",
            notes=_notes(gate_input.get("notes"), "Declared response scope intersects bridge forbidden_response_scope."),
        )

    safe_context_refs_for_future_llm = bridge_candidate.get("safe_context_refs_for_future_llm")
    safe_context_refs = _clean_refs_map(safe_context_refs_for_future_llm)
    cited_safe_context_ref_keys = _clean_str_list(response_candidate.get("cited_safe_context_ref_keys"))
    if not cited_safe_context_ref_keys:
        return _result(
            status="BLOCKED_UNSAFE_CONTEXT_REF",
            blocked_reason="cited_safe_context_ref_keys_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response candidate requires cited_safe_context_ref_keys."),
        )
    if any(key not in safe_context_refs for key in cited_safe_context_ref_keys):
        return _result(
            status="BLOCKED_UNSAFE_CONTEXT_REF",
            blocked_reason="cited_safe_context_ref_key_not_allowed",
            notes=_notes(gate_input.get("notes"), "All cited safe context ref keys must exist in bridge safe_context_refs_for_future_llm."),
        )

    bridge_next_action = _clean_required_ref(bridge_candidate.get("next_conversational_action"))
    declared_next_action = _clean_required_ref(response_candidate.get("declared_next_conversational_action"))
    if declared_next_action is None:
        return _result(
            status="BLOCKED_NEXT_ACTION_MISMATCH",
            blocked_reason="declared_next_conversational_action_required",
            notes=_notes(gate_input.get("notes"), "Guarded LLM response candidate requires declared_next_conversational_action."),
        )
    if bridge_next_action is None or declared_next_action != bridge_next_action:
        return _result(
            status="BLOCKED_NEXT_ACTION_MISMATCH",
            blocked_reason="declared_next_conversational_action_must_match_bridge",
            notes=_notes(gate_input.get("notes"), "Declared next conversational action must match the bridge candidate."),
        )

    owner_ref = str(bridge_candidate["owner_ref"]).strip()
    case_ref = str(bridge_candidate["case_ref"]).strip()
    source_session_ref = str(bridge_candidate["source_session_ref"]).strip()
    source_owner_message_ref_candidate = _clean_required_ref(bridge_candidate.get("owner_message_ref_candidate"))

    candidate: Service1LlmGuardedResponseCandidateV1 = {
        "gate_kind": GATE_KIND,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "source_bridge_ref_candidate": _source_bridge_ref_candidate(bridge_candidate),
        "source_owner_message_ref_candidate": source_owner_message_ref_candidate,
        "owner_intent": str(bridge_candidate["owner_intent"]),
        "next_conversational_action": declared_next_action,
        "response_text_candidate": response_text_candidate,
        "allowed_response_scope": list(allowed_response_scope),
        "forbidden_response_scope": list(forbidden_response_scope),
        "applied_response_scope": list(declared_response_scope),
        "cited_safe_context_refs": {key: safe_context_refs[key] for key in cited_safe_context_ref_keys},
        "follow_up_question_candidates": _clean_str_list(response_candidate.get("follow_up_question_candidates")),
        "missing_evidence_request_candidates": _clean_str_list(response_candidate.get("missing_evidence_request_candidates")),
        "clarification_capture_candidates": _clean_str_list(response_candidate.get("clarification_capture_candidates")),
        "correction_capture_candidates": _clean_str_list(response_candidate.get("correction_capture_candidates")),
        "owner_visible_disclaimer_candidates": _clean_str_list(response_candidate.get("owner_visible_disclaimer_candidates")),
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
        status="GUARDED_LLM_RESPONSE_CANDIDATE_READY",
        guarded_llm_response_candidate=candidate,
        notes=_notes(gate_input.get("notes"), "Guarded LLM response candidate validated inside bridge scope without runtime authority."),
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
    safe_context_refs = _clean_refs_map(bridge_candidate.get("safe_context_refs_for_future_llm"))
    if not safe_context_refs:
        return "bridge_safe_context_refs_required"
    allowed_response_scope = _clean_str_list(bridge_candidate.get("allowed_response_scope"))
    if not allowed_response_scope:
        return "bridge_allowed_response_scope_required"
    if _flags_are_unsafe(bridge_candidate, ALWAYS_FALSE_FLAG_NAMES):
        return "bridge_flags_must_be_false"
    return None


def _flags_are_unsafe(candidate: dict[str, object], flag_names: tuple[str, ...]) -> bool:
    return any(candidate.get(flag_name) is not False for flag_name in flag_names)


def _source_bridge_ref_candidate(bridge_candidate: dict[str, object]) -> str | None:
    explicit_ref = _clean_required_ref(bridge_candidate.get("source_bridge_ref_candidate"))
    if explicit_ref is not None:
        return explicit_ref
    owner_ref = _clean_required_ref(bridge_candidate.get("owner_ref"))
    case_ref = _clean_required_ref(bridge_candidate.get("case_ref"))
    if owner_ref is None or case_ref is None:
        return None
    return f"conversational_owner_bridge_candidate:{_safe_ref(owner_ref)}:{_safe_ref(case_ref)}"


def _safe_ref(value: str) -> str:
    return " ".join(value.strip().split()).replace(" ", "_")


def _normalize_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return normalized


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
    status: LlmGuardedResponseGateStatusV1,
    guarded_llm_response_candidate: Service1LlmGuardedResponseCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1LlmGuardedResponseGateResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "guarded_llm_response_candidate": guarded_llm_response_candidate,
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
    "GATE_KIND",
    "SOURCE_BRIDGE_KIND",
    "ALWAYS_FALSE_FLAG_NAMES",
    "RESPONSE_CANDIDATE_ALWAYS_FALSE_FLAG_NAMES",
    "Service1LlmGuardedResponseGateInputV1",
    "Service1FutureLlmResponseCandidateV1",
    "Service1LlmGuardedResponseCandidateV1",
    "Service1LlmGuardedResponseGateResultV1",
    "build_service_1_llm_guarded_response_gate_v1",
]
