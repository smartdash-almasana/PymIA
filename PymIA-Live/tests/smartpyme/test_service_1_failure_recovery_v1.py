from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_failure_recovery_v1 import (
    FALLBACK_KIND,
    RETRY_KIND,
    SCHEMA_VERSION,
    build_service_1_failure_recovery_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "PROCESSING_CANDIDATE",
        "current_chain_status": "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
        },
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _job() -> dict[str, object]:
    return {
        "job_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "requested_job_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "source_file_intake_ref": "evidence_candidate:owner:pyme:001:case:s1:001:file:ventas",
        "autonomous_chain_candidate_refs": {"pipeline_request_candidate_ref": "pipeline_request:s1:001"},
        "planned_job_steps": ["validate_non_executable_job_candidate"],
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _failure_event(**overrides: object) -> dict[str, object]:
    event: dict[str, object] = {
        "failure_kind": "JOB_ORCHESTRATION_BLOCKED_TEMPORARY",
        "failure_status": "BLOCKED_MISSING_JOB_INPUT_REFS",
        "failure_summary": "Job orchestration is missing a retryable input ref.",
        "failure_ref_suffix": "failure-001",
        "source_slice_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "source_ref_keys": ["source_session_ref", "source_file_intake_ref", "pipeline_request_candidate_ref"],
        "recovery_attempt_count": 1,
        "recovery_max_attempts": 3,
        "is_recoverable": False,
        "owner_visible": False,
        "mutation_requested": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }
    event.update(overrides)
    return event


def _payload() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _session(),
        "saas_file_intake_candidate": None,
        "saas_job_orchestration_candidate": _job(),
        "audit_log_append_candidate": None,
        "conversational_owner_bridge_candidate": None,
        "guarded_llm_response_candidate": None,
        "owner_question_route_candidate": None,
        "failure_event": _failure_event(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_failure_recovery_v1(payload)  # type: ignore[arg-type]


def test_ready_path_emits_retry_candidate() -> None:
    result = _build(_payload())
    candidate = result["failure_recovery_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "FAILURE_RECOVERY_RETRY_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["is_recoverable"] is True
    assert candidate is not None
    assert candidate["recovery_kind"] == RETRY_KIND
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["source_session_ref"] == "case:s1:001"
    assert candidate["failure_event_ref_candidate"] == (
        "failure_event_candidate:owner:pyme:001:case:s1:001:job_orchestration_blocked_temporary:failure-001"
    )
    assert candidate["failure_kind"] == "JOB_ORCHESTRATION_BLOCKED_TEMPORARY"
    assert candidate["source_slice_kind"] == "SAAS_JOB_ORCHESTRATION_CANDIDATE"
    assert candidate["source_slice_ref"] == "evidence_candidate:owner:pyme:001:case:s1:001:file:ventas"
    assert candidate["recovery_attempt_count"] == 1
    assert candidate["recovery_max_attempts"] == 3
    assert candidate["source_context_refs"] == {
        "source_session_ref": "case:s1:001",
        "source_file_intake_ref": "evidence_candidate:owner:pyme:001:case:s1:001:file:ventas",
        "pipeline_request_candidate_ref": "pipeline_request:s1:001",
    }
    assert candidate["recovery_execution_authorized"] is False
    assert candidate["scheduled_retry_authorized"] is False
    assert candidate["worker_authorized"] is False
    assert candidate["queue_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert candidate["pydantic_ai_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["api_exposed"] is False


def test_non_recoverable_kind_emits_fallback_candidate() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(failure_kind="SLICE_BLOCKED_PERMANENT")
    result = _build(payload)
    candidate = result["failure_recovery_candidate"]
    assert result["status"] == "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY"
    assert result["is_recoverable"] is False
    assert candidate is not None
    assert candidate["recovery_kind"] == FALLBACK_KIND
    assert candidate["fallback_reason"] == "failure_kind_not_recoverable"
    assert candidate["hide_failure"] is False
    assert candidate["owner_notified"] is False
    assert candidate["operator_escalation_authorized"] is False


def test_exhausted_recoverable_failure_emits_fallback_not_retry() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(recovery_attempt_count=3, recovery_max_attempts=3)
    result = _build(payload)
    candidate = result["failure_recovery_candidate"]
    assert result["status"] == "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY"
    assert result["is_recoverable"] is False
    assert candidate is not None
    assert candidate["recovery_kind"] == FALLBACK_KIND
    assert candidate["fallback_reason"] == "recovery_attempt_exhausted"


def test_blocks_if_session_is_missing() -> None:
    payload = _payload()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"


def test_blocks_if_session_is_invalid() -> None:
    payload = _payload()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["session_kind"] = "REAL_SESSION"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_kind_must_be_saas_case_session_candidate"


def test_blocks_if_failure_event_is_missing() -> None:
    payload = _payload()
    payload["failure_event"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FAILURE_EVENT"
    assert result["blocked_reason"] == "failure_event_required"


def test_blocks_if_failure_kind_is_unsupported() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(failure_kind="MADE_UP_FAILURE")
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_FAILURE_KIND"
    assert result["blocked_reason"] == "failure_kind_not_supported"


def test_blocks_if_attempt_count_is_invalid() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(recovery_attempt_count=-1)
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FAILURE_EVENT"
    assert result["blocked_reason"] == "recovery_attempt_count_invalid"


def test_blocks_if_recovery_flags_are_unsafe() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(runtime_authorized=True)
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_RECOVERY_FLAGS"
    assert result["blocked_reason"] == "runtime_authorized_must_be_false"


def test_blocks_hide_failure_violation() -> None:
    payload = _payload()
    payload["failure_event"] = _failure_event(hide_failure=True)
    result = _build(payload)
    assert result["status"] == "BLOCKED_HIDE_FAILURE_VIOLATION"
    assert result["blocked_reason"] == "hide_failure_must_be_false"


def test_blocks_if_source_candidate_is_missing() -> None:
    payload = _payload()
    payload["saas_job_orchestration_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SOURCE_CANDIDATE"
    assert result["blocked_reason"] == "source_candidate_required_for_failure_kind"


def test_blocks_if_source_candidate_kind_mismatches() -> None:
    payload = _payload()
    job = copy.deepcopy(payload["saas_job_orchestration_candidate"])
    job["job_kind"] = "REAL_JOB"
    payload["saas_job_orchestration_candidate"] = job
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SOURCE_CANDIDATE"
    assert result["blocked_reason"] == "source_candidate_kind_mismatch"


def test_cross_tenant_failure_emits_visible_fallback_candidate() -> None:
    payload = _payload()
    job = copy.deepcopy(payload["saas_job_orchestration_candidate"])
    job["owner_ref"] = "owner:pyme:other"
    payload["saas_job_orchestration_candidate"] = job
    result = _build(payload)
    candidate = result["failure_recovery_candidate"]
    assert result["status"] == "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY"
    assert result["is_recoverable"] is False
    assert candidate is not None
    assert candidate["recovery_kind"] == FALLBACK_KIND
    assert candidate["fallback_reason"] == "source_candidate_owner_ref_must_match_session"
    assert candidate["requires_owner_intervention"] is True
    assert candidate["requires_operator_escalation"] is True
    assert candidate["hide_failure"] is False


def test_case_mismatch_failure_emits_visible_fallback_candidate() -> None:
    payload = _payload()
    job = copy.deepcopy(payload["saas_job_orchestration_candidate"])
    job["case_ref"] = "case:s1:other"
    payload["saas_job_orchestration_candidate"] = job
    result = _build(payload)
    candidate = result["failure_recovery_candidate"]
    assert result["status"] == "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["recovery_kind"] == FALLBACK_KIND
    assert candidate["fallback_reason"] == "source_candidate_case_ref_must_match_session"


def test_unsafe_source_flags_emit_visible_fallback_candidate() -> None:
    payload = _payload()
    job = copy.deepcopy(payload["saas_job_orchestration_candidate"])
    job["runner_authorized"] = True
    payload["saas_job_orchestration_candidate"] = job
    result = _build(payload)
    candidate = result["failure_recovery_candidate"]
    assert result["status"] == "FAILURE_RECOVERY_FALLBACK_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["recovery_kind"] == FALLBACK_KIND
    assert candidate["fallback_reason"] == "runner_authorized_must_be_false"
    assert candidate["recovery_execution_authorized"] is False


def test_flags_stay_false_on_result_and_candidates() -> None:
    for result in (
        _build(_payload()),
        _build({**_payload(), "failure_event": _failure_event(failure_kind="SLICE_BLOCKED_PERMANENT")}),
    ):
        candidate = result["failure_recovery_candidate"]
        assert result["recovery_execution_authorized"] is False
        assert result["scheduled_retry_authorized"] is False
        assert result["worker_authorized"] is False
        assert result["queue_authorized"] is False
        assert result["db_authorized"] is False
        assert result["storage_write_authorized"] is False
        assert result["pipeline_authorized"] is False
        assert result["runner_authorized"] is False
        assert result["llm_authorized"] is False
        assert result["pydantic_ai_authorized"] is False
        assert result["mutation_authorized"] is False
        assert result["runtime_authorized"] is False
        assert result["api_exposed"] is False
        assert candidate is not None
        assert candidate["recovery_execution_authorized"] is False
        assert candidate["scheduled_retry_authorized"] is False
        assert candidate["worker_authorized"] is False
        assert candidate["queue_authorized"] is False
        assert candidate["db_authorized"] is False
        assert candidate["storage_write_authorized"] is False
        assert candidate["pipeline_authorized"] is False
        assert candidate["runner_authorized"] is False
        assert candidate["llm_authorized"] is False
        assert candidate["pydantic_ai_authorized"] is False
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


def test_module_source_does_not_import_io_time_uuid_random_api_db_worker_pipeline_runner_or_llm() -> None:
    import pymia.smartpyme.service_1_failure_recovery_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "from pathlib",
        "tempfile",
        "import time",
        "from time",
        "datetime",
        "import uuid",
        "from uuid",
        "import random",
        "from random",
        "open(",
        "write(",
        "fastapi",
        "starlette",
        "flask",
        "django",
        "sqlalchemy",
        "supabase",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "autonomous_pipeline_runner",
        "run_service_1_pipeline",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "import pydantic_ai",
        "from pydantic_ai",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
