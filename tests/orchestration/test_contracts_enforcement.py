"""Contract guardrails anti-drift para Orchestration."""

from __future__ import annotations

import json
from pathlib import Path

from pymia.orchestration.conversation_adapter import adapt_text_message
from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import save_state


def test_graph_has_no_direct_smartpyme_imports() -> None:
    source = Path("pymia/orchestration/graph.py").read_text(encoding="utf-8").lower()
    assert "from pymia.smartpyme" not in source
    assert "import pymia.smartpyme" not in source


def test_conversation_adapter_has_no_telegram_hermes_langgraph() -> None:
    source = Path("pymia/orchestration/conversation_adapter.py").read_text(encoding="utf-8").lower()
    assert "telegram" not in source
    assert "hermes" not in source
    assert "langgraph" not in source


def test_pymia_state_persisted_payload_is_valid_json_and_has_required_fields(tmp_path: Path) -> None:
    state = PymIAState(
        tenant_id="tenant",
        chat_id="chat",
        conversation_id="conv",
        progressive_context={"stage": "anamnesis", "turns": [1, 2]},
        delivery_status="READY_TO_DELIVER",
        gate_verdict="PASS",
        delivery_summary="ready",
        output_refs=["/tmp/report.md"],
        findings_count=2,
    )
    save_state("tenant", "chat", state, tmp_path)

    state_file = tmp_path / "tenant" / "conversation_states.jsonl"
    assert state_file.exists()
    lines = [line for line in state_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 1

    for line in lines:
        payload = json.loads(line)
        assert isinstance(payload, dict)
        assert payload.get("progressive_context") == {"stage": "anamnesis", "turns": [1, 2]}
        assert payload.get("delivery_summary") == "ready"
        assert payload.get("output_refs") == ["/tmp/report.md"]
        assert payload.get("findings_count") == 2
        assert "delivery_package" not in payload


def test_progressive_context_after_adapter_is_json_serializable_and_input_immutable() -> None:
    original_context = {"fsm_state": {"phase": "INIT"}, "x": [1, 2]}
    snapshot = json.loads(json.dumps(original_context))
    result = adapt_text_message(
        text="hola",
        tenant_id="tenant",
        user_id="user",
        progressive_context=original_context,
    )
    json.dumps(result.updated_progressive_context)
    assert original_context == snapshot


def test_state_storage_writes_valid_jsonl(tmp_path: Path) -> None:
    state = PymIAState(tenant_id="tenant", chat_id="chat", conversation_id="conv")
    save_state("tenant", "chat", state, tmp_path)
    save_state("tenant", "chat", state, tmp_path)
    state_file = tmp_path / "tenant" / "conversation_states.jsonl"
    assert state_file.exists()
    lines = [line for line in state_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 2
    for line in lines:
        parsed = json.loads(line)
        assert isinstance(parsed, dict)


def test_audit_cli_has_required_commands() -> None:
    source = Path("pymia/orchestration/audit_cli.py").read_text(encoding="utf-8")
    assert '"list"' in source
    assert '"show"' in source
    assert '"history"' in source
    assert '"export"' in source
    assert '"verify"' not in source


def test_e2e_longitudinal_exists_and_has_at_least_three_tests() -> None:
    e2e_path = Path("tests/orchestration/test_e2e_longitudinal.py")
    assert e2e_path.exists()
    source = e2e_path.read_text(encoding="utf-8")
    assert source.count("def test_") >= 3


def test_contracts_doc_exists_and_mentions_required_terms() -> None:
    doc = Path("docs/CONTRACTS.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8").lower()
    assert "pymia os" in text
    assert "smartpyme" in text
    assert "telegram" in text
    assert "progressive_context" in text
    assert "conversation_adapter" in text
    assert "decision_trail" in text
    assert "objetos complejos" in text
