from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_conversational_owner_bridge_contract_v1 import (
    BRIDGE_KIND,
    NEXT_ACTION_BY_INTENT,
    SCHEMA_VERSION,
    build_service_1_conversational_owner_bridge_contract_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "OWNER_REVIEW_PENDING",
        "current_chain_status": "OWNER_DELIVERY_PACKET_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "pipeline_request_candidate_ref": "pipeline_request_candidate:s1:001",
        },
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _session(),
        "owner_message": "  ¿Qué   pasó con  mi caso?  ",
        "owner_intent": None,
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "pipeline_request_candidate_ref": "pipeline_request_candidate:s1:001",
        },
        "generated_folder_refs": {
            "manifest.json": "generated:case:s1:001:manifest.json",
            "owner_message.md": "generated:case:s1:001:owner_message.md",
        },
        "owner_delivery_packet_candidate": {
            "packet_kind": "OWNER_DELIVERY_PACKET_CANDIDATE",
            "source_pipeline_run_ref": "run:s1:001",
            "case_ref": "case:s1:001",
            "publishable": False,
            "signoff_required": True,
            "delivery_authorized": False,
            "autonomous_delivery_authorized": False,
            "signoff_authorized": False,
        },
        "saas_job_orchestration_candidate": {
            "job_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
            "source_session_ref": "case:s1:001",
            "requested_job_kind": "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE",
            "runtime_authorized": False,
            "pipeline_authorized": False,
            "runner_authorized": False,
            "api_exposed": False,
        },
        "notes": ["input note"],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_conversational_owner_bridge_contract_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_session_is_missing() -> None:
    payload = _payload()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"
    assert result["conversational_owner_bridge_candidate"] is None


def test_blocks_if_session_is_invalid() -> None:
    cases = [
        ("session_kind", "HTTP_SESSION", "BLOCKED_INVALID_SESSION", "session_kind_must_be_saas_case_session_candidate"),
        ("service_name", "SERVICE_2", "BLOCKED_INVALID_SESSION", "session_service_name_must_be_service_1"),
        ("owner_ref", "", "BLOCKED_INVALID_SESSION", "session_owner_ref_required"),
        ("case_ref", "", "BLOCKED_INVALID_SESSION", "session_case_ref_required"),
    ]
    for key, value, expected_status, expected_reason in cases:
        payload = _payload()
        session = copy.deepcopy(payload["saas_case_session_candidate"])
        session[key] = value
        payload["saas_case_session_candidate"] = session
        result = _build(payload)
        assert result["status"] == expected_status
        assert result["blocked_reason"] == expected_reason


def test_blocks_if_session_has_unsafe_flags() -> None:
    cases = [
        ("api_exposed", True, "session_api_exposed_must_be_false"),
        ("runtime_authorized", True, "session_runtime_authorized_must_be_false"),
        ("job_authorized", True, "session_job_authorized_must_be_false"),
        ("file_upload_authorized", True, "session_file_upload_authorized_must_be_false"),
    ]
    for key, value, expected_reason in cases:
        payload = _payload()
        session = copy.deepcopy(payload["saas_case_session_candidate"])
        session[key] = value
        payload["saas_case_session_candidate"] = session
        result = _build(payload)
        assert result["status"] == "BLOCKED_UNSAFE_SESSION_FLAGS"
        assert result["blocked_reason"] == expected_reason


def test_blocks_if_owner_message_is_empty() -> None:
    payload = _payload()
    payload["owner_message"] = "   \n\t   "
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_OWNER_MESSAGE"
    assert result["blocked_reason"] == "owner_message_required"


def test_blocks_if_service_1_state_refs_are_empty_after_cleaning() -> None:
    payload = _payload()
    payload["service_1_state_refs"] = {"": "", "case_truth_ref": "   "}
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_STATE_REFS"
    assert result["blocked_reason"] == "service_1_state_refs_required"


def test_blocks_if_explicit_owner_intent_is_not_supported() -> None:
    payload = _payload()
    payload["owner_intent"] = "OWNER_REQUESTS_LEGAL_CERTIFICATION"
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_INTENT"
    assert result["blocked_reason"] == "owner_intent_not_supported"


def test_builds_ready_candidate_with_valid_payload() -> None:
    result = _build(_payload())
    candidate = result["conversational_owner_bridge_candidate"]
    assert result["status"] == "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate == {
        "bridge_kind": BRIDGE_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "owner_message_ref_candidate": "owner_message_candidate:owner:pyme:001:case:s1:001:0eb5b85b9e5d",
        "normalized_owner_message": "¿Qué pasó con mi caso?",
        "owner_intent": "OWNER_ASKS_STATUS",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "pipeline_request_candidate_ref": "pipeline_request_candidate:s1:001",
        },
        "generated_folder_refs": {
            "manifest.json": "generated:case:s1:001:manifest.json",
            "owner_message.md": "generated:case:s1:001:owner_message.md",
        },
        "owner_delivery_packet_ref": "run:s1:001",
        "saas_job_orchestration_ref": "case:s1:001",
        "next_conversational_action": "PREPARE_STATUS_EXPLANATION_CANDIDATE",
        "safe_context_refs_for_future_llm": {
            "source_session_ref": "case:s1:001",
            "owner_message_ref_candidate": "owner_message_candidate:owner:pyme:001:case:s1:001:0eb5b85b9e5d",
            "service_1_state_ref:case_truth_ref": "case_truth:s1:001",
            "service_1_state_ref:pipeline_request_candidate_ref": "pipeline_request_candidate:s1:001",
            "generated_folder_ref:manifest.json": "generated:case:s1:001:manifest.json",
            "generated_folder_ref:owner_message.md": "generated:case:s1:001:owner_message.md",
            "owner_delivery_packet_ref": "run:s1:001",
            "saas_job_orchestration_ref": "case:s1:001",
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


def test_normalizes_owner_message_with_trim_and_space_collapse_only() -> None:
    payload = _payload()
    payload["owner_message"] = "  Hola   dueño \n PyME \t  "
    result = _build(payload)
    candidate = result["conversational_owner_bridge_candidate"]
    assert candidate is not None
    assert candidate["normalized_owner_message"] == "Hola dueño PyME"


def test_classifies_owner_intents_with_simple_rules() -> None:
    cases = [
        ("¿Cómo va esto?", "OWNER_ASKS_STATUS"),
        ("No entiendo qué significa este estado", "OWNER_ASKS_EXPLANATION"),
        ("Aclaro que faltó una factura", "OWNER_PROVIDES_CLARIFICATION"),
        ("Está mal ese costo", "OWNER_PROVIDES_CORRECTION"),
        ("Corré de nuevo el caso", "OWNER_REQUESTS_RERUN"),
        ("¿Qué hago ahora?", "OWNER_ASKS_NEXT_STEP"),
        ("¿Qué me entregaste?", "OWNER_ASKS_DELIVERY_SUMMARY"),
        ("Necesito auditoría legal final", "OWNER_PROVIDES_UNSUPPORTED_MESSAGE"),
    ]
    for owner_message, expected_intent in cases:
        payload = _payload()
        payload["owner_message"] = owner_message
        result = _build(payload)
        candidate = result["conversational_owner_bridge_candidate"]
        assert result["status"] == "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY"
        assert candidate is not None
        assert candidate["owner_intent"] == expected_intent


def test_unknown_if_owner_intent_is_not_recognized() -> None:
    payload = _payload()
    payload["owner_message"] = "Te comparto esto."
    result = _build(payload)
    candidate = result["conversational_owner_bridge_candidate"]
    assert result["status"] == "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["owner_intent"] == "UNKNOWN"


def test_maps_next_conversational_action_correctly() -> None:
    for owner_intent, expected_action in NEXT_ACTION_BY_INTENT.items():
        payload = _payload()
        payload["owner_intent"] = owner_intent
        result = _build(payload)
        candidate = result["conversational_owner_bridge_candidate"]
        assert result["status"] == "CONVERSATIONAL_OWNER_BRIDGE_CANDIDATE_READY"
        assert candidate is not None
        assert candidate["next_conversational_action"] == expected_action


def test_preserves_owner_case_and_source_session_refs() -> None:
    result = _build(_payload())
    candidate = result["conversational_owner_bridge_candidate"]
    assert candidate is not None
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["source_session_ref"] == "case:s1:001"


def test_preserves_service_state_and_generated_folder_refs() -> None:
    payload = _payload()
    result = _build(payload)
    candidate = result["conversational_owner_bridge_candidate"]
    assert candidate is not None
    assert candidate["service_1_state_refs"] == payload["service_1_state_refs"]
    assert candidate["generated_folder_refs"] == payload["generated_folder_refs"]


def test_safe_context_refs_for_future_llm_contains_only_string_refs() -> None:
    result = _build(_payload())
    candidate = result["conversational_owner_bridge_candidate"]
    assert candidate is not None
    safe_refs = candidate["safe_context_refs_for_future_llm"]
    assert safe_refs
    assert all(isinstance(key, str) for key in safe_refs)
    assert all(isinstance(value, str) for value in safe_refs.values())
    assert "normalized_owner_message" not in safe_refs
    assert "¿Qué pasó con mi caso?" not in safe_refs.values()


def test_all_dangerous_flags_are_false_in_result_and_candidate() -> None:
    cases = []
    missing_session = _payload()
    missing_session["saas_case_session_candidate"] = None
    cases.append(missing_session)
    unsupported_intent = _payload()
    unsupported_intent["owner_intent"] = "OWNER_REQUESTS_LEGAL_CERTIFICATION"
    cases.append(unsupported_intent)
    cases.append(_payload())

    for payload in cases:
        result = _build(payload)
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
        candidate = result["conversational_owner_bridge_candidate"]
        if candidate is not None:
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
    import pymia.smartpyme.service_1_conversational_owner_bridge_contract_v1 as module

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
        "import openpyxl",
        "from openpyxl",
        "import pandas",
        "from pandas",
        "service_1_pipeline",
        "autonomous_pipeline_runner",
        "tools.document_ingestion",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
