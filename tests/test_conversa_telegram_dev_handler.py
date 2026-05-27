from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "conversa-engine" / "telegram_dev_handler.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("telegram_dev_handler_for_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeMessage:
    def __init__(self, text: str):
        self.text = text


class _FakeChat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class _FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class _FakeUpdate:
    def __init__(self, chat_id: int, user_id: int, text: str):
        self.effective_chat = _FakeChat(chat_id)
        self.effective_user = _FakeUser(user_id)
        self.message = _FakeMessage(text)


class _FakeBot:
    def __init__(self):
        self.sent = []

    async def send_message(self, *, chat_id, text):
        self.sent.append({"chat_id": chat_id, "text": text})


class _FakeContext:
    def __init__(self):
        self.bot = _FakeBot()


@pytest.mark.anyio
async def test_telegram_text_update_routes_to_hermes_and_sends_reply(monkeypatch):
    module = _load_module()

    seen = {}

    def _fake_process(*, tenant_id, user_id, session_key, message_text):
        seen["tenant_id"] = tenant_id
        seen["user_id"] = user_id
        seen["session_key"] = session_key
        seen["message_text"] = message_text
        return "respuesta desde pymia"

    monkeypatch.setattr(module, "_process_telegram_message", _fake_process)

    update = _FakeUpdate(chat_id=999, user_id=123, text="hola")
    context = _FakeContext()

    reply = await module.handle_text_update(update, context)

    assert reply == "respuesta desde pymia"
    assert seen == {
        "tenant_id": "telegram",
        "user_id": "123",
        "session_key": "telegram:999:123",
        "message_text": "hola",
    }
    assert context.bot.sent == [{"chat_id": "999", "text": "respuesta desde pymia"}]


@pytest.mark.anyio
async def test_telegram_text_update_fail_open_on_process_error(monkeypatch):
    module = _load_module()

    def _failing_process(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(module, "_process_telegram_message", _failing_process)

    update = _FakeUpdate(chat_id=555, user_id=777, text="hola")
    context = _FakeContext()

    reply = await module.handle_text_update(update, context)

    assert reply == "No pude procesar el mensaje en este momento."
    assert context.bot.sent == [
        {"chat_id": "555", "text": "No pude procesar el mensaje en este momento."}
    ]
