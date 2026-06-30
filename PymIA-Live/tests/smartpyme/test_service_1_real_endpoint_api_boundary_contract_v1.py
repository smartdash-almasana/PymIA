from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_real_endpoint_api_boundary_contract_v1 import (
    BOUNDARY_KIND,
    COST_AND_RATE_LIMIT_GUARD_KIND,
    SCHEMA_VERSION,
    TENANT_ISOLATION_GUARD_KIND,
    build_service_1_real_endpoint_api_boundary_contract_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "PROCESSING_CANDIDATE",
        "current_chain_status": "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY",
        "service_1_state_refs": {"case_truth_ref": "case_truth:s1:001"},
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _tenant_isolation_candidate() -> dict[str, object]:
    return {
        "guard_kind": TENANT_ISOLATION_GUARD_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "checked_source_candidate_kinds": ["SAAS_CASE_SESSION_CANDIDATE"],
        "checked_source_refs": {"session.session_ref": "case:s1:001"},
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
        "source_session_ref": "case:s1:001",
        "requested_operation_kind": "SUBMIT_CASE_PAYLOAD",
        "estimated_cost_units": 1,
        "max_cost_units": 5,
        "current_window_request_count": 0,
        "max_window_request_count": 10,
        "current_budget_used_units": 3,
        "max_budget_units": 20,
        "projected_budget_used_units": 4,
        "remaining_cost_headroom_units": 4,
        "remaining_window_request_capacity": 10,
        "remaining_budget_units": 16,
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


def _payload() -> dict[str, object]:
    return {
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "case_creation_payload": None,
        "request_id": "req-001",
        "operation_kind": "SUBMIT_CASE_PAYLOAD",
        "payload_ref": "payload_ref:ventas_marzo",
        "payload": {"rows_ref": "rows:ventas_marzo"},
        "idempotency_key": "idem-001",
        "client_channel": "WEB_PORTAL",
        "saas_case_session_candidate": _session(),
        "tenant_isolation_candidate": _tenant_isolation_candidate(),
        "cost_rate_limit_candidate": _cost_rate_limit_candidate(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_real_endpoint_api_boundary_contract_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["api_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "API_BOUNDARY_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["next_required_action"] == "PREPARE_CASE_PAYLOAD_CANDIDATE"
    assert candidate is not None
    assert candidate["boundary_kind"] == BOUNDARY_KIND
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["request_id"] == "req-001"
    assert candidate["idempotency_key"] == "idem-001"
    assert candidate["client_channel"] == "WEB_PORTAL"
    assert candidate["accepted_operation_kind"] == "SUBMIT_CASE_PAYLOAD"
    assert candidate["case_session_candidate_ref"] == "case:s1:001"
    assert candidate["payload_ref"] == "payload_ref:ventas_marzo"
    assert candidate["payload_present"] is True
    assert candidate["next_required_action"] == "PREPARE_CASE_PAYLOAD_CANDIDATE"
    assert candidate["runtime_authorization_required"] is False
    assert candidate["warnings"] == []
    assert candidate["errors"] == []
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "API_BOUNDARY_CANDIDATE_READY"
    assert audit_event_candidate["source_slice_kind"] == "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE"
    assert audit_event_candidate["source_context_refs"]["tenant_ref"] == "tenant:pyme:001"
    assert audit_event_candidate["source_context_refs"]["request_id"] == "req-001"
    assert audit_event_candidate["api_exposed"] is False
    assert audit_event_candidate["runtime_authorized"] is False


def test_missing_tenant() -> None:
    payload = _payload()
    payload["tenant_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_TENANT"
    assert result["blocked_reason"] == "tenant_ref_required"


def test_missing_owner() -> None:
    payload = _payload()
    payload["owner_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_OWNER"
    assert result["blocked_reason"] == "owner_ref_required"


def test_invalid_operation() -> None:
    payload = _payload()
    payload["operation_kind"] = "MADE_UP_OPERATION"
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_OPERATION"
    assert result["blocked_reason"] == "operation_kind_not_supported"


def test_invalid_session() -> None:
    payload = _payload()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["session_kind"] = "REAL_SESSION"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_kind_must_be_saas_case_session_candidate"


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


def test_unauthorized_runtime_blocked() -> None:
    payload = _payload()
    payload["operation_kind"] = "REQUEST_RUNTIME_EXECUTION"
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNAUTHORIZED_RUNTIME"
    assert result["blocked_reason"] == "runtime_execution_not_authorized_by_endpoint_boundary"


def test_needs_owner_input() -> None:
    payload = _payload()
    payload["operation_kind"] = "CREATE_CASE_SESSION"
    payload["case_ref"] = None
    payload["case_creation_payload"] = None
    payload["saas_case_session_candidate"] = None
    payload["tenant_isolation_candidate"] = None
    payload["cost_rate_limit_candidate"] = None
    result = _build(payload)
    assert result["status"] == "NEEDS_OWNER_INPUT"
    assert result["blocked_reason"] == "case_creation_payload_required_for_create_case_session"


def test_needs_evidence() -> None:
    payload = _payload()
    payload["payload_ref"] = None
    payload["payload"] = None
    result = _build(payload)
    assert result["status"] == "NEEDS_EVIDENCE"
    assert result["blocked_reason"] == "payload_or_payload_ref_required_for_submit_case_payload"


def test_unknown_fallback() -> None:
    payload = _payload()
    payload["client_channel"] = ""
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "client_channel_required"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["api_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["api_exposed"] is False
    assert result["runtime_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["llm_authorized"] is False
    assert result["mutation_authorized"] is False
    assert candidate is not None
    assert candidate["api_exposed"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert audit_event_candidate is not None
    assert audit_event_candidate["api_exposed"] is False
    assert audit_event_candidate["runtime_authorized"] is False
    assert audit_event_candidate["pipeline_authorized"] is False
    assert audit_event_candidate["runner_authorized"] is False
    assert audit_event_candidate["storage_write_authorized"] is False
    assert audit_event_candidate["db_authorized"] is False
    assert audit_event_candidate["llm_authorized"] is False


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
    import pymia.smartpyme.service_1_real_endpoint_api_boundary_contract_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "fastapi",
        "flask",
        "django",
        "requests",
        "httpx",
        "socket",
        "sqlalchemy",
        "supabase",
        "psycopg",
        "sqlite3",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "import schedule",
        "from schedule",
        "autonomous_pipeline_runner",
        "run_service_1_pipeline",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "import pydantic_ai",
        "from pydantic_ai",
        "from pathlib",
        "tempfile",
        "import os",
        "open(",
        "write(",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
