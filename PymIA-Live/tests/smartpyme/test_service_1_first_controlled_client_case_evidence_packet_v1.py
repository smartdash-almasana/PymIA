from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_first_controlled_client_case_evidence_packet_v1 import (
    build_service_1_first_controlled_client_case_evidence_packet_v1,
)


DANGEROUS_FLAGS = (
    "runtime_authorized",
    "publish_executed",
    "notification_sent",
    "handoff_executed",
    "api_exposed",
    "storage_write_authorized",
    "db_authorized",
    "worker_authorized",
    "queue_authorized",
    "mutation_authorized",
    "llm_authorized",
)


def _valid_readiness_gate_result() -> dict:
    return {
        "gate_kind": "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE",
        "status": "CONTROLLED_CASE_READY",
        "ready": True,
        "controlled_case_candidate": {
            "owner_ref": "owner-001",
            "tenant_ref": "tenant-001",
            "case_ref": "case-001",
        },
        "blocked_reasons": [],
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        "runtime_authorized": False,
        "publish_executed": False,
        "notification_sent": False,
        "handoff_executed": False,
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _build(**overrides: object) -> dict:
    payload = {
        "readiness_gate_result": _valid_readiness_gate_result(),
        "owner_ref": "owner-001",
        "tenant_ref": "tenant-001",
        "case_ref": "case-001",
        "evidence_refs": ["evidence-001", "evidence-002"],
        "file_refs": ["file-001", "file-002"],
        "scope": "Primer caso controlado con revisión supervisada.",
        "owner_consent_ref": "consent-001",
        "operator_oversight_ref": "oversight-001",
        "rollback_plan_ref": "rollback-001",
    }
    payload.update(overrides)
    return build_service_1_first_controlled_client_case_evidence_packet_v1(**payload)


def test_ready_path() -> None:
    result = _build()

    candidate = result["controlled_case_evidence_packet_candidate"]
    assert result["schema_version"] == "S1_FIRST_CONTROLLED_CLIENT_CASE_EVIDENCE_PACKET_V1"
    assert result["status"] == "EVIDENCE_PACKET_READY"
    assert result["blocked_reason"] is None
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert candidate is not None
    assert candidate["candidate_kind"] == "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE"
    assert candidate["source_gate_kind"] == "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"
    assert candidate["source_gate_status"] == "CONTROLLED_CASE_READY"
    assert candidate["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert candidate["evidence_refs"] == ["evidence-001", "evidence-002"]
    assert candidate["file_refs"] == ["file-001", "file-002"]


def test_invalid_readiness_gate() -> None:
    readiness_gate_result = _valid_readiness_gate_result()
    readiness_gate_result["status"] = "BLOCKED_MISSING_EVIDENCE"
    readiness_gate_result["ready"] = False

    result = _build(readiness_gate_result=readiness_gate_result)

    assert result["status"] == "BLOCKED_INVALID_READINESS_GATE"


def test_missing_owner() -> None:
    result = _build(owner_ref="")
    assert result["status"] == "BLOCKED_MISSING_OWNER"


def test_missing_tenant() -> None:
    result = _build(tenant_ref="")
    assert result["status"] == "BLOCKED_MISSING_TENANT"


def test_missing_case() -> None:
    result = _build(case_ref="")
    assert result["status"] == "BLOCKED_MISSING_CASE"


def test_missing_evidence_refs() -> None:
    result = _build(evidence_refs=[])
    assert result["status"] == "BLOCKED_MISSING_EVIDENCE_REFS"


def test_missing_file_refs() -> None:
    result = _build(file_refs=[])
    assert result["status"] == "BLOCKED_MISSING_FILE_REFS"


def test_missing_scope() -> None:
    result = _build(scope="")
    assert result["status"] == "BLOCKED_MISSING_SCOPE"


def test_missing_consent_ref() -> None:
    result = _build(owner_consent_ref="")
    assert result["status"] == "BLOCKED_MISSING_OWNER_CONSENT"


def test_missing_operator_oversight_ref() -> None:
    result = _build(operator_oversight_ref="")
    assert result["status"] == "BLOCKED_MISSING_OPERATOR_OVERSIGHT"


def test_missing_rollback_ref() -> None:
    result = _build(rollback_plan_ref="")
    assert result["status"] == "BLOCKED_MISSING_ROLLBACK"


def test_unsafe_flags_blocked() -> None:
    readiness_gate_result = _valid_readiness_gate_result()
    readiness_gate_result["runtime_authorized"] = True

    result = _build(readiness_gate_result=readiness_gate_result)

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"


def test_unknown_fallback() -> None:
    readiness_gate_result = _valid_readiness_gate_result()
    readiness_gate_result["status"] = "UNKNOWN"
    readiness_gate_result["ready"] = False

    result = _build(readiness_gate_result=readiness_gate_result)

    assert result["status"] == "UNKNOWN"


def test_dangerous_flags_false() -> None:
    result = _build()
    candidate = result["controlled_case_evidence_packet_candidate"]

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False
    assert candidate is not None
    for flag in DANGEROUS_FLAGS:
        assert candidate[flag] is False


def test_no_input_mutation() -> None:
    readiness_gate_result = _valid_readiness_gate_result()
    evidence_refs = ["evidence-001", "evidence-002"]
    file_refs = ["file-001", "file-002"]

    before_gate = deepcopy(readiness_gate_result)
    before_evidence = deepcopy(evidence_refs)
    before_files = deepcopy(file_refs)

    _ = _build(
        readiness_gate_result=readiness_gate_result,
        evidence_refs=evidence_refs,
        file_refs=file_refs,
    )

    assert readiness_gate_result == before_gate
    assert evidence_refs == before_evidence
    assert file_refs == before_files


def test_deterministic() -> None:
    first = _build()
    second = _build()
    assert first == second


def test_source_guard() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_first_controlled_client_case_evidence_packet_v1.py"
    )
    source = source_path.read_text(encoding="utf-8").lower()

    forbidden = (
        "requests",
        "fastapi",
        "sqlalchemy",
        "sqlite3",
        "boto3",
        "celery",
        "redis",
        "smtplib",
        "twilio",
        "openai",
        "langchain",
        "pydantic_ai",
    )
    for token in forbidden:
        assert token not in source
