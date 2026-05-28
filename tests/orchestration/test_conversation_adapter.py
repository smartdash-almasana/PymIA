"""Tests del adapter conversacional OS -> SmartPyme anamnesis."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from pymia.orchestration.conversation_adapter import (
    ConversationAdapterResult,
    adapt_text_message,
)


def test_adapter_returns_required_result_fields() -> None:
    result = adapt_text_message(
        text="hola",
        tenant_id="tenant",
        user_id="user",
        progressive_context={},
    )
    assert isinstance(result, ConversationAdapterResult)
    assert isinstance(result.reply_text, str)
    assert isinstance(result.updated_progressive_context, dict)
    assert result.phase_hint in {"CONVERSATIONAL", "NEEDS_EVIDENCE", "BLOCKED"}
    assert isinstance(result.decision_trail_entry, str)


def test_updated_progressive_context_is_json_serializable() -> None:
    result = adapt_text_message(
        text="hola",
        tenant_id="tenant",
        user_id="user",
        progressive_context={},
    )
    json.dumps(result.updated_progressive_context)


def test_adapter_does_not_mutate_input_context() -> None:
    original = {"k": {"nested": 1}}
    snapshot = {"k": {"nested": 1}}
    _ = adapt_text_message(
        text="hola",
        tenant_id="tenant",
        user_id="user",
        progressive_context=original,
    )
    assert original == snapshot


def test_adapter_handles_empty_context() -> None:
    result = adapt_text_message(
        text="",
        tenant_id="tenant",
        user_id="user",
        progressive_context={},
    )
    assert isinstance(result.updated_progressive_context, dict)


def test_adapter_fail_closed_on_exception() -> None:
    with patch("pymia.orchestration.conversation_adapter.run_anamnesis_turn", side_effect=RuntimeError("boom")):
        result = adapt_text_message(
            text="hola",
            tenant_id="tenant",
            user_id="user",
            progressive_context={"a": 1},
        )
    assert result.phase_hint == "BLOCKED"
    assert result.updated_progressive_context == {"a": 1}
    assert "error" in result.decision_trail_entry.lower()


def test_adapter_source_has_no_forbidden_tokens() -> None:
    source = Path("pymia/orchestration/conversation_adapter.py").read_text(encoding="utf-8").lower()
    assert "import telegram" not in source
    assert "from telegram" not in source
    assert "import hermes" not in source
    assert "from hermes" not in source
    assert "langgraph" not in source


def test_phase_hint_is_in_allowed_set() -> None:
    result = adapt_text_message(
        text="necesito ayuda",
        tenant_id="tenant",
        user_id="user",
        progressive_context={},
    )
    assert result.phase_hint in {"CONVERSATIONAL", "NEEDS_EVIDENCE", "BLOCKED"}
