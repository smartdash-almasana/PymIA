from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_human_review_release_integration_gate_v1 import (
    AUTH_BOUNDARY_KIND,
    DELIVERY_RELEASE_KIND,
    ENDPOINT_BOUNDARY_KIND,
    GATE_KIND,
    OWNER_PACKET_KIND,
    SCHEMA_VERSION,
    STORAGE_BOUNDARY_KIND,
    WORKER_BOUNDARY_KIND,
    build_service_1_human_review_release_integration_gate_v1,
)


def _audit_event(source_slice_kind: str, source_slice_ref: str) -> dict[str, object]:
    return {
        "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
        "event_kind": f"{source_slice_kind}_RECORDED",
        "event_status": "READY",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "session:s1:001",
        "source_slice_kind": source_slice_kind,
        "source_slice_ref": source_slice_ref,
        "audit_log_ref_candidate": "audit_log:owner:pyme:001:case:s1:001",
        "audit_event_ref_candidate": f"audit_event:{source_slice_kind}:{source_slice_ref}",
        "append_operation": "APPEND_EVENT",
        "event_summary": "Recorded.",
        "source_context_refs": {"source_slice_ref": source_slice_ref},
        "owner_visible": False,
        "mutation_requested": False,
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


def _delivery_release_candidate() -> dict[str, object]:
    return {
        "source_pipeline_run_ref": "pipeline_run:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "release_kind": DELIVERY_RELEASE_KIND,
        "publishable": False,
        "signoff_required": True,
    }


def _owner_delivery_packet_candidate() -> dict[str, object]:
    return {
        "source_pipeline_run_ref": "pipeline_run:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "owner_facing_summary": "Owner packet candidate pending human review.",
        "packet_kind": OWNER_PACKET_KIND,
        "publishable": False,
        "signoff_required": True,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "signoff_authorized": False,
    }


def _endpoint_api_boundary_candidate() -> dict[str, object]:
    return {
        "boundary_kind": ENDPOINT_BOUNDARY_KIND,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "request_id": "req:001",
        "idempotency_key": "idem:001",
        "client_channel": "WEB_PORTAL",
        "accepted_operation_kind": "SUBMIT_CASE_PAYLOAD",
        "case_session_candidate_ref": "session:s1:001",
        "payload_ref": "payload:001",
        "payload_present": True,
        "next_required_action": "PREPARE_CASE_PAYLOAD_CANDIDATE",
        "runtime_authorization_required": False,
        "warnings": [],
        "errors": [],
        "audit_event_candidate": _audit_event(ENDPOINT_BOUNDARY_KIND, "req:001"),
        "api_exposed": False,
        "runtime_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "llm_authorized": False,
        "mutation_authorized": False,
    }


def _auth_boundary_candidate() -> dict[str, object]:
    return {
        "boundary_kind": AUTH_BOUNDARY_KIND,
        "auth_subject_ref": "auth_subject:001",
        "external_identity_ref": "external_identity:001",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "service_name": "SERVICE_1",
        "authorized_operation_kind": "REQUEST_CASE_STATUS",
        "client_channel": "WEB_PORTAL",
        "case_access_candidate": {
            "candidate_kind": "CASE_ACCESS_CANDIDATE",
            "tenant_ref": "tenant:pyme:001",
            "owner_ref": "owner:pyme:001",
            "case_ref": "case:s1:001",
            "session_ref": None,
            "access_granted": False,
        },
        "session_access_candidate": {
            "candidate_kind": "SESSION_ACCESS_CANDIDATE",
            "tenant_ref": "tenant:pyme:001",
            "owner_ref": "owner:pyme:001",
            "case_ref": "case:s1:001",
            "session_ref": "session:s1:001",
            "access_granted": False,
        },
        "warnings": [],
        "errors": [],
        "audit_event_candidate": _audit_event(AUTH_BOUNDARY_KIND, "auth_subject:001"),
        "auth_authorized": False,
        "api_exposed": False,
        "db_authorized": False,
        "storage_write_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
    }


def _storage_upload_boundary_candidate() -> dict[str, object]:
    return {
        "boundary_kind": STORAGE_BOUNDARY_KIND,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "upload_request_ref": "upload:req:001",
        "client_channel": "WEB_PORTAL",
        "file_name": "ventas.xlsx",
        "file_kind": "XLSX",
        "file_size_bytes": 4096,
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "storage_object_ref": "storage:file:001",
        "checksum": "sha256:001",
        "safe_file_ref": "safe_file_ref:001",
        "file_intake_candidate_ref": "storage:file:001",
        "evidence_ref_candidate": "evidence_candidate:001",
        "processing_job_candidate_required": False,
        "warnings": [],
        "errors": [],
        "audit_event_candidate": _audit_event(STORAGE_BOUNDARY_KIND, "storage:file:001"),
        "storage_write_authorized": False,
        "file_processing_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "evidence_authorized": False,
        "mutation_authorized": False,
        "db_authorized": False,
        "api_exposed": False,
        "llm_authorized": False,
    }


def _worker_runtime_boundary_candidate() -> dict[str, object]:
    return {
        "boundary_kind": WORKER_BOUNDARY_KIND,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "service_name": "SERVICE_1",
        "job_candidate_ref": "job_candidate:001",
        "operation_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "pipeline_request_candidate_ref": None,
        "file_intake_candidate_ref": "file_intake:001",
        "next_required_action": "KEEP_WORKER_RUNTIME_GOVERNED",
        "job_execution_candidate": {
            "candidate_kind": "JOB_EXECUTION_CANDIDATE",
            "tenant_ref": "tenant:pyme:001",
            "owner_ref": "owner:pyme:001",
            "case_ref": "case:s1:001",
            "session_ref": "session:s1:001",
            "job_candidate_ref": "job_candidate:001",
            "operation_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
            "pipeline_request_candidate_ref": None,
            "file_intake_candidate_ref": "file_intake:001",
            "cost_estimate_units": 2,
            "rate_limit_context_ref": "rate_limit:001",
            "execution_granted": False,
        },
        "runtime_authorization_candidate": {
            "candidate_kind": "RUNTIME_AUTHORIZATION_CANDIDATE",
            "tenant_ref": "tenant:pyme:001",
            "owner_ref": "owner:pyme:001",
            "case_ref": "case:s1:001",
            "session_ref": "session:s1:001",
            "operation_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
            "runtime_execution_authorized": False,
            "pipeline_execution_authorized": False,
            "retry_authorized": False,
        },
        "failure_recovery_candidate": None,
        "audit_event_candidate": _audit_event(WORKER_BOUNDARY_KIND, "job_candidate:001"),
        "warnings": [],
        "errors": [],
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "retry_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "mutation_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "delivery_release_candidate": _delivery_release_candidate(),
        "owner_delivery_packet_candidate": _owner_delivery_packet_candidate(),
        "endpoint_api_boundary_candidate": _endpoint_api_boundary_candidate(),
        "auth_boundary_candidate": _auth_boundary_candidate(),
        "storage_upload_boundary_candidate": _storage_upload_boundary_candidate(),
        "worker_runtime_boundary_candidate": _worker_runtime_boundary_candidate(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_human_review_release_integration_gate_v1(payload)  # type: ignore[arg-type]


def test_ready_pending_human_review() -> None:
    result = _build(_payload())
    candidate = result["human_review_release_integration_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "PENDING_DELIVERY_POLICY_GUARD"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate["gate_kind"] == GATE_KIND
    assert candidate["candidate_status"] == "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY"
    assert candidate["status"] == "PENDING_DELIVERY_POLICY_GUARD"
    assert candidate["source_pipeline_run_ref"] == "pipeline_run:001"
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["session_ref"] == "session:s1:001"
    assert candidate["artifact_refs"] == ["artifact:001", "artifact:002"]
    assert candidate["warning_refs"] == ["warning:001"]
    assert candidate["delivery_policy_guard_required"] is True
    assert candidate["policy_guard_agent"] == "policy_guard_agent"
    assert candidate["decision_required_before_client_use"] is True
    assert candidate["publishable"] is False
    assert candidate["signoff_required"] is True
    assert candidate["final_release_authorized"] is False
    assert candidate["warnings"] == []
    assert candidate["errors"] == []
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "PENDING_DELIVERY_POLICY_GUARD"


def test_invalid_delivery_release() -> None:
    payload = _payload()
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    delivery_release_candidate["release_kind"] = "NOT_RELEASE"
    payload["delivery_release_candidate"] = delivery_release_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_DELIVERY_RELEASE"
    assert result["blocked_reason"] == "release_kind_must_be_delivery_release_candidate"


def test_invalid_owner_packet() -> None:
    payload = _payload()
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    owner_delivery_packet_candidate["artifact_refs"] = ["artifact:only"]
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_OWNER_PACKET"
    assert result["blocked_reason"] == "artifact_refs_must_match_delivery_release_candidate"


def test_invalid_endpoint_boundary() -> None:
    payload = _payload()
    endpoint_api_boundary_candidate = copy.deepcopy(payload["endpoint_api_boundary_candidate"])
    endpoint_api_boundary_candidate["boundary_kind"] = "WRONG_BOUNDARY"
    payload["endpoint_api_boundary_candidate"] = endpoint_api_boundary_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_ENDPOINT_BOUNDARY"
    assert result["blocked_reason"] == "endpoint_boundary_kind_must_match"


def test_invalid_auth_boundary() -> None:
    payload = _payload()
    auth_boundary_candidate = copy.deepcopy(payload["auth_boundary_candidate"])
    auth_boundary_candidate["tenant_ref"] = ""
    payload["auth_boundary_candidate"] = auth_boundary_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_AUTH_BOUNDARY"
    assert result["blocked_reason"] == "auth_tenant_ref_required"


def test_invalid_storage_boundary() -> None:
    payload = _payload()
    storage_upload_boundary_candidate = copy.deepcopy(payload["storage_upload_boundary_candidate"])
    storage_upload_boundary_candidate["case_ref"] = ""
    payload["storage_upload_boundary_candidate"] = storage_upload_boundary_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_STORAGE_BOUNDARY"
    assert result["blocked_reason"] == "storage_case_ref_required"


def test_invalid_worker_boundary() -> None:
    payload = _payload()
    worker_runtime_boundary_candidate = copy.deepcopy(payload["worker_runtime_boundary_candidate"])
    worker_runtime_boundary_candidate["session_ref"] = ""
    payload["worker_runtime_boundary_candidate"] = worker_runtime_boundary_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_WORKER_BOUNDARY"
    assert result["blocked_reason"] == "worker_session_ref_required"


def test_unsafe_publish_flags_blocked() -> None:
    payload = _payload()
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    delivery_release_candidate["publishable"] = True
    payload["delivery_release_candidate"] = delivery_release_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_PUBLISH_FLAGS"
    assert result["blocked_reason"] == "publishable_must_be_false"


def test_needs_signoff() -> None:
    payload = _payload()
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    owner_delivery_packet_candidate["signoff_required"] = False
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "NEEDS_SIGNOFF"
    assert result["blocked_reason"] == "owner_delivery_packet_candidate_must_require_signoff"


def test_unknown_fallback() -> None:
    payload = _payload()
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    delivery_release_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    owner_delivery_packet_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    payload["delivery_release_candidate"] = delivery_release_candidate
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "source_pipeline_run_ref_unknown"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["human_review_release_integration_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["publish_authorized"] is False
    assert result["final_release_authorized"] is False
    assert result["api_exposed"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["worker_authorized"] is False
    assert result["queue_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["llm_authorized"] is False
    assert candidate is not None
    assert candidate["publish_authorized"] is False
    assert candidate["final_release_authorized"] is False
    assert candidate["api_exposed"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["worker_authorized"] is False
    assert candidate["queue_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert audit_event_candidate is not None
    assert audit_event_candidate["api_exposed"] is False
    assert audit_event_candidate["storage_write_authorized"] is False
    assert audit_event_candidate["db_authorized"] is False
    assert audit_event_candidate["worker_authorized"] is False
    assert audit_event_candidate["runtime_authorized"] is False


def test_no_input_mutation() -> None:
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
    import pymia.smartpyme.service_1_human_review_release_integration_gate_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "fastapi",
        "flask",
        "django",
        "streamlit",
        "gradio",
        "tkinter",
        "requests",
        "httpx",
        "socket",
        "sqlalchemy",
        "psycopg",
        "sqlite3",
        "boto3",
        "supabase",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "redis",
        "smtplib",
        "twilio",
        "slack",
        "open(",
        "write(",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
