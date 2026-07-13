from __future__ import annotations

import copy
import inspect

from pymia.smartpyme.service_1_cost_and_rate_limit_guard_v1 import (
    GUARD_KIND,
    SCHEMA_VERSION,
    build_service_1_cost_and_rate_limit_guard_v1,
)


def _session() -> dict[str, object]:
    return {
        "session_kind": "SAAS_CASE_SESSION_CANDIDATE",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "session_lifecycle": "PROCESSING_CANDIDATE",
        "current_chain_status": "FAILURE_RECOVERY_RETRY_CANDIDATE_READY",
        "service_1_state_refs": {
            "case_truth_ref": "case_truth:s1:001",
            "owner_delivery_packet_ref": "owner_packet:s1:001",
        },
        "runtime_authorized": False,
        "job_authorized": False,
        "file_upload_authorized": False,
        "api_exposed": False,
    }


def _payload() -> dict[str, object]:
    return {
        "saas_case_session_candidate": _session(),
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "estimated_cost_units": 3,
        "max_cost_units": 5,
        "current_window_request_count": 2,
        "max_window_request_count": 4,
        "current_budget_used_units": 10,
        "max_budget_units": 20,
        "requested_operation_kind": "PREPARE_AUTONOMOUS_RUNTIME_CANDIDATE",
        "notes": [],
    }


def _build(payload: dict[str, object]) -> dict[str, object]:
    return build_service_1_cost_and_rate_limit_guard_v1(payload)  # type: ignore[arg-type]


def test_ready_path() -> None:
    result = _build(_payload())
    candidate = result["cost_and_rate_limit_guard_candidate"]
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["status"] == "COST_AND_RATE_LIMIT_GUARD_CANDIDATE_READY"
    assert result["blocked_reason"] is None
    assert candidate == {
        "guard_kind": GUARD_KIND,
        "tenant_ref": "tenant:pyme:001",
        "owner_ref": "owner:pyme:001",
        "case_ref": "case:s1:001",
        "service_name": "SERVICE_1",
        "source_session_ref": "case:s1:001",
        "requested_operation_kind": "PREPARE_AUTONOMOUS_RUNTIME_CANDIDATE",
        "estimated_cost_units": 3,
        "max_cost_units": 5,
        "current_window_request_count": 2,
        "max_window_request_count": 4,
        "current_budget_used_units": 10,
        "max_budget_units": 20,
        "projected_budget_used_units": 13,
        "remaining_cost_headroom_units": 2,
        "remaining_window_request_capacity": 2,
        "remaining_budget_units": 7,
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


def test_missing_session() -> None:
    payload = _payload()
    payload["saas_case_session_candidate"] = None
    result = _build(payload)
    assert result["status"] == "BLOCKED_MISSING_SESSION"
    assert result["blocked_reason"] == "saas_case_session_candidate_required"


def test_invalid_session() -> None:
    payload = _payload()
    session = copy.deepcopy(payload["saas_case_session_candidate"])
    session["session_kind"] = "REAL_SESSION"
    payload["saas_case_session_candidate"] = session
    result = _build(payload)
    assert result["status"] == "BLOCKED_INVALID_SESSION"
    assert result["blocked_reason"] == "session_kind_must_be_saas_case_session_candidate"


def test_invalid_cost_values() -> None:
    cases = [
        ("estimated_cost_units", -1, "estimated_cost_units_must_be_non_negative_int"),
        ("max_cost_units", 0, "max_cost_units_must_be_positive_int"),
        ("current_window_request_count", -1, "current_window_request_count_must_be_non_negative_int"),
        ("max_window_request_count", 0, "max_window_request_count_must_be_positive_int"),
        ("current_budget_used_units", -1, "current_budget_used_units_must_be_non_negative_int"),
        ("max_budget_units", 0, "max_budget_units_must_be_positive_int"),
    ]
    for key, value, reason in cases:
        payload = _payload()
        payload[key] = value
        result = _build(payload)
        assert result["status"] == "BLOCKED_INVALID_LIMIT_INPUT"
        assert result["blocked_reason"] == reason


def test_cost_limit_exceeded() -> None:
    payload = _payload()
    payload["estimated_cost_units"] = 6
    result = _build(payload)
    assert result["status"] == "BLOCKED_COST_LIMIT_EXCEEDED"
    assert result["blocked_reason"] == "estimated_cost_units_exceeds_max_cost_units"


def test_rate_limit_exceeded() -> None:
    payload = _payload()
    payload["current_window_request_count"] = 4
    result = _build(payload)
    assert result["status"] == "BLOCKED_RATE_LIMIT_EXCEEDED"
    assert result["blocked_reason"] == "current_window_request_count_exceeds_or_meets_limit"


def test_budget_exhausted() -> None:
    payload = _payload()
    payload["estimated_cost_units"] = 11
    payload["max_cost_units"] = 12
    result = _build(payload)
    assert result["status"] == "BLOCKED_BUDGET_EXHAUSTED"
    assert result["blocked_reason"] == "estimated_budget_charge_exceeds_max_budget_units"


def test_unsafe_flags_blocked() -> None:
    payload = _payload()
    payload["runtime_authorized"] = True
    result = _build(payload)
    assert result["status"] == "BLOCKED_UNSAFE_FLAGS"
    assert result["blocked_reason"] == "runtime_authorized_must_be_false"


def test_all_dangerous_flags_false() -> None:
    result = _build(_payload())
    candidate = result["cost_and_rate_limit_guard_candidate"]
    assert result["cost_charge_authorized"] is False
    assert result["rate_limit_mutation_authorized"] is False
    assert result["billing_authorized"] is False
    assert result["storage_write_authorized"] is False
    assert result["db_authorized"] is False
    assert result["worker_authorized"] is False
    assert result["queue_authorized"] is False
    assert result["scheduler_authorized"] is False
    assert result["pipeline_authorized"] is False
    assert result["runner_authorized"] is False
    assert result["llm_authorized"] is False
    assert result["pydantic_ai_authorized"] is False
    assert result["mutation_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["api_exposed"] is False
    assert candidate is not None
    assert candidate["cost_charge_authorized"] is False
    assert candidate["rate_limit_mutation_authorized"] is False
    assert candidate["billing_authorized"] is False
    assert candidate["storage_write_authorized"] is False
    assert candidate["db_authorized"] is False
    assert candidate["worker_authorized"] is False
    assert candidate["queue_authorized"] is False
    assert candidate["scheduler_authorized"] is False
    assert candidate["pipeline_authorized"] is False
    assert candidate["runner_authorized"] is False
    assert candidate["llm_authorized"] is False
    assert candidate["pydantic_ai_authorized"] is False
    assert candidate["mutation_authorized"] is False
    assert candidate["runtime_authorized"] is False
    assert candidate["api_exposed"] is False


def test_does_not_mutate_input() -> None:
    payload = _payload()
    original = copy.deepcopy(payload)
    _build(payload)
    assert payload == original


def test_deterministic_output() -> None:
    payload = _payload()
    first = _build(copy.deepcopy(payload))
    second = _build(copy.deepcopy(payload))
    assert first == second


def test_source_guard_no_forbidden_imports() -> None:
    import pymia.smartpyme.service_1_cost_and_rate_limit_guard_v1 as module

    source = inspect.getsource(module).lower()
    forbidden_source_fragments = [
        "import os",
        "from pathlib",
        "tempfile",
        "import time",
        "from time",
        "datetime",
        "import uuid",
        "from uuid",
        "import random",
        "from random",
        "open(",
        "write(",
        "fastapi",
        "starlette",
        "flask",
        "django",
        "sqlalchemy",
        "supabase",
        "celery",
        "\nimport rq",
        "\nfrom rq",
        "autonomous_pipeline_runner",
        "run_service_1_pipeline",
        "import openai",
        "from openai",
        "import anthropic",
        "from anthropic",
        "import pydantic_ai",
        "from pydantic_ai",
    ]
    for fragment in forbidden_source_fragments:
        assert fragment not in source
