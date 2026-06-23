from __future__ import annotations

from pymia.smartpyme.service_1_case_folder_manifest_contract_v1 import (
    build_service_1_case_folder_manifest_contract_v1,
)
from pymia.smartpyme.service_1_delivery_manifest_audit_contract_v1 import (
    build_service_1_delivery_manifest_audit_contract_v1,
)
from pymia.smartpyme.service_1_operator_harness_v2_contract import (
    build_service_1_operator_harness_v2_contract,
)


def _manifest_input() -> dict[str, object]:
    return {
        "case_id": "SERVICE1_CASE_E2E_0001",
        "client_alias": "cliente_demo",
        "case_family": "accounting_workpaper_basic",
        "period": "2026-06",
        "operator": "operator_demo",
        "human_reviewer": "reviewer_demo",
        "intake_status": "ACCEPTED",
        "accepted_scope": "operational_draft_review",
        "input_files": ["ventas.xlsx", "cobros.xlsx"],
        "human_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_status": "READY_FOR_CLIENT_DELIVERY",
        "next_safe_action": "SEND_TO_QA",
    }


def _audit_input() -> dict[str, object]:
    return {
        "case_id": "SERVICE1_CASE_E2E_0001",
        "manifest_present": True,
        "case_family": "accounting_workpaper_basic",
        "period_present": True,
        "operator_present": True,
        "human_reviewer_present": True,
        "input_files_listed": True,
        "output_files_listed": True,
        "xlsx_review_file_present": True,
        "qa_checklist_present": True,
        "qa_status": "PASSED",
        "owner_message_present": True,
        "operator_notes_present": True,
        "evidence_gap_log_present": True,
        "visible_differences_log_present": True,
        "human_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_status": "READY_FOR_CLIENT_DELIVERY",
        "next_safe_action": "DELIVER_AS_OPERATIONAL_DRAFT_UNDER_HUMAN_REVIEW",
    }


def _operator_input_from_contracts(
    *,
    manifest_result: dict[str, object],
    audit_result: dict[str, object],
    operator_requested_action: str,
    stop_conditions: object = "NONE",
    human_reviewer_present: bool = True,
    human_review_status: str = "REQUIRED",
    forbidden_claims_check: str = "PASSED",
) -> dict[str, object]:
    return {
        "case_folder_manifest_status": manifest_result["status"],
        "delivery_manifest_audit_status": audit_result["status"],
        "operator_requested_action": operator_requested_action,
        "human_reviewer_present": human_reviewer_present,
        "human_review_status": human_review_status,
        "forbidden_claims_check": forbidden_claims_check,
        "stop_conditions": stop_conditions,
        "delivery_allowed_by_audit": audit_result["delivery_allowed"],
    }


def test_e2e_pass_path_allows_operational_draft_delivery_only_after_manifest_and_audit_pass() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
        )
    )

    assert manifest_result["status"] == "READY_FOR_QA"
    assert manifest_result["delivery_allowed"] is True
    assert audit_result["status"] == "PASS_READY_FOR_DELIVERY"
    assert audit_result["delivery_allowed"] is True
    assert harness_result["status"] == "READY_FOR_OPERATIONAL_DRAFT_DELIVERY"
    assert harness_result["delivery_allowed"] is True
    assert harness_result["next_allowed_action"] == "deliver_operational_draft"


def test_e2e_human_review_action_does_not_allow_delivery_even_when_manifest_and_audit_pass() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="send_to_human_review",
        )
    )

    assert manifest_result["status"] == "READY_FOR_QA"
    assert audit_result["status"] == "PASS_READY_FOR_DELIVERY"
    assert harness_result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert harness_result["delivery_allowed"] is False
    assert harness_result["blocked_operator_actions"] == ["deliver_operational_draft"]


def test_e2e_manifest_stop_condition_blocks_before_delivery_audit_can_authorize_harness_delivery() -> None:
    manifest_input = _manifest_input()
    manifest_input["stop_conditions"] = "MISSING_MINIMUM_EVIDENCE"

    manifest_result = build_service_1_case_folder_manifest_contract_v1(manifest_input)
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
        )
    )

    assert manifest_result["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert manifest_result["delivery_allowed"] is False
    assert audit_result["status"] == "PASS_READY_FOR_DELIVERY"
    assert harness_result["status"] == "BLOCKED_BY_CASE_MANIFEST"
    assert harness_result["delivery_allowed"] is False


def test_e2e_delivery_audit_qa_failure_blocks_harness_delivery() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_input = _audit_input()
    audit_input["qa_status"] = "FAILED"
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
        )
    )

    assert manifest_result["status"] == "READY_FOR_QA"
    assert audit_result["status"] == "FAIL_MISSING_QA"
    assert audit_result["delivery_allowed"] is False
    assert harness_result["status"] == "BLOCKED_BY_DELIVERY_AUDIT"
    assert harness_result["delivery_allowed"] is False


def test_e2e_delivery_audit_warning_passes_but_harness_keeps_operational_draft_boundary() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_input = _audit_input()
    audit_input["warning_flags"] = ["duplicate_payments_or_collections_present"]
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
        )
    )

    assert audit_result["status"] == "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW"
    assert audit_result["delivery_allowed"] is True
    assert harness_result["status"] == "READY_FOR_OPERATIONAL_DRAFT_DELIVERY"
    assert harness_result["delivery_allowed"] is True
    assert harness_result["next_allowed_action"] == "deliver_operational_draft"


def test_e2e_forbidden_operator_action_is_blocked_even_when_manifest_and_audit_pass() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="run_autonomous_chatbot",
        )
    )

    assert manifest_result["status"] == "READY_FOR_QA"
    assert audit_result["status"] == "PASS_READY_FOR_DELIVERY"
    assert harness_result["status"] == "BLOCKED_BY_FORBIDDEN_ACTION"
    assert harness_result["delivery_allowed"] is False
    assert "run_autonomous_chatbot" in harness_result["blocked_operator_actions"]


def test_e2e_forbidden_claims_failure_blocks_at_manifest_and_harness_layers() -> None:
    manifest_input = _manifest_input()
    manifest_input["forbidden_claims_check"] = "FAILED"
    manifest_result = build_service_1_case_folder_manifest_contract_v1(manifest_input)
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
            forbidden_claims_check="FAILED",
        )
    )

    assert manifest_result["status"] == "BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK"
    assert manifest_result["delivery_allowed"] is False
    assert harness_result["status"] == "BLOCKED_BY_CASE_MANIFEST"
    assert harness_result["delivery_allowed"] is False


def test_e2e_harness_blocks_delivery_if_stop_condition_reappears_after_audit() -> None:
    manifest_result = build_service_1_case_folder_manifest_contract_v1(_manifest_input())
    audit_result = build_service_1_delivery_manifest_audit_contract_v1(_audit_input())
    harness_result = build_service_1_operator_harness_v2_contract(
        _operator_input_from_contracts(
            manifest_result=manifest_result,
            audit_result=audit_result,
            operator_requested_action="deliver_operational_draft",
            stop_conditions="FINAL_RECONCILIATION_REQUESTED",
        )
    )

    assert manifest_result["status"] == "READY_FOR_QA"
    assert audit_result["status"] == "PASS_READY_FOR_DELIVERY"
    assert harness_result["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert harness_result["delivery_allowed"] is False
