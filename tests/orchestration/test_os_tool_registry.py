from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pymia.orchestration.os_tool_registry import (
    OS_TOOLS,
    get_conversation_state,
    request_diagnostic,
    submit_document,
    submit_text_message,
)


def test_registry_exposes_exactly_four_tools_with_schema_keys() -> None:
    assert len(OS_TOOLS) == 4
    names = {tool["name"] for tool in OS_TOOLS}
    assert names == {"submit_text_message", "submit_document", "request_diagnostic", "get_conversation_state"}
    for tool in OS_TOOLS:
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert "returns" in tool


def test_submit_text_message_returns_phase_and_reply_text(tmp_path: Path) -> None:
    result = submit_text_message(
        tenant_id="tenant_a",
        chat_id="chat_a",
        conversation_id="conv_a",
        text="hola",
        base_dir=tmp_path,
    )
    assert "phase" in result
    assert "reply_text" in result
    assert isinstance(result["reply_text"], str)
    assert result["error"] is None


def test_submit_document_then_request_diagnostic_basic_flow(tmp_path: Path) -> None:
    doc_path = tmp_path / "ventas.xlsx"
    pd.DataFrame([{"producto": "A", "ventas": 100, "costo": 80}]).to_excel(doc_path, index=False)

    doc_result = submit_document(
        tenant_id="tenant_b",
        chat_id="chat_b",
        conversation_id="conv_b",
        document_path=doc_path,
        document_name="ventas.xlsx",
        base_dir=tmp_path,
    )
    assert doc_result["error"] is None
    assert doc_result["phase"] in {"EVIDENCE_RECEIVED", "NEW", "WAITING_FOR_EVIDENCE", "BLOCKED", "FAILED", "DELIVERED", "READY_TO_EXECUTE"}

    diag_result = request_diagnostic(
        tenant_id="tenant_b",
        chat_id="chat_b",
        conversation_id="conv_b",
        base_dir=tmp_path,
    )
    assert diag_result["error"] is None
    assert isinstance(diag_result["output_refs"], list)
    assert isinstance(diag_result["findings_count"], int)


def test_get_conversation_state_returns_serializable_dict(tmp_path: Path) -> None:
    _ = submit_text_message(
        tenant_id="tenant_c",
        chat_id="chat_c",
        conversation_id="conv_c",
        text="hola",
        base_dir=tmp_path,
    )
    state = get_conversation_state(tenant_id="tenant_c", chat_id="chat_c", base_dir=tmp_path)
    json.dumps(state)
    assert "phase" in state
    assert "progressive_context" in state


def test_invalid_params_return_error_without_exception(tmp_path: Path) -> None:
    invalid_text = submit_text_message(
        tenant_id="",
        chat_id="chat_x",
        conversation_id="conv_x",
        text="hola",
        base_dir=tmp_path,
    )
    assert invalid_text["error"] is not None

    invalid_doc = submit_document(
        tenant_id="tenant_x",
        chat_id="chat_x",
        conversation_id="conv_x",
        document_path=tmp_path / "missing.xlsx",
        document_name="missing.xlsx",
        base_dir=tmp_path,
    )
    assert invalid_doc["error"] is not None

    invalid_state = get_conversation_state(tenant_id="", chat_id="chat_x", base_dir=tmp_path)
    assert invalid_state["error"] is not None


def test_source_has_no_forbidden_tokens_or_direct_smartpyme() -> None:
    source = Path("pymia/orchestration/os_tool_registry.py").read_text(encoding="utf-8").lower()
    assert "telegram" not in source
    assert "hermes" not in source
    assert "langgraph" not in source
    assert "openai" not in source
    assert "anthropic" not in source
    assert "pydantic_ai" not in source
    assert "pymia.smartpyme" not in source
