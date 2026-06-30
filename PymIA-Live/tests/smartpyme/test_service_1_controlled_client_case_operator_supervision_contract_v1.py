from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_controlled_client_case_operator_supervision_contract_v1 import (
    build_service_1_controlled_client_case_operator_supervision_contract_v1,
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


def _valid_packet() -> dict:
    return {
        "candidate_kind": "CONTROLLED_CASE_EVIDENCE_PACKET_CANDIDATE",
        "packet_ref": "packet-001",
        "status": "EVIDENCE_PACKET_READY",
        "ready": True,
        "owner_ref": "owner-001",
        "tenant_ref": "tenant-001",
        "case_ref": "case-001",
        "allowed_execution_mode": "SUPERVISED_CLI_OPERATOR_FLOW",
        "runtime_authorized": False,
        "publish_executed": False,
        "notification_sent": False,
        "handoff_executed": False,
    }


def _valid_abort_policy() -> dict:
    return {
        "abort_allowed": True,
        "rollback_ref": "rollback-001",
        "allowed_actions": [
            "inspect_evidence_packet",
            "run_supervised_cli_flow",
            "review_generated_artifacts",
            "abort_controlled_case",
        ],
    }


def test_ready_path_returns_operator_supervision_ready() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    assert result["contract_kind"] == "CONTROLLED_CLIENT_CASE_OPERATOR_SUPERVISION_CONTRACT"
    assert result["status"] == "OPERATOR_SUPERVISION_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    candidate = result["operator_supervision_candidate"]
    assert candidate["candidate_kind"] == "OPERATOR_SUPERVISION_CANDIDATE"
    assert candidate["operator_ref"] == "operator-001"
    assert candidate["case_ref"] == "case-001"
    assert candidate["review_required"] is True


def test_blocks_invalid_evidence_packet_kind() -> None:
    packet = _valid_packet()
    packet["candidate_kind"] = "OTHER"

    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    assert result["status"] == "BLOCKED_INVALID_EVIDENCE_PACKET"
    assert result["ready"] is False
    assert result["operator_supervision_candidate"] is None


def test_blocks_evidence_packet_not_ready() -> None:
    packet = _valid_packet()
    packet["ready"] = False

    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    assert result["status"] == "BLOCKED_INVALID_EVIDENCE_PACKET"


def test_blocks_missing_operator() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="",
        abort_policy=_valid_abort_policy(),
    )

    assert result["status"] == "BLOCKED_MISSING_OPERATOR"
    assert result["ready"] is False


def test_blocks_missing_abort_policy() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=None,
    )

    assert result["status"] == "BLOCKED_MISSING_ABORT_POLICY"
    assert result["ready"] is False


def test_blocks_abort_policy_without_rollback_ref() -> None:
    abort_policy = _valid_abort_policy()
    abort_policy["rollback_ref"] = ""

    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )

    assert result["status"] == "BLOCKED_MISSING_ABORT_POLICY"


def test_blocks_unsafe_requested_actions() -> None:
    abort_policy = _valid_abort_policy()
    abort_policy["allowed_actions"] = ["send_whatsapp_to_owner"]

    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )

    assert result["status"] == "BLOCKED_UNSAFE_ACTIONS"
    assert result["allowed_actions"] == []


def test_blocks_unsafe_runtime_flags() -> None:
    packet = _valid_packet()
    packet["runtime_authorized"] = True

    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_for_non_mapping_packet() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=None,
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False


def test_dangerous_flags_are_always_false_on_result_and_candidate() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
    )

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False
        assert result["operator_supervision_candidate"][flag] is False


def test_does_not_mutate_inputs() -> None:
    packet = _valid_packet()
    abort_policy = _valid_abort_policy()
    before_packet = deepcopy(packet)
    before_abort_policy = deepcopy(abort_policy)

    build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )

    assert packet == before_packet
    assert abort_policy == before_abort_policy


def test_result_is_deterministic() -> None:
    packet = _valid_packet()
    abort_policy = _valid_abort_policy()

    first = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )
    second = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=packet,
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )

    assert first == second


def test_review_required_can_be_false_without_authorizing_runtime() -> None:
    result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=_valid_packet(),
        operator_ref="operator-001",
        abort_policy=_valid_abort_policy(),
        review_required=False,
    )

    assert result["status"] == "OPERATOR_SUPERVISION_READY"
    assert result["operator_supervision_candidate"]["review_required"] is False
    assert result["runtime_authorized"] is False


def test_source_guard_no_runtime_or_infrastructure_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_controlled_client_case_operator_supervision_contract_v1.py"
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
