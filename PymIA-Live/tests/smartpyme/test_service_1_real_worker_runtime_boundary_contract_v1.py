from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_real_worker_runtime_boundary_contract_v1 import (
    AUTONOMOUS_RERUN_PROCESSING_CANDIDATE,
    BOUNDARY_KIND,
    COST_AND_RATE_LIMIT_GUARD_KIND,
    FAILURE_RECOVERY_RETRY_KIND,
    INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
    REQUEST_RUNTIME_EXECUTION,
    SCHEMA_VERSION,
    TENANT_ISOLATION_GUARD_KIND,
    build_service_1_real_worker_runtime_boundary_contract_v1,
)


def _tenant_isolation_candidate() -> dict[str, object]:
    return {
        "guard_kind": TENANT_ISOLATION_GUARD_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "session:s1:001",
        "checked_source_candidate_kinds": ["SAAS_JOB_ORCHESTRATION_CANDIDATE"],
        "checked_source_refs": {
            "identity.tenant_ref": "tenant:pyme:001",
            "job.session_ref": "session:s1:001",
        },
        "tenant_isolation_passed": True,
        "cross_tenant_access_detected": False,
        "cross_case_access_detected": False,
        "cross_session_access_detected": False,
        "correction_applied": False,
        "auth_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _cost_rate_limit_candidate() -> dict[str, object]:
    return {
        "guard_kind": COST_AND_RATE_LIMIT_GUARD_KIND,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "session:s1:001",
        "requested_operation_kind": INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
        "estimated_cost_units": 2,
        "max_cost_units": 5,
        "current_window_request_count": 0,
        "max_window_request_count": 10,
        "current_budget_used_units": 3,
        "max_budget_units": 20,
        "projected_budget_used_units": 5,
        "remaining_cost_headroom_units": 3,
        "remaining_window_request_capacity": 10,
        "remaining_budget_units": 15,
        "cost_limit_passed": True,
        "rate_limit_passed": True,
        "budget_limit_passed": True,
        "cost_charge_authorized": False,
        "rate_limit_mutation_authorized": False,
        "billing_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _failure_recovery_candidate() -> dict[str, object]:
    return {
        "recovery_kind": FAILURE_RECOVERY_RETRY_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "session:s1:001",
        "failure_event_ref_candidate": "failure_event:001",
        "failure_kind": "JOB_ORCHESTRATION_BLOCKED_TEMPORARY",
        "failure_status": "BLOCKED",
        "failure_summary": "Temporary orchestration block.",
        "source_slice_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "source_slice_ref": "job_candidate:001",
        "recovery_attempt_count": 0,
        "recovery_max_attempts": 2,
        "source_context_refs": {"session_ref": "session:s1:001"},
        "recovery_execution_authorized": False,
        "scheduled_retry_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "job_candidate_ref": "job_candidate:001",
        "operation_kind": INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
        "pipeline_request_candidate_ref": None,
        "file_intake_candidate_ref": "file_intake:001",
        "cost_estimate_units": 2,
        "rate_limit_context_ref": "rate_limit:001",
        "retry_context": None,
        "tenant_isolation_candidate": _tenant_isolation_candidate(),
        "cost_rate_limit_candidate": _cost_rate_limit_candidate(),
        "failure_recovery_candidate": None,
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_real_worker_runtime_boundary_contract_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["worker_runtime_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["next_required_action"] == "KEEP_WORKER_RUNTIME_GOVERNED"
    assert candidate is not None
    assert candidate["boundary_kind"] == BOUNDARY_KIND
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["session_ref"] == "session:s1:001"
    assert candidate["job_candidate_ref"] == "job_candidate:001"
    assert candidate["operation_kind"] == INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE
    assert candidate["file_intake_candidate_ref"] == "file_intake:001"
    assert candidate["pipeline_request_candidate_ref"] is None
    assert candidate["warnings"] == []
    assert candidate["errors"] == []
    assert candidate["job_execution_candidate"] == {
        "candidate_kind": "JOB_EXECUTION_CANDIDATE",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "job_candidate_ref": "job_candidate:001",
        "operation_kind": INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
        "pipeline_request_candidate_ref": None,
        "file_intake_candidate_ref": "file_intake:001",
        "cost_estimate_units": 2,
        "rate_limit_context_ref": "rate_limit:001",
        "execution_granted": False,
    }
    assert candidate["runtime_authorization_candidate"] == {
        "candidate_kind": "RUNTIME_AUTHORIZATION_CANDIDATE",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "operation_kind": INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE,
        "runtime_execution_authorized": False,
        "pipeline_execution_authorized": False,
        "retry_authorized": False,
    }
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "WORKER_RUNTIME_BOUNDARY_CANDIDATE_READY"
    assert audit_event_candidate["source_slice_kind"] == "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE"
    assert audit_event_candidate["source_context_refs"]["job_candidate_ref"] == "job_candidate:001"


def test_missing_session() -> None:
    payload = _payload()
    payload["session_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "session_ref_required"


def test_invalid_job() -> None:
    payload = _payload()
    payload["job_candidate_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_JOB"
    assert result["blocked_reason"] == "job_candidate_ref_required"


def test_tenant_isolation_blocked() -> None:
    payload = _payload()
    tenant_isolation_candidate = copy.deepcopy(payload["tenant_isolation_candidate"])
    tenant_isolation_candidate["tenant_isolation_passed"] = False
    payload["tenant_isolation_candidate"] = tenant_isolation_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_TENANT_ISOLATION"
    assert result["blocked_reason"] == "tenant_isolation_pass_must_be_true"


def test_cost_rate_blocked() -> None:
    payload = _payload()
    cost_rate_limit_candidate = copy.deepcopy(payload["cost_rate_limit_candidate"])
    cost_rate_limit_candidate["budget_limit_passed"] = False
    payload["cost_rate_limit_candidate"] = cost_rate_limit_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_COST_OR_RATE_LIMIT"
    assert result["blocked_reason"] == "budget_limit_must_be_passed"


def test_runtime_not_authorized() -> None:
    payload = _payload()
    payload["operation_kind"] = REQUEST_RUNTIME_EXECUTION
    result = _build(payload)
    assert result["status"] == "BLOCKED_RUNTIME_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "runtime_execution_not_authorized_by_worker_boundary"


def test_pipeline_not_authorized() -> None:
    payload = _payload()
    payload["operation_kind"] = AUTONOMOUS_RERUN_PROCESSING_CANDIDATE
    payload["pipeline_request_candidate_ref"] = None
    cost_rate_limit_candidate = copy.deepcopy(payload["cost_rate_limit_candidate"])
    cost_rate_limit_candidate["requested_operation_kind"] = AUTONOMOUS_RERUN_PROCESSING_CANDIDATE
    payload["cost_rate_limit_candidate"] = cost_rate_limit_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_PIPELINE_NOT_AUTHORIZED"
    assert result["blocked_reason"] == "pipeline_request_candidate_ref_required_for_operation"


def test_failure_recovery_required() -> None:
    payload = _payload()
    payload["retry_context"] = {
        "retry_requested": True,
        "owner_confirmation_required": False,
        "retry_reason": "temporary_block",
    }
    payload["failure_recovery_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_FAILURE_RECOVERY_REQUIRED"
    assert result["blocked_reason"] == "failure_recovery_candidate_required_for_retry"


def test_needs_owner_input() -> None:
    payload = _payload()
    payload["retry_context"] = {
        "retry_requested": False,
        "owner_confirmation_required": True,
        "retry_reason": "owner_review",
    }
    result = _build(payload)
    assert result["status"] == "NEEDS_OWNER_INPUT"
    assert result["blocked_reason"] == "owner_confirmation_required_before_worker_runtime"


def test_needs_evidence() -> None:
    payload = _payload()
    payload["file_intake_candidate_ref"] = None
    result = _build(payload)
    assert result["status"] == "NEEDS_EVIDENCE"
    assert result["blocked_reason"] == "file_intake_candidate_ref_required_for_initial_file_intake"


def test_unknown_fallback() -> None:
    payload = _payload()
    payload["tenant_ref"] = ""
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "tenant_ref_required"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["worker_runtime_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["worker_authorized"] is False
    assert result["queue_authorized"] is False
    assert result["scheduler_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["retry_authorized"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["api_exposed"] is False
    assert candidate is not None
    assert candidate["worker_authorized"] is False
    assert candidate["queue_authorized"] is False
    assert candidate["scheduler_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["retry_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["api_exposed"] is False
    assert audit_event_candidate is not None
    assert audit_event_candidate["worker_authorized"] is False
    assert audit_event_candidate["pipeline_authorized"] is False
    assert audit_event_candidate["runner_authorized"] is False
    assert audit_event_candidate["runtime_authorized"] is False
    assert audit_event_candidate["storage_write_authorized"] is False
    assert audit_event_candidate["db_authorized"] is False
    assert audit_event_candidate["api_exposed"] is False


def test_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_deterministic() -> None:
    payload = _payload()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second


def test_source_guard_no_forbidden_imports() -> None:
    import pymia.smartpyme.service_1_real_worker_runtime_boundary_contract_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import asyncio",
        "from asyncio",
        "\nimport queue",
        "\nfrom queue",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "bullmq",
        "temporal",
        "prefect",
        "threading",
        "multiprocessing",
        "redis",
        "autonomous_pipeline_runner",
        "run_service_1_pipeline",
        "open(",
        "write(",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
