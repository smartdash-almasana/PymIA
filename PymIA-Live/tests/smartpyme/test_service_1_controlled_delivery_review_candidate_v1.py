from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_controlled_delivery_review_candidate_v1 import (
    build_service_1_controlled_delivery_review_candidate_v1,
)


DANGEROUS_FLAGS = (
    "delivery_executed",
    "publish_executed",
    "notification_executed",
    "notification_sent",
    "cli_executed",
    "execution_executed",
    "rollback_executed",
    "runtime_authorized",
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


def _valid_abort_rollback_result_no_abort() -> dict[str, object]:
    return {
        "contract_kind": "ABORT_ROLLBACK_RESULT_CANDIDATE",
        "status": "NO_ABORT_OR_ROLLBACK_REQUIRED",
        "ready": True,
        "abort_rollback_result_candidate": None,
        "blocked_reasons": [],
        "allowed_execution_mode": "NONE",
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
    abort_rollback_result_candidate: dict[str, object] | None = None,
    controlled_execution_candidate: dict[str, object] | None = None,
    operator_ref: str = "operator-001",
    delivery_artifact_refs: list[str] | object = ["delivery-artifact-001"],
    review_observation: str = "Review completed: delivery artifacts are valid.",
    delivery_review_required: bool = True,
    owner_delivery_ready: bool = True,
) -> dict[str, object]:
    return build_service_1_controlled_delivery_review_candidate_v1(
        supervised_cli_run_result_candidate=supervised_cli_run_result_candidate or _valid_run_result(),
        abort_rollback_result_candidate=abort_rollback_result_candidate or _valid_abort_rollback_result_no_abort(),
        controlled_execution_candidate=controlled_execution_candidate or _valid_execution_candidate(),
        operator_ref=operator_ref,
        delivery_artifact_refs=delivery_artifact_refs,
        review_observation=review_observation,
        delivery_review_required=delivery_review_required,
        owner_delivery_ready=owner_delivery_ready,
    )


def test_ready_path() -> None:
    result = _build()

    assert result["contract_kind"] == "CONTROLLED_DELIVERY_REVIEW_CANDIDATE"
    assert result["status"] == "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"

    candidate = result["controlled_delivery_review_candidate"]
    assert candidate is not None
    assert candidate["candidate_kind"] == "CONTROLLED_DELIVERY_REVIEW_CANDIDATE"
    assert candidate["delivery_review_recorded"] is True
    assert candidate["delivery_executed"] is False
    assert candidate["publish_executed"] is False
    assert candidate["notification_executed"] is False
    assert candidate["cli_executed"] is False
    assert candidate["execution_executed"] is False
    assert candidate["operator_ref"] == "operator-001"
    assert candidate["owner_ref"] == "owner-001"
    assert candidate["tenant_ref"] == "tenant-001"
    assert candidate["case_ref"] == "case-001"
    assert candidate["delivery_artifact_refs"] == ["delivery-artifact-001"]
    assert candidate["delivery_review_required"] is True
    assert candidate["owner_delivery_ready"] is True


def test_invalid_supervised_run_result_wrong_contract_kind() -> None:
    run_result = _valid_run_result()
    run_result["contract_kind"] = "OTHER"

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
    assert result["ready"] is False
    assert result["controlled_delivery_review_candidate"] is None


def test_invalid_supervised_run_result_not_ready() -> None:
    run_result = _valid_run_result()
    run_result["status"] = "BLOCKED"
    run_result["ready"] = False

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"
    assert result["ready"] is False


def test_invalid_abort_rollback_result_wrong_contract_kind() -> None:
    abort = _valid_abort_rollback_result_no_abort()
    abort["contract_kind"] = "OTHER"

    result = _build(abort_rollback_result_candidate=abort)

    assert result["status"] == "BLOCKED_INVALID_ABORT_ROLLBACK_RESULT"
    assert result["ready"] is False


def test_invalid_abort_rollback_result_unknown_status() -> None:
    abort = _valid_abort_rollback_result_no_abort()
    abort["status"] = "UNKNOWN"

    result = _build(abort_rollback_result_candidate=abort)

    assert result["status"] == "BLOCKED_INVALID_ABORT_ROLLBACK_RESULT"
    assert result["ready"] is False


def test_invalid_execution_candidate_wrong_contract_kind() -> None:
    execution = _valid_execution_candidate()
    execution["contract_kind"] = "OTHER"

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False


def test_invalid_execution_candidate_not_ready() -> None:
    execution = _valid_execution_candidate()
    execution["status"] = "BLOCKED"
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


def test_abort_or_rollback_required_blocks() -> None:
    abort = _valid_abort_rollback_result_no_abort()
    abort["status"] = "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"
    abort["abort_rollback_result_candidate"] = {
        "abort_requested": True,
        "rollback_required": True,
    }

    result = _build(abort_rollback_result_candidate=abort)

    assert result["status"] == "BLOCKED_ABORT_OR_ROLLBACK_REQUIRED"
    assert result["ready"] is False


def test_missing_delivery_artifact_refs() -> None:
    result = _build(delivery_artifact_refs=[])

    assert result["status"] == "BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS"
    assert result["ready"] is False


def test_owner_delivery_not_ready() -> None:
    result = _build(owner_delivery_ready=False)

    assert result["status"] == "BLOCKED_OWNER_DELIVERY_NOT_READY"
    assert result["ready"] is False


def test_delivery_review_required_false_blocks() -> None:
    result = _build(delivery_review_required=False)

    assert result["status"] == "BLOCKED_OWNER_DELIVERY_NOT_READY"
    assert result["ready"] is False


def test_unsafe_flags_blocked() -> None:
    run_result = _valid_run_result()
    run_result["runtime_authorized"] = True

    result = _build(supervised_cli_run_result_candidate=run_result)

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_fallback() -> None:
    result = build_service_1_controlled_delivery_review_candidate_v1(
        supervised_cli_run_result_candidate=None,
        abort_rollback_result_candidate=None,
        controlled_execution_candidate=None,
        operator_ref="op",
        delivery_artifact_refs=[],
        review_observation="",
        delivery_review_required=False,
        owner_delivery_ready=False,
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False
    assert result["controlled_delivery_review_candidate"] is None


def test_dangerous_flags_are_always_false() -> None:
    result = _build()

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False

    candidate = result["controlled_delivery_review_candidate"]
    assert candidate is not None
    for flag in DANGEROUS_FLAGS:
        assert candidate[flag] is False


def test_does_not_mutate_inputs() -> None:
    run_result = _valid_run_result()
    abort = _valid_abort_rollback_result_no_abort()
    execution = _valid_execution_candidate()
    artifacts = ["delivery-artifact-001"]
    observation = "observation"

    before_run = deepcopy(run_result)
    before_abort = deepcopy(abort)
    before_execution = deepcopy(execution)
    before_artifacts = deepcopy(artifacts)
    before_observation = observation

    _build(
        supervised_cli_run_result_candidate=run_result,
        abort_rollback_result_candidate=abort,
        controlled_execution_candidate=execution,
        delivery_artifact_refs=artifacts,
        review_observation=observation,
    )

    assert run_result == before_run
    assert abort == before_abort
    assert execution == before_execution
    assert artifacts == before_artifacts
    assert observation == before_observation


def test_result_is_deterministic() -> None:
    first = _build()
    second = _build()

    assert first == second


def test_source_guard_no_runtime_or_infrastructure_imports() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_controlled_delivery_review_candidate_v1.py"
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
