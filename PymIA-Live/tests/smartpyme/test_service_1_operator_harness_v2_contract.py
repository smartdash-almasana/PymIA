from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_operator_harness_v2_contract import (
    REQUIRED_FIELDS,
    build_service_1_operator_harness_v2_contract,
)


def _valid_input() -> dict[str, object]:
    return {
        "case_folder_manifest_status": "READY_FOR_QA",
        "delivery_manifest_audit_status": "PASS_READY_FOR_DELIVERY",
        "operator_requested_action": "deliver_operational_draft",
        "human_reviewer_present": True,
        "human_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_allowed_by_audit": True,
    }


def test_valid_delivery_action_allows_operational_draft_delivery() -> None:
    result = build_service_1_operator_harness_v2_contract(_valid_input())

    assert result["status"] == "READY_FOR_OPERATIONAL_DRAFT_DELIVERY"
    assert result["delivery_allowed"] is True
    assert result["blocked_operator_actions"] == []
    assert result["next_allowed_action"] == "deliver_operational_draft"


def test_non_dict_input_is_invalid() -> None:
    result = build_service_1_operator_harness_v2_contract("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["delivery_allowed"] is False
    assert result["allowed_operator_actions"] == ["block_delivery"]
    assert result["next_allowed_action"] == "fix_operator_input"


def test_missing_fields_block_delivery() -> None:
    operator_input = _valid_input()
    del operator_input["case_folder_manifest_status"]
    del operator_input["delivery_allowed_by_audit"]

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["delivery_allowed"] is False
    assert result["required_human_actions"] == ["complete_required_fields"]
    assert set(REQUIRED_FIELDS) >= {"case_folder_manifest_status", "delivery_allowed_by_audit"}


def test_case_manifest_not_ready_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["case_folder_manifest_status"] = "MISSING_REQUIRED_FIELDS"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_CASE_MANIFEST"
    assert "deliver_operational_draft" in result["blocked_operator_actions"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "repair_case_manifest"


def test_delivery_audit_not_passing_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["delivery_manifest_audit_status"] = "FAIL_REWORK_REQUIRED"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_DELIVERY_AUDIT"
    assert "deliver_operational_draft" in result["blocked_operator_actions"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "repair_delivery_audit"


def test_delivery_audit_disallow_flag_blocks_delivery_even_if_status_passes() -> None:
    operator_input = _valid_input()
    operator_input["delivery_allowed_by_audit"] = False

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_DELIVERY_AUDIT"
    assert result["delivery_allowed"] is False


def test_active_stop_condition_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["stop_conditions"] = "FINAL_RECONCILIATION_REQUESTED"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert result["required_human_actions"] == ["resolve_stop_conditions"]
    assert result["delivery_allowed"] is False


def test_missing_human_review_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["human_reviewer_present"] = False

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_MISSING_HUMAN_REVIEW"
    assert "assign_human_reviewer" in result["required_human_actions"]
    assert result["delivery_allowed"] is False


def test_invalid_human_review_status_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["human_review_status"] = "NOT_REQUIRED"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_MISSING_HUMAN_REVIEW"
    assert result["delivery_allowed"] is False


def test_forbidden_claims_not_passed_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["forbidden_claims_check"] = "FAILED"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_CLAIMS"
    assert result["required_human_actions"] == ["remove_forbidden_claims"]
    assert result["delivery_allowed"] is False


def test_forbidden_operator_action_blocks_delivery() -> None:
    operator_input = _valid_input()
    operator_input["operator_requested_action"] = "run_autonomous_chatbot"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_ACTION"
    assert "run_autonomous_chatbot" in result["blocked_operator_actions"]
    assert "deliver_operational_draft" in result["blocked_operator_actions"]
    assert result["delivery_allowed"] is False


def test_send_to_human_review_is_allowed_but_does_not_allow_delivery() -> None:
    operator_input = _valid_input()
    operator_input["operator_requested_action"] = "send_to_human_review"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["delivery_allowed"] is False
    assert result["blocked_operator_actions"] == ["deliver_operational_draft"]
    assert result["next_allowed_action"] == "send_to_human_review"


def test_prepare_operator_notes_is_allowed_but_does_not_allow_delivery() -> None:
    operator_input = _valid_input()
    operator_input["operator_requested_action"] = "prepare_operator_notes"

    result = build_service_1_operator_harness_v2_contract(operator_input)

    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["delivery_allowed"] is False
    assert "deliver_operational_draft" in result["blocked_operator_actions"]


def test_module_has_no_io_xlsx_parser_api_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_operator_harness_v2_contract.py"
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
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_operator_harness_v2_contract.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
