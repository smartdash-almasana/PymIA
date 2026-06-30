from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_controlled_client_case_execution_candidate_v1 import (
    build_service_1_controlled_client_case_execution_candidate_v1,
)


DANGEROUS_FLAGS = (
    "execution_executed",
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


def _valid_readiness_gate_result() -> dict[str, object]:
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


def _valid_evidence_packet_candidate() -> dict[str, object]:
    return {
        "candidate_kind": "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE",
        "packet_ref": "packet-001",
        "status": "EVIDENCE_PACKET_READY",
        "ready": True,
        "service_name": "SERVICE_1",
        "source_gate_kind": "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE",
        "source_gate_status": "CONTROLLED_CASE_READY",
        "owner_ref": "owner-001",
        "tenant_ref": "tenant-001",
        "case_ref": "case-001",
        "evidence_refs": ["evidence-001"],
        "file_refs": ["file-001"],
        "scope": "scope-001",
        "owner_consent_ref": "consent-001",
        "operator_oversight_ref": "operator-001",
        "rollback_plan_ref": "rollback-001",
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


def _valid_operator_supervision_candidate() -> dict[str, object]:
    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT",
        "status": "OPERATOR_SUPERVISION_READY",
        "ready": True,
        "operator_supervision_candidate": {
            "candidate_kind": "OPERATOR_SUPERVISION_CANDIDATE",
            "source_evidence_packet_ref": "packet-001",
            "owner_ref": "owner-001",
            "tenant_ref": "tenant-001",
            "case_ref": "case-001",
            "operator_ref": "operator-001",
            "review_required": True,
            "abort_policy": {
                "abort_allowed": True,
                "rollback_ref": "rollback-001",
            },
            "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
            "allowed_actions": [
                "inspect_evidence_packet",
                "run_supervised_cli_flow",
                "review_generated_artifacts",
                "abort_controlled_case",
            ],
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
        },
        "blocked_reasons": [],
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        "allowed_actions": [
            "inspect_evidence_packet",
            "run_supervised_cli_flow",
            "review_generated_artifacts",
            "abort_controlled_case",
        ],
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


def _build(
    *,
    operator_supervision_candidate: dict[str, object] | None = None,
    evidence_packet_candidate: dict[str, object] | None = None,
    readiness_gate_result: dict[str, object] | None = None,
    execution_window_ref: str = "window-001",
    operator_ref: str = "operator-001",
    dry_run_required: bool = True,
) -> dict[str, object]:
    return build_service_1_controlled_client_case_execution_candidate_v1(
        operator_supervision_candidate=operator_supervision_candidate or _valid_operator_supervision_candidate(),
        evidence_packet_candidate=evidence_packet_candidate or _valid_evidence_packet_candidate(),
        readiness_gate_result=readiness_gate_result or _valid_readiness_gate_result(),
        execution_window_ref=execution_window_ref,
        operator_ref=operator_ref,
        dry_run_required=dry_run_required,
    )


def test_ready_path() -> None:
    result = _build()

    assert result["contract_kind"] == "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE"
    assert result["status"] == "CONTROLLED_EXECUTION_CANDIDATE_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"

    candidate = result["controlled_execution_candidate"]
    assert candidate is not None
    assert candidate["candidate_kind"] == "CONTROLLED_EXECUTION_CANDIDATE"
    assert candidate["execution_authorized"] is True
    assert candidate["execution_executed"] is False
    assert candidate["dry_run_required"] is True
    assert candidate["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert candidate["operator_ref"] == "operator-001"
    assert candidate["owner_ref"] == "owner-001"
    assert candidate["tenant_ref"] == "tenant-001"
    assert candidate["case_ref"] == "case-001"
    assert candidate["execution_window_ref"] == "window-001"


def test_invalid_operator_supervision_wrong_contract_kind() -> None:
    supervision = _valid_operator_supervision_candidate()
    supervision["contract_kind"] = "OTHER"

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    assert result["ready"] is False
    assert result["controlled_execution_candidate"] is None


def test_invalid_operator_supervision_not_ready() -> None:
    supervision = _valid_operator_supervision_candidate()
    supervision["status"] = "BLOCKED_MISSING_OPERATOR"
    supervision["ready"] = False

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    assert result["ready"] is False


def test_invalid_evidence_packet_wrong_kind() -> None:
    evidence = _valid_evidence_packet_candidate()
    evidence["candidate_kind"] = "OTHER"

    result = _build(evidence_packet_candidate=evidence)

    assert result["status"] == "BLOCKED_INVALID_EVIDENCE_PACKET"
    assert result["ready"] is False


def test_invalid_evidence_packet_not_ready() -> None:
    evidence = _valid_evidence_packet_candidate()
    evidence["ready"] = False
    evidence["status"] = "BLOCKED"

    result = _build(evidence_packet_candidate=evidence)

    assert result["status"] == "BLOCKED_INVALID_EVIDENCE_PACKET"
    assert result["ready"] is False


def test_invalid_readiness_wrong_gate_kind() -> None:
    readiness = _valid_readiness_gate_result()
    readiness["gate_kind"] = "OTHER"

    result = _build(readiness_gate_result=readiness)

    assert result["status"] == "BLOCKED_INVALID_READINESS"
    assert result["ready"] is False


def test_invalid_readiness_not_ready() -> None:
    readiness = _valid_readiness_gate_result()
    readiness["status"] = "BLOCKED_MISSING_EVIDENCE"
    readiness["ready"] = False

    result = _build(readiness_gate_result=readiness)

    assert result["status"] == "BLOCKED_INVALID_READINESS"
    assert result["ready"] is False


def test_missing_execution_window() -> None:
    result = _build(execution_window_ref="")

    assert result["status"] == "BLOCKED_MISSING_EXECUTION_WINDOW"
    assert result["ready"] is False


def test_operator_mismatch() -> None:
    result = _build(operator_ref="operator-002")

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_dry_run_required_false_blocks() -> None:
    result = _build(dry_run_required=False)

    assert result["status"] == "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    assert result["ready"] is False


def test_unsafe_flags_blocked() -> None:
    supervision = _valid_operator_supervision_candidate()
    supervision["runtime_authorized"] = True

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_fallback() -> None:
    result = build_service_1_controlled_client_case_execution_candidate_v1(
        operator_supervision_candidate=None,
        evidence_packet_candidate=None,
        readiness_gate_result=None,
        execution_window_ref="window",
        operator_ref="op",
        dry_run_required=True,
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False
    assert result["controlled_execution_candidate"] is None


def test_dangerous_flags_are_always_false() -> None:
    result = _build()

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False

    candidate = result["controlled_execution_candidate"]
    assert candidate is not None
    for flag in DANGEROUS_FLAGS:
        assert candidate[flag] is False


def test_does_not_mutate_inputs() -> None:
    supervision = _valid_operator_supervision_candidate()
    evidence = _valid_evidence_packet_candidate()
    readiness = _valid_readiness_gate_result()

    before_supervision = deepcopy(supervision)
    before_evidence = deepcopy(evidence)
    before_readiness = deepcopy(readiness)

    _build(
        operator_supervision_candidate=supervision,
        evidence_packet_candidate=evidence,
        readiness_gate_result=readiness,
    )

    assert supervision == before_supervision
    assert evidence == before_evidence
    assert readiness == before_readiness


def test_result_is_deterministic() -> None:
    first = _build()
    second = _build()

    assert first == second


def test_source_guard_no_runtime_or_infrastructure_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_controlled_client_case_execution_candidate_v1.py"
    )
    source = source_path.read_text(encoding="utf-8")

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
    lowered = source.lower()
    for token in forbidden:
        assert token not in lowered
