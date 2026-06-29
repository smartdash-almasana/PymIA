from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_owner_question_router_v1 import (
    ROUTER_KIND,
    SCHEMA_VERSION,
    build_service_1_owner_question_router_v1,
)


def _bridge_candidate() -> dict[str, object]:
    return {
        "bridge_kind": "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "owner_message_ref_candidate": "owner_message_candidate:owner:pyme:001:case:s1:001:abc123def456",
        "normalized_owner_message": "¿Qué pasó con mi caso?",
        "owner_intent": "OWNER_ASKS_STATUS",
        "service_1_state_refs": {"case_truth_ref": "case_truth:s1:001"},
        "generated_folder_refs": {"manifest.json": "generated:case:s1:001:manifest.json"},
        "owner_delivery_packet_ref": "run:s1:001",
        "saas_job_orchestration_ref": "case:s1:001",
        "next_conversational_action": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
        "safe_context_refs_for_future_llm": {
            "source_session_ref": "case:s1:001",
            "owner_message_ref_candidate": "owner_message_candidate:owner:pyme:001:case:s1:001:abc123def456",
            "service_1_state_ref:case_truth_ref": "case_truth:s1:001",
            "generated_folder_ref:manifest.json": "generated:case:s1:001:manifest.json",
            "owner_delivery_packet_ref": "run:s1:001",
        },
        "allowed_response_scope": [
            "explain_existing_state",
            "summarize_existing_delivery_candidate",
            "ask_for_missing_evidence",
            "capture_owner_clarification",
            "capture_owner_correction",
            "explain_next_safe_step",
        ],
        "forbidden_response_scope": [
            "invent_case_truth",
            "diagnose_without_evidence",
            "promise_final_delivery",
            "authorize_runtime",
            "execute_tools",
            "trigger_pipeline",
            "mutate_case",
            "publish_outputs",
            "provide_legal_tax_accounting_certainty",
            "act_as_human_operator",
        ],
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


def _guarded_candidate() -> dict[str, object]:
    return {
        "gate_kind": "GUARDED_LLM_RESPONSE_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "source_bridge_ref_candidate": "conversational_owner_bridge_candidate:owner:pyme:001:case:s1:001",
        "source_owner_message_ref_candidate": "owner_message_candidate:owner:pyme:001:case:s1:001:abc123def456",
        "owner_intent": "OWNER_ASKS_STATUS",
        "next_conversational_action": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
        "response_text_candidate": "El caso sigue en revisión y ya existe estado verificado.",
        "allowed_response_scope": [
            "explain_existing_state",
            "summarize_existing_delivery_candidate",
            "ask_for_missing_evidence",
            "capture_owner_clarification",
            "capture_owner_correction",
            "explain_next_safe_step",
        ],
        "forbidden_response_scope": [
            "invent_case_truth",
            "diagnose_without_evidence",
            "promise_final_delivery",
            "authorize_runtime",
            "execute_tools",
            "trigger_pipeline",
            "mutate_case",
            "publish_outputs",
            "provide_legal_tax_accounting_certainty",
            "act_as_human_operator",
        ],
        "applied_response_scope": ["explain_existing_state", "explain_next_safe_step"],
        "cited_safe_context_refs": {
            "source_session_ref": "case:s1:001",
            "service_1_state_ref:case_truth_ref": "case_truth:s1:001",
        },
        "follow_up_question_candidates": ["¿Querés que te explique el próximo paso seguro?"],
        "missing_evidence_request_candidates": [],
        "clarification_capture_candidates": [],
        "correction_capture_candidates": [],
        "owner_visible_disclaimer_candidates": ["Esta respuesta no autoriza ejecución ni reemplaza revisión humana."],
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


def _payload() -> dict[str, object]:
    return {
        "conversational_owner_bridge_candidate": _bridge_candidate(),
        "guarded_llm_response_candidate": _guarded_candidate(),
        "notes": ["input note"],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_owner_question_router_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["owner_question_route_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "OWNER_QUESTION_ROUTE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate == {
        "router_kind": ROUTER_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "owner_intent": "OWNER_ASKS_STATUS",
        "next_conversational_action": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
        "selected_route": "ROUTE_STATUS_EXPLANATION",
        "route_family": "EXPLANATION",
        "route_reason": "status_intent_and_action_match",
        "route_response_text_candidate": "El caso sigue en revisión y ya existe estado verificado.",
        "route_follow_up_question_candidates": ["¿Querés que te explique el próximo paso seguro?"],
        "route_missing_evidence_request_candidates": [],
        "route_clarification_capture_candidates": [],
        "route_correction_capture_candidates": [],
        "route_owner_visible_disclaimer_candidates": ["Esta respuesta no autoriza ejecución ni reemplaza revisión humana."],
        "cited_safe_context_refs": {
            "source_session_ref": "case:s1:001",
            "service_1_state_ref:case_truth_ref": "case_truth:s1:001",
        },
        "allowed_response_scope": [
            "explain_existing_state",
            "summarize_existing_delivery_candidate",
            "ask_for_missing_evidence",
            "capture_owner_clarification",
            "capture_owner_correction",
            "explain_next_safe_step",
        ],
        "forbidden_response_scope": [
            "invent_case_truth",
            "diagnose_without_evidence",
            "promise_final_delivery",
            "authorize_runtime",
            "execute_tools",
            "trigger_pipeline",
            "mutate_case",
            "publish_outputs",
            "provide_legal_tax_accounting_certainty",
            "act_as_human_operator",
        ],
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


def test_bridge_missing_or_invalid() -> None:
    payload = _payload()
    payload["conversational_owner_bridge_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_BRIDGE"
    assert result["blocked_reason"] == "conversational_owner_bridge_candidate_required"

    payload = _payload()
    bridge = copy.deepcopy(payload["conversational_owner_bridge_candidate"])
    bridge["bridge_kind"] = "REAL_CHATBOT_BRIDGE"
    payload["conversational_owner_bridge_candidate"] = bridge
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_BRIDGE"
    assert result["blocked_reason"] == "bridge_kind_must_be_conversational_owner_bridge_candidate"


def test_guarded_gate_missing_or_invalid() -> None:
    payload = _payload()
    payload["guarded_llm_response_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_GUARDED_CANDIDATE"
    assert result["blocked_reason"] == "guarded_llm_response_candidate_required"

    payload = _payload()
    guarded = copy.deepcopy(payload["guarded_llm_response_candidate"])
    guarded["gate_kind"] = "REAL_LLM_RESPONSE"
    payload["guarded_llm_response_candidate"] = guarded
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_GUARDED_CANDIDATE"
    assert result["blocked_reason"] == "guarded_candidate_kind_must_be_guarded_llm_response_candidate"


def test_action_mismatch() -> None:
    payload = _payload()
    guarded = copy.deepcopy(payload["guarded_llm_response_candidate"])
    guarded["next_conversational_action"] = "PREPARE_STATE_EXPLANATION_CANDIDATE"
    payload["guarded_llm_response_candidate"] = guarded
    result = _build(payload)
    assert result["status"] == "BLOCKED_NEXT_ACTION_MISMATCH"
    assert result["blocked_reason"] == "next_conversational_action_must_match_between_bridge_and_guarded_candidate"


def test_scope_invalid() -> None:
    payload = _payload()
    guarded = copy.deepcopy(payload["guarded_llm_response_candidate"])
    guarded["applied_response_scope"] = ["summarize_existing_delivery_candidate"]
    payload["guarded_llm_response_candidate"] = guarded
    result = _build(payload)
    assert result["status"] == "BLOCKED_ROUTE_NOT_ALLOWED"
    assert result["blocked_reason"] == "selected_route_not_allowed_for_guarded_scope"


def test_blocked_route() -> None:
    payload = _payload()
    bridge = copy.deepcopy(payload["conversational_owner_bridge_candidate"])
    bridge["owner_intent"] = "OWNER_PROVIDES_UNSUPPORTED_MESSAGE"
    bridge["next_conversational_action"] = "BLOCK_UNSUPPORTED_MESSAGE"
    payload["conversational_owner_bridge_candidate"] = bridge
    guarded = copy.deepcopy(payload["guarded_llm_response_candidate"])
    guarded["owner_intent"] = "OWNER_PROVIDES_UNSUPPORTED_MESSAGE"
    guarded["next_conversational_action"] = "BLOCK_UNSUPPORTED_MESSAGE"
    guarded["applied_response_scope"] = ["explain_existing_state"]
    payload["guarded_llm_response_candidate"] = guarded
    result = _build(payload)
    candidate = result["owner_question_route_candidate"]
    assert result["status"] == "OWNER_QUESTION_ROUTE_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["selected_route"] == "ROUTE_BLOCK_UNSUPPORTED_MESSAGE"
    assert candidate["route_family"] == "BLOCK"


def test_flags_false() -> None:
    cases = []
    unsafe_bridge = _payload()
    bridge = copy.deepcopy(unsafe_bridge["conversational_owner_bridge_candidate"])
    bridge["runtime_authorized"] = True
    unsafe_bridge["conversational_owner_bridge_candidate"] = bridge
    cases.append(unsafe_bridge)
    unsafe_guarded = _payload()
    guarded = copy.deepcopy(unsafe_guarded["guarded_llm_response_candidate"])
    guarded["tool_authorized"] = True
    unsafe_guarded["guarded_llm_response_candidate"] = guarded
    cases.append(unsafe_guarded)
    cases.append(_payload())

    for payload in cases:
        result = _build(payload)
        assert result["client_delivery_authorized"] is False
        assert result["llm_authorized"] is False
        assert result["pydantic_ai_authorized"] is False
        assert result["prompt_runtime_authorized"] is False
        assert result["chatbot_authorized"] is False
        assert result["tool_authorized"] is False
        assert result["pipeline_authorized"] is False
        assert result["runner_authorized"] is False
        assert result["mutation_authorized"] is False
        assert result["runtime_authorized"] is False
        assert result["api_exposed"] is False
        candidate = result["owner_question_route_candidate"]
        if candidate is not None:
            assert candidate["client_delivery_authorized"] is False
            assert candidate["llm_authorized"] is False
            assert candidate["pydantic_ai_authorized"] is False
            assert candidate["prompt_runtime_authorized"] is False
            assert candidate["chatbot_authorized"] is False
            assert candidate["tool_authorized"] is False
            assert candidate["pipeline_authorized"] is False
            assert candidate["runner_authorized"] is False
            assert candidate["mutation_authorized"] is False
            assert candidate["runtime_authorized"] is False
            assert candidate["api_exposed"] is False


def test_no_mutation() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_determinism() -> None:
    payload = _payload()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second


def test_source_guard_imports_prohibidos() -> None:
    import pymia.smartpyme.service_1_owner_question_router_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import openai",
        "from openai",
        "import pydantic_ai",
        "from pydantic_ai",
        "import langchain",
        "from langchain",
        "import langgraph",
        "from langgraph",
        "import fastapi",
        "from fastapi",
        "import supabase",
        "from supabase",
        "import sqlalchemy",
        "from sqlalchemy",
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import os",
        "from pathlib",
        "service_1_pipeline",
        "autonomous_pipeline_runner",
        "openpyxl",
        "pandas",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
