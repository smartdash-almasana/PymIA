from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_abort_rollback_result_candidate_v1 import build_service_1_abort_rollback_result_candidate_v1
from pymia.smartpyme.service_1_controlled_client_case_execution_candidate_v1 import build_service_1_controlled_client_case_execution_candidate_v1
from pymia.smartpyme.service_1_controlled_client_case_operator_supervision_contract_v1 import build_service_1_controlled_client_case_operator_supervision_contract_v1
from pymia.smartpyme.service_1_controlled_delivery_review_candidate_v1 import build_service_1_controlled_delivery_review_candidate_v1
from pymia.smartpyme.service_1_first_controlled_client_case_evidence_packet_v1 import build_service_1_first_controlled_client_case_evidence_packet_v1
from pymia.smartpyme.service_1_first_controlled_client_case_readiness_gate_v1 import build_service_1_first_controlled_client_case_readiness_gate_v1
from pymia.smartpyme.service_1_supervised_cli_run_result_candidate_v1 import build_service_1_supervised_cli_run_result_candidate_v1


def _case_candidate() -> dict[str, object]:
    return {
        "owner_ref": "owner-001", "tenant_ref": "tenant-001", "case_ref": "case-001",
        "owner_consent": True,
        "evidence_refs": ["evidence-xlsx-001", "evidence-bank-001"],
        "scope": {"problem_statement": "controlled case", "too_broad": False},
        "operator_oversight_enabled": True,
        "rollback_plan": {"abort_allowed": True, "fallback_mode": "CLI_OPERATOR_FLOW"},
        "runtime_authorized": False, "publish_executed": False, "notification_sent": False,
        "handoff_executed": False, "api_exposed": False, "storage_write_authorized": False,
        "db_authorized": False, "worker_authorized": False, "queue_authorized": False,
        "mutation_authorized": False, "llm_authorized": False,
    }


def _abort_policy() -> dict[str, object]:
    return {
        "abort_allowed": True,
        "rollback_ref": "rollback-plan-001",
        "allowed_actions": [
            "inspect_evidence_packet", "run_supervised_cli_flow",
            "review_generated_artifacts", "abort_controlled_case",
        ],
    }


def _opening_chain(
    *,
    case_candidate: dict[str, object] | None = None,
    abort_policy: dict[str, object] | None = None,
    operator_ref: str = "operator-001",
) -> dict[str, object]:
    readiness = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=case_candidate or _case_candidate()
    )
    evidence = build_service_1_first_controlled_client_case_evidence_packet_v1(
        readiness_gate_result=readiness,
        owner_ref="owner-001", tenant_ref="tenant-001", case_ref="case-001",
        evidence_refs=["evidence-xlsx-001", "evidence-bank-001"],
        file_refs=["file-sales-001", "file-bank-001"],
        scope="controlled case", owner_consent_ref="consent-001",
        operator_oversight_ref=operator_ref,
        rollback_plan_ref="rollback-plan-001",
    )
    evidence_candidate = evidence["controlled_case_evidence_packet_candidate"]
    supervision = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=evidence_candidate,
        operator_ref=operator_ref,
        abort_policy=abort_policy or _abort_policy(),
    )
    return {
        "readiness": readiness, "evidence": evidence,
        "evidence_candidate": evidence_candidate, "supervision": supervision,
    }


def _full_chain(
    *,
    operator_ref: str = "operator-001",
    execution_operator_ref: str = "operator-001",
    run_artifact_refs: list[str] | object = ["artifact-cli-run-001"],
    delivery_artifact_refs: list[str] | object = ["delivery-artifact-001"],
    abort_requested: bool = False,
    rollback_required: bool = False,
    unsafe_supervision_flag: bool = False,
) -> dict[str, object]:
    chain = _opening_chain(operator_ref=operator_ref)
    supervision = chain["supervision"]
    assert isinstance(supervision, dict)
    if unsafe_supervision_flag:
        supervision = deepcopy(supervision)
        supervision["runtime_authorized"] = True

    execution = build_service_1_controlled_client_case_execution_candidate_v1(
        operator_supervision_candidate=supervision,
        evidence_packet_candidate=chain["evidence_candidate"],
        readiness_gate_result=chain["readiness"],
        execution_window_ref="window-001",
        operator_ref=execution_operator_ref,
        dry_run_required=True,
    )
    run = build_service_1_supervised_cli_run_result_candidate_v1(
        controlled_execution_candidate=execution,
        operator_supervision_candidate=supervision,
        artifact_refs=run_artifact_refs,
        warning_refs=[], error_refs=[],
        run_observation="CLI run candidate completed successfully; no errors.",
        operator_ref=operator_ref,
    )
    rollback = build_service_1_abort_rollback_result_candidate_v1(
        supervised_cli_run_result_candidate=run,
        controlled_execution_candidate=execution,
        operator_ref=operator_ref,
        abort_requested=abort_requested,
        rollback_required=rollback_required,
        rollback_reason="Operator controlled abort.",
        rollback_artifact_refs=["rollback-artifact-001"],
        rollback_observation="Rollback candidate recorded but not executed.",
    )
    review = build_service_1_controlled_delivery_review_candidate_v1(
        supervised_cli_run_result_candidate=run,
        abort_rollback_result_candidate=rollback,
        controlled_execution_candidate=execution,
        operator_ref=operator_ref,
        delivery_artifact_refs=delivery_artifact_refs,
        review_observation="Delivery review candidate completed successfully.",
        delivery_review_required=True,
        owner_delivery_ready=True,
    )
    return {**chain, "execution": execution, "run": run, "rollback": rollback, "review": review}


def _assert_no_real_execution_flags(payload: dict[str, object]) -> None:
    guarded_flags = (
        "cli_executed", "execution_executed", "rollback_executed",
        "delivery_executed", "publish_executed", "notification_executed",
        "notification_sent", "runtime_authorized",
    )
    for flag in guarded_flags:
        if flag in payload:
            assert payload[flag] is False
    for value in payload.values():
        if isinstance(value, dict):
            _assert_no_real_execution_flags(value)


def test_phase_i_full_chain_happy_path_reaches_delivery_review_ready() -> None:
    chain = _full_chain()
    assert chain["readiness"]["status"] == "CONTROLLED_CASE_READY"
    assert chain["evidence"]["status"] == "EVIDENCE_PACKET_READY"
    assert chain["supervision"]["status"] == "OPERATOR_SUPERVISION_READY"
    assert chain["execution"]["status"] == "CONTROLLED_EXECUTION_CANDIDATE_READY"
    assert chain["run"]["status"] == "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"
    assert chain["rollback"]["status"] == "NO_ABORT_OR_ROLLBACK_REQUIRED"
    assert chain["review"]["status"] == "CONTROLLED_DELIVERY_REVIEW_CANDIDATE_READY"
    assert chain["review"]["ready"] is True


def test_phase_i_full_chain_keeps_real_execution_flags_false() -> None:
    for payload in _full_chain().values():
        assert isinstance(payload, dict)
        _assert_no_real_execution_flags(payload)


def test_operator_ref_mismatch_blocks_chain_before_run_and_delivery_review() -> None:
    chain = _full_chain(execution_operator_ref="operator-002")
    assert chain["execution"]["status"] == "BLOCKED_OPERATOR_MISMATCH"
    assert chain["run"]["status"] == "BLOCKED_INVALID_EXECUTION_CANDIDATE"
    assert chain["review"]["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"


def test_missing_run_artifact_refs_blocks_run_result_and_review() -> None:
    chain = _full_chain(run_artifact_refs=[])
    assert chain["run"]["status"] == "BLOCKED_MISSING_ARTIFACT_REFS"
    assert chain["review"]["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"


def test_missing_delivery_artifact_refs_blocks_delivery_review_only() -> None:
    chain = _full_chain(delivery_artifact_refs=[])
    assert chain["run"]["status"] == "SUPERVISED_CLI_RUN_RESULT_CANDIDATE_READY"
    assert chain["review"]["status"] == "BLOCKED_MISSING_DELIVERY_ARTIFACT_REFS"


def test_abort_or_rollback_required_blocks_delivery_review() -> None:
    chain = _full_chain(abort_requested=True, rollback_required=True)
    assert chain["rollback"]["status"] == "ABORT_ROLLBACK_RESULT_CANDIDATE_READY"
    assert chain["review"]["status"] == "BLOCKED_ABORT_OR_ROLLBACK_REQUIRED"


def test_unsafe_runtime_flag_in_upstream_blocks_downstream_chain() -> None:
    chain = _full_chain(unsafe_supervision_flag=True)
    assert chain["execution"]["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert chain["run"]["status"] == "BLOCKED_UNSAFE_RUNTIME_FLAGS"
    assert chain["review"]["status"] == "BLOCKED_INVALID_SUPERVISED_RUN_RESULT"


def test_phase_i_full_chain_does_not_mutate_seed_inputs() -> None:
    case_candidate = _case_candidate()
    abort_policy = _abort_policy()
    before_case_candidate = deepcopy(case_candidate)
    before_abort_policy = deepcopy(abort_policy)
    opening = _opening_chain(case_candidate=case_candidate, abort_policy=abort_policy)
    assert opening["supervision"]["status"] == "OPERATOR_SUPERVISION_READY"
    assert case_candidate == before_case_candidate
    assert abort_policy == before_abort_policy


def test_phase_i_full_chain_is_deterministic() -> None:
    assert _full_chain() == _full_chain()
