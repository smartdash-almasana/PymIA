from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_saas_case_session_model_v1 import (
    SCHEMA_VERSION,
    build_service_1_saas_case_session_model_v1,
)


def _base_input() -> dict[str, object]:
    return {
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "current_chain_status": "AUTONOMOUS_RERUN_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "requested_session_lifecycle": "RERUN_CANDIDATE_READY",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_saas_case_session_model_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_owner_ref_is_missing() -> None:
    payload = _base_input()
    payload["owner_ref"] = ""
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_OWNER_REF"
    assert result["blocked_reason"] == "owner_ref_required"
    assert result["saas_case_session_candidate"] is None


def test_blocks_if_case_ref_is_missing() -> None:
    payload = _base_input()
    payload["case_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE_REF"
    assert result["blocked_reason"] == "case_ref_required"


def test_blocks_if_service_name_is_not_service_1() -> None:
    payload = _base_input()
    payload["service_name"] = "SERVICE_2"
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SERVICE_STATE"
    assert result["blocked_reason"] == "service_name_must_be_service_1"


def test_blocks_if_current_chain_status_is_missing() -> None:
    payload = _base_input()
    payload["current_chain_status"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SERVICE_STATE"
    assert result["blocked_reason"] == "current_chain_status_required"


def test_blocks_if_service_state_refs_are_missing() -> None:
    payload = _base_input()
    payload["service_1_state_refs"] = {}
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SERVICE_STATE"
    assert result["blocked_reason"] == "service_1_state_refs_required"


def test_unknown_if_requested_session_lifecycle_is_missing() -> None:
    payload = _base_input()
    payload["requested_session_lifecycle"] = ""
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "requested_session_lifecycle_required"


def test_unknown_if_requested_session_lifecycle_is_not_allowed() -> None:
    payload = _base_input()
    payload["requested_session_lifecycle"] = "API_SESSION_STARTED"
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "requested_session_lifecycle_not_allowed"


def test_ready_builds_saas_case_session_candidate() -> None:
    result = _build(_base_input())
    assert result["status"] == "SAAS_CASE_SESSION_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["saas_case_session_candidate"] == {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "RERUN_CANDIDATE_READY",
        "current_chain_status": "AUTONOMOUS_RERUN_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def test_preserves_service_1_state_refs_without_alteration() -> None:
    payload = _base_input()
    result = _build(payload)
    candidate = result["saas_case_session_candidate"]
    assert candidate is not None
    assert candidate["service_1_state_refs"] == payload["service_1_state_refs"]
    assert candidate["service_1_state_refs"] is not payload["service_1_state_refs"]


def test_result_never_authorizes_runtime_jobs_upload_or_api() -> None:
    cases = []
    missing_owner = _base_input()
    missing_owner["owner_ref"] = ""
    cases.append(missing_owner)
    bad_lifecycle = _base_input()
    bad_lifecycle["requested_session_lifecycle"] = "API_SESSION_STARTED"
    cases.append(bad_lifecycle)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["runtime_authorized"] is False
        assert result["job_authorized"] is False
        assert result["file_upload_authorized"] is False
        assert result["api_exposed"] is False
        candidate = result["saas_case_session_candidate"]
        if candidate is not None:
            assert candidate["runtime_authorized"] is False
            assert candidate["job_authorized"] is False
            assert candidate["file_upload_authorized"] is False
            assert candidate["api_exposed"] is False


def test_all_allowed_lifecycles_can_create_candidate() -> None:
    allowed = [
        "CREATED",
        "INTAKE_PENDING",
        "PROCESSING_CANDIDATE",
        "OWNER_REVIEW_PENDING",
        "REENTRY_PENDING",
        "RERUN_CANDIDATE_READY",
        "CLOSED_CANDIDATE",
    ]
    for lifecycle in allowed:
        payload = _base_input()
        payload["requested_session_lifecycle"] = lifecycle
        result = _build(payload)
        candidate = result["saas_case_session_candidate"]
        assert result["status"] == "SAAS_CASE_SESSION_CANDIDATE_READY"
        assert candidate is not None
        assert candidate["session_lifecycle"] == lifecycle


def test_module_source_does_not_import_io_cli_api_db_auth_jobs_pipeline_runner_llm_or_chatbot() -> None:
    import pymia.smartpyme.service_1_saas_case_session_model_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "import shutil",
        "from pathlib",
        "tempfile",
        "open(",
        "write(",
        "import pymia.cli",
        "from pymia.cli",
        "fastapi",
        "starlette",
        "flask",
        "django",
        "supabase",
        "sqlalchemy",
        "jwt",
        "celery",
        "rq",
        "run_service_1_pipeline_v1",
        "autonomous_pipeline_runner",
        "llm",
        "chatbot",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source


def test_does_not_mutate_input() -> None:
    payload = _base_input()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_output_is_deterministic() -> None:
    payload = _base_input()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second
