from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_final_release_to_owner_handoff_contract_v1 import (
    FINAL_RELEASE_KIND,
    HANDOFF_CHANNEL_KIND,
    HANDOFF_KIND,
    OWNER_PACKET_KIND,
    SCHEMA_VERSION,
    build_service_1_final_release_to_owner_handoff_contract_v1,
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


def _final_owner_release_candidate() -> dict[str, object]:
    return {
        "candidate_kind": FINAL_RELEASE_KIND,
        "service_name": "SERVICE_1",
        "source_pipeline_run_ref": "pipeline_run:001",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "session:s1:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "owner_facing_summary": "Owner packet candidate pending supervised handoff.",
        "signoff_status": "SIGNED_OFF_FOR_DELIVERY",
        "signoff_decision": "APPROVED_FOR_DELIVERY",
        "qa_gate_status": "PASS",
        "qa_checks_passed": 1,
        "qa_checks_total": 1,
        "delivery_status_before_signoff": "PENDING_DELIVERY_POLICY_GUARD",
        "delivery_status_after_signoff": "APPROVED_FOR_HUMAN_SUPERVISED_DELIVERY",
        "publishable": False,
        "final_release_authorized": True,
        "publish_executed": False,
        "notification_sent": False,
        "audit_event_candidate": _audit_event(FINAL_RELEASE_KIND, "pipeline_run:001"),
        "warnings": [],
        "errors": [],
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _owner_delivery_packet_candidate() -> dict[str, object]:
    return {
        "source_pipeline_run_ref": "pipeline_run:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "owner_facing_summary": "Owner packet candidate pending supervised handoff.",
        "packet_kind": OWNER_PACKET_KIND,
        "publishable": False,
        "signoff_required": True,
        "delivery_authorized": False,
        "autonomous_delivery_authorized": False,
        "signoff_authorized": False,
    }


def _delivery_release_candidate() -> dict[str, object]:
    return {
        "source_pipeline_run_ref": "pipeline_run:001",
        "artifact_refs": ["artifact:001", "artifact:002"],
        "warning_refs": ["warning:001"],
        "release_kind": "DELIVERY_RELEASE_CANDIDATE",
        "publishable": False,
        "signoff_required": True,
        "release_authorized": False,
    }


def _handoff_channel_candidate() -> dict[str, object]:
    return {
        "channel_candidate_kind": HANDOFF_CHANNEL_KIND,
        "channel_kind": "OWNER_PORTAL_LINK",
        "channel_ref": "handoff_channel:portal:001",
        "channel_ready": True,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "handoff_authorized": False,
        "handoff_executed": False,
        "publish_executed": False,
        "notification_sent": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "runtime_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _payload() -> dict[str, object]:
    return {
        "final_owner_release_candidate": _final_owner_release_candidate(),
        "owner_delivery_packet_candidate": _owner_delivery_packet_candidate(),
        "delivery_release_candidate": _delivery_release_candidate(),
        "handoff_channel_candidate": _handoff_channel_candidate(),
        "owner_ref": "owner:pyme:001",
        "tenant_ref": "tenant:pyme:001",
        "case_ref": "case:s1:001",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_final_release_to_owner_handoff_contract_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["owner_handoff_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "OWNER_HANDOFF_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate["candidate_kind"] == HANDOFF_KIND
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["source_pipeline_run_ref"] == "pipeline_run:001"
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["session_ref"] == "session:s1:001"
    assert candidate["artifact_refs"] == ["artifact:001", "artifact:002"]
    assert candidate["warning_refs"] == ["warning:001"]
    assert candidate["owner_facing_summary"] == "Owner packet candidate pending supervised handoff."
    assert candidate["handoff_channel_kind"] == "OWNER_PORTAL_LINK"
    assert candidate["handoff_channel_ref"] == "handoff_channel:portal:001"
    assert candidate["handoff_authorized"] is True
    assert candidate["handoff_executed"] is False
    assert candidate["publish_executed"] is False
    assert candidate["notification_sent"] is False
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "OWNER_HANDOFF_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "OWNER_HANDOFF_CANDIDATE_READY"


def test_invalid_final_release() -> None:
    payload = _payload()
    final_owner_release_candidate = copy.deepcopy(payload["final_owner_release_candidate"])
    final_owner_release_candidate["candidate_kind"] = "OTHER_FINAL_RELEASE"
    payload["final_owner_release_candidate"] = final_owner_release_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FINAL_RELEASE"
    assert result["blocked_reason"] == "candidate_kind_must_be_final_owner_release_candidate"


def test_invalid_owner_packet() -> None:
    payload = _payload()
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    owner_delivery_packet_candidate["packet_kind"] = "OTHER_PACKET"
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_OWNER_PACKET"
    assert result["blocked_reason"] == "packet_kind_must_be_owner_delivery_packet_candidate"


def test_invalid_delivery_release() -> None:
    payload = _payload()
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    delivery_release_candidate["release_kind"] = "OTHER_RELEASE"
    payload["delivery_release_candidate"] = delivery_release_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_DELIVERY_RELEASE"
    assert result["blocked_reason"] == "release_kind_must_be_delivery_release_candidate"


def test_missing_owner() -> None:
    payload = _payload()
    payload["owner_ref"] = " "
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_OWNER"
    assert result["blocked_reason"] == "owner_ref_required"


def test_missing_tenant() -> None:
    payload = _payload()
    payload["tenant_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_TENANT"
    assert result["blocked_reason"] == "tenant_ref_required"


def test_missing_case() -> None:
    payload = _payload()
    payload["case_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE"
    assert result["blocked_reason"] == "case_ref_required"


def test_invalid_handoff_channel() -> None:
    payload = _payload()
    handoff_channel_candidate = copy.deepcopy(payload["handoff_channel_candidate"])
    handoff_channel_candidate["channel_kind"] = "OTHER_CHANNEL"
    payload["handoff_channel_candidate"] = handoff_channel_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_HANDOFF_CHANNEL"
    assert result["blocked_reason"] == "channel_kind_not_allowed"


def test_unsafe_handoff_flags_blocked() -> None:
    payload = _payload()
    handoff_channel_candidate = copy.deepcopy(payload["handoff_channel_candidate"])
    handoff_channel_candidate["runtime_authorized"] = True
    payload["handoff_channel_candidate"] = handoff_channel_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_HANDOFF_FLAGS"
    assert result["blocked_reason"] == "runtime_authorized_must_be_false"


def test_unknown_fallback() -> None:
    payload = _payload()
    final_owner_release_candidate = copy.deepcopy(payload["final_owner_release_candidate"])
    owner_delivery_packet_candidate = copy.deepcopy(payload["owner_delivery_packet_candidate"])
    delivery_release_candidate = copy.deepcopy(payload["delivery_release_candidate"])
    final_owner_release_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    owner_delivery_packet_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    delivery_release_candidate["source_pipeline_run_ref"] = "pipeline_run:unknown"
    payload["final_owner_release_candidate"] = final_owner_release_candidate
    payload["owner_delivery_packet_candidate"] = owner_delivery_packet_candidate
    payload["delivery_release_candidate"] = delivery_release_candidate
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "source_pipeline_run_ref_unknown"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["owner_handoff_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["handoff_executed"] is False
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
    assert candidate["handoff_executed"] is False
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
    import pymia.smartpyme.service_1_final_release_to_owner_handoff_contract_v1 as module

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
        "whatsapp",
        "open(",
        "write(",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
