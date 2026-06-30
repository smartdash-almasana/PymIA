from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_final_owner_release_decision_gate_v1 import (
    DECISION_GATE_KIND,
    DELIVERY_RELEASE_KIND,
    HUMAN_REVIEW_INTEGRATION_KIND,
    OWNER_PACKET_KIND,
    SCHEMA_VERSION,
    build_service_1_final_owner_release_decision_gate_v1,
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


def _human_review_release_integration_candidate() -> dict[str, object]:
    return {
        "gate_kind": HUMAN_REVIEW_INTEGRATION_KIND,
        "candidate_status": "HUMAN_REVIEW_RELEASE_INTEGRATION_CANDIDATE_READY",
        "status": "PENDING_HUMAN_REVIEW",
        "service_name": "SERVICE_1",
        "source_pipeline_run_ref": "pipeline_run:001",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "owner_facing_summary": "Owner packet candidate pending human review.",
        "human_review_required": True,
        "reviewer_role": "operator_or_accountant",
        "decision_required_before_client_use": True,
        "allowed_decisions": ["APPROVED_FOR_DELIVERY", "NEEDS_CORRECTION", "BLOCKED"],
        "blocked_claims": ["auditoria"],
        "publishable": False,
        "signoff_required": True,
        "final_release_authorized": False,
        "boundary_candidate_kinds": {
            "endpoint_api_boundary_kind": "REAL_ENDPOINT_API_BOUNDARY_CANDIDATE",
            "auth_boundary_kind": "REAL_AUTH_BOUNDARY_CANDIDATE",
            "storage_upload_boundary_kind": "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE",
            "worker_runtime_boundary_kind": "REAL_WORKER_RUNTIME_BOUNDARY_CANDIDATE",
        },
        "audit_event_candidate": _audit_event(HUMAN_REVIEW_INTEGRATION_KIND, "pipeline_run:001"),
        "warnings": [],
        "errors": [],
        "publish_authorized": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _human_review_signoff_result() -> dict[str, object]:
    return {
        "schema_version": "SERVICE_1_HUMAN_REVIEW_SIGNOFF_FLOW_V1",
        "service_name": "SERVICE_1",
        "signoff_type": "SERVICE_1_HUMAN_REVIEW_SIGNOFF",
        "status": "SIGNED_OFF_FOR_DELIVERY",
        "decision": "APPROVED_FOR_DELIVERY",
        "reviewer_id": "operator_1",
        "reviewer_role": "operator_or_accountant",
        "case_id": "case:s1:001",
        "delivery_status_before": "READY_FOR_HUMAN_REVIEW",
        "delivery_status_after": "APPROVED_FOR_HUMAN_SUPERVISED_DELIVERY",
        "blocked_reason": None,
        "reviewer_notes": "Reviewed for controlled delivery.",
        "correction_required": False,
        "delivery_allowed_after_signoff": True,
        "runtime_authorized": False,
        "human_review_required": True,
        "autonomous_use_authorized": False,
        "created_at": "2026-06-30T00:00:00+00:00",
        "blocked_claims": ["auditoria"],
        "metadata": {},
    }


def _qa_delivery_gate_result() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "gate_type": "QA_DELIVERY_GATE",
        "status": "PASS",
        "runtime_authorized": False,
        "checks": [
            {"check_id": "qa_001", "label": "dummy", "status": "PASS", "required": True},
        ],
        "checks_passed": 1,
        "checks_total": 1,
        "warnings": [],
        "blockers": [],
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


def _payload() -> dict[str, object]:
    return {
        "human_review_release_integration_candidate": _human_review_release_integration_candidate(),
        "human_review_signoff_result": _human_review_signoff_result(),
        "qa_delivery_gate_result": _qa_delivery_gate_result(),
        "delivery_release_candidate": _delivery_release_candidate(),
        "owner_delivery_packet_candidate": _owner_delivery_packet_candidate(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_final_owner_release_decision_gate_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["final_owner_release_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "FINAL_OWNER_RELEASE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate["candidate_kind"] == DECISION_GATE_KIND
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["source_pipeline_run_ref"] == "pipeline_run:001"
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["session_ref"] == "session:s1:001"
    assert candidate["artifact_refs"] == ["artifact:001", "artifact:002"]
    assert candidate["warning_refs"] == ["warning:001"]
    assert candidate["signoff_status"] == "SIGNED_OFF_FOR_DELIVERY"
    assert candidate["signoff_decision"] == "APPROVED_FOR_DELIVERY"
    assert candidate["qa_gate_status"] == "PASS"
    assert candidate["qa_checks_passed"] == 1
    assert candidate["qa_checks_total"] == 1
    assert candidate["publishable"] is False
    assert candidate["final_release_authorized"] is True
    assert candidate["publish_executed"] is False
    assert candidate["notification_sent"] is False
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "FINAL_OWNER_RELEASE_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "FINAL_OWNER_RELEASE_CANDIDATE_READY"


def test_invalid_human_review_integration() -> None:
    payload = _payload()
    integration_candidate = copy.deepcopy(payload["human_review_release_integration_candidate"])
    integration_candidate["gate_kind"] = "WRONG_GATE"
    payload["human_review_release_integration_candidate"] = integration_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_HUMAN_REVIEW_INTEGRATION"
    assert result["blocked_reason"] == "gate_kind_must_be_human_review_release_integration_candidate"


def test_missing_signoff() -> None:
    payload = _payload()
    payload["human_review_signoff_result"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SIGNOFF"
    assert result["blocked_reason"] == "human_review_signoff_result_required"


def test_rejected_signoff() -> None:
    payload = _payload()
    signoff_result = copy.deepcopy(payload["human_review_signoff_result"])
    signoff_result["status"] = "REJECTED"
    payload["human_review_signoff_result"] = signoff_result
    result = _build(payload)
    assert result["status"] == "BLOCKED_REJECTED_SIGNOFF"
    assert result["blocked_reason"] == "signoff_result_rejected"


def test_invalid_qa() -> None:
    payload = _payload()
    qa_delivery_gate_result = copy.deepcopy(payload["qa_delivery_gate_result"])
    qa_delivery_gate_result["gate_type"] = "OTHER_QA"
    payload["qa_delivery_gate_result"] = qa_delivery_gate_result
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_QA"
    assert result["blocked_reason"] == "qa_gate_type_must_be_qa_delivery_gate"


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
    owner_delivery_packet_candidate["packet_kind"] = "OTHER_PACKET"
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_OWNER_PACKET"
    assert result["blocked_reason"] == "packet_kind_must_be_owner_delivery_packet_candidate"


def test_unsafe_release_flags_blocked() -> None:
    payload = _payload()
    integration_candidate = copy.deepcopy(payload["human_review_release_integration_candidate"])
    integration_candidate["publish_authorized"] = True
    payload["human_review_release_integration_candidate"] = integration_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_RELEASE_FLAGS"
    assert result["blocked_reason"] == "publish_authorized_must_be_false"


def test_needs_signoff() -> None:
    payload = _payload()
    signoff_result = copy.deepcopy(payload["human_review_signoff_result"])
    signoff_result["status"] = "NEEDS_CORRECTION"
    signoff_result["delivery_allowed_after_signoff"] = False
    payload["human_review_signoff_result"] = signoff_result
    result = _build(payload)
    assert result["status"] == "NEEDS_SIGNOFF"
    assert result["blocked_reason"] == "signoff_not_approved_for_delivery"


def test_needs_qa() -> None:
    payload = _payload()
    qa_delivery_gate_result = copy.deepcopy(payload["qa_delivery_gate_result"])
    qa_delivery_gate_result["status"] = "BLOCKED"
    payload["qa_delivery_gate_result"] = qa_delivery_gate_result
    result = _build(payload)
    assert result["status"] == "NEEDS_QA"
    assert result["blocked_reason"] == "qa_delivery_gate_blocked"


def test_unknown_fallback() -> None:
    payload = _payload()
    integration_candidate = copy.deepcopy(payload["human_review_release_integration_candidate"])
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    integration_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    delivery_release_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    owner_delivery_packet_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    payload["human_review_release_integration_candidate"] = integration_candidate
    payload["delivery_release_candidate"] = delivery_release_candidate
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "source_pipeline_run_ref_unknown"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["final_owner_release_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["publish_executed"] is False
    assert result["notification_sent"] is False
    assert result["api_exposed"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["worker_authorized"] is False
    assert result["queue_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["llm_authorized"] is False
    assert candidate is not None
    assert candidate["publish_executed"] is False
    assert candidate["notification_sent"] is False
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
    import pymia.smartpyme.service_1_final_owner_release_decision_gate_v1 as module

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
