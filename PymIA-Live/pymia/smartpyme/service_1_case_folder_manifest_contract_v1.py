from __future__ import annotations

from typing import Any, Literal, TypedDict

Service1CaseFolderManifestContractStatus = Literal[
    "VALID",
    "INVALID_INPUT",
    "MISSING_REQUIRED_FIELDS",
    "BLOCKED_BY_STOP_CONDITION",
    "BLOCKED_BY_MISSING_HUMAN_REVIEWER",
    "BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK",
    "READY_FOR_QA",
]

Service1CaseFolderManifestNextAllowedAction = Literal[
    "fix_manifest_input",
    "complete_required_fields",
    "assign_human_reviewer",
    "resolve_stop_conditions",
    "run_forbidden_claims_check",
    "send_to_qa",
]

REQUIRED_SERVICE_1_CASE_FOLDER_MANIFEST_FIELDS: tuple[str, ...] = (
    "case_id",
    "client_alias",
    "case_family",
    "period",
    "operator",
    "human_reviewer",
    "intake_status",
    "accepted_scope",
    "input_files",
    "human_review_status",
    "forbidden_claims_check",
    "stop_conditions",
    "delivery_status",
    "next_safe_action",
)

VALID_HUMAN_REVIEW_STATUSES: tuple[str, ...] = ("REQUIRED", "COMPLETED")
NO_STOP_CONDITION_VALUE = "NONE"
PASSED_FORBIDDEN_CLAIMS_CHECK_VALUE = "PASSED"


class Service1CaseFolderManifestContractV1(TypedDict):
    status: Service1CaseFolderManifestContractStatus
    missing_fields: list[str]
    active_stop_conditions: list[str]
    human_review_required: bool
    forbidden_claims_check_status: str
    delivery_allowed: bool
    next_allowed_action: Service1CaseFolderManifestNextAllowedAction


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list | tuple | set | dict):
        return len(value) == 0
    return False


def _missing_required_fields(manifest_input: dict[str, Any]) -> list[str]:
    return [
        field
        for field in REQUIRED_SERVICE_1_CASE_FOLDER_MANIFEST_FIELDS
        if field not in manifest_input or _is_blank(manifest_input[field])
    ]


def _active_stop_conditions(stop_conditions: Any) -> list[str]:
    if _is_blank(stop_conditions):
        return []
    if isinstance(stop_conditions, str):
        normalized = stop_conditions.strip()
        return [] if normalized == NO_STOP_CONDITION_VALUE else [normalized]
    if isinstance(stop_conditions, list | tuple | set):
        return [str(item) for item in stop_conditions if not _is_blank(item) and str(item).strip() != NO_STOP_CONDITION_VALUE]
    return [str(stop_conditions)]


def _has_valid_human_reviewer(manifest_input: dict[str, Any]) -> bool:
    return not _is_blank(manifest_input.get("human_reviewer")) and manifest_input.get(
        "human_review_status"
    ) in VALID_HUMAN_REVIEW_STATUSES


def build_service_1_case_folder_manifest_contract_v1(
    manifest_input: dict[str, Any],
) -> Service1CaseFolderManifestContractV1:
    if not isinstance(manifest_input, dict):
        return {
            "status": "INVALID_INPUT",
            "missing_fields": list(REQUIRED_SERVICE_1_CASE_FOLDER_MANIFEST_FIELDS),
            "active_stop_conditions": [],
            "human_review_required": True,
            "forbidden_claims_check_status": "NOT_EVALUATED",
            "delivery_allowed": False,
            "next_allowed_action": "fix_manifest_input",
        }

    missing_fields = _missing_required_fields(manifest_input)
    active_stop_conditions = _active_stop_conditions(manifest_input.get("stop_conditions"))
    forbidden_claims_check_status = str(manifest_input.get("forbidden_claims_check", "NOT_EVALUATED"))
    has_valid_human_reviewer = _has_valid_human_reviewer(manifest_input)
    human_review_required = not has_valid_human_reviewer
    forbidden_claims_check_passed = forbidden_claims_check_status == PASSED_FORBIDDEN_CLAIMS_CHECK_VALUE

    if missing_fields:
        status: Service1CaseFolderManifestContractStatus = "MISSING_REQUIRED_FIELDS"
        next_allowed_action: Service1CaseFolderManifestNextAllowedAction = "complete_required_fields"
    elif not has_valid_human_reviewer:
        status = "BLOCKED_BY_MISSING_HUMAN_REVIEWER"
        next_allowed_action = "assign_human_reviewer"
    elif active_stop_conditions:
        status = "BLOCKED_BY_STOP_CONDITION"
        next_allowed_action = "resolve_stop_conditions"
    elif not forbidden_claims_check_passed:
        status = "BLOCKED_BY_FORBIDDEN_CLAIMS_CHECK"
        next_allowed_action = "run_forbidden_claims_check"
    else:
        status = "READY_FOR_QA"
        next_allowed_action = "send_to_qa"

    delivery_allowed = (
        not missing_fields
        and not active_stop_conditions
        and forbidden_claims_check_passed
        and has_valid_human_reviewer
    )

    return {
        "status": status,
        "missing_fields": missing_fields,
        "active_stop_conditions": active_stop_conditions,
        "human_review_required": human_review_required,
        "forbidden_claims_check_status": forbidden_claims_check_status,
        "delivery_allowed": delivery_allowed,
        "next_allowed_action": next_allowed_action,
    }
