from __future__ import annotations

import pytest

from pydantic_ai.exceptions import ModelHTTPError
import pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 as provider_module

from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    Service1SemanticProviderStepV1,
    Service1SemanticProviderTimeoutError,
    Service1SemanticTimeoutError,
    build_service_1_semantic_fallback_provider_v1,
    build_service_1_semantic_provider_chain_v1,
    service_1_semantic_execution_scope_v1,
)

GEMINI = "GEMINI"
NVIDIA_NIM = "NVIDIA_NIM"
OPENCODE_ZEN = "OPENCODE_ZEN"
GEMINI_MODEL = "gemini-3.6-flash"
NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"
OPENCODE_MODEL = "muse-spark-1.3-contributor-free"


@pytest.fixture(autouse=True)
def _disable_test_backoff(monkeypatch):
    monkeypatch.setattr(provider_module, "SEMANTIC_RETRY_BACKOFF_SECONDS", 0.0)


class _FakeProvider:
    """Callable provider fake with the same interface as the real one."""

    def __init__(self, behavior):
        self._behavior = behavior

    def __call__(self, payload):
        return self._invoke("__call__", payload)

    def understand_workbook(self, payload):
        return self._invoke("understand_workbook", payload)

    def assist(self, payload):
        return self._invoke("assist", payload)

    def _invoke(self, method, payload):
        outcome = self._behavior(method)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _step(provider, name, model):
    return Service1SemanticProviderStepV1(provider=provider, provider_name=name, model=model)


def _chain(gemini, nvidia, opencode):
    return build_service_1_semantic_provider_chain_v1(
        steps=[
            _step(gemini, GEMINI, GEMINI_MODEL),
            _step(nvidia, NVIDIA_NIM, NVIDIA_MODEL),
            _step(opencode, OPENCODE_ZEN, OPENCODE_MODEL),
        ]
    )


def _transient():
    return ModelHTTPError(status_code=503, model_name="test", body={"message": "err"})


def _non_transient():
    return ModelHTTPError(status_code=400, model_name="test", body={"message": "err"})


def _ok():
    return {"status": "ok", "decisions": [1]}


# ---------------------------------------------------------------------------
# Productive order: GEMINI -> NVIDIA_NIM -> OPENCODE_ZEN -> block.
# ---------------------------------------------------------------------------


def test_gemini_pass_does_not_invoke_nvidia_or_opencode() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _ok()),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["primary_provider"] == GEMINI
    assert out["provenance"]["final_provider"] == GEMINI
    assert out["provenance"]["fallback_used"] is False
    assert out["provenance"]["primary_failure_reason"] is None
    assert out["provenance"]["attempted_providers"] == [GEMINI]


def test_gemini_503_falls_back_to_nvidia() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _ok()),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["primary_provider"] == GEMINI
    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert out["provenance"]["fallback_used"] is True
    assert out["provenance"]["primary_failure_reason"] is not None
    assert out["provenance"]["attempted_providers"] == [GEMINI, NVIDIA_NIM]


def test_gemini_503_and_nvidia_503_falls_back_to_opencode() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _ok()),
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["final_provider"] == OPENCODE_ZEN
    assert out["provenance"]["fallback_used"] is True
    assert out["provenance"]["attempted_providers"] == [GEMINI, NVIDIA_NIM, OPENCODE_ZEN]


def test_all_three_transient_fails_structured() -> None:
    from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
        Service1TransientProviderFailureV1,
    )

    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
    )
    with pytest.raises(Service1TransientProviderFailureV1) as caught:
        wrapper({})
    assert isinstance(caught.value.__cause__, ModelHTTPError)


def test_all_three_transient_failures_preserve_provider_attempts() -> None:
    from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
        Service1TransientProviderFailureV1,
    )

    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
    )
    with pytest.raises(Service1TransientProviderFailureV1) as caught:
        wrapper({})

    attempts = getattr(caught.value, "service1_provider_attempts")
    assert [item["provider"] for item in attempts] == [
        GEMINI,
        GEMINI,
        NVIDIA_NIM,
        NVIDIA_NIM,
        OPENCODE_ZEN,
        OPENCODE_ZEN,
    ]
    assert [item["retry_number"] for item in attempts] == [0, 1, 0, 1, 0, 1]
    assert all(item["classification"] == "transient_fallback_eligible" for item in attempts)
    assert all(item["http_status"] == 503 for item in attempts)
    assert all("global_budget_before_seconds" in item for item in attempts)
    assert all("global_budget_after_seconds" in item for item in attempts)


def test_gemini_503_retry_succeeds_without_nvidia() -> None:
    outcomes = iter([_transient(), _ok()])
    gemini = _FakeProvider(lambda m: next(outcomes))
    nvidia = _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called"))
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    out = _chain(gemini, nvidia, opencode)({})

    assert out["status"] == "ok"
    assert out["provenance"]["final_provider"] == GEMINI
    assert [item["retry_number"] for item in out["provenance"]["provider_attempts"]] == [0, 1]


def test_gemini_503_twice_advances_to_nvidia() -> None:
    gemini = _FakeProvider(lambda m: _transient())
    nvidia = _FakeProvider(lambda m: _ok())
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    out = _chain(gemini, nvidia, opencode)({})

    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert [item["provider"] for item in out["provenance"]["provider_attempts"]] == [
        GEMINI,
        GEMINI,
        NVIDIA_NIM,
    ]


def test_nvidia_529_retry_succeeds_without_opencode() -> None:
    nvidia_outcomes = iter([_transient(), _ok()])
    gemini = _FakeProvider(lambda m: _transient())
    nvidia = _FakeProvider(lambda m: next(nvidia_outcomes))
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    out = _chain(gemini, nvidia, opencode)({})

    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert [item["provider"] for item in out["provenance"]["provider_attempts"]] == [
        GEMINI,
        GEMINI,
        NVIDIA_NIM,
        NVIDIA_NIM,
    ]


def test_exhausted_gemini_and_nvidia_then_opencode_retry_succeeds() -> None:
    opencode_outcomes = iter([_transient(), _ok()])
    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: next(opencode_outcomes)),
    )

    out = wrapper({})

    assert out["provenance"]["final_provider"] == OPENCODE_ZEN
    attempts = out["provenance"]["provider_attempts"]
    assert [item["provider"] for item in attempts] == [
        GEMINI,
        GEMINI,
        NVIDIA_NIM,
        NVIDIA_NIM,
        OPENCODE_ZEN,
        OPENCODE_ZEN,
    ]
    assert attempts[-1]["retry_decision"] == "retry_succeeded"


def test_global_budget_skips_retry_without_resetting_deadline() -> None:
    gemini = _FakeProvider(lambda m: _transient())
    nvidia = _FakeProvider(lambda m: _ok())
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    with service_1_semantic_execution_scope_v1(total_timeout_seconds=1.0):
        out = _chain(gemini, nvidia, opencode)({})

    attempts = out["provenance"]["provider_attempts"]
    assert attempts[1]["retry_decision"] == "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET"
    assert attempts[1]["terminal_condition"] == "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET"
    assert attempts[2]["provider"] == NVIDIA_NIM
    budgets = [
        item["global_budget_before_seconds"]
        for item in attempts
        if item["global_budget_before_seconds"] is not None
    ]
    assert budgets == sorted(budgets, reverse=True)


def test_global_budget_preserves_nvidia_window_before_retrying_gemini(monkeypatch) -> None:
    """A second 120 s Gemini attempt must not starve the 180 s NVIDIA fallback."""
    monkeypatch.setattr(provider_module, "SEMANTIC_RETRY_BACKOFF_SECONDS", 2.0)
    gemini_calls = 0

    def _gemini_behavior(_method):
        nonlocal gemini_calls
        gemini_calls += 1
        if gemini_calls == 1:
            return _transient()
        pytest.fail("Gemini retry must be skipped to preserve NVIDIA budget")

    gemini = _FakeProvider(_gemini_behavior)
    gemini._provider_timeout_seconds = 120.0
    nvidia = _FakeProvider(lambda _method: _ok())
    nvidia._provider_timeout_seconds = 180.0
    opencode = _FakeProvider(lambda _method: pytest.fail("OpenCode must not be called"))

    with service_1_semantic_execution_scope_v1(total_timeout_seconds=300.0):
        out = _chain(gemini, nvidia, opencode)({})

    assert gemini_calls == 1
    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    attempts = out["provenance"]["provider_attempts"]
    assert attempts[0]["retry_decision"] == "SKIPPED_INSUFFICIENT_GLOBAL_BUDGET"
    assert attempts[-1]["provider"] == NVIDIA_NIM


@pytest.mark.parametrize("status_code", [429, 500, 502, 504, 529])
def test_transient_status_codes_advance_down_the_chain(status_code: int) -> None:
    def _http_error():
        return ModelHTTPError(status_code=status_code, model_name="test", body={"message": "err"})

    wrapper = _chain(
        _FakeProvider(lambda m: _http_error()),
        _FakeProvider(lambda m: _http_error()),
        _FakeProvider(lambda m: _ok()),
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["final_provider"] == OPENCODE_ZEN


def test_gemini_provider_timeout_falls_back_to_nvidia() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: Service1SemanticProviderTimeoutError("PROVIDER_TIMEOUT")),
        _FakeProvider(lambda m: _ok()),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert out["provenance"]["fallback_used"] is True


def test_provider_timeout_with_global_budget_remaining_advances_chain() -> None:
    gemini = _FakeProvider(lambda m: Service1SemanticTimeoutError("provider attempt timeout"))
    nvidia = _FakeProvider(lambda m: _ok())
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    with service_1_semantic_execution_scope_v1(total_timeout_seconds=300.0):
        out = _chain(gemini, nvidia, opencode)({})

    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert [item["provider"] for item in out["provenance"]["provider_attempts"]] == [
        GEMINI,
        GEMINI,
        NVIDIA_NIM,
    ]
    assert all(
        item["classification"] == "transient_fallback_eligible"
        for item in out["provenance"]["provider_attempts"][:2]
    )


def test_provider_timeout_after_global_deadline_does_not_fallback() -> None:
    def _expired_timeout(_method):
        import time

        time.sleep(0.02)
        return Service1SemanticTimeoutError("global deadline timeout")

    gemini = _FakeProvider(_expired_timeout)
    nvidia = _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called"))
    opencode = _FakeProvider(lambda m: pytest.fail("OpenCode must not be called"))

    with service_1_semantic_execution_scope_v1(total_timeout_seconds=0.001):
        with pytest.raises(Service1SemanticTimeoutError):
            _chain(gemini, nvidia, opencode)({})


def test_total_timeout_does_not_trigger_fallback() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: Service1SemanticTimeoutError("deadline")),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    with pytest.raises(Service1SemanticTimeoutError):
        wrapper({})


def test_non_transient_http_error_no_fallback() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _non_transient()),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    with pytest.raises(ModelHTTPError):
        wrapper({})


def test_schema_validation_error_no_fallback() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: ValueError("invalid JSON schema")),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    with pytest.raises(ValueError):
        wrapper({})


def test_refusal_does_not_fallback() -> None:
    def _refusal():
        raise Service1SemanticProviderTimeoutError

    wrapper = _chain(
        _FakeProvider(lambda m: RuntimeError("model refused the request")),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    with pytest.raises(RuntimeError):
        wrapper({})


def test_structural_invalid_output_no_fallback() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: ["not", "a", "mapping"]),
        _FakeProvider(lambda m: pytest.fail("NVIDIA must not be called")),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    with pytest.raises(RuntimeError, match="non-mapping"):
        wrapper({})


def test_understand_workbook_chain_order_and_fallback() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: {"status": "ok", "tables": [{"sheet_name": "A"}]}),
    )
    out = wrapper.understand_workbook({"workbook_semantic_context": {}})
    assert out["tables"][0]["sheet_name"] == "A"
    assert out["provenance"]["final_provider"] == OPENCODE_ZEN
    assert out["provenance"]["fallback_used"] is True


def test_assist_falls_back_on_transient_but_stays_raw() -> None:
    wrapper = _chain(
        _FakeProvider(lambda m: _transient()),
        _FakeProvider(lambda m: {"response_text": "ok"}),
        _FakeProvider(lambda m: pytest.fail("OpenCode must not be called")),
    )
    out = wrapper.assist({})
    assert out == {"response_text": "ok"}


# ---------------------------------------------------------------------------
# Generic two-step builder remains a valid primary + one fallback seam.
# ---------------------------------------------------------------------------


def test_two_step_builder_still_wraps_two_providers() -> None:
    wrapper = build_service_1_semantic_fallback_provider_v1(
        primary_provider=_FakeProvider(lambda m: _ok()),
        fallback_provider=_FakeProvider(lambda m: pytest.fail("fallback must not run")),
        primary_provider_name=GEMINI,
        primary_model=GEMINI_MODEL,
        fallback_provider_name=NVIDIA_NIM,
        fallback_model=NVIDIA_MODEL,
    )
    out = wrapper({})
    assert out["status"] == "ok"
    assert out["provenance"]["primary_provider"] == GEMINI
    assert out["provenance"]["final_provider"] == GEMINI
    assert out["provenance"]["fallback_used"] is False
