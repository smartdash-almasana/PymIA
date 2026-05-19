from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


class _DummyApplication:
    @classmethod
    def builder(cls):
        return cls()

    def token(self, _token: str):
        return self

    def build(self):
        return self

    def add_handler(self, _handler):
        return None

    def run_polling(self, allowed_updates=None):
        return None


class _DummyHandler:
    def __init__(self, *args, **kwargs):
        pass


class _DummyFilters:
    TEXT = object()
    COMMAND = object()


class _DummyUpdate:
    ALL_TYPES = object()


def _install_telegram_stubs(monkeypatch):
    telegram_module = types.ModuleType("telegram")
    telegram_module.Update = _DummyUpdate

    ext_module = types.ModuleType("telegram.ext")
    ext_module.Application = _DummyApplication
    ext_module.CommandHandler = _DummyHandler
    ext_module.ContextTypes = object
    ext_module.MessageHandler = _DummyHandler
    ext_module.filters = _DummyFilters()

    monkeypatch.setitem(sys.modules, "telegram", telegram_module)
    monkeypatch.setitem(sys.modules, "telegram.ext", ext_module)


def _load_telegram_bot(monkeypatch):
    _install_telegram_stubs(monkeypatch)
    module_path = Path(__file__).resolve().parents[1] / "conversa-engine" / "telegram_bot.py"
    spec = importlib.util.spec_from_file_location("telegram_bot", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_telegram_uses_same_fail_closed_parser(monkeypatch):
    telegram_bot = _load_telegram_bot(monkeypatch)

    exit_code, stdout, stderr = telegram_bot._cli_message_from_args(["--foo"])

    assert exit_code == 1
    assert stdout == ""
    assert stderr == "COMANDO_NO_PERMITIDO: --foo"
