from __future__ import annotations

from typing import Any, Literal, TypedDict

from pymia.smartpyme.service_1_web_test_route_registry_v1 import (
    assert_service_1_web_test_route_allowed_v1,
)

RunSpecStatus = Literal[
    "READY_FOR_SANDBOX_REHEARSAL",
    "INVALID_INPUT",
    "BLOCKED_ROUTE",
    "BLOCKED_DATA_MODE",
]

RunState = Literal[
    "CREATED",
    "ROUTE_CONFIRMED",
    "INPUT_CONFIRMED",
    "ARTIFACTS_EXPECTED",
    "OPERATOR_REVIEW_REQUIRED",
    "CLOSED_AS_SANDBOX_REHEARSAL",
    "BLOCKED",
]

ReviewDecision = Literal[
    "PENDING_REVIEW",
    "CLOSE_SANDBOX_REHEARSAL",
    "BLOCK_RUN",
    "REQUEST_MORE_EVIDENCE",
]

REQUIRED_WEB_TEST_RUN_SPEC_FIELDS: tuple[str, ...] = (
    "status",
    "run_id",
    "route_id",
    "route_label",
    "data_mode",
    "operator_label",
    "case_label",
    "state",
    "review_decision",
    "human_review_required",
    "runtime_authorized",
    "production_allowed",
    "expected_artifacts",
    "forbidden_claims",
    "blocked_reason",
    "next_allowed_action",
)

ALLOWED_INITIAL_RUN_STATES: tuple[RunState, ...] = (
    "CREATED",
    "ROUTE_CONFIRMED",
    "INPUT_CONFIRMED",
    "ARTIFACTS_EXPECTED",
    "OPERATOR_REVIEW_REQUIRED",
)

ALLOWED_REVIEW_DECISIONS: tuple[ReviewDecision, ...] = (
    "PENDING_REVIEW",
    "CLOSE_SANDBOX_REHEARSAL",
    "BLOCK_RUN",
    "REQUEST_MORE_EVIDENCE",
)


class Service1WebTestRunSpecV1(TypedDict):
    status: RunSpecStatus
    run_id: str | None
    route_id: str | None
    route_label: str
    data_mode: str
    operator_label: str
    case_label: str
    state: RunState
    review_decision: ReviewDecision
    human_review_required: bool
    runtime_authorized: bool
    production_allowed: bool
    expected_artifacts: list[str]
    forbidden_claims: list[str]
    blocked_reason: str
    next_allowed_action: str


def build_service_1_web_test_run_spec_v1(run_input: dict[str, Any]) -> Service1WebTestRunSpecV1:
    if not isinstance(run_input, dict):
        return _blocked_result(
            status="INVALID_INPUT",
            blocked_reason="run_input_must_be_dict",
            next_allowed_action="provide_run_input_dict",
        )

    run_id = _required_text(run_input.get("run_id"))
    if run_id is None:
        return _blocked_result(
            status="INVALID_INPUT",
            blocked_reason="missing_run_id",
            next_allowed_action="provide_run_id",
        )

    route_id = _required_text(run_input.get("route_id"))
    if route_id is None:
        return _blocked_result(
            status="INVALID_INPUT",
            run_id=run_id,
            blocked_reason="missing_route_id",
            next_allowed_action="select_allowed_route_id",
        )

    try:
        route = assert_service_1_web_test_route_allowed_v1(route_id)
    except ValueError:
        return _blocked_result(
            status="BLOCKED_ROUTE",
            run_id=run_id,
            route_id=route_id,
            blocked_reason="blocked_or_unknown_route",
            next_allowed_action="select_allowed_service_1_web_test_route",
        )

    data_mode = _required_text(run_input.get("data_mode")) or "SYNTHETIC_FIXTURE"
    if data_mode not in route["allowed_data_modes"] or data_mode in route["blocked_data_modes"]:
        return _blocked_result(
            status="BLOCKED_DATA_MODE",
            run_id=run_id,
            route_id=route["route_id"],
            route_label=route["label"],
            data_mode=data_mode,
            blocked_reason="data_mode_not_allowed_for_route",
            next_allowed_action="select_allowed_data_mode",
            forbidden_claims=route["forbidden_claims"],
        )

    operator_label = _required_text(run_input.get("operator_label")) or "internal_operator"
    case_label = _required_text(run_input.get("case_label")) or "sandbox_rehearsal_case"

    return {
        "status": "READY_FOR_SANDBOX_REHEARSAL",
        "run_id": run_id,
        "route_id": route["route_id"],
        "route_label": route["label"],
        "data_mode": data_mode,
        "operator_label": operator_label,
        "case_label": case_label,
        "state": "OPERATOR_REVIEW_REQUIRED",
        "review_decision": "PENDING_REVIEW",
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
        "expected_artifacts": list(route["expected_artifacts"]),
        "forbidden_claims": list(route["forbidden_claims"]),
        "blocked_reason": "",
        "next_allowed_action": "perform_sandbox_rehearsal_under_operator_review",
    }


def close_service_1_web_test_run_spec_v1(
    run_spec: Service1WebTestRunSpecV1,
    *,
    review_decision: ReviewDecision,
) -> Service1WebTestRunSpecV1:
    if review_decision not in ALLOWED_REVIEW_DECISIONS:
        raise ValueError(f"Unsupported review decision: {review_decision}")

    updated = _copy_run_spec(run_spec)
    updated["review_decision"] = review_decision

    if run_spec["status"] != "READY_FOR_SANDBOX_REHEARSAL":
        updated["state"] = "BLOCKED"
        updated["next_allowed_action"] = "fix_blocked_run_before_review"
        return updated

    if review_decision == "CLOSE_SANDBOX_REHEARSAL":
        updated["state"] = "CLOSED_AS_SANDBOX_REHEARSAL"
        updated["next_allowed_action"] = "archive_sandbox_rehearsal_evidence"
        return updated

    if review_decision == "BLOCK_RUN":
        updated["state"] = "BLOCKED"
        updated["blocked_reason"] = "operator_blocked_run"
        updated["next_allowed_action"] = "record_block_reason_and_stop"
        return updated

    if review_decision == "REQUEST_MORE_EVIDENCE":
        updated["state"] = "OPERATOR_REVIEW_REQUIRED"
        updated["blocked_reason"] = "more_evidence_required"
        updated["next_allowed_action"] = "request_more_evidence_before_closing"
        return updated

    updated["state"] = "OPERATOR_REVIEW_REQUIRED"
    updated["next_allowed_action"] = "complete_human_review_checklist"
    return updated


def _required_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text


def _blocked_result(
    *,
    status: RunSpecStatus,
    blocked_reason: str,
    next_allowed_action: str,
    run_id: str | None = None,
    route_id: str | None = None,
    route_label: str = "",
    data_mode: str = "",
    forbidden_claims: list[str] | None = None,
) -> Service1WebTestRunSpecV1:
    return {
        "status": status,
        "run_id": run_id,
        "route_id": route_id,
        "route_label": route_label,
        "data_mode": data_mode,
        "operator_label": "",
        "case_label": "",
        "state": "BLOCKED",
        "review_decision": "PENDING_REVIEW",
        "human_review_required": True,
        "runtime_authorized": False,
        "production_allowed": False,
        "expected_artifacts": [],
        "forbidden_claims": list(forbidden_claims or []),
        "blocked_reason": blocked_reason,
        "next_allowed_action": next_allowed_action,
    }


def _copy_run_spec(run_spec: Service1WebTestRunSpecV1) -> Service1WebTestRunSpecV1:
    return {
        "status": run_spec["status"],
        "run_id": run_spec["run_id"],
        "route_id": run_spec["route_id"],
        "route_label": run_spec["route_label"],
        "data_mode": run_spec["data_mode"],
        "operator_label": run_spec["operator_label"],
        "case_label": run_spec["case_label"],
        "state": run_spec["state"],
        "review_decision": run_spec["review_decision"],
        "human_review_required": bool(run_spec["human_review_required"]),
        "runtime_authorized": bool(run_spec["runtime_authorized"]),
        "production_allowed": bool(run_spec["production_allowed"]),
        "expected_artifacts": list(run_spec["expected_artifacts"]),
        "forbidden_claims": list(run_spec["forbidden_claims"]),
        "blocked_reason": run_spec["blocked_reason"],
        "next_allowed_action": run_spec["next_allowed_action"],
    }
