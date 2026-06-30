from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_controlled_client_case_operator_supervision_contract_v1 import (
    build_service_1_controlled_client_case_operator_supervision_contract_v1,
)
from pymia.smartpyme.service_1_first_controlled_client_case_evidence_packet_v1 import (
    build_service_1_first_controlled_client_case_evidence_packet_v1,
)
from pymia.smartpyme.service_1_first_controlled_client_case_readiness_gate_v1 import (
    build_service_1_first_controlled_client_case_readiness_gate_v1,
)


def _case_candidate() -> dict[str, object]:
    return {
        "owner_ref": "owner-001",
        "tenant_ref": "tenant-001",
        "case_ref": "case-001",
        "owner_consent": True,
        "evidence_refs": ["evidence-xlsx-001", "evidence-bank-001"],
        "scope": {
            "problem_statement": "Primer caso controlado con validación supervisada.",
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
        "api_exposed": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "mutation_authorized": False,
        "llm_authorized": False,
    }


def _abort_policy() -> dict[str, object]:
    return {
        "abort_allowed": True,
        "rollback_ref": "rollback-plan-001",
        "allowed_actions": [
            "inspect_evidence_packet",
            "run_supervised_cli_flow",
            "review_generated_artifacts",
            "abort_controlled_case",
        ],
    }


def test_phase_i_controlled_case_chain_composition_e2e_pure() -> None:
    case_candidate = _case_candidate()
    abort_policy = _abort_policy()

    original_case_candidate = deepcopy(case_candidate)
    original_abort_policy = deepcopy(abort_policy)

    readiness_result = build_service_1_first_controlled_client_case_readiness_gate_v1(
        case_candidate=case_candidate
    )
    assert readiness_result["status"] == "CONTROLLED_CASE_READY"
    assert readiness_result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert readiness_result["runtime_authorized"] is False
    assert readiness_result["publish_executed"] is False
    assert readiness_result["notification_sent"] is False
    assert readiness_result["handoff_executed"] is False
    assert readiness_result["api_exposed"] is False
    assert readiness_result["storage_write_authorized"] is False
    assert readiness_result["worker_authorized"] is False
    assert readiness_result["llm_authorized"] is False

    evidence_packet_result = build_service_1_first_controlled_client_case_evidence_packet_v1(
        readiness_gate_result=readiness_result,
        owner_ref="owner-001",
        tenant_ref="tenant-001",
        case_ref="case-001",
        evidence_refs=["evidence-xlsx-001", "evidence-bank-001"],
        file_refs=["file-sales-001", "file-bank-001"],
        scope="Primer caso controlado con validación supervisada.",
        owner_consent_ref="consent-001",
        operator_oversight_ref="oversight-001",
        rollback_plan_ref="rollback-plan-001",
    )
    assert evidence_packet_result["status"] == "EVIDENCE_PACKET_READY"
    assert evidence_packet_result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert evidence_packet_result["runtime_authorized"] is False
    assert evidence_packet_result["publish_executed"] is False
    assert evidence_packet_result["notification_sent"] is False
    assert evidence_packet_result["handoff_executed"] is False
    assert evidence_packet_result["api_exposed"] is False
    assert evidence_packet_result["storage_write_authorized"] is False
    assert evidence_packet_result["worker_authorized"] is False
    assert evidence_packet_result["llm_authorized"] is False

    evidence_packet_candidate = evidence_packet_result["controlled_case_evidence_packet_candidate"]
    assert evidence_packet_candidate is not None

    operator_supervision_result = build_service_1_controlled_client_case_operator_supervision_contract_v1(
        evidence_packet_candidate=evidence_packet_candidate,
        operator_ref="operator-001",
        abort_policy=abort_policy,
    )
    assert operator_supervision_result["status"] == "OPERATOR_SUPERVISION_READY"
    assert operator_supervision_result["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert operator_supervision_result["runtime_authorized"] is False
    assert operator_supervision_result["publish_executed"] is False
    assert operator_supervision_result["notification_sent"] is False
    assert operator_supervision_result["handoff_executed"] is False
    assert operator_supervision_result["api_exposed"] is False
    assert operator_supervision_result["storage_write_authorized"] is False
    assert operator_supervision_result["worker_authorized"] is False
    assert operator_supervision_result["llm_authorized"] is False

    operator_supervision_candidate = operator_supervision_result["operator_supervision_candidate"]
    assert operator_supervision_candidate is not None
    assert operator_supervision_candidate["allowed_execution_mode"] == "SUPERVISED_CLI_OPERATOR_FLOW"
    assert operator_supervision_candidate["runtime_authorized"] is False
    assert operator_supervision_candidate["publish_executed"] is False
    assert operator_supervision_candidate["notification_sent"] is False
    assert operator_supervision_candidate["handoff_executed"] is False
    assert operator_supervision_candidate["api_exposed"] is False
    assert operator_supervision_candidate["storage_write_authorized"] is False
    assert operator_supervision_candidate["worker_authorized"] is False
    assert operator_supervision_candidate["llm_authorized"] is False

    assert case_candidate == original_case_candidate
    assert abort_policy == original_abort_policy
