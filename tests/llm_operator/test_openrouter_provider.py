from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pymia.llm_operator.providers import ToolDecision
from pymia.llm_operator.providers_openrouter import OpenRouterProvider


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_model_default_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYMIA_OPERATOR_MODEL", "openrouter/custom-model")
    provider = OpenRouterProvider(api_key="k")
    assert provider.model == "openrouter/custom-model"


def test_model_default_fallback_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYMIA_OPERATOR_MODEL", raising=False)
    provider = OpenRouterProvider(api_key="k")
    assert provider.model == "openrouter/owl-alpha"


def test_request_uses_chat_completions_endpoint_and_auth_header() -> None:
    seen = {}

    def _fake_urlopen(request, timeout=0):
        seen["url"] = request.full_url
        seen["auth"] = request.headers.get("Authorization")
        seen["timeout"] = timeout
        return _FakeResponse({"choices": [{"message": {"tool_calls": []}}]})

    provider = OpenRouterProvider(api_key="my-secret", model="openrouter/test")
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen):
        _ = provider.choose_tool("hola", state={}, tools_schema=[])

    assert seen["url"].endswith("/chat/completions")
    assert seen["auth"] == "Bearer my-secret"
    assert seen["timeout"] == provider.timeout


def test_parses_tool_call_submit_text_message() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "submit_text_message",
                                "arguments": "{\"text\":\"hola\"}",
                            }
                        }
                    ]
                }
            }
        ]
    }
    provider = OpenRouterProvider(api_key="k")
    with patch("urllib.request.urlopen", return_value=_FakeResponse(payload)):
        decision = provider.choose_tool("hola", state={}, tools_schema=[])
    assert isinstance(decision, ToolDecision)
    assert decision.tool_name == "submit_text_message"
    assert decision.extra_args == {"text": "hola"}


def test_parses_tool_call_request_diagnostic() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "request_diagnostic", "arguments": "{}"}}
                    ]
                }
            }
        ]
    }
    provider = OpenRouterProvider(api_key="k")
    with patch("urllib.request.urlopen", return_value=_FakeResponse(payload)):
        decision = provider.choose_tool("diagnosticar", state={}, tools_schema=[])
    assert decision.tool_name == "request_diagnostic"
    assert decision.extra_args == {}


def test_response_without_tool_call_produces_safe_fallback() -> None:
    provider = OpenRouterProvider(api_key="k")
    payload = {"choices": [{"message": {"content": "sin tool"}}]}
    with patch("urllib.request.urlopen", return_value=_FakeResponse(payload)):
        decision = provider.choose_tool("hola", state={}, tools_schema=[])
    assert decision.tool_name == "submit_text_message"
    assert decision.extra_args == {"text": "hola"}


def test_http_error_does_not_raise_to_caller() -> None:
    provider = OpenRouterProvider(api_key="k")
    with patch("urllib.request.urlopen", side_effect=OSError("http fail")):
        decision = provider.choose_tool("hola", state={}, tools_schema=[])
    assert decision.tool_name == "submit_text_message"
    assert decision.extra_args == {"text": "hola"}


def test_invalid_json_does_not_raise_to_caller() -> None:
    class _BadResponse:
        def read(self) -> bytes:
            return b"{not-json"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    provider = OpenRouterProvider(api_key="k")
    with patch("urllib.request.urlopen", return_value=_BadResponse()):
        decision = provider.choose_tool("hola", state={}, tools_schema=[])
    assert decision.tool_name == "submit_text_message"
    assert decision.extra_args == {"text": "hola"}


def test_source_has_no_forbidden_tokens() -> None:
    source = Path("pymia/llm_operator/providers_openrouter.py").read_text(encoding="utf-8").lower()
    assert "telegram" not in source
    assert "hermes" not in source
    assert "langgraph" not in source
    assert "smartpyme" not in source
    assert "openai" not in source
    assert "anthropic" not in source
    assert "pydantic_ai" not in source
