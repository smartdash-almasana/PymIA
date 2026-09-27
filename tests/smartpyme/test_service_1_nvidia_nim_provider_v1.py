from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic_ai import Agent, NativeOutput

import pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 as provider_module
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticAssistanceReplyV1,
    ColumnSemanticBatchV1,
    NVIDIA_NIM_BASE_URL,
    NVIDIA_NIM_MODEL,
    NVIDIA_NIM_PROVIDER,
    GEMINI_PROVIDER,
    GEMINI_MODEL,
    OPENCODE_ZEN_BASE_URL,
    OPENCODE_ZEN_MODEL,
    OPENCODE_ZEN_MODEL_ENV,
    OPENCODE_ZEN_PROVIDER,
    WorkbookBusinessUnderstandingV1,
    build_service_1_nvidia_nim_column_semantic_provider_v1,
    build_service_1_opencode_zen_column_semantic_provider_v1,
    semantic_provider_from_environment_v1,
)


def _patch_provider_builders(monkeypatch: pytest.MonkeyPatch) -> tuple[dict[str, object], dict[str, dict]]:
    sentinels = {"gemini": object(), "nvidia": object(), "opencode": object()}
    captured: dict[str, dict] = {}

    monkeypatch.setattr(
        provider_module,
        "build_service_1_gemini_column_semantic_provider_v1",
        lambda **kwargs: (captured.update(gemini=kwargs), sentinels["gemini"])[1],
    )
    monkeypatch.setattr(
        provider_module,
        "build_service_1_nvidia_nim_column_semantic_provider_v1",
        lambda **kwargs: (captured.update(nvidia=kwargs), sentinels["nvidia"])[1],
    )
    monkeypatch.setattr(
        provider_module,
        "build_service_1_opencode_zen_column_semantic_provider_v1",
        lambda **kwargs: (captured.update(opencode=kwargs), sentinels["opencode"])[1],
    )
    return sentinels, captured


def _chain_provider_names(chain: "provider_module.Service1SemanticProviderChainV1") -> list[str]:
    return [step.provider_name for step in chain._steps]


def test_environment_builds_ordered_chain_from_current_configured_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinels, captured = _patch_provider_builders(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-secret")
    monkeypatch.setenv("NVIDIA_API_KEY", "test-nvidia-secret")
    monkeypatch.setenv("OPENCODE_API_KEY", "test-opencode-secret")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("NVIDIA_NIM_MODEL", raising=False)
    monkeypatch.delenv("PYMIA_SEMANTIC_LLM_MODEL", raising=False)
    monkeypatch.delenv(OPENCODE_ZEN_MODEL_ENV, raising=False)

    chain = semantic_provider_from_environment_v1()

    assert isinstance(chain, provider_module.Service1SemanticProviderChainV1)
    assert _chain_provider_names(chain) == [GEMINI_PROVIDER, NVIDIA_NIM_PROVIDER]
    assert [step.model for step in chain._steps] == [GEMINI_MODEL, NVIDIA_NIM_MODEL]
    assert [step.provider for step in chain._steps] == [
        sentinels["gemini"],
        sentinels["nvidia"],
    ]
    assert captured["gemini"]["model"] == GEMINI_MODEL
    assert captured["nvidia"]["model"] == NVIDIA_NIM_MODEL
    assert "opencode" not in captured
    assert captured["gemini"]["api_key"] == "test-gemini-secret"
    assert captured["nvidia"]["api_key"] == "test-nvidia-secret"


def test_environment_keeps_separate_models_per_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    _, captured = _patch_provider_builders(monkeypatch)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom")
    monkeypatch.setenv("NVIDIA_NIM_MODEL", "nvidia-custom")
    monkeypatch.setenv("PYMIA_SEMANTIC_LLM_MODEL", "gemini-shared")
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.setenv("NVIDIA_API_KEY", "n")
    monkeypatch.setenv("OPENCODE_API_KEY", "z")

    chain = semantic_provider_from_environment_v1()

    assert [step.model for step in chain._steps] == ["gemini-custom", "nvidia-custom"]
    assert captured["gemini"]["model"] == "gemini-custom"
    assert captured["nvidia"]["model"] == "nvidia-custom"
    assert "opencode" not in captured


def test_environment_does_not_auto_add_opencode_from_model_override(monkeypatch: pytest.MonkeyPatch) -> None:
    _, captured = _patch_provider_builders(monkeypatch)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom")
    monkeypatch.setenv("PYMIA_SEMANTIC_LLM_MODEL", "gemini-shared")
    monkeypatch.setenv(OPENCODE_ZEN_MODEL_ENV, "opencode-custom")
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.setenv("NVIDIA_API_KEY", "n")
    monkeypatch.setenv("OPENCODE_API_KEY", "z")

    chain = semantic_provider_from_environment_v1()

    assert [step.model for step in chain._steps] == ["gemini-custom", NVIDIA_NIM_MODEL]
    assert captured["gemini"]["model"] == "gemini-custom"
    assert "opencode" not in captured


def test_environment_omits_unconfigured_fallback_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    _, captured = _patch_provider_builders(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("OPENCODE_API_KEY", raising=False)

    chain = semantic_provider_from_environment_v1()

    assert _chain_provider_names(chain) == [GEMINI_PROVIDER]
    assert "nvidia" not in captured
    assert "opencode" not in captured


def test_environment_fails_closed_without_any_configured_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("OPENCODE_API_KEY", raising=False)

    provider = semantic_provider_from_environment_v1()

    with pytest.raises(RuntimeError, match="PYMIA_SEMANTIC_LLM_MODEL"):
        provider({})


def test_nvidia_nim_builder_reuses_sem8_agent_contract() -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_agent_factory(model: object, **kwargs: object):
        calls.append((str(model), kwargs))
        return SimpleNamespace(run_sync=lambda prompt: SimpleNamespace(output=None))

    provider = build_service_1_nvidia_nim_column_semantic_provider_v1(
        model=NVIDIA_NIM_MODEL,
        base_url=NVIDIA_NIM_BASE_URL,
        api_key="test-only-secret",
        agent_factory=fake_agent_factory,
    )

    assert provider is not None
    assert len(calls) == 3
    assert {call[0] for call in calls} == {NVIDIA_NIM_MODEL}
    assert {call[1]["instructions"] for call in calls} == {
        provider_module._SYSTEM_PROMPT,
        provider_module._ASSISTANT_SYSTEM_PROMPT,
        provider_module._BUSINESS_UNDERSTANDING_SYSTEM_PROMPT,
    }
    assert [kwargs["output_type"] for _, kwargs in calls] == [
        ColumnSemanticBatchV1,
        ColumnSemanticAssistanceReplyV1,
        WorkbookBusinessUnderstandingV1,
    ]
    for index, (_, kwargs) in enumerate(calls):
        assert kwargs["retries"] == provider_module.NVIDIA_NIM_MAX_RETRIES == 0
        expected_settings = {
            "timeout": provider_module.NVIDIA_NIM_TIMEOUT_SECONDS,
            "max_tokens": (
                provider_module.NVIDIA_NIM_WORKBOOK_MAX_TOKENS
                if index == 2
                else provider_module.NVIDIA_NIM_COLUMN_MAX_TOKENS
                if index == 0
                else provider_module.NVIDIA_NIM_MAX_TOKENS
            ),
            "thinking": False,
            "extra_body": {"chat_template_kwargs": {"thinking": False}},
        }
        assert kwargs["model_settings"] == expected_settings


def test_opencode_zen_builder_uses_responses_model_and_existing_typed_contracts() -> None:
    calls: list[tuple[object, dict[str, object]]] = []

    def fake_agent_factory(model: object, **kwargs: object):
        calls.append((model, kwargs))
        return SimpleNamespace(run_sync=lambda prompt: SimpleNamespace(output=None))

    provider = build_service_1_opencode_zen_column_semantic_provider_v1(
        model=OPENCODE_ZEN_MODEL,
        base_url=OPENCODE_ZEN_BASE_URL,
        api_key="test-only-opencode-secret",
        agent_factory=fake_agent_factory,
    )

    assert provider is not None
    assert len(calls) == 3
    assert {call[0] for call in calls} == {OPENCODE_ZEN_MODEL}
    assert [kwargs["output_type"] for _, kwargs in calls[:2]] == [
        ColumnSemanticBatchV1,
        ColumnSemanticAssistanceReplyV1,
    ]
    assert isinstance(calls[2][1]["output_type"], NativeOutput)
    assert calls[2][1]["output_type"].outputs is WorkbookBusinessUnderstandingV1
    for index, (_, kwargs) in enumerate(calls):
        assert kwargs["retries"] == provider_module.NVIDIA_NIM_MAX_RETRIES == 0
        assert kwargs["model_settings"] == {
            "timeout": provider_module.NVIDIA_NIM_TIMEOUT_SECONDS,
            "max_tokens": (
                provider_module.OPENCODE_ZEN_WORKBOOK_MAX_TOKENS
                if index == 2
                else provider_module.OPENCODE_ZEN_COLUMN_MAX_TOKENS
                if index == 0
                else provider_module.NVIDIA_NIM_MAX_TOKENS
            ),
            "thinking": False,
        }


def test_opencode_zen_workbook_budget_is_scoped_without_changing_nvidia() -> None:
    assert provider_module.SEMANTIC_WORKBOOK_MAX_TOKENS == 768
    assert provider_module.SEMANTIC_COLUMN_MAX_TOKENS == 3072
    assert provider_module.NVIDIA_NIM_WORKBOOK_MAX_TOKENS == 768
    assert provider_module.NVIDIA_NIM_COLUMN_MAX_TOKENS == 3072
    assert provider_module.OPENCODE_ZEN_WORKBOOK_MAX_TOKENS == 8192
    assert provider_module.OPENCODE_ZEN_COLUMN_MAX_TOKENS == 8192
    assert provider_module._OPENCODE_ZEN_WORKBOOK_MODEL_SETTINGS == {
        "timeout": provider_module.SEMANTIC_TIMEOUT_SECONDS,
        "max_tokens": 8192,
        "thinking": False,
    }
    assert provider_module._OPENCODE_ZEN_COLUMN_MODEL_SETTINGS["max_tokens"] == 8192


def test_opencode_zen_workbook_uses_native_json_schema_without_changing_schema() -> None:
    model = provider_module._build_opencode_zen_responses_model_v1(
        model_name=OPENCODE_ZEN_MODEL,
        base_url=OPENCODE_ZEN_BASE_URL,
        api_key="test-only-opencode-secret",
    )
    native_agent = Agent(model, output_type=NativeOutput(WorkbookBusinessUnderstandingV1), instructions="offline")
    prompted_agent = Agent(model, output_type=WorkbookBusinessUnderstandingV1, instructions="offline")

    assert native_agent._output_schema.mode == "native"
    assert native_agent._output_schema.object_def.name == "WorkbookBusinessUnderstandingV1"
    assert native_agent._output_schema.object_def.json_schema == prompted_agent._output_schema.object_def.json_schema


def test_opencode_zen_native_request_uses_responses_json_schema_format() -> None:
    import asyncio

    from pydantic_ai.models import ModelRequestParameters

    model = provider_module._build_opencode_zen_responses_model_v1(
        model_name=OPENCODE_ZEN_MODEL,
        base_url=OPENCODE_ZEN_BASE_URL,
        api_key="test-only-opencode-secret",
    )
    agent = Agent(model, output_type=NativeOutput(WorkbookBusinessUnderstandingV1), instructions="offline")
    parameters = ModelRequestParameters(
        output_mode="native",
        output_object=agent._output_schema.object_def,
    )
    _, prepared = model.prepare_request(None, parameters)
    request = asyncio.run(model._build_responses_request_params([], {}, prepared, model.profile))

    assert prepared.output_mode == "native"
    assert request.text["format"]["type"] == "json_schema"
    assert request.text["format"]["name"] == "WorkbookBusinessUnderstandingV1"
    assert request.text["format"]["schema"] == prepared.output_object.json_schema
    assert "strict" not in request.text["format"]
    assert not isinstance(request.tools, list)
    assert "json_object" not in repr(request.text)


def test_opencode_zen_builder_constructs_openai_responses_api_model() -> None:
    model = provider_module._build_opencode_zen_responses_model_v1(
        model_name=OPENCODE_ZEN_MODEL,
        base_url=OPENCODE_ZEN_BASE_URL,
        api_key="test-only-opencode-secret",
    )

    assert type(model).__name__ == "OpenAIResponsesModel"
    assert model.model_name == OPENCODE_ZEN_MODEL
    assert str(model.client.base_url).rstrip("/") == OPENCODE_ZEN_BASE_URL


# ---------------------------------------------------------------------------
# F4 transient retry policy (NVIDIA NIM only). One logical call, at most two
# physical requests, single retry on transient provider errors, then fail-closed.
# ---------------------------------------------------------------------------


def _provider_with_agent(agent, *, retry_transient: bool = True) -> "provider_module.Service1PydanticAIColumnSemanticProviderV1":
    return provider_module.Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        assistant_agent=SimpleNamespace(run_sync=lambda p: SimpleNamespace(output=None)),
        business_understanding_agent=SimpleNamespace(run_sync=lambda p: SimpleNamespace(output=None)),
        retry_transient=retry_transient,
    )


def _counting_agent(behavior):
    state = {"count": 0}

    def run_sync(prompt):
        state["count"] += 1
        outcome = behavior(state["count"])
        if isinstance(outcome, Exception):
            raise outcome
        return SimpleNamespace(output=outcome)

    return SimpleNamespace(run_sync=run_sync), state


def _http_error(status: int) -> Exception:
    from pydantic_ai.exceptions import ModelHTTPError
    return ModelHTTPError(status_code=status, model_name="test", body={"message": "err"})


def _timeout_error() -> Exception:
    from pydantic_ai.exceptions import ModelAPIError
    return ModelAPIError(model_name="test", message="Request timed out.")


def _run_once(provider):
    # use _run_sync directly on the counting agent to count physical requests
    return provider._run_sync(provider._agent, "prompt")


def test_transient_529_retries_then_succeeds() -> None:
    agent, state = _counting_agent(lambda n: _http_error(529) if n == 1 else "ok")
    provider = _provider_with_agent(agent)
    _run_once(provider)
    assert state["count"] == 2


def test_transient_timeout_retries_then_succeeds() -> None:
    agent, state = _counting_agent(lambda n: _timeout_error() if n == 1 else "ok")
    provider = _provider_with_agent(agent)
    _run_once(provider)
    assert state["count"] == 2


def test_transient_503_retries_then_succeeds() -> None:
    agent, state = _counting_agent(lambda n: _http_error(503) if n == 1 else "ok")
    provider = _provider_with_agent(agent)
    _run_once(provider)
    assert state["count"] == 2


def test_transient_529_twice_fails_closed() -> None:
    from pydantic_ai.exceptions import ModelHTTPError
    agent, state = _counting_agent(lambda n: _http_error(529))
    provider = _provider_with_agent(agent)
    with pytest.raises(ModelHTTPError):
        _run_once(provider)
    assert state["count"] == 2


def test_transient_timeout_twice_fails_closed() -> None:
    from pydantic_ai.exceptions import ModelAPIError
    agent, state = _counting_agent(lambda n: _timeout_error())
    provider = _provider_with_agent(agent)
    with pytest.raises(ModelAPIError):
        _run_once(provider)
    assert state["count"] == 2


def test_auth_401_no_retry() -> None:
    agent, state = _counting_agent(lambda n: _http_error(401))
    provider = _provider_with_agent(agent)
    with pytest.raises(Exception):
        _run_once(provider)
    assert state["count"] == 1


def test_bad_request_400_no_retry() -> None:
    agent, state = _counting_agent(lambda n: _http_error(400))
    provider = _provider_with_agent(agent)
    with pytest.raises(Exception):
        _run_once(provider)
    assert state["count"] == 1


def test_invalid_structured_output_no_retry() -> None:
    agent, state = _counting_agent(lambda n: ValueError("invalid JSON schema"))
    provider = _provider_with_agent(agent)
    with pytest.raises(ValueError):
        _run_once(provider)
    assert state["count"] == 1


def test_max_two_physical_requests() -> None:
    agent, state = _counting_agent(lambda n: _http_error(529))
    provider = _provider_with_agent(agent)
    with pytest.raises(Exception):
        _run_once(provider)
    assert state["count"] == 2


def test_nvidia_provider_client_retry_disabled_for_chain_owned_retry() -> None:
    provider = provider_module.build_service_1_nvidia_nim_column_semantic_provider_v1(
        model=NVIDIA_NIM_MODEL,
        base_url=NVIDIA_NIM_BASE_URL,
        api_key="test-only-secret",
        agent_factory=lambda model, **kwargs: SimpleNamespace(run_sync=lambda p: SimpleNamespace(output=None)),
    )
    assert provider._retry_transient is False
    # backoff constant exists and is short
    assert provider_module.NVIDIA_NIM_RETRY_BACKOFF_SECONDS == 2.0
    assert provider_module.NVIDIA_NIM_MAX_RETRIES == 0


def test_opencode_zen_retry_disabled() -> None:
    provider = provider_module.build_service_1_opencode_zen_column_semantic_provider_v1(
        model=OPENCODE_ZEN_MODEL,
        base_url=OPENCODE_ZEN_BASE_URL,
        api_key="test-only-opencode-secret",
        agent_factory=lambda model, **kwargs: SimpleNamespace(run_sync=lambda p: SimpleNamespace(output=None)),
    )
    assert provider._retry_transient is False
