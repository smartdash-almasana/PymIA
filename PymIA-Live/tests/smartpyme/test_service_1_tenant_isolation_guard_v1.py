from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_tenant_isolation_guard_v1 import (
    GUARD_KIND,
    SCHEMA_VERSION,
    build_service_1_tenant_isolation_guard_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "INTAKE_PENDING",
        "current_chain_status": "SAAS_FILE_INTAKE_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
        },
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _file_intake() -> dict[str, object]:
    return {
        "intake_kind": "SAAS_FILE_INTAKE_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "file_ref": "upload_ref:file:ventas_marzo",
        "evidence_ref_candidate": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
        "task_spec_candidate_allowed": False,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _audit_log_append() -> dict[str, object]:
    return {
        "audit_kind": "AUDIT_LOG_APPEND_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "audit_log_ref_candidate": "audit_log_candidate:owner:pyme:001:case:s1:001",
        "append_operation": "APPEND_EVENT",
        "appended_event_count": 1,
        "audit_event_candidate": {
            "audit_event_kind": "AUDIT_EVENT_CANDIDATE",
            "event_kind": "FILE_INTAKE_CANDIDATE_RECORDED",
            "event_status": "SAAS_FILE_INTAKE_CANDIDATE_READY",
            "owner_ref": "owner:pyme:001",
            "case_ref": "case:s1:001",
            "service_name": "SERVICE_1",
            "source_session_ref": "case:s1:001",
            "source_slice_kind": "SAAS_FILE_INTAKE_CANDIDATE",
            "source_slice_ref": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
            "audit_log_ref_candidate": "audit_log_candidate:owner:pyme:001:case:s1:001",
            "audit_event_ref_candidate": "audit_event_candidate:owner:pyme:001:case:s1:001:FILE_INTAKE_CANDIDATE_RECORDED:evt-001",
            "append_operation": "APPEND_EVENT",
            "event_summary": "File intake candidate accepted for audit trail.",
            "source_context_refs": {
                "source_session_ref": "case:s1:001",
                "file_ref": "upload_ref:file:ventas_marzo",
                "evidence_ref_candidate": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
            },
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
        },
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


def _payload() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _session(),
        "saas_file_intake_candidate": _file_intake(),
        "saas_job_orchestration_candidate": None,
        "audit_log_append_candidate": _audit_log_append(),
        "conversational_owner_bridge_candidate": None,
        "guarded_llm_response_candidate": None,
        "owner_question_route_candidate": None,
        "requested_source_candidate_kinds": [
            "SAAS_FILE_INTAKE_CANDIDATE",
            "AUDIT_LOG_APPEND_CANDIDATE",
        ],
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_tenant_isolation_guard_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["tenant_isolation_guard_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "TENANT_ISOLATION_GUARD_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate == {
        "guard_kind": GUARD_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "checked_source_candidate_kinds": [
            "SAAS_FILE_INTAKE_CANDIDATE",
            "AUDIT_LOG_APPEND_CANDIDATE",
        ],
        "checked_source_refs": {
            "file_intake.file_ref": "upload_ref:file:ventas_marzo",
            "file_intake.evidence_ref_candidate": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
            "file_intake.source_session_ref": "case:s1:001",
            "audit.audit_log_ref_candidate": "audit_log_candidate:owner:pyme:001:case:s1:001",
            "audit.source_session_ref": "case:s1:001",
            "audit.audit_event.audit_event_ref_candidate": "audit_event_candidate:owner:pyme:001:case:s1:001:FILE_INTAKE_CANDIDATE_RECORDED:evt-001",
            "audit.audit_event.source_slice_ref": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
            "audit.audit_event.audit_log_ref_candidate": "audit_log_candidate:owner:pyme:001:case:s1:001",
            "audit.audit_event.source_session_ref": "case:s1:001",
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


def test_blocks_if_session_is_missing() -> None:
    payload = _payload()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"


def test_blocks_if_session_is_invalid() -> None:
    payload = _payload()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["session_kind"] = "HTTP_SESSION"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_kind_must_be_saas_case_session_candidate"


def test_blocks_if_requested_source_kinds_are_missing() -> None:
    payload = _payload()
    payload["requested_source_candidate_kinds"] = []
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SOURCE_CANDIDATES"
    assert result["blocked_reason"] == "requested_source_candidate_kinds_required"


def test_blocks_if_source_kind_is_invalid() -> None:
    payload = _payload()
    payload["requested_source_candidate_kinds"] = ["UNSUPPORTED_KIND"]
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_SOURCE_KIND"
    assert result["blocked_reason"] == "source_candidate_kind_not_supported"


def test_blocks_if_source_candidate_is_missing() -> None:
    payload = _payload()
    payload["requested_source_candidate_kinds"] = ["SAAS_JOB_ORCHESTRATION_CANDIDATE"]
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SOURCE_CANDIDATE"
    assert result["blocked_reason"] == "source_candidate_required"


def test_blocks_if_source_candidate_kind_mismatches() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["intake_kind"] = "REAL_UPLOAD"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SOURCE_CANDIDATE"
    assert result["blocked_reason"] == "source_candidate_kind_mismatch"


def test_blocks_if_owner_ref_mismatches() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["owner_ref"] = "owner:pyme:other"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_CROSS_TENANT_CONTEXT"
    assert result["blocked_reason"] == "source_owner_ref_must_match_session"


def test_blocks_if_case_ref_mismatches() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["case_ref"] = "case:s1:other"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_CROSS_CASE_CONTEXT"
    assert result["blocked_reason"] == "source_case_ref_must_match_session"


def test_blocks_if_source_session_ref_mismatches() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["source_session_ref"] = "case:s1:other"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_CROSS_SESSION_CONTEXT"
    assert result["blocked_reason"] == "source_session_ref_must_match_session_anchor"


def test_blocks_if_unsafe_flags_are_present() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["runtime_authorized"] = True
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "runtime_authorized_must_be_false"


def test_blocks_if_correction_is_attempted() -> None:
    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["correction_applied"] = True
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "correction_applied_must_be_false"


def test_flags_stay_false_on_ready_result() -> None:
    result = _build(_payload())
    candidate = result["tenant_isolation_guard_candidate"]
    assert result["auth_authorized"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["worker_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert result["llm_authorized"] is False
    assert result["pydantic_ai_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["api_exposed"] is False
    assert candidate is not None
    assert candidate["tenant_isolation_passed"] is True
    assert candidate["cross_tenant_access_detected"] is False
    assert candidate["cross_case_access_detected"] is False
    assert candidate["cross_session_access_detected"] is False
    assert candidate["correction_applied"] is False
    assert candidate["auth_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["worker_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert candidate["pydantic_ai_authorized"] is False
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


def test_module_source_does_not_import_io_time_uuid_random_api_db_auth_worker_pipeline_runner_or_llm() -> None:
    import pymia.smartpyme.service_1_tenant_isolation_guard_v1 as module

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
        "jwt",
        "authlib",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "autonomous_pipeline_runner",
        "run_service_1_pipeline",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
