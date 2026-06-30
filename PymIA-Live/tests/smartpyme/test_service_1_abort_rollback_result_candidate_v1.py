from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_abort_rollback_result_candidate_v1 import (
    build_service_1_abort_rollback_result_candidate_v1,
)


DANGEROUS_FLAGS = (
    "execution_executed",
    "cli_executed",
    "rollback_executed",
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


def _valid_run_result() -> dict[str, object]:
    return {
        "contract_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
        "status": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY",
        "ready": True,
        "supervised_cli_run_result_candidate": {
            "candidate_kind": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE",
            "status": "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY",
            "ready": True,
            "run_recorded": True,
            "cli_executed": False,
            "execution_executed": False,
            "source_execution_candidate_ref": "execution-001",
            "source_operator_supervision_ref": "supervision-001",
            "operator_ref": "operator-001",
            "owner_ref": "owner-001",
            "tenant_ref": "tenant-001",
            "case_ref": "case-001",
            "artifact_refs": ["artifact-001"],
            "warning_refs": [],
            "error_refs": [],
            "run_observation": "Run completed successfully.",
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


def _valid_execution_candidate() -> dict[str, object]:
    return {
        "contract_kind": "CONTROLLED_CLIENT_CASE_EXECUTION_CANDIDATE",
        "status": "CONTROLLED_EXECUTION_CANDIDATE_READY",
        "ready": True,
        "controlled_execution_candidate": {
            "candidate_kind": "CONTROLLED_EXECUTION_CANDIDATE",
            "status": "CONTROLLED_EXECUTION_CANDIDATE_READY",
            "ready": True,
            "execution_authorized": True,
            "execution_executed": False,
            "source_operator_supervision_ref": "supervision-001",
            "source_evidence_packet_ref": "packet-001",
            "source_readiness_gate_ref": "readiness-001",
            "execution_window_ref": "window-001",
            "operator_ref": "operator-001",
            "owner_ref": "owner-001",
            "tenant_ref": "tenant-001",
            "case_ref": "case-001",
            "dry_run_required": True,
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


def _build(
    *,
    supervised_cli_run_result_candidate: dict[str, object] | None = None,
    controlled_execution_candidate: dict[str, object] | None = None,
    operator_ref: str = "operator-001",
    abort_requested: bool = True,
    rollback_required: bool = True,
    rollback_reason: str = "Owner requested rollback due to incorrect data.",
    rollback_artifact_refs: list[str] | object = ["rollback-artifact-001"],
    rollback_observation: str = "Rollback prepared but not executed.",
) -> dict[str, object]:
    return build_service_1_abort_rollback_result_candidate_v1(
        supervised_cli_run_result_candidate=supervised_cli_run_result_candidate or _valid_run_result(),
        controlled_execution_candidate=controlled_execution_candidate or _valid_execution_candidate(),
        operator_ref=operator_ref,
        abort_requested=abort_requested,
        rollback_required=rollback_required,
        rollback_reason=rollback_reason,
        rollback_artifact_refs=rollback_artifact_refs,
        rollback_observation=rollback_observation,
    )


def test_ready_path() -> None:
    result = _build()

    assert result["contract_kind"] == "ABORT_ROLLBACK_RESULT_CANDIDATE"
    assert result["status"] == "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"

    candidate = result["abort_rollback_result_candidate"]
    assert candidate is not None
    assert candidate["candidate_kind"] == "ABORT_ROLLBACK_RESULT_CANDIDATE"
    assert candidate["abort_requested"] is True
    assert candidate["rollback_required"] is True
    assert candidate["rollback_recorded"] is True
    assert candidate["rollback_executed"] is False
    assert candidate["cli_executed"] is False
    assert candidate["execution_executed"] is False
    assert candidate["operator_ref"] == "operator-001"
    assert candidate["owner_ref"] == "owner-001"
    assert candidate["tenant_ref"] == "tenant-001"
    assert candidate["case_ref"] == "case-001"
    assert candidate["rollback_artifact_refs"] == ["rollback-artifact-001"]


def test_no_abort_or_rollback_required() -> None:
    result = _build(abort_requested=False, rollback_required=False)

    assert result["status"] == "NO_ABORT_OR_ROLLBACK_REQUIRED"
    assert result["ready"] is True
    assert result["abort_rollback_result_candidate"] is None
    assert result["allowed_execution_mode"] == "NONE"


def test_invalid_supervised_run_result_wrong_contract_kind() -> None:
    run_result = _valid_run_result()
    run_result["contract_kind"] = "OTHER"

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
    assert result["ready"] is False
    assert result["abort_rollback_result_candidate"] is None


def test_invalid_supervised_run_result_not_ready() -> None:
    run_result = _valid_run_result()
    run_result["status"] = "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    run_result["ready"] = False

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
    assert result["ready"] is False


def test_invalid_execution_candidate_wrong_contract_kind() -> None:
    execution = _valid_execution_candidate()
    execution["contract_kind"] = "OTHER"

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False


def test_invalid_execution_candidate_not_ready() -> None:
    execution = _valid_execution_candidate()
    execution["status"] = "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    execution["ready"] = False

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False


def test_operator_mismatch_against_run_result() -> None:
    result = _build(operator_ref="operator-002")

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_operator_mismatch_against_execution() -> None:
    execution = _valid_execution_candidate()
    inner = execution["controlled_execution_candidate"]
    assert isinstance(inner, dict)
    inner["operator_ref"] = "operator-002"

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_missing_rollback_reason_when_abort_requested() -> None:
    result = _build(abort_requested=True, rollback_required=False, rollback_reason="")

    assert result["status"] == "BLOCKED_MISSING_ROLLBACK_REASON"
    assert result["ready"] is False


def test_missing_rollback_reason_when_rollback_required() -> None:
    result = _build(rollback_required=True, rollback_reason="")

    assert result["status"] == "BLOCKED_MISSING_ROLLBACK_REASON"
    assert result["ready"] is False


def test_missing_rollback_artifact_refs_when_rollback_required() -> None:
    result = _build(rollback_required=True, rollback_artifact_refs=[])

    assert result["status"] == "BLOCKED_MISSING_ROLLBACK_ARTIFACT_REFS"
    assert result["ready"] is False


def test_unsafe_flags_blocked() -> None:
    run_result = _valid_run_result()
    run_result["runtime_authorized"] = True

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_fallback() -> None:
    result = build_service_1_abort_rollback_result_candidate_v1(
        supervised_cli_run_result_candidate=None,
        controlled_execution_candidate=None,
        operator_ref="op",
        abort_requested=False,
        rollback_required=False,
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False
    assert result["abort_rollback_result_candidate"] is None


def test_dangerous_flags_are_always_false() -> None:
    result = _build()

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False

    candidate = result["abort_rollback_result_candidate"]
    assert candidate is not None
    for flag in DANGEROUS_FLAGS:
        assert candidate[flag] is False


def test_does_not_mutate_inputs() -> None:
    run_result = _valid_run_result()
    execution = _valid_execution_candidate()
    artifacts = ["rollback-artifact-001"]

    before_run = deepcopy(run_result)
    before_execution = deepcopy(execution)
    before_artifacts = deepcopy(artifacts)

    _build(
        supervised_cli_run_result_candidate=run_result,
        controlled_execution_candidate=execution,
        rollback_artifact_refs=artifacts,
    )

    assert run_result == before_run
    assert execution == before_execution
    assert artifacts == before_artifacts


def test_result_is_deterministic() -> None:
    first = _build()
    second = _build()

    assert first == second


def test_source_guard_no_runtime_or_infrastructure_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_abort_rollback_result_candidate_v1.py"
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
