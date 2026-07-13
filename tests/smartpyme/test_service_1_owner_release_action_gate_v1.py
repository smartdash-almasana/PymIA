from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_owner_release_action_gate_v1 import (
    REQUIRED_FIELDS,
    build_service_1_owner_release_action_gate_v1,
)


def _valid_input() -> dict[str, object]:
    return {
        "case_folder_manifest_status": "READY_FOR_QA",
        "delivery_manifest_audit_status": "PASS_READY_FOR_DELIVERY",
        "requested_release_action": "deliver_operational_draft",
        "release_responsible_present": True,
        "release_review_status": "REQUIRED",
        "forbidden_claims_check": "PASSED",
        "stop_conditions": "NONE",
        "delivery_allowed_by_audit": True,
    }


def test_valid_release_action_allows_operational_draft_delivery() -> None:
    result = build_service_1_owner_release_action_gate_v1(_valid_input())

    assert result["status"] == "READY_FOR_OPERATIONAL_DRAFT_DELIVERY"
    assert result["delivery_allowed"] is True
    assert result["blocked_release_actions"] == []
    assert result["next_allowed_action"] == "deliver_operational_draft"


def test_non_dict_input_is_invalid() -> None:
    result = build_service_1_owner_release_action_gate_v1("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["delivery_allowed"] is False
    assert result["allowed_release_actions"] == ["block_delivery"]
    assert result["next_allowed_action"] == "fix_release_input"


def test_missing_fields_block_delivery() -> None:
    release_input = _valid_input()
    del release_input["case_folder_manifest_status"]
    del release_input["delivery_allowed_by_audit"]

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["delivery_allowed"] is False
    assert result["required_responsible_actions"] == ["complete_required_fields"]
    assert set(REQUIRED_FIELDS) >= {"case_folder_manifest_status", "delivery_allowed_by_audit"}


def test_case_manifest_not_ready_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["case_folder_manifest_status"] = "MISSING_REQUIRED_FIELDS"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_CASE_MANIFEST"
    assert "deliver_operational_draft" in result["blocked_release_actions"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "repair_case_manifest"


def test_delivery_audit_not_passing_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["delivery_manifest_audit_status"] = "FAIL_REWORK_REQUIRED"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_DELIVERY_AUDIT"
    assert "deliver_operational_draft" in result["blocked_release_actions"]
    assert result["delivery_allowed"] is False
    assert result["next_allowed_action"] == "repair_delivery_audit"


def test_delivery_audit_disallow_flag_blocks_delivery_even_if_status_passes() -> None:
    release_input = _valid_input()
    release_input["delivery_allowed_by_audit"] = False

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_DELIVERY_AUDIT"
    assert result["delivery_allowed"] is False


def test_active_stop_condition_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["stop_conditions"] = "FINAL_RECONCILIATION_REQUESTED"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_STOP_CONDITION"
    assert result["required_responsible_actions"] == ["resolve_stop_conditions"]
    assert result["delivery_allowed"] is False


def test_missing_release_review_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["release_responsible_present"] = False

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_MISSING_RELEASE_REVIEW"
    assert "assign_release_responsible" in result["required_responsible_actions"]
    assert result["delivery_allowed"] is False


def test_invalid_release_review_status_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["release_review_status"] = "NOT_REQUIRED"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_MISSING_RELEASE_REVIEW"
    assert result["delivery_allowed"] is False


def test_forbidden_claims_not_passed_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["forbidden_claims_check"] = "FAILED"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_CLAIMS"
    assert result["required_responsible_actions"] == ["remove_forbidden_claims"]
    assert result["delivery_allowed"] is False


def test_forbidden_release_action_blocks_delivery() -> None:
    release_input = _valid_input()
    release_input["requested_release_action"] = "run_autonomous_chatbot"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_ACTION"
    assert "run_autonomous_chatbot" in result["blocked_release_actions"]
    assert "deliver_operational_draft" in result["blocked_release_actions"]
    assert result["delivery_allowed"] is False


def test_send_to_owner_or_responsible_review_is_allowed_but_does_not_allow_delivery() -> None:
    release_input = _valid_input()
    release_input["requested_release_action"] = "send_to_owner_or_responsible_review"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "READY_FOR_OWNER_OR_RESPONSIBLE_REVIEW"
    assert result["delivery_allowed"] is False
    assert result["blocked_release_actions"] == ["deliver_operational_draft"]
    assert result["next_allowed_action"] == "send_to_owner_or_responsible_review"


def test_prepare_delivery_notes_is_allowed_but_does_not_allow_delivery() -> None:
    release_input = _valid_input()
    release_input["requested_release_action"] = "prepare_delivery_notes"

    result = build_service_1_owner_release_action_gate_v1(release_input)

    assert result["status"] == "READY_FOR_OWNER_OR_RESPONSIBLE_REVIEW"
    assert result["delivery_allowed"] is False
    assert "deliver_operational_draft" in result["blocked_release_actions"]


def test_module_has_no_io_xlsx_parser_api_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_owner_release_action_gate_v1.py"
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
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_owner_release_action_gate_v1.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
