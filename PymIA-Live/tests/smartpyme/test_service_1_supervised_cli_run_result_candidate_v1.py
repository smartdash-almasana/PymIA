from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.smartpyme.service_1_supervised_cli_run_result_candidate_v1 import (
    build_service_1_supervised_cli_run_result_candidate_v1,
)


DANGEROUS_FLAGS = (
    "execution_executed",
    "cli_executed",
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
    controlled_execution_candidate: dict[str, object] | None = None,
    operator_supervision_candidate: dict[str, object] | None = None,
    artifact_refs: list[str] | object = ["artifact-001"],
    warning_refs: list[str] | object = [],
    error_refs: list[str] | object = [],
    run_observation: str = "CLI run completed successfully with no errors.",
    operator_ref: str = "operator-001",
) -> dict[str, object]:
    return build_service_1_supervised_cli_run_result_candidate_v1(
        controlled_execution_candidate=controlled_execution_candidate or _valid_execution_candidate(),
        operator_supervision_candidate=operator_supervision_candidate or _valid_operator_supervision_candidate(),
        artifact_refs=artifact_refs,
        warning_refs=warning_refs,
        error_refs=error_refs,
        run_observation=run_observation,
        operator_ref=operator_ref,
    )


def test_ready_path() -> None:
    result = _build()

    assert result["contract_kind"] == "SUPERVISED_CLI_RUN_RESULT_CANDIDATE"
    assert result["status"] == "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"
    assert result["ready"] is True
    assert result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"

    candidate = result["supervised_cli_run_result_candidate"]
    assert candidate is not None
    assert candidate["candidate_kind"] == "SUPERVISED_CLI_RUN_RESULT_CANDIDATE"
    assert candidate["run_recorded"] is True
    assert candidate["cli_executed"] is False
    assert candidate["execution_executed"] is False
    assert candidate["operator_ref"] == "operator-001"
    assert candidate["owner_ref"] == "owner-001"
    assert candidate["tenant_ref"] == "tenant-001"
    assert candidate["case_ref"] == "case-001"
    assert candidate["artifact_refs"] == ["artifact-001"]
    assert candidate["warning_refs"] == []
    assert candidate["error_refs"] == []


def test_invalid_execution_candidate_wrong_contract_kind() -> None:
    execution = _valid_execution_candidate()
    execution["contract_kind"] = "OTHER"

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False
    assert result["supervised_cli_run_result_candidate"] is None


def test_invalid_execution_candidate_not_ready() -> None:
    execution = _valid_execution_candidate()
    execution["status"] = "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    execution["ready"] = False

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False


def test_invalid_execution_candidate_execution_executed_true() -> None:
    execution = _valid_execution_candidate()
    inner = execution["controlled_execution_candidate"]
    assert isinstance(inner, dict)
    inner["execution_executed"] = True

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert result["ready"] is False


def test_invalid_operator_supervision_wrong_contract_kind() -> None:
    supervision = _valid_operator_supervision_candidate()
    supervision["contract_kind"] = "OTHER"

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    assert result["ready"] is False


def test_invalid_operator_supervision_not_ready() -> None:
    supervision = _valid_operator_supervision_candidate()
    supervision["status"] = "BLOCKED_MISSING_OPERATOR"
    supervision["ready"] = False

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_INVALID_OPERATOR_SUPERVISION"
    assert result["ready"] is False


def test_operator_mismatch_against_execution() -> None:
    result = _build(operator_ref="operator-002")

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_operator_mismatch_against_supervision() -> None:
    supervision = _valid_operator_supervision_candidate()
    inner = supervision["operator_supervision_candidate"]
    assert isinstance(inner, dict)
    inner["operator_ref"] = "operator-002"

    result = _build(operator_supervision_candidate=supervision)

    assert result["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert result["ready"] is False


def test_missing_artifact_refs() -> None:
    result = _build(artifact_refs=[])

    assert result["status"] == "BLOCKED_MISSING_ARTIFACT_REFS"
    assert result["ready"] is False


def test_run_failed_from_error_refs() -> None:
    result = _build(error_refs=["error-001"])

    assert result["status"] == "BLOCKED_RUN_FAILED"
    assert result["ready"] is False


def test_run_failed_from_observation_failed() -> None:
    result = _build(run_observation="The CLI run failed due to missing file.")

    assert result["status"] == "BLOCKED_RUN_FAILED"
    assert result["ready"] is False


def test_run_failed_from_observation_error() -> None:
    result = _build(run_observation="An error occurred during processing.")

    assert result["status"] == "BLOCKED_RUN_FAILED"
    assert result["ready"] is False


def test_unsafe_flags_blocked() -> None:
    execution = _valid_execution_candidate()
    execution["runtime_authorized"] = True

    result = _build(controlled_execution_candidate=execution)

    assert result["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert result["ready"] is False


def test_unknown_fallback() -> None:
    result = build_service_1_supervised_cli_run_result_candidate_v1(
        controlled_execution_candidate=None,
        operator_supervision_candidate=None,
        artifact_refs=[],
        warning_refs=[],
        error_refs=[],
        run_observation="",
        operator_ref="op",
    )

    assert result["status"] == "UNKNOWN"
    assert result["ready"] is False
    assert result["supervised_cli_run_result_candidate"] is None


def test_dangerous_flags_are_always_false() -> None:
    result = _build()

    for flag in DANGEROUS_FLAGS:
        assert result[flag] is False

    candidate = result["supervised_cli_run_result_candidate"]
    assert candidate is not None
    for flag in DANGEROUS_FLAGS:
        assert candidate[flag] is False


def test_does_not_mutate_inputs() -> None:
    execution = _valid_execution_candidate()
    supervision = _valid_operator_supervision_candidate()
    artifacts = ["artifact-001"]
    warnings = ["warning-001"]
    errors = []
    observation = "observation"

    before_execution = deepcopy(execution)
    before_supervision = deepcopy(supervision)
    before_artifacts = deepcopy(artifacts)
    before_warnings = deepcopy(warnings)
    before_errors = deepcopy(errors)
    before_observation = observation

    _build(
        controlled_execution_candidate=execution,
        operator_supervision_candidate=supervision,
        artifact_refs=artifacts,
        warning_refs=warnings,
        error_refs=errors,
        run_observation=observation,
    )

    assert execution == before_execution
    assert supervision == before_supervision
    assert artifacts == before_artifacts
    assert warnings == before_warnings
    assert errors == before_errors
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
        / "service_1_supervised_cli_run_result_candidate_v1.py"
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
