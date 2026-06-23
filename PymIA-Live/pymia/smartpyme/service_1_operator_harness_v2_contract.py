from __future__ import annotations

from typing import Any, Literal, TypedDict

Status = Literal[
    "INVALID_INPUT",
    "MISSING_REQUIRED_FIELDS",
    "BLOCKED_BY_CASE_MANIFEST",
    "BLOCKED_BY_DELIVERY_AUDIT",
    "BLOCKED_BY_STOP_CONDITION",
    "BLOCKED_BY_MISSING_HUMAN_REVIEW",
    "BLOCKED_BY_FORBIDDEN_CLAIMS",
    "BLOCKED_BY_FORBIDDEN_ACTION",
    "READY_FOR_HUMAN_REVIEW",
    "READY_FOR_OPERATIONAL_DRAFT_DELIVERY",
]

NextAction = Literal[
    "fix_operator_input",
    "complete_required_fields",
    "repair_case_manifest",
    "repair_delivery_audit",
    "resolve_stop_conditions",
    "assign_human_reviewer",
    "remove_forbidden_claims",
    "request_allowed_operator_action",
    "send_to_human_review",
    "deliver_operational_draft",
]

REQUIRED_FIELDS: tuple[str, ...] = (
    "case_folder_manifest_status",
    "delivery_manifest_audit_status",
    "operator_requested_action",
    "human_reviewer_present",
    "human_review_status",
    "forbidden_claims_check",
    "stop_conditions",
    "delivery_allowed_by_audit",
)

READY_MANIFEST_STATUSES = ("READY_FOR_QA", "VALID")
PASSING_AUDIT_STATUSES = ("PASS_READY_FOR_DELIVERY", "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW")
VALID_HUMAN_REVIEW_STATUSES = ("REQUIRED", "COMPLETED")
ALLOWED_OPERATOR_ACTIONS: tuple[str, ...] = (
    "request_missing_evidence",
    "prepare_owner_summary",
    "prepare_operator_notes",
    "prepare_operational_xlsx_draft",
    "send_to_human_review",
    "deliver_operational_draft",
    "block_delivery",
)
NON_DELIVERY_ACTIONS = [
    "request_missing_evidence",
    "prepare_owner_summary",
    "prepare_operator_notes",
    "prepare_operational_xlsx_draft",
    "send_to_human_review",
    "block_delivery",
]


class Service1OperatorHarnessV2Contract(TypedDict):
    status: Status
    allowed_operator_actions: list[str]
    blocked_operator_actions: list[str]
    required_human_actions: list[str]
    delivery_allowed: bool
    next_allowed_action: NextAction


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _missing_fields(operator_input: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if field not in operator_input or _is_blank(operator_input[field])]


def _has_active_stop_condition(stop_conditions: Any) -> bool:
    if _is_blank(stop_conditions):
        return False
    if isinstance(stop_conditions, str):
        return stop_conditions.strip() != "NONE"
    if isinstance(stop_conditions, (list, tuple, set)):
        return any(not _is_blank(item) and str(item).strip() != "NONE" for item in stop_conditions)
    return True


def _contract(
    *,
    status: Status,
    allowed: list[str],
    blocked: list[str],
    required_human: list[str],
    delivery_allowed: bool,
    next_action: NextAction,
) -> Service1OperatorHarnessV2Contract:
    return {
        "status": status,
        "allowed_operator_actions": allowed,
        "blocked_operator_actions": blocked,
        "required_human_actions": required_human,
        "delivery_allowed": delivery_allowed,
        "next_allowed_action": next_action,
    }


def build_service_1_operator_harness_v2_contract(operator_input: dict[str, Any]) -> Service1OperatorHarnessV2Contract:
    if not isinstance(operator_input, dict):
        return _contract(
            status="INVALID_INPUT",
            allowed=["block_delivery"],
            blocked=list(ALLOWED_OPERATOR_ACTIONS[:-1]),
            required_human=["provide_valid_operator_input"],
            delivery_allowed=False,
            next_action="fix_operator_input",
        )

    missing = _missing_fields(operator_input)
    if missing:
        return _contract(
            status="MISSING_REQUIRED_FIELDS",
            allowed=["block_delivery"],
            blocked=list(ALLOWED_OPERATOR_ACTIONS[:-1]),
            required_human=["complete_required_fields"],
            delivery_allowed=False,
            next_action="complete_required_fields",
        )

    action = str(operator_input["operator_requested_action"])
    if operator_input["case_folder_manifest_status"] not in READY_MANIFEST_STATUSES:
        return _contract(
            status="BLOCKED_BY_CASE_MANIFEST",
            allowed=["request_missing_evidence", "block_delivery"],
            blocked=["prepare_owner_summary", "prepare_operator_notes", "prepare_operational_xlsx_draft", "send_to_human_review", "deliver_operational_draft"],
            required_human=["repair_case_manifest"],
            delivery_allowed=False,
            next_action="repair_case_manifest",
        )

    if operator_input["delivery_manifest_audit_status"] not in PASSING_AUDIT_STATUSES or operator_input["delivery_allowed_by_audit"] is not True:
        return _contract(
            status="BLOCKED_BY_DELIVERY_AUDIT",
            allowed=["prepare_operator_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_human_review", "deliver_operational_draft"],
            required_human=["repair_delivery_audit"],
            delivery_allowed=False,
            next_action="repair_delivery_audit",
        )

    if _has_active_stop_condition(operator_input["stop_conditions"]):
        return _contract(
            status="BLOCKED_BY_STOP_CONDITION",
            allowed=["prepare_operator_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_human_review", "deliver_operational_draft"],
            required_human=["resolve_stop_conditions"],
            delivery_allowed=False,
            next_action="resolve_stop_conditions",
        )

    if operator_input["human_reviewer_present"] is not True or operator_input["human_review_status"] not in VALID_HUMAN_REVIEW_STATUSES:
        return _contract(
            status="BLOCKED_BY_MISSING_HUMAN_REVIEW",
            allowed=["request_missing_evidence", "prepare_operator_notes", "send_to_human_review", "block_delivery"],
            blocked=["prepare_owner_summary", "prepare_operational_xlsx_draft", "deliver_operational_draft"],
            required_human=["assign_human_reviewer"],
            delivery_allowed=False,
            next_action="assign_human_reviewer",
        )

    if operator_input["forbidden_claims_check"] != "PASSED":
        return _contract(
            status="BLOCKED_BY_FORBIDDEN_CLAIMS",
            allowed=["prepare_operator_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_human_review", "deliver_operational_draft"],
            required_human=["remove_forbidden_claims"],
            delivery_allowed=False,
            next_action="remove_forbidden_claims",
        )

    if action not in ALLOWED_OPERATOR_ACTIONS:
        return _contract(
            status="BLOCKED_BY_FORBIDDEN_ACTION",
            allowed=list(NON_DELIVERY_ACTIONS),
            blocked=[action, "deliver_operational_draft"],
            required_human=["request_allowed_operator_action"],
            delivery_allowed=False,
            next_action="request_allowed_operator_action",
        )

    if action == "deliver_operational_draft":
        return _contract(
            status="READY_FOR_OPERATIONAL_DRAFT_DELIVERY",
            allowed=list(ALLOWED_OPERATOR_ACTIONS),
            blocked=[],
            required_human=[],
            delivery_allowed=True,
            next_action="deliver_operational_draft",
        )

    return _contract(
        status="READY_FOR_HUMAN_REVIEW",
        allowed=list(NON_DELIVERY_ACTIONS),
        blocked=["deliver_operational_draft"],
        required_human=["complete_human_review_before_delivery"],
        delivery_allowed=False,
        next_action="send_to_human_review",
    )
