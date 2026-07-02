from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_saas_file_intake_api_v1 import (
    SCHEMA_VERSION,
    build_service_1_saas_file_intake_api_v1,
)


def _base_session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "INTAKE_PENDING",
        "current_chain_status": "SAAS_CASE_SESSION_CANDIDATE_READY",
        "service_1_state_refs": {"case_truth_ref": "case_truth:s1:001"},
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _base_input() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _base_session(),
        "file_ref": "upload_ref:file:ventas_marzo",
        "declared_filename": "ventas_marzo.xlsx",
        "declared_file_kind": "XLSX",
        "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "declared_size_bytes": 1024,
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_saas_file_intake_api_v1(payload)  # type: ignore[arg-type]


def test_blocks_if_session_is_missing() -> None:
    payload = _base_input()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"
    assert result["saas_file_intake_candidate"] is None


def test_blocks_if_session_kind_is_wrong() -> None:
    payload = _base_input()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["session_kind"] = "HTTP_SESSION"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_kind_must_be_saas_case_session_candidate"


def test_blocks_if_session_service_name_is_not_service_1() -> None:
    payload = _base_input()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["service_name"] = "SERVICE_2"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_service_name_must_be_service_1"


def test_blocks_if_session_owner_ref_is_missing() -> None:
    payload = _base_input()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["owner_ref"] = ""
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_owner_ref_required"


def test_blocks_if_session_case_ref_is_missing() -> None:
    payload = _base_input()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["case_ref"] = ""
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_case_ref_required"


def test_blocks_if_session_api_exposed_is_true() -> None:
    payload = _base_input()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["api_exposed"] = True
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_api_exposed_must_be_false"


def test_blocks_if_file_ref_is_missing() -> None:
    payload = _base_input()
    payload["file_ref"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FILE_REF"
    assert result["blocked_reason"] == "file_ref_required"


def test_blocks_if_declared_filename_is_missing() -> None:
    payload = _base_input()
    payload["declared_filename"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FILE_METADATA"
    assert result["blocked_reason"] == "declared_filename_required"


def test_blocks_if_declared_file_kind_is_missing() -> None:
    payload = _base_input()
    payload["declared_file_kind"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FILE_METADATA"
    assert result["blocked_reason"] == "declared_file_kind_required"


def test_blocks_if_declared_file_kind_is_unsupported() -> None:
    payload = _base_input()
    payload["declared_file_kind"] = "PDF"
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_FILE_KIND"
    assert result["blocked_reason"] == "declared_file_kind_not_supported"


def test_blocks_if_declared_mime_type_is_missing() -> None:
    payload = _base_input()
    payload["declared_mime_type"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FILE_METADATA"
    assert result["blocked_reason"] == "declared_mime_type_required"


def test_blocks_if_declared_mime_type_is_unsupported() -> None:
    payload = _base_input()
    payload["declared_mime_type"] = "application/pdf"
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_FILE_KIND"
    assert result["blocked_reason"] == "declared_mime_type_not_supported"


def test_blocks_if_declared_size_bytes_is_negative() -> None:
    payload = _base_input()
    payload["declared_size_bytes"] = -1
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_FILE_METADATA"
    assert result["blocked_reason"] == "declared_size_bytes_must_be_non_negative_int_or_none"


def test_ready_builds_saas_file_intake_candidate() -> None:
    result = _build(_base_input())
    assert result["status"] == "SAAS_FILE_INTAKE_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert result["saas_file_intake_candidate"] == {
        "intake_kind": "SAAS_FILE_INTAKE_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "file_ref": "upload_ref:file:ventas_marzo",
        "declared_filename": "ventas_marzo.xlsx",
        "declared_file_kind": "XLSX",
        "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "declared_size_bytes": 1024,
        "evidence_ref_candidate": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
        "task_spec_candidate_allowed": False,
        "upload_authorized": False,
        "file_read_authorized": False,
        "parser_authorized": False,
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def test_blocks_csv_and_text_metadata_to_match_file_intake_v1() -> None:
    cases = [
        ("CSV", "text/csv", "ventas.csv"),
        ("TXT", "text/plain", "notas.txt"),
    ]
    for file_kind, mime_type, filename in cases:
        payload = _base_input()
        payload["declared_file_kind"] = file_kind
        payload["declared_mime_type"] = mime_type
        payload["declared_filename"] = filename
        result = _build(payload)
        assert result["status"] == "BLOCKED_UNSUPPORTED_FILE_KIND"
        assert result["blocked_reason"] == "declared_file_kind_not_supported"
        assert result["saas_file_intake_candidate"] is None


def test_preserves_session_owner_case_and_file_refs() -> None:
    result = _build(_base_input())
    candidate = result["saas_file_intake_candidate"]
    assert candidate is not None
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["source_session_ref"] == "case:s1:001"
    assert candidate["file_ref"] == "upload_ref:file:ventas_marzo"


def test_generates_deterministic_evidence_ref_candidate() -> None:
    first = _build(_base_input())
    second = _build(_base_input())
    assert first["saas_file_intake_candidate"] is not None
    assert second["saas_file_intake_candidate"] is not None
    assert first["saas_file_intake_candidate"]["evidence_ref_candidate"] == second["saas_file_intake_candidate"]["evidence_ref_candidate"]


def test_result_never_authorizes_upload_read_parse_job_runtime_or_api() -> None:
    cases = []
    missing_session = _base_input()
    missing_session["saas_case_session_candidate"] = None
    cases.append(missing_session)
    unsupported = _base_input()
    unsupported["declared_file_kind"] = "PDF"
    cases.append(unsupported)
    cases.append(_base_input())

    for payload in cases:
        result = _build(payload)
        assert result["upload_authorized"] is False
        assert result["file_read_authorized"] is False
        assert result["parser_authorized"] is False
        assert result["job_authorized"] is False
        assert result["runtime_authorized"] is False
        assert result["api_exposed"] is False
        candidate = result["saas_file_intake_candidate"]
        if candidate is not None:
            assert candidate["task_spec_candidate_allowed"] is False
            assert candidate["upload_authorized"] is False
            assert candidate["file_read_authorized"] is False
            assert candidate["parser_authorized"] is False
            assert candidate["job_authorized"] is False
            assert candidate["runtime_authorized"] is False
            assert candidate["api_exposed"] is False


def test_module_source_does_not_import_io_cli_api_db_auth_parser_pipeline_runner_llm_or_chatbot() -> None:
    import pymia.smartpyme.service_1_saas_file_intake_api_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "import shutil",
        "from pathlib",
        "tempfile",
        "open(",
        "write(",
        "openpyxl",
        "pandas",
        "import csv",
        "ocr",
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
