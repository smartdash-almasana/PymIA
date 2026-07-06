from __future__ import annotations

from typing import Any, Literal, TypedDict

Status = Literal[
    "INVALID_INPUT",
    "MISSING_REQUIRED_FIELDS",
    "BLOCKED_BY_CASE_MANIFEST",
    "BLOCKED_BY_DELIVERY_AUDIT",
    "BLOCKED_BY_STOP_CONDITION",
    "BLOCKED_BY_MISSING_RELEASE_REVIEW",
    "BLOCKED_BY_FORBIDDEN_CLAIMS",
    "BLOCKED_BY_FORBIDDEN_ACTION",
    "READY_FOR_OWNER_OR_RESPONSIBLE_REVIEW",
    "READY_FOR_OPERATIONAL_DRAFT_DELIVERY",
]

NextAction = Literal[
    "fix_release_input",
    "complete_required_fields",
    "repair_case_manifest",
    "repair_delivery_audit",
    "resolve_stop_conditions",
    "assign_release_responsible",
    "remove_forbidden_claims",
    "request_allowed_release_action",
    "send_to_owner_or_responsible_review",
    "deliver_operational_draft",
]

REQUIRED_FIELDS: tuple[str, ...] = (
    "case_folder_manifest_status",
    "delivery_manifest_audit_status",
    "requested_release_action",
    "release_responsible_present",
    "release_review_status",
    "forbidden_claims_check",
    "stop_conditions",
    "delivery_allowed_by_audit",
)

READY_MANIFEST_STATUSES = ("READY_FOR_QA", "VALID")
PASSING_AUDIT_STATUSES = ("PASS_READY_FOR_DELIVERY", "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW")
VALID_RELEASE_REVIEW_STATUSES = ("REQUIRED", "COMPLETED")
ALLOWED_RELEASE_ACTIONS: tuple[str, ...] = (
    "request_missing_evidence",
    "prepare_owner_summary",
    "prepare_delivery_notes",
    "prepare_operational_xlsx_draft",
    "send_to_owner_or_responsible_review",
    "deliver_operational_draft",
    "block_delivery",
)
NON_DELIVERY_RELEASE_ACTIONS = [
    "request_missing_evidence",
    "prepare_owner_summary",
    "prepare_delivery_notes",
    "prepare_operational_xlsx_draft",
    "send_to_owner_or_responsible_review",
    "block_delivery",
]


class Service1OwnerReleaseActionGateV1(TypedDict):
    status: Status
    allowed_release_actions: list[str]
    blocked_release_actions: list[str]
    required_responsible_actions: list[str]
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


def _missing_fields(release_input: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if field not in release_input or _is_blank(release_input[field])]


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
    required_responsible: list[str],
    delivery_allowed: bool,
    next_action: NextAction,
) -> Service1OwnerReleaseActionGateV1:
    return {
        "status": status,
        "allowed_release_actions": allowed,
        "blocked_release_actions": blocked,
        "required_responsible_actions": required_responsible,
        "delivery_allowed": delivery_allowed,
        "next_allowed_action": next_action,
    }


def build_service_1_owner_release_action_gate_v1(release_input: dict[str, Any]) -> Service1OwnerReleaseActionGateV1:
    if not isinstance(release_input, dict):
        return _contract(
            status="INVALID_INPUT",
            allowed=["block_delivery"],
            blocked=list(ALLOWED_RELEASE_ACTIONS[:-1]),
            required_responsible=["provide_valid_release_input"],
            delivery_allowed=False,
            next_action="fix_release_input",
        )

    missing = _missing_fields(release_input)
    if missing:
        return _contract(
            status="MISSING_REQUIRED_FIELDS",
            allowed=["block_delivery"],
            blocked=list(ALLOWED_RELEASE_ACTIONS[:-1]),
            required_responsible=["complete_required_fields"],
            delivery_allowed=False,
            next_action="complete_required_fields",
        )

    action = str(release_input["requested_release_action"])
    if release_input["case_folder_manifest_status"] not in READY_MANIFEST_STATUSES:
        return _contract(
            status="BLOCKED_BY_CASE_MANIFEST",
            allowed=["request_missing_evidence", "block_delivery"],
            blocked=["prepare_owner_summary", "prepare_delivery_notes", "prepare_operational_xlsx_draft", "send_to_owner_or_responsible_review", "deliver_operational_draft"],
            required_responsible=["repair_case_manifest"],
            delivery_allowed=False,
            next_action="repair_case_manifest",
        )

    if release_input["delivery_manifest_audit_status"] not in PASSING_AUDIT_STATUSES or release_input["delivery_allowed_by_audit"] is not True:
        return _contract(
            status="BLOCKED_BY_DELIVERY_AUDIT",
            allowed=["prepare_delivery_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_owner_or_responsible_review", "deliver_operational_draft"],
            required_responsible=["repair_delivery_audit"],
            delivery_allowed=False,
            next_action="repair_delivery_audit",
        )

    if _has_active_stop_condition(release_input["stop_conditions"]):
        return _contract(
            status="BLOCKED_BY_STOP_CONDITION",
            allowed=["prepare_delivery_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_owner_or_responsible_review", "deliver_operational_draft"],
            required_responsible=["resolve_stop_conditions"],
            delivery_allowed=False,
            next_action="resolve_stop_conditions",
        )

    if release_input["release_responsible_present"] is not True or release_input["release_review_status"] not in VALID_RELEASE_REVIEW_STATUSES:
        return _contract(
            status="BLOCKED_BY_MISSING_RELEASE_REVIEW",
            allowed=["request_missing_evidence", "prepare_delivery_notes", "send_to_owner_or_responsible_review", "block_delivery"],
            blocked=["prepare_owner_summary", "prepare_operational_xlsx_draft", "deliver_operational_draft"],
            required_responsible=["assign_release_responsible"],
            delivery_allowed=False,
            next_action="assign_release_responsible",
        )

    if release_input["forbidden_claims_check"] != "PASSED":
        return _contract(
            status="BLOCKED_BY_FORBIDDEN_CLAIMS",
            allowed=["prepare_delivery_notes", "block_delivery"],
            blocked=["request_missing_evidence", "prepare_owner_summary", "prepare_operational_xlsx_draft", "send_to_owner_or_responsible_review", "deliver_operational_draft"],
            required_responsible=["remove_forbidden_claims"],
            delivery_allowed=False,
            next_action="remove_forbidden_claims",
        )

    if action not in ALLOWED_RELEASE_ACTIONS:
        return _contract(
            status="BLOCKED_BY_FORBIDDEN_ACTION",
            allowed=list(NON_DELIVERY_RELEASE_ACTIONS),
            blocked=[action, "deliver_operational_draft"],
            required_responsible=["request_allowed_release_action"],
            delivery_allowed=False,
            next_action="request_allowed_release_action",
        )

    if action == "deliver_operational_draft":
        return _contract(
            status="READY_FOR_OPERATIONAL_DRAFT_DELIVERY",
            allowed=list(ALLOWED_RELEASE_ACTIONS),
            blocked=[],
            required_responsible=[],
            delivery_allowed=True,
            next_action="deliver_operational_draft",
        )

    return _contract(
        status="READY_FOR_OWNER_OR_RESPONSIBLE_REVIEW",
        allowed=list(NON_DELIVERY_RELEASE_ACTIONS),
        blocked=["deliver_operational_draft"],
        required_responsible=["complete_release_review_before_delivery"],
        delivery_allowed=False,
        next_action="send_to_owner_or_responsible_review",
    )
