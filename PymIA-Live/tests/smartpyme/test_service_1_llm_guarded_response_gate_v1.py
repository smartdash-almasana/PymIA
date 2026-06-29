from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_llm_guarded_response_gate_v1 import (
    GATE_KIND,
    SCHEMA_VERSION,
    build_service_1_llm_guarded_response_gate_v1,
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


def _response_candidate() -> dict[str, object]:
    return {
        "response_text_candidate": "  El caso sigue en revisión y ya existe estado verificado.  ",
        "declared_response_scope": ["explain_existing_state", "explain_next_safe_step"],
        "cited_safe_context_ref_keys": [
            "source_session_ref",
            "service_1_state_ref:case_truth_ref",
        ],
        "declared_next_conversational_action": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
        "follow_up_question_candidates": ["¿Querés que te explique el próximo paso seguro?"],
        "missing_evidence_request_candidates": [],
        "clarification_capture_candidates": [],
        "correction_capture_candidates": [],
        "owner_visible_disclaimer_candidates": ["Esta respuesta no autoriza ejecución ni reemplaza revisión humana."],
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
        "llm_response_candidate": _response_candidate(),
        "notes": ["input note"],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_llm_guarded_response_gate_v1(payload)  # type: ignore[arg-type]


def test_ready_valid_candidate() -> None:
    result = _build(_payload())
    candidate = result["guarded_llm_response_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "GUARDED_LLM_RESPONSE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate == {
        "gate_kind": GATE_KIND,
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


def test_blocks_if_bridge_candidate_is_missing() -> None:
    payload = _payload()
    payload["conversational_owner_bridge_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_BRIDGE"
    assert result["blocked_reason"] == "conversational_owner_bridge_candidate_required"


def test_blocks_if_bridge_candidate_is_invalid() -> None:
    payload = _payload()
    bridge = copy.deepcopy(payload["conversational_owner_bridge_candidate"])
    bridge["bridge_kind"] = "REAL_CHATBOT_BRIDGE"
    payload["conversational_owner_bridge_candidate"] = bridge
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_BRIDGE"
    assert result["blocked_reason"] == "bridge_kind_must_be_conversational_owner_bridge_candidate"


def test_blocks_if_bridge_flags_are_unsafe() -> None:
    payload = _payload()
    bridge = copy.deepcopy(payload["conversational_owner_bridge_candidate"])
    bridge["runtime_authorized"] = True
    payload["conversational_owner_bridge_candidate"] = bridge
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "bridge_flags_must_be_false"


def test_blocks_if_response_candidate_is_missing() -> None:
    payload = _payload()
    payload["llm_response_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_LLM_RESPONSE_CANDIDATE"
    assert result["blocked_reason"] == "llm_response_candidate_required"


def test_blocks_if_declared_scope_is_not_allowed() -> None:
    payload = _payload()
    response_candidate = copy.deepcopy(payload["llm_response_candidate"])
    response_candidate["declared_response_scope"] = ["authorize_runtime"]
    payload["llm_response_candidate"] = response_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_SCOPE_NOT_ALLOWED"
    assert result["blocked_reason"] == "declared_response_scope_not_allowed"


def test_blocks_if_declared_scope_is_forbidden() -> None:
    payload = _payload()
    bridge = copy.deepcopy(payload["conversational_owner_bridge_candidate"])
    bridge["allowed_response_scope"] = [
        "explain_existing_state",
        "authorize_runtime",
    ]
    payload["conversational_owner_bridge_candidate"] = bridge
    response_candidate = copy.deepcopy(payload["llm_response_candidate"])
    response_candidate["declared_response_scope"] = ["authorize_runtime"]
    payload["llm_response_candidate"] = response_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_FORBIDDEN_SCOPE"
    assert result["blocked_reason"] == "declared_response_scope_contains_forbidden_scope"


def test_blocks_if_cited_safe_context_ref_does_not_exist() -> None:
    payload = _payload()
    response_candidate = copy.deepcopy(payload["llm_response_candidate"])
    response_candidate["cited_safe_context_ref_keys"] = ["unknown_ref"]
    payload["llm_response_candidate"] = response_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_CONTEXT_REF"
    assert result["blocked_reason"] == "cited_safe_context_ref_key_not_allowed"


def test_blocks_if_declared_next_action_does_not_match_bridge() -> None:
    payload = _payload()
    response_candidate = copy.deepcopy(payload["llm_response_candidate"])
    response_candidate["declared_next_conversational_action"] = "PREPARE_RERUN_REQUEST_CANDIDATE"
    payload["llm_response_candidate"] = response_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_NEXT_ACTION_MISMATCH"
    assert result["blocked_reason"] == "declared_next_conversational_action_must_match_bridge"


def test_blocks_if_response_candidate_attempts_unsafe_authorization() -> None:
    payload = _payload()
    response_candidate = copy.deepcopy(payload["llm_response_candidate"])
    response_candidate["tool_authorized"] = True
    payload["llm_response_candidate"] = response_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "llm_response_candidate_flags_must_be_false"


def test_dangerous_flags_are_always_false() -> None:
    cases = []
    missing_bridge = _payload()
    missing_bridge["conversational_owner_bridge_candidate"] = None
    cases.append(missing_bridge)
    unsafe_response = _payload()
    unsafe_candidate = copy.deepcopy(unsafe_response["llm_response_candidate"])
    unsafe_candidate["chatbot_authorized"] = True
    unsafe_response["llm_response_candidate"] = unsafe_candidate
    cases.append(unsafe_response)
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
        candidate = result["guarded_llm_response_candidate"]
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


def test_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_output_is_deterministic() -> None:
    payload = _payload()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second


def test_module_source_does_not_import_forbidden_dependencies() -> None:
    import pymia.smartpyme.service_1_llm_guarded_response_gate_v1 as module

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
