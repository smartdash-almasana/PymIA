from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_first_controlled_client_case_readiness_gate_v1 import (
    build_service_1_first_controlled_client_case_readiness_gate_v1,
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


def _valid_candidate() -> dict:
    return {
        "owner_ref": "owner-001",
        "tenant_ref": "tenant-001",
        "case_ref": "case-001",
        "owner_consent": True,
        "evidence_refs": ["evidence-xlsx-001"],
        "scope": {
            "problem_statement": "Ventas, cobros y diferencias del mes a revisar.",
            "too_broad": False,
        },
        "operator_oversight_enabled": True,
        "rollback_plan": {
            "abort_allowed": True,
            "fallback_mode": "CLI_OPERATOR_FLOW",
        },
        "runtime_authorized": False,
        "publish_executed": False,
        "notification_sent": False,
        "handoff_executed": False,
    }


def test_ready_path_returns_controlled_case_ready() -> None:
    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=_valid_candidate()
    )

    assert result["gate_kind"] == "FIRST_CONTROLLED_CLIENT_CASE_READINESS_GATE"
    assert result["status"] == "CONTROLLED_CASE_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert result["controlled_case_candidate"]["case_ref"] == "case-001"
    assert result["blocked_reasons"] == []


def test_blocks_missing_owner_ref() -> None:
    candidate = _valid_candidate()
    candidate["owner_ref"] = ""

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_MISSING_OWNER_CONSENT"
    assert result["ready"] is False


def test_blocks_missing_owner_consent() -> None:
    candidate = _valid_candidate()
    candidate["owner_consent"] = False

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_MISSING_OWNER_CONSENT"
    assert result["ready"] is False


def test_blocks_missing_evidence() -> None:
    candidate = _valid_candidate()
    candidate["evidence_refs"] = []

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_MISSING_EVIDENCE"
    assert result["ready"] is False


def test_blocks_unclear_scope() -> None:
    candidate = _valid_candidate()
    candidate["scope"] = {"problem_statement": ""}

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_UNCLEAR_SCOPE"
    assert result["ready"] is False


def test_needs_scope_reduction_when_scope_too_broad() -> None:
    candidate = _valid_candidate()
    candidate["scope"]["too_broad"] = True

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "NEEDS_SCOPE_REDUCTION"
    assert result["ready"] is False


def test_blocks_without_operator_oversight() -> None:
    candidate = _valid_candidate()
    candidate["operator_oversight_enabled"] = False

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_NO_OPERATOR_OVERSIGHT"
    assert result["ready"] is False


def test_blocks_without_rollback_plan() -> None:
    candidate = _valid_candidate()
    candidate["rollback_plan"] = {"abort_allowed": False}

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_NO_ROLLBACK_PLAN"
    assert result["ready"] is False


def test_blocks_unsafe_runtime_flags() -> None:
    candidate = _valid_candidate()
    candidate["runtime_authorized"] = True

    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_for_non_mapping_candidate() -> None:
    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=None
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False


def test_dangerous_flags_are_always_false() -> None:
    result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=_valid_candidate()
    )

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False


def test_does_not_mutate_input() -> None:
    candidate = _valid_candidate()
    before = deepcopy(candidate)

    build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert candidate == before


def test_result_is_deterministic() -> None:
    candidate = _valid_candidate()

    first = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )
    second = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=candidate
    )

    assert first == second


def test_source_guard_no_runtime_or_infrastructure_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_first_controlled_client_case_readiness_gate_v1.py"
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
