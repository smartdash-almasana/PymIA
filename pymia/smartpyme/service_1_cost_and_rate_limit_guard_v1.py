from __future__ import annotations

from typing import Final, Literal, TypedDict

SCHEMA_VERSION: Final[str] = "S1_COST_AND_RATE_LIMIT_GUARD_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
GUARD_KIND: Final[str] = "COST_AND_RATE_LIMIT_GUARD_CANDIDATE"
SESSION_KIND: Final[str] = "SAAS_CASE_SESSION_CANDIDATE"

SESSION_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "runtime_authorized": "session_runtime_authorized_must_be_false",
    "job_authorized": "session_job_authorized_must_be_false",
    "file_upload_authorized": "session_file_upload_authorized_must_be_false",
    "api_exposed": "session_api_exposed_must_be_false",
}

FORBIDDEN_INPUT_FLAG_REASON_BY_NAME: Final[dict[str, str]] = {
    "correction_applied": "correction_applied_must_be_false",
    "cost_charge_authorized": "cost_charge_authorized_must_be_false",
    "rate_limit_mutation_authorized": "rate_limit_mutation_authorized_must_be_false",
    "billing_authorized": "billing_authorized_must_be_false",
    "storage_write_authorized": "storage_write_authorized_must_be_false",
    "db_authorized": "db_authorized_must_be_false",
    "worker_authorized": "worker_authorized_must_be_false",
    "queue_authorized": "queue_authorized_must_be_false",
    "scheduler_authorized": "scheduler_authorized_must_be_false",
    "pipeline_authorized": "pipeline_authorized_must_be_false",
    "runner_authorized": "runner_authorized_must_be_false",
    "llm_authorized": "llm_authorized_must_be_false",
    "pydantic_ai_authorized": "pydantic_ai_authorized_must_be_false",
    "mutation_authorized": "mutation_authorized_must_be_false",
    "runtime_authorized": "runtime_authorized_must_be_false",
    "api_exposed": "api_exposed_must_be_false",
}

CostAndRateLimitGuardStatusV1 = Literal[
    "COST_AND_RATE_LIMIT_GUARD_CANDIDATE_READY",
    "BLOCKED_MISSING_SESSION",
    "BLOCKED_INVALID_SESSION",
    "BLOCKED_INVALID_LIMIT_INPUT",
    "BLOCKED_COST_LIMIT_EXCEEDED",
    "BLOCKED_RATE_LIMIT_EXCEEDED",
    "BLOCKED_BUDGET_EXHAUSTED",
    "BLOCKED_UNSAFE_FLAGS",
    "UNKNOWN",
]


class Service1CostAndRateLimitGuardInputV1(TypedDict):
    saas_case_session_candidate: dict[str, object] | None
    tenant_ref: str
    owner_ref: str
    case_ref: str
    estimated_cost_units: int
    max_cost_units: int
    current_window_request_count: int
    max_window_request_count: int
    current_budget_used_units: int
    max_budget_units: int
    requested_operation_kind: str
    notes: list[str]


class Service1CostAndRateLimitGuardCandidateV1(TypedDict):
    guard_kind: Literal["COST_AND_RATE_LIMIT_GUARD_CANDIDATE"]
    tenant_ref: str
    owner_ref: str
    case_ref: str
    service_name: Literal["SERVICE_1"]
    source_session_ref: str
    requested_operation_kind: str
    estimated_cost_units: int
    max_cost_units: int
    current_window_request_count: int
    max_window_request_count: int
    current_budget_used_units: int
    max_budget_units: int
    projected_budget_used_units: int
    remaining_cost_headroom_units: int
    remaining_window_request_capacity: int
    remaining_budget_units: int
    cost_limit_passed: Literal[True]
    rate_limit_passed: Literal[True]
    budget_limit_passed: Literal[True]
    cost_charge_authorized: Literal[False]
    rate_limit_mutation_authorized: Literal[False]
    billing_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    scheduler_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]


class Service1CostAndRateLimitGuardResultV1(TypedDict):
    schema_version: str
    service_name: str
    status: CostAndRateLimitGuardStatusV1
    cost_and_rate_limit_guard_candidate: Service1CostAndRateLimitGuardCandidateV1 | None
    blocked_reason: str | None
    cost_charge_authorized: Literal[False]
    rate_limit_mutation_authorized: Literal[False]
    billing_authorized: Literal[False]
    storage_write_authorized: Literal[False]
    db_authorized: Literal[False]
    worker_authorized: Literal[False]
    queue_authorized: Literal[False]
    scheduler_authorized: Literal[False]
    pipeline_authorized: Literal[False]
    runner_authorized: Literal[False]
    llm_authorized: Literal[False]
    pydantic_ai_authorized: Literal[False]
    mutation_authorized: Literal[False]
    runtime_authorized: Literal[False]
    api_exposed: Literal[False]
    notes: list[str]


def build_service_1_cost_and_rate_limit_guard_v1(
    guard_input: Service1CostAndRateLimitGuardInputV1,
) -> Service1CostAndRateLimitGuardResultV1:
    """Validate deterministic cost/rate/budget limits for Servicio 1 candidates.

    This guard does not mutate counters, charge billing, execute real rate
    limiting, write persistence, or authorize runtime behavior.
    """
    session = guard_input.get("saas_case_session_candidate")
    if session is None:
        return _result(
            status="BLOCKED_MISSING_SESSION",
            blocked_reason="saas_case_session_candidate_required",
            notes=_notes(guard_input.get("notes"), "Cost and rate limit guard requires a SaaS case session candidate."),
        )
    if not isinstance(session, dict) or not session:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason="saas_case_session_candidate_invalid",
            notes=_notes(guard_input.get("notes"), "SaaS case session candidate is invalid for cost and rate guard."),
        )

    session_validation_reason = _validate_session(session)
    if session_validation_reason is not None:
        return _result(
            status="BLOCKED_INVALID_SESSION",
            blocked_reason=session_validation_reason,
            notes=_notes(guard_input.get("notes"), "SaaS case session candidate failed cost/rate anchor validation."),
        )

    tenant_ref = _clean_required_ref(guard_input.get("tenant_ref"))
    if tenant_ref is None:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="tenant_ref_required",
            notes=_notes(guard_input.get("notes"), "Cost and rate limit guard requires tenant_ref."),
        )

    owner_ref = _clean_required_ref(guard_input.get("owner_ref"))
    if owner_ref is None:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="owner_ref_required",
            notes=_notes(guard_input.get("notes"), "Cost and rate limit guard requires owner_ref."),
        )
    session_owner_ref = str(session["owner_ref"]).strip()
    if owner_ref != session_owner_ref:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="owner_ref_must_match_session",
            notes=_notes(guard_input.get("notes"), "owner_ref must match the SaaS case session candidate."),
        )

    case_ref = _clean_required_ref(guard_input.get("case_ref"))
    if case_ref is None:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="case_ref_required",
            notes=_notes(guard_input.get("notes"), "Cost and rate limit guard requires case_ref."),
        )
    session_case_ref = str(session["case_ref"]).strip()
    if case_ref != session_case_ref:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="case_ref_must_match_session",
            notes=_notes(guard_input.get("notes"), "case_ref must match the SaaS case session candidate."),
        )

    requested_operation_kind = _clean_required_ref(guard_input.get("requested_operation_kind"))
    if requested_operation_kind is None:
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason="requested_operation_kind_required",
            notes=_notes(guard_input.get("notes"), "Cost and rate limit guard requires requested_operation_kind."),
        )

    estimated_cost_units = _validate_non_negative_int(
        guard_input.get("estimated_cost_units"),
        "estimated_cost_units_must_be_non_negative_int",
    )
    if isinstance(estimated_cost_units, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=estimated_cost_units,
            notes=_notes(guard_input.get("notes"), "estimated_cost_units must be a non-negative integer."),
        )

    max_cost_units = _validate_positive_int(
        guard_input.get("max_cost_units"),
        "max_cost_units_must_be_positive_int",
    )
    if isinstance(max_cost_units, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=max_cost_units,
            notes=_notes(guard_input.get("notes"), "max_cost_units must be a positive integer."),
        )

    current_window_request_count = _validate_non_negative_int(
        guard_input.get("current_window_request_count"),
        "current_window_request_count_must_be_non_negative_int",
    )
    if isinstance(current_window_request_count, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=current_window_request_count,
            notes=_notes(guard_input.get("notes"), "current_window_request_count must be a non-negative integer."),
        )

    max_window_request_count = _validate_positive_int(
        guard_input.get("max_window_request_count"),
        "max_window_request_count_must_be_positive_int",
    )
    if isinstance(max_window_request_count, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=max_window_request_count,
            notes=_notes(guard_input.get("notes"), "max_window_request_count must be a positive integer."),
        )

    current_budget_used_units = _validate_non_negative_int(
        guard_input.get("current_budget_used_units"),
        "current_budget_used_units_must_be_non_negative_int",
    )
    if isinstance(current_budget_used_units, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=current_budget_used_units,
            notes=_notes(guard_input.get("notes"), "current_budget_used_units must be a non-negative integer."),
        )

    max_budget_units = _validate_positive_int(
        guard_input.get("max_budget_units"),
        "max_budget_units_must_be_positive_int",
    )
    if isinstance(max_budget_units, str):
        return _result(
            status="BLOCKED_INVALID_LIMIT_INPUT",
            blocked_reason=max_budget_units,
            notes=_notes(guard_input.get("notes"), "max_budget_units must be a positive integer."),
        )

    unsafe_flag_reason = _unsafe_flag_reason(guard_input)
    if unsafe_flag_reason is not None:
        return _result(
            status="BLOCKED_UNSAFE_FLAGS",
            blocked_reason=unsafe_flag_reason,
            notes=_notes(guard_input.get("notes"), "Unsafe authority or correction flag detected in cost/rate guard input."),
        )

    if estimated_cost_units > max_cost_units:
        return _result(
            status="BLOCKED_COST_LIMIT_EXCEEDED",
            blocked_reason="estimated_cost_units_exceeds_max_cost_units",
            notes=_notes(guard_input.get("notes"), "estimated_cost_units exceeds max_cost_units."),
        )

    if current_window_request_count >= max_window_request_count:
        return _result(
            status="BLOCKED_RATE_LIMIT_EXCEEDED",
            blocked_reason="current_window_request_count_exceeds_or_meets_limit",
            notes=_notes(guard_input.get("notes"), "current_window_request_count exceeds or meets max_window_request_count."),
        )

    projected_budget_used_units = current_budget_used_units + estimated_cost_units
    if projected_budget_used_units > max_budget_units:
        return _result(
            status="BLOCKED_BUDGET_EXHAUSTED",
            blocked_reason="estimated_budget_charge_exceeds_max_budget_units",
            notes=_notes(guard_input.get("notes"), "Projected budget usage exceeds max_budget_units."),
        )

    source_session_ref = _source_session_ref(session)
    candidate: Service1CostAndRateLimitGuardCandidateV1 = {
        "guard_kind": GUARD_KIND,
        "tenant_ref": tenant_ref,
        "owner_ref": owner_ref,
        "case_ref": case_ref,
        "service_name": SERVICE_NAME,
        "source_session_ref": source_session_ref,
        "requested_operation_kind": requested_operation_kind,
        "estimated_cost_units": estimated_cost_units,
        "max_cost_units": max_cost_units,
        "current_window_request_count": current_window_request_count,
        "max_window_request_count": max_window_request_count,
        "current_budget_used_units": current_budget_used_units,
        "max_budget_units": max_budget_units,
        "projected_budget_used_units": projected_budget_used_units,
        "remaining_cost_headroom_units": max_cost_units - estimated_cost_units,
        "remaining_window_request_capacity": max_window_request_count - current_window_request_count,
        "remaining_budget_units": max_budget_units - projected_budget_used_units,
        "cost_limit_passed": True,
        "rate_limit_passed": True,
        "budget_limit_passed": True,
        "cost_charge_authorized": False,
        "rate_limit_mutation_authorized": False,
        "billing_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
    }

    return _result(
        status="COST_AND_RATE_LIMIT_GUARD_CANDIDATE_READY",
        cost_and_rate_limit_guard_candidate=candidate,
        notes=_notes(guard_input.get("notes"), "Cost and rate limit guard candidate created without charging, mutation, or runtime authority."),
    )


def _validate_session(session: dict[str, object]) -> str | None:
    if session.get("session_kind") != SESSION_KIND:
        return "session_kind_must_be_saas_case_session_candidate"
    if session.get("service_name") != SERVICE_NAME:
        return "session_service_name_must_be_service_1"
    if _clean_required_ref(session.get("owner_ref")) is None:
        return "session_owner_ref_required"
    if _clean_required_ref(session.get("case_ref")) is None:
        return "session_case_ref_required"
    for flag_name, reason in SESSION_FLAG_REASON_BY_NAME.items():
        if session.get(flag_name) is not False:
            return reason
    return None


def _validate_non_negative_int(value: object, reason: str) -> int | str:
    if not isinstance(value, int) or value < 0:
        return reason
    return value


def _validate_positive_int(value: object, reason: str) -> int | str:
    if not isinstance(value, int) or value <= 0:
        return reason
    return value


def _unsafe_flag_reason(values: dict[str, object]) -> str | None:
    for flag_name, reason in FORBIDDEN_INPUT_FLAG_REASON_BY_NAME.items():
        if flag_name in values and values.get(flag_name) is not False:
            return reason
    return None


def _source_session_ref(session: dict[str, object]) -> str:
    for key in ("session_ref", "case_ref"):
        value = session.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "saas_case_session:unknown"


def _clean_required_ref(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def _notes(values: object, extra_note: str) -> list[str]:
    cleaned_notes: list[str] = []
    if isinstance(values, list):
        cleaned_notes = [value for value in values if isinstance(value, str) and value.strip()]
    return [*cleaned_notes, extra_note]


def _result(
    *,
    status: CostAndRateLimitGuardStatusV1,
    cost_and_rate_limit_guard_candidate: Service1CostAndRateLimitGuardCandidateV1 | None = None,
    blocked_reason: str | None = None,
    notes: list[str] | None = None,
) -> Service1CostAndRateLimitGuardResultV1:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": status,
        "cost_and_rate_limit_guard_candidate": cost_and_rate_limit_guard_candidate,
        "blocked_reason": blocked_reason,
        "cost_charge_authorized": False,
        "rate_limit_mutation_authorized": False,
        "billing_authorized": False,
        "storage_write_authorized": False,
        "db_authorized": False,
        "worker_authorized": False,
        "queue_authorized": False,
        "scheduler_authorized": False,
        "pipeline_authorized": False,
        "runner_authorized": False,
        "llm_authorized": False,
        "pydantic_ai_authorized": False,
        "mutation_authorized": False,
        "runtime_authorized": False,
        "api_exposed": False,
        "notes": list(notes or []),
    }


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "GUARD_KIND",
    "SESSION_KIND",
    "Service1CostAndRateLimitGuardInputV1",
    "Service1CostAndRateLimitGuardCandidateV1",
    "Service1CostAndRateLimitGuardResultV1",
    "build_service_1_cost_and_rate_limit_guard_v1",
]
