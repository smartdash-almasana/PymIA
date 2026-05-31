from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pymia.llm_operator import smoke_openrouter
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


@dataclass
class _FakeResult:
    selected_tool: str | None
    reply_text: str
    error: str | None


class _FakeProvider:
    def __init__(self, api_key: str, model: str | None = None, base_url: str = "", timeout: float = 0.0) -> None:
        self.api_key = api_key
        self.model = model or "openrouter/owl-alpha"
        self.base_url = base_url
        self.timeout = timeout


class _FakeOperator:
    def __init__(self, provider, registry) -> None:
        self.provider = provider
        self.registry = registry

    def handle_turn(self, **kwargs):
        _ = kwargs
        return _FakeResult(
            selected_tool="submit_text_message",
            reply_text="[PymIA:TELEGRAM_RUNTIME] ok",
            error=None,
        )


def test_loads_key_from_env_local_and_runs_without_exposing_key(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text("OPENROUTER_API_KEY=secret-key-123\n", encoding="utf-8")

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(smoke_openrouter, "OpenRouterProvider", _FakeProvider)
    monkeypatch.setattr(smoke_openrouter, "LLMOperator", _FakeOperator)

    code = smoke_openrouter.main(["--message", RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY, "--env-file", str(env_file)])
    out = capsys.readouterr().out

    assert code == 0
    assert "selected_tool: submit_text_message" in out
    assert "reply_text:" in out
    assert "error: None" in out
    assert "model: openrouter/owl-alpha" in out
    assert "secret-key-123" not in out


def test_missing_key_fails_controlled(tmp_path: Path, monkeypatch, capsys) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text("OTHER_KEY=x\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    code = smoke_openrouter.main(["--message", "hola", "--env-file", str(env_file)])
    out = capsys.readouterr().out
    assert code == 2
    assert "OPENROUTER_API_KEY missing" in out
    assert "selected_tool: None" in out


def test_source_has_no_forbidden_tokens() -> None:
    source = Path("pymia/llm_operator/smoke_openrouter.py").read_text(encoding="utf-8").lower()
    assert "telegram" not in source
    assert "hermes" not in source
    assert "langgraph" not in source
