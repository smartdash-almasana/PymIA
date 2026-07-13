from __future__ import annotations

from typing import Any, Literal, TypedDict

Service1DeliveryManifestAuditStatus = Literal[
    "INVALID_INPUT",
    "MISSING_REQUIRED_FIELDS",
    "FAIL_MISSING_QA",
    "FAIL_MISSING_HUMAN_REVIEW",
    "FAIL_BLOCKED_BY_STOP_CONDITION",
    "FAIL_FORBIDDEN_CLAIM_DETECTED",
    "FAIL_REWORK_REQUIRED",
    "PASS_READY_FOR_DELIVERY",
    "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW",
]

Service1DeliveryManifestAuditNextAllowedAction = Literal[
    "fix_audit_input",
    "complete_required_fields",
    "complete_qa_checklist",
    "assign_human_reviewer",
    "resolve_stop_conditions",
    "remove_forbidden_claims",
    "rework_delivery_package",
    "deliver_operational_draft_under_human_review",
]

REQUIRED_SERVICE_1_DELIVERY_MANIFEST_AUDIT_FIELDS: tuple[str, ...] = (
    "case_id",
    "manifest_present",
    "case_family",
    "period_present",
    "operator_present",
    "human_reviewer_present",
    "input_files_listed",
    "output_files_listed",
    "xlsx_review_file_present",
    "qa_checklist_present",
    "qa_status",
    "owner_message_present",
    "operator_notes_present",
    "evidence_gap_log_present",
    "visible_differences_log_present",
    "human_review_status",
    "forbidden_claims_check",
    "stop_conditions",
    "delivery_status",
    "next_safe_action",
)

BOOLEAN_TRUE_REQUIRED_FIELDS: tuple[str, ...] = (
    "manifest_present",
    "period_present",
    "operator_present",
    "human_reviewer_present",
    "input_files_listed",
    "output_files_listed",
    "xlsx_review_file_present",
    "qa_checklist_present",
    "owner_message_present",
    "operator_notes_present",
    "evidence_gap_log_present",
    "visible_differences_log_present",
)

VALID_HUMAN_REVIEW_STATUSES: tuple[str, ...] = ("REQUIRED", "COMPLETED")
PASSED_QA_STATUS = "PASSED"
PASSED_FORBIDDEN_CLAIMS_CHECK = "PASSED"
NO_STOP_CONDITION_VALUE = "NONE"

ALLOWED_DELIVERY_STATUSES: tuple[str, ...] = (
    "READY_FOR_CLIENT_DELIVERY",
    "DELIVERED_AS_OPERATIONAL_DRAFT",
)

WARNING_KEYS: tuple[str, ...] = (
    "duplicate_payments_or_collections_present",
    "missing_master_data_exists",
    "transaction_keys_incomplete",
    "negative_amounts_or_credit_notes_present",
    "material_evidence_gaps_documented",
    "aggregate_only_due_to_missing_keys",
    "operational_draft_only",
)


class Service1DeliveryManifestAuditContractV1(TypedDict):
    status: Service1DeliveryManifestAuditStatus
    missing_fields: list[str]
    failed_gates: list[str]
    active_stop_conditions: list[str]
    delivery_allowed: bool
    human_review_required: bool
    next_allowed_action: Service1DeliveryManifestAuditNextAllowedAction


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list | tuple | set | dict):
        return len(value) == 0
    return False


def _missing_required_fields(audit_input: dict[str, Any]) -> list[str]:
    return [
        field
        for field in REQUIRED_SERVICE_1_DELIVERY_MANIFEST_AUDIT_FIELDS
        if field not in audit_input or _is_blank(audit_input[field])
    ]


def _active_stop_conditions(stop_conditions: Any) -> list[str]:
    if _is_blank(stop_conditions):
        return []
    if isinstance(stop_conditions, str):
        normalized = stop_conditions.strip()
        return [] if normalized == NO_STOP_CONDITION_VALUE else [normalized]
    if isinstance(stop_conditions, list | tuple | set):
        return [
            str(item)
            for item in stop_conditions
            if not _is_blank(item) and str(item).strip() != NO_STOP_CONDITION_VALUE
        ]
    return [str(stop_conditions)]


def _warning_flags(audit_input: dict[str, Any]) -> list[str]:
    warnings = audit_input.get("warning_flags", [])
    explicit_warning_keys = [key for key in WARNING_KEYS if audit_input.get(key) is True]
    if isinstance(warnings, str):
        listed_warnings = [] if warnings.strip() in ("", "NONE") else [warnings.strip()]
    elif isinstance(warnings, list | tuple | set):
        listed_warnings = [str(item) for item in warnings if not _is_blank(item)]
    else:
        listed_warnings = []
    return listed_warnings + explicit_warning_keys


def _failed_presence_gates(audit_input: dict[str, Any]) -> list[str]:
    return [field for field in BOOLEAN_TRUE_REQUIRED_FIELDS if audit_input.get(field) is not True]


def build_service_1_delivery_manifest_audit_contract_v1(
    audit_input: dict[str, Any],
) -> Service1DeliveryManifestAuditContractV1:
    if not isinstance(audit_input, dict):
        return {
            "status": "INVALID_INPUT",
            "missing_fields": list(REQUIRED_SERVICE_1_DELIVERY_MANIFEST_AUDIT_FIELDS),
            "failed_gates": ["audit_input_must_be_dict"],
            "active_stop_conditions": [],
            "delivery_allowed": False,
            "human_review_required": True,
            "next_allowed_action": "fix_audit_input",
        }

    missing_fields = _missing_required_fields(audit_input)
    active_stop_conditions = _active_stop_conditions(audit_input.get("stop_conditions"))
    failed_gates = _failed_presence_gates(audit_input)

    qa_is_valid = (
        audit_input.get("qa_checklist_present") is True
        and audit_input.get("qa_status") == PASSED_QA_STATUS
    )
    human_review_is_valid = (
        audit_input.get("human_reviewer_present") is True
        and audit_input.get("human_review_status") in VALID_HUMAN_REVIEW_STATUSES
    )
    forbidden_claims_check_passed = audit_input.get("forbidden_claims_check") == PASSED_FORBIDDEN_CLAIMS_CHECK
    delivery_status_is_allowed = audit_input.get("delivery_status") in ALLOWED_DELIVERY_STATUSES
    next_safe_action_present = not _is_blank(audit_input.get("next_safe_action"))
    warning_flags = _warning_flags(audit_input)

    if missing_fields:
        status: Service1DeliveryManifestAuditStatus = "MISSING_REQUIRED_FIELDS"
        next_allowed_action: Service1DeliveryManifestAuditNextAllowedAction = "complete_required_fields"
    elif not qa_is_valid:
        status = "FAIL_MISSING_QA"
        next_allowed_action = "complete_qa_checklist"
        if "qa_checklist_present" not in failed_gates:
            failed_gates.append("qa_checklist_or_status")
    elif not human_review_is_valid:
        status = "FAIL_MISSING_HUMAN_REVIEW"
        next_allowed_action = "assign_human_reviewer"
        if "human_reviewer_present" not in failed_gates:
            failed_gates.append("human_review_gate")
    elif active_stop_conditions:
        status = "FAIL_BLOCKED_BY_STOP_CONDITION"
        next_allowed_action = "resolve_stop_conditions"
        failed_gates.append("stop_conditions")
    elif not forbidden_claims_check_passed:
        status = "FAIL_FORBIDDEN_CLAIM_DETECTED"
        next_allowed_action = "remove_forbidden_claims"
        failed_gates.append("forbidden_claims_check")
    elif not delivery_status_is_allowed or not next_safe_action_present or failed_gates:
        status = "FAIL_REWORK_REQUIRED"
        next_allowed_action = "rework_delivery_package"
        if not delivery_status_is_allowed:
            failed_gates.append("delivery_status")
        if not next_safe_action_present:
            failed_gates.append("next_safe_action")
    elif warning_flags:
        status = "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW"
        next_allowed_action = "deliver_operational_draft_under_human_review"
        failed_gates = []
    else:
        status = "PASS_READY_FOR_DELIVERY"
        next_allowed_action = "deliver_operational_draft_under_human_review"
        failed_gates = []

    delivery_allowed = status in (
        "PASS_READY_FOR_DELIVERY",
        "PASS_WITH_WARNINGS_REQUIRES_HUMAN_REVIEW",
    )
    human_review_required = audit_input.get("human_review_status") != "COMPLETED"

    return {
        "status": status,
        "missing_fields": missing_fields,
        "failed_gates": failed_gates,
        "active_stop_conditions": active_stop_conditions,
        "delivery_allowed": delivery_allowed,
        "human_review_required": human_review_required,
        "next_allowed_action": next_allowed_action,
    }
