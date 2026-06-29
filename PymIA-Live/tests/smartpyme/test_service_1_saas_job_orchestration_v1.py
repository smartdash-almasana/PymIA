from __future__ import annotations

import copy

from pymia.smartpyme.service_1_saas_job_orchestration_v1 import (
    SCHEMA_VERSION,
    build_service_1_saas_job_orchestration_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "INTAKE_PENDING",
        "current_chain_status": "SAAS_FILE_INTAKE_CANDIDATE_READY",
        "service_1_state_refs": {"case_truth_ref": "case_truth:s1:001"},
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
        "job_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _session(),
        "saas_file_intake_candidate": _file_intake(),
        "autonomous_chain_candidate_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "requested_job_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_saas_job_orchestration_v1(payload)  # type: ignore[arg-type]


def test_blocks_missing_session() -> None:
    payload = _payload()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"


def test_blocks_invalid_session_fields() -> None:
    cases = [
        ("session_kind", "HTTP_SESSION", "session_kind_must_be_saas_case_session_candidate"),
        ("service_name", "SERVICE_2", "session_service_name_must_be_service_1"),
        ("owner_ref", "", "session_owner_ref_required"),
        ("case_ref", "", "session_case_ref_required"),
        ("api_exposed", True, "session_api_exposed_must_be_false"),
        ("runtime_authorized", True, "session_runtime_authorized_must_be_false"),
    ]
    for key, value, reason in cases:
        payload = _payload()
        session = copy.deepcopy(payload["saas_case_session_candidate"])
        session[key] = value
        payload["saas_case_session_candidate"] = session
        result = _build(payload)
        assert result["status"] == "BLOCKED_INVALID_SESSION"
        assert result["blocked_reason"] == reason


def test_blocks_missing_or_unsupported_job_kind() -> None:
    payload = _payload()
    payload["requested_job_kind"] = ""
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_JOB_KIND"
    assert result["blocked_reason"] == "requested_job_kind_required"

    payload = _payload()
    payload["requested_job_kind"] = "UNSUPPORTED_JOB"
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSUPPORTED_JOB_KIND"
    assert result["blocked_reason"] == "requested_job_kind_not_supported"


def test_initial_file_intake_requires_valid_file_intake_candidate() -> None:
    payload = _payload()
    payload["saas_file_intake_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_JOB_INPUT_REFS"
    assert result["blocked_reason"] == "saas_file_intake_candidate_required_for_initial_file_intake"

    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["intake_kind"] = "REAL_UPLOAD"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["blocked_reason"] == "file_intake_kind_must_be_saas_file_intake_candidate"

    payload = _payload()
    intake = copy.deepcopy(payload["saas_file_intake_candidate"])
    intake["owner_ref"] = "owner:other"
    payload["saas_file_intake_candidate"] = intake
    result = _build(payload)
    assert result["blocked_reason"] == "file_intake_owner_ref_must_match_session"


def test_rerun_and_delivery_refresh_require_expected_refs() -> None:
    payload = _payload()
    payload["requested_job_kind"] = "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE"
    payload["saas_file_intake_candidate"] = None
    payload["autonomous_chain_candidate_refs"] = {"case_truth_ref": "case_truth:s1:001"}
    result = _build(payload)
    assert result["blocked_reason"] == "autonomous_rerun_candidate_ref_required"

    payload = _payload()
    payload["requested_job_kind"] = "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE"
    payload["saas_file_intake_candidate"] = None
    payload["autonomous_chain_candidate_refs"] = {"case_truth_ref": "case_truth:s1:001"}
    result = _build(payload)
    assert result["blocked_reason"] == "owner_delivery_packet_ref_required"


def test_ready_builds_initial_file_intake_job_candidate() -> None:
    result = _build(_payload())
    assert result["status"] == "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY"
    candidate = result["saas_job_orchestration_candidate"]
    assert candidate == {
        "job_kind": "SAAS_JOB_ORCHESTRATION_CANDIDATE",
        "requested_job_kind": "INITIAL_FILE_INTAKE_PROCESSING_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "source_file_intake_ref": "evidence_candidate:owner:pyme:001:case:s1:001:upload_ref:file:ventas_marzo",
        "autonomous_chain_candidate_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
            "autonomous_rerun_candidate_ref": "rerun_candidate:s1:001",
        },
        "planned_job_steps": [
            "validate_session_candidate_refs",
            "validate_file_intake_candidate_refs",
            "prepare_file_processing_job_candidate",
        ],
        "worker_authorized": False,
        "queue_authorized": False,
        "async_execution_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }


def test_ready_builds_other_supported_job_candidates() -> None:
    payload = _payload()
    payload["requested_job_kind"] = "AUTONOMOUS_RERUN_PROCESSING_CANDIDATE"
    payload["saas_file_intake_candidate"] = None
    result = _build(payload)
    candidate = result["saas_job_orchestration_candidate"]
    assert result["status"] == "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["source_file_intake_ref"] is None
    assert candidate["planned_job_steps"] == [
        "validate_session_candidate_refs",
        "validate_autonomous_rerun_candidate_ref",
        "prepare_rerun_processing_job_candidate",
    ]

    payload = _payload()
    payload["requested_job_kind"] = "OWNER_DELIVERY_PACKET_REFRESH_CANDIDATE"
    payload["saas_file_intake_candidate"] = None
    result = _build(payload)
    candidate = result["saas_job_orchestration_candidate"]
    assert result["status"] == "SAAS_JOB_ORCHESTRATION_CANDIDATE_READY"
    assert candidate is not None
    assert candidate["planned_job_steps"] == [
        "validate_session_candidate_refs",
        "validate_owner_delivery_packet_ref",
        "prepare_owner_delivery_refresh_job_candidate",
    ]


def test_preserves_owner_case_session_and_chain_refs() -> None:
    result = _build(_payload())
    candidate = result["saas_job_orchestration_candidate"]
    assert candidate is not None
    assert candidate["owner_ref"] == "owner:pyme:001"
    assert candidate["case_ref"] == "case:s1:001"
    assert candidate["source_session_ref"] == "case:s1:001"
    assert candidate["autonomous_chain_candidate_refs"] == _payload()["autonomous_chain_candidate_refs"]


def test_never_authorizes_execution_or_runtime() -> None:
    for payload in [_payload(), {**_payload(), "saas_case_session_candidate": None}, {**_payload(), "requested_job_kind": "UNSUPPORTED_JOB"}]:
        result = _build(payload)
        assert result["worker_authorized"] is False
        assert result["queue_authorized"] is False
        assert result["async_execution_authorized"] is False
        assert result["pipeline_authorized"] is False
        assert result["runner_authorized"] is False
        assert result["runtime_authorized"] is False
        assert result["api_exposed"] is False
        candidate = result["saas_job_orchestration_candidate"]
        if candidate is not None:
            assert candidate["worker_authorized"] is False
            assert candidate["queue_authorized"] is False
            assert candidate["async_execution_authorized"] is False
            assert candidate["pipeline_authorized"] is False
            assert candidate["runner_authorized"] is False
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
