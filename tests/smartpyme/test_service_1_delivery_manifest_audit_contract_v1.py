from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_delivery_manifest_audit_contract_v1 import (
    REQUIRED_SERVICE_1_DELIVERY_MANIFEST_AUDIT_FIELDS,
    build_service_1_delivery_manifest_audit_contract_v1,
)


def _valid_audit_input() -> dict[str, object]:
    return {
        "case_id": "SERVICE1_CASE_0001",
        "manifest_present": True,
        "case_family": "ventas_declaradas_vs_cobros_declarados",
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


def test_valid_audit_input_passes_ready_for_delivery() -> None:
    result = build_service_1_delivery_manifest_audit_contract_v1(_valid_audit_input())

    assert result == {
        "status": "PASS_READY_FOR_DELIVERY",
        "missing_fields": [],
        "failed_gates": [],
        "active_stop_conditions": [],
        "delivery_allowed": True,
        "human_review_required": True,
        "next_allowed_action": "deliver_operational_draft_under_human_review",
    }


def test_valid_audit_input_with_completed_human_review_does_not_require_review() -> None:
    audit_input = _valid_audit_input()
    audit_input["human_review_status"] = "COMPLETED"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "PASS_READY_FOR_DELIVERY"
    assert result["delivery_allowed"] is True
    assert result["human_review_required"] is False


def test_non_dict_input_returns_invalid_input() -> None:
    result = build_service_1_delivery_manifest_audit_contract_v1("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["missing_fields"] == list(REQUIRED_SERVICE_1_DELIVERY_MANIFEST_AUDIT_FIELDS)
    assert result["failed_gates"] == ["audit_input_must_be_dict"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "fix_audit_input"


def test_missing_required_fields_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    del audit_input["case_id"]
    del audit_input["next_safe_action"]

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["missing_fields"] == ["case_id", "next_safe_action"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "complete_required_fields"


def test_missing_or_failed_qa_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    audit_input["qa_status"] = "FAILED"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_MISSING_QA"
    assert "qa_checklist_or_status" in result["failed_gates"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "complete_qa_checklist"


def test_missing_human_review_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    audit_input["human_reviewer_present"] = False

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_MISSING_HUMAN_REVIEW"
    assert "human_reviewer_present" in result["failed_gates"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "assign_human_reviewer"


def test_invalid_human_review_status_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    audit_input["human_review_status"] = "NOT_REQUIRED"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_MISSING_HUMAN_REVIEW"
    assert "human_review_gate" in result["failed_gates"]
    assert result["delivery_allowed"] is False


def test_active_stop_condition_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    audit_input["stop_conditions"] = "FINAL_RECONCILIATION_REQUESTED"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_BLOCKED_BY_STOP_CONDITION"
    assert result["active_stop_conditions"] == ["FINAL_RECONCILIATION_REQUESTED"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "resolve_stop_conditions"


def test_forbidden_claims_check_not_passed_blocks_delivery() -> None:
    audit_input = _valid_audit_input()
    audit_input["forbidden_claims_check"] = "FAILED"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_FORBIDDEN_CLAIM_DETECTED"
    assert result["failed_gates"] == ["forbidden_claims_check"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "remove_forbidden_claims"


def test_final_accounting_delivery_status_blocks_as_rework_required() -> None:
    audit_input = _valid_audit_input()
    audit_input["delivery_status"] = "FINAL_ACCOUNTING_RESULT"

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_REWORK_REQUIRED"
    assert "delivery_status" in result["failed_gates"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "rework_delivery_package"


def test_documented_warning_passes_with_human_review_requirement() -> None:
    audit_input = _valid_audit_input()
    audit_input["warning_flags"] = ["duplicate_payments_or_collections_present"]

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW"
    assert result["failed_gates"] == []
    assert result["delivery_allowed"] is True
    assert result["human_review_required"] is True


def test_boolean_presence_gate_false_reworks_delivery_package() -> None:
    audit_input = _valid_audit_input()
    audit_input["owner_message_present"] = False

    result = build_service_1_delivery_manifest_audit_contract_v1(audit_input)

    assert result["status"] == "FAIL_REWORK_REQUIRED"
    assert "owner_message_present" in result["failed_gates"]
    assert result["delivery_allowed"] is False


def test_contract_module_does_not_import_io_xlsx_parser_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_delivery_manifest_audit_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    forbidden_fragments = (
        "openpyxl",
        "pandas",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "from pathlib",
        "requests",
        "httpx",
        "llm",
        "chatbot",
        "ocr",
        "parser",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_vertical_slice_was_not_imported_or_referenced() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_delivery_manifest_audit_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
