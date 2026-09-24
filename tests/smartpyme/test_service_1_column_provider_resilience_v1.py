from __future__ import annotations

import pytest

from pydantic_ai.exceptions import ModelHTTPError
import pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 as provider_module

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    build_service_1_llm_semantic_context_v1,
)
from pymia.smartpyme.service_1_llm_semantic_interpreter_v1 import (
    BLOCK_TRANSIENT_PROVIDER_FAILURE,
    interpret_service_1_semantics_v1,
)
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    Service1SemanticProviderChainV1,
    Service1SemanticProviderStepV1,
    Service1TransientProviderFailureV1,
    build_service_1_semantic_provider_chain_v1,
    semantic_provider_from_environment_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    build_service_1_workbook_profile_v1,
)

NVIDIA_NIM = "NVIDIA_NIM"
OPENCODE_ZEN = "OPENCODE_ZEN"
NVIDIA_MODEL = "nvidia/nemotron-3-super-120b-a12b"
OPENCODE_MODEL = "muse-spark-1.3-contributor-free"


@pytest.fixture(autouse=True)
def _disable_test_backoff(monkeypatch):
    monkeypatch.setattr(provider_module, "SEMANTIC_RETRY_BACKOFF_SECONDS", 0.0)


class _FakeProvider:
    def __init__(self, behavior):
        self._behavior = behavior
        self.calls = 0

    def __call__(self, payload):
        self.calls += 1
        return self._invoke("__call__", payload)

    def _invoke(self, method, payload):
        outcome = self._behavior(method, self.calls)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _step(provider, name, model):
    return Service1SemanticProviderStepV1(provider=provider, provider_name=name, model=model)


def _http_error(status_code: int):
    return ModelHTTPError(status_code=status_code, model_name="test", body={"message": "err"})


def _ok():
    return {"status": "ok", "decisions": [1]}


def _chain_single(provider):
    return build_service_1_semantic_provider_chain_v1(
        steps=[_step(provider, NVIDIA_NIM, NVIDIA_MODEL)]
    )


def test_503_retries_once_then_structured_failure() -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(503))
    chain = _chain_single(nvidia)
    with pytest.raises(Service1TransientProviderFailureV1):
        chain({})
    assert nvidia.calls == 2


def test_503_then_success_returns_semantic_result() -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(503) if n == 1 else _ok())
    out = _chain_single(nvidia)({})
    assert out["status"] == "ok"
    assert out["provenance"]["final_provider"] == NVIDIA_NIM
    assert out["provenance"]["provider_attempts"][-1]["retry_decision"] == "retry_succeeded"


def test_repeated_503_bounded_singular_attempts() -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(503))
    with pytest.raises(Service1TransientProviderFailureV1):
        _chain_single(nvidia)({})
    assert nvidia.calls == 2


def test_repeated_503_structured_not_raw() -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(503))
    with pytest.raises(Service1TransientProviderFailureV1) as caught:
        _chain_single(nvidia)({})
    assert isinstance(caught.value.__cause__, ModelHTTPError)
    assert caught.value.__cause__.status_code == 503
    assert caught.value.attempted_providers == [NVIDIA_NIM]
    assert len(caught.value.provider_attempts) == 2
    assert getattr(caught.value, "service1_provider_attempts") is not None


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 410])
def test_permanent_failures_never_retry(status_code: int) -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(status_code))
    with pytest.raises(ModelHTTPError):
        _chain_single(nvidia)({})
    assert nvidia.calls == 1


def _minimal_context():
    ingestion_output = {
        "case_id": "case-resilience",
        "filename": "taller.xlsx",
        "source_file_ref": "taller.xlsx",
        "workbook_context": {"case_id": "case-resilience"},
        "provenance": {"source_file_ref": "taller.xlsx"},
        "column_refs": [
            {
                "question_id": "q1",
                "field_id": "q1",
                "sheet_name": "Ordenes",
                "column_name": "Trabajo",
                "normalized_column_name": "trabajo",
            },
        ],
        "normalized_tables": [
            {
                "schema_version": "1.0",
                "service_name": "SERVICE_1",
                "status": "OK",
                "source_kind": "xlsx",
                "source_path": "taller.xlsx",
                "sheet_name": "Ordenes",
                "headers": ["Trabajo"],
                "normalized_headers": ["trabajo"],
                "rows": [{"trabajo": "aceite"}],
                "header_row_number": 1,
                "source_row_numbers": [2],
                "row_count": 1,
                "column_count": 1,
                "warnings": [],
                "blocking_errors": [],
                "runtime_authorized": False,
            },
        ],
    }
    profile = build_service_1_workbook_profile_v1(ingestion_output=ingestion_output)
    return build_service_1_llm_semantic_context_v1(
        case_id="case-resilience",
        requested_capability=None,
        workbook_profile=profile,
        deterministic_hypotheses=(),
        allowed_semantic_roles=("quantity",),
        capability_relevant_roles=("quantity",),
        compatible_tenant_memory_hints=(),
    )


def test_interpreter_maps_transient_to_blocked_packet_not_ambiguity() -> None:
    def _failing(_payload):
        raise Service1TransientProviderFailureV1(
            "TRANSIENT_PROVIDER_FAILURE: provider unavailable after bounded retries",
            provider_attempts=[{"provider": NVIDIA_NIM}],
            attempted_providers=[NVIDIA_NIM],
        )

    packet = interpret_service_1_semantics_v1(context=_minimal_context(), provider=_failing)
    assert packet["status"] == "BLOCKED"
    assert packet["blocked_reason"] == BLOCK_TRANSIENT_PROVIDER_FAILURE
    assert packet["proposal"] is None
    assert packet["runtime_authorized"] is False
    assert "owner_questions" not in packet


def test_nvidia_503_twice_then_zen_403_structured_no_raw_403() -> None:
    nvidia = _FakeProvider(lambda m, n: _http_error(503))
    zen = _FakeProvider(lambda m, n: _http_error(403))
    chain = build_service_1_semantic_provider_chain_v1(
        steps=[
            _step(nvidia, NVIDIA_NIM, NVIDIA_MODEL),
            _step(zen, OPENCODE_ZEN, OPENCODE_MODEL),
        ]
    )
    with pytest.raises(Service1TransientProviderFailureV1) as caught:
        chain({})
    assert nvidia.calls == 2
    assert zen.calls == 1
    assert isinstance(caught.value.__cause__, ModelHTTPError)
    assert caught.value.__cause__.status_code == 403
    providers = [item["provider"] for item in caught.value.provider_attempts]
    assert providers == [NVIDIA_NIM, NVIDIA_NIM, OPENCODE_ZEN]


def test_env_builder_returns_governed_chain(monkeypatch) -> None:
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENCODE_API_KEY", raising=False)
    chain = semantic_provider_from_environment_v1()
    assert isinstance(chain, Service1SemanticProviderChainV1)


def test_env_builder_excludes_zen_automatic_fallback(monkeypatch) -> None:
    """Free-tier Zen credentials cannot serve server-side (HTTP 403), so the
    productive chain must not invoke Zen automatically even when its key exists."""
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key")
    monkeypatch.setenv("OPENCODE_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    chain = semantic_provider_from_environment_v1()
    assert isinstance(chain, Service1SemanticProviderChainV1)
    assert [step.provider_name for step in chain._steps] == ["NVIDIA_NIM"]
