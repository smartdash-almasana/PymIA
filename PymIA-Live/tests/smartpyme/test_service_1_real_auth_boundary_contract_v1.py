from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_real_auth_boundary_contract_v1 import (
    BOUNDARY_KIND,
    SCHEMA_VERSION,
    TENANT_ISOLATION_GUARD_KIND,
    build_service_1_real_auth_boundary_contract_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "PROCESSING_CANDIDATE",
        "current_chain_status": "API_BOUNDARY_CANDIDATE_READY",
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
        "checked_source_refs": {
            "session.session_ref": "case:s1:001",
            "identity.tenant_ref": "tenant:pyme:001",
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


def _payload() -> dict[str, object]:
    return {
        "auth_subject_ref": "auth_subject:001",
        "external_identity_ref": "external_identity:001",
        "tenant_claim_ref": "tenant:pyme:001",
        "owner_claim_ref": "owner:pyme:001",
        "requested_operation_kind": "REQUEST_CASE_STATUS",
        "case_ref": "case:s1:001",
        "session_ref": "case:s1:001",
        "client_channel": "WEB_PORTAL",
        "tenant_isolation_candidate": _tenant_isolation_candidate(),
        "case_session_candidate": _session(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_real_auth_boundary_contract_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["auth_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "AUTH_BOUNDARY_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate["boundary_kind"] == BOUNDARY_KIND
    assert candidate["auth_subject_ref"] == "auth_subject:001"
    assert candidate["external_identity_ref"] == "external_identity:001"
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["authorized_operation_kind"] == "REQUEST_CASE_STATUS"
    assert candidate["client_channel"] == "WEB_PORTAL"
    assert candidate["warnings"] == []
    assert candidate["errors"] == []
    assert candidate["case_access_candidate"] == {
        "candidate_kind": "CASE_ACCESS_CANDIDATE",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": None,
        "access_granted": False,
    }
    assert candidate["session_access_candidate"] == {
        "candidate_kind": "SESSION_ACCESS_CANDIDATE",
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "session_ref": "case:s1:001",
        "access_granted": False,
    }
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "REAL_AUTH_BOUNDARY_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "AUTH_BOUNDARY_CANDIDATE_READY"
    assert audit_event_candidate["source_slice_kind"] == "REAL_AUTH_BOUNDARY_CANDIDATE"
    assert audit_event_candidate["source_context_refs"]["tenant_ref"] == "tenant:pyme:001"
    assert audit_event_candidate["api_exposed"] is False


def test_missing_subject() -> None:
    payload = _payload()
    payload["auth_subject_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SUBJECT"
    assert result["blocked_reason"] == "auth_subject_ref_required"


def test_missing_tenant_claim() -> None:
    payload = _payload()
    payload["tenant_claim_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_TENANT_CLAIM"
    assert result["blocked_reason"] == "tenant_claim_ref_required"


def test_missing_owner_claim() -> None:
    payload = _payload()
    payload["owner_claim_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_OWNER_CLAIM"
    assert result["blocked_reason"] == "owner_claim_ref_required"


def test_tenant_mismatch() -> None:
    payload = _payload()
    tenant_isolation_candidate = copy.deepcopy(payload["tenant_isolation_candidate"])
    tenant_isolation_candidate["checked_source_refs"] = {
        "identity.tenant_ref": "tenant:pyme:other",
    }
    payload["tenant_isolation_candidate"] = tenant_isolation_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_TENANT_MISMATCH"
    assert result["blocked_reason"] == "tenant_claim_ref_must_match_tenant_isolation_refs"


def test_owner_case_mismatch() -> None:
    payload = _payload()
    session = copy.deepcopy(payload["case_session_candidate"])
    session["case_ref"] = "case:s1:other"
    payload["case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_SESSION_NOT_ALLOWED"
    assert result["blocked_reason"] == "session_case_ref_must_match_input"

    payload = _payload()
    tenant_isolation_candidate = copy.deepcopy(payload["tenant_isolation_candidate"])
    tenant_isolation_candidate["owner_ref"] = "owner:pyme:other"
    payload["tenant_isolation_candidate"] = tenant_isolation_candidate
    result = _build(payload)
    assert result["status"] == "BLOCKED_OWNER_CASE_MISMATCH"
    assert result["blocked_reason"] == "tenant_isolation_owner_ref_must_match_owner_claim_ref"


def test_operation_not_allowed() -> None:
    payload = _payload()
    payload["requested_operation_kind"] = "REQUEST_RUNTIME_EXECUTION"
    result = _build(payload)
    assert result["status"] == "BLOCKED_OPERATION_NOT_ALLOWED"
    assert result["blocked_reason"] == "runtime_operation_not_allowed_at_auth_boundary"


def test_session_not_allowed() -> None:
    payload = _payload()
    payload["session_ref"] = "session:other"
    result = _build(payload)
    assert result["status"] == "BLOCKED_SESSION_NOT_ALLOWED"
    assert result["blocked_reason"] == "session_ref_must_match_case_session_candidate"


def test_unknown_fallback() -> None:
    payload = _payload()
    payload["client_channel"] = ""
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "client_channel_required"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["auth_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["auth_authorized"] is False
    assert result["api_exposed"] is False
    assert result["db_authorized"] is False
    assert result["storage_write_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["llm_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert candidate is not None
    assert candidate["auth_authorized"] is False
    assert candidate["api_exposed"] is False
    assert candidate["db_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert audit_event_candidate is not None
    assert audit_event_candidate["api_exposed"] is False
    assert audit_event_candidate["runtime_authorized"] is False
    assert audit_event_candidate["db_authorized"] is False
    assert audit_event_candidate["storage_write_authorized"] is False
    assert audit_event_candidate["llm_authorized"] is False
    assert audit_event_candidate["pipeline_authorized"] is False
    assert audit_event_candidate["runner_authorized"] is False


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
    import pymia.smartpyme.service_1_real_auth_boundary_contract_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "jwt",
        "oauth",
        "supabase",
        "auth0",
        "clerk",
        "sqlalchemy",
        "psycopg",
        "sqlite3",
        "http",
        "requests",
        "socket",
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
