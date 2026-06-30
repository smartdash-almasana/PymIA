from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_real_storage_upload_boundary_contract_v1 import (
    BOUNDARY_KIND,
    COST_AND_RATE_LIMIT_GUARD_KIND,
    FILE_INTAKE_KIND,
    SCHEMA_VERSION,
    TENANT_ISOLATION_GUARD_KIND,
    build_service_1_real_storage_upload_boundary_contract_v1,
)


def _tenant_isolation_candidate() -> dict[str, object]:
    return {
        "guard_kind": TENANT_ISOLATION_GUARD_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "checked_source_candidate_kinds": ["SAAS_FILE_INTAKE_CANDIDATE"],
        "checked_source_refs": {
            "identity.tenant_ref": "tenant:pyme:001",
            "file_intake.file_ref": "storage:file:001",
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
        "source_session_ref": "case:s1:001",
        "requested_operation_kind": "REGISTER_STORAGE_UPLOAD_CANDIDATE",
        "estimated_cost_units": 1,
        "max_cost_units": 5,
        "current_window_request_count": 0,
        "max_window_request_count": 10,
        "current_budget_used_units": 2,
        "max_budget_units": 20,
        "projected_budget_used_units": 3,
        "remaining_cost_headroom_units": 4,
        "remaining_window_request_capacity": 10,
        "remaining_budget_units": 17,
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


def _file_intake_candidate() -> dict[str, object]:
    return {
        "intake_kind": FILE_INTAKE_KIND,
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "file_ref": "storage:file:001",
        "declared_filename": "ventas_marzo.xlsx",
        "declared_file_kind": "XLSX",
        "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "declared_size_bytes": 4096,
        "evidence_ref_candidate": "evidence_candidate:owner:pyme:001:case:s1:001:storage:file:001",
        "task_spec_candidate_allowed": False,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "upload_request_ref": "upload:req:001",
        "file_name": "ventas_marzo.xlsx",
        "file_kind": "XLSX",
        "file_size_bytes": 4096,
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "storage_object_ref": "storage:file:001",
        "checksum": "sha256:001",
        "client_channel": "WEB_PORTAL",
        "tenant_isolation_candidate": _tenant_isolation_candidate(),
        "cost_rate_limit_candidate": _cost_rate_limit_candidate(),
        "file_intake_candidate": _file_intake_candidate(),
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_real_storage_upload_boundary_contract_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["storage_upload_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate is not None
    assert candidate["boundary_kind"] == BOUNDARY_KIND
    assert candidate["tenant_ref"] == "tenant:pyme:001"
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["service_name"] == "SERVICE_1"
    assert candidate["upload_request_ref"] == "upload:req:001"
    assert candidate["client_channel"] == "WEB_PORTAL"
    assert candidate["file_name"] == "ventas_marzo.xlsx"
    assert candidate["file_kind"] == "XLSX"
    assert candidate["file_size_bytes"] == 4096
    assert candidate["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert candidate["storage_object_ref"] == "storage:file:001"
    assert candidate["checksum"] == "sha256:001"
    assert candidate["file_intake_candidate_ref"] == "storage:file:001"
    assert candidate["processing_job_candidate_required"] is False
    assert candidate["warnings"] == []
    assert candidate["errors"] == []
    assert audit_event_candidate is not None
    assert candidate["audit_event_candidate"] == audit_event_candidate
    assert audit_event_candidate["event_kind"] == "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE_RECORDED"
    assert audit_event_candidate["event_status"] == "STORAGE_UPLOAD_BOUNDARY_CANDIDATE_READY"
    assert audit_event_candidate["source_slice_kind"] == "REAL_STORAGE_UPLOAD_BOUNDARY_CANDIDATE"
    assert audit_event_candidate["source_context_refs"]["tenant_ref"] == "tenant:pyme:001"
    assert audit_event_candidate["source_context_refs"]["storage_object_ref"] == "storage:file:001"
    assert audit_event_candidate["api_exposed"] is False


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


def test_missing_case() -> None:
    payload = _payload()
    payload["case_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_CASE"
    assert result["blocked_reason"] == "case_ref_required"


def test_invalid_file_name() -> None:
    payload = _payload()
    payload["file_name"] = "nested/ventas.xlsx"
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FILE_NAME"
    assert result["blocked_reason"] == "file_name_required_or_invalid"


def test_invalid_file_kind() -> None:
    payload = _payload()
    payload["file_kind"] = "DOCX"
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FILE_KIND"
    assert result["blocked_reason"] == "file_kind_not_supported"


def test_invalid_file_size() -> None:
    payload = _payload()
    payload["file_size_bytes"] = 0
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_FILE_SIZE"
    assert result["blocked_reason"] == "file_size_bytes_must_be_positive_int"


def test_missing_storage_ref() -> None:
    payload = _payload()
    payload["storage_object_ref"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_STORAGE_REF"
    assert result["blocked_reason"] == "storage_object_ref_required"


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


def test_needs_file_intake() -> None:
    payload = _payload()
    payload["file_intake_candidate"] = None
    result = _build(payload)
    assert result["status"] == "NEEDS_FILE_INTAKE"
    assert result["blocked_reason"] == "file_intake_candidate_required"


def test_needs_owner_confirmation() -> None:
    payload = _payload()
    payload["checksum"] = None
    result = _build(payload)
    assert result["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert result["blocked_reason"] == "checksum_required_for_owner_confirmation"


def test_unknown_fallback() -> None:
    payload = _payload()
    payload["client_channel"] = ""
    result = _build(payload)
    assert result["status"] == "UNKNOWN"
    assert result["blocked_reason"] == "client_channel_required"


def test_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["storage_upload_boundary_candidate"]
    audit_event_candidate = result["audit_event_candidate"]
    assert result["storage_write_authorized"] is False
    assert result["file_processing_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["evidence_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["db_authorized"] is False
    assert result["api_exposed"] is False
    assert result["llm_authorized"] is False
    assert candidate is not None
    assert candidate["storage_write_authorized"] is False
    assert candidate["file_processing_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["evidence_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["api_exposed"] is False
    assert candidate["llm_authorized"] is False
    assert audit_event_candidate is not None
    assert audit_event_candidate["storage_write_authorized"] is False
    assert audit_event_candidate["db_authorized"] is False
    assert audit_event_candidate["pipeline_authorized"] is False
    assert audit_event_candidate["runner_authorized"] is False
    assert audit_event_candidate["runtime_authorized"] is False
    assert audit_event_candidate["api_exposed"] is False
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
    import pymia.smartpyme.service_1_real_storage_upload_boundary_contract_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "from pathlib",
        "shutil",
        "boto3",
        "supabase",
        "google.cloud.storage",
        "ocr",
        "pdf",
        "openpyxl",
        "pandas",
        "requests",
        "http",
        "open(",
        "write(",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
