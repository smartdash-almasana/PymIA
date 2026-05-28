"""Tests E2E longitudinales de continuidad para Orchestration OS."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pymia.orchestration.graph import run_pymia_graph
from pymia.orchestration.state import PymIAEvent
from pymia.orchestration.state_storage import (
    export_conversation_jsonl,
    get_conversation_history,
    replay_conversation,
)


def _run_longitudinal_flow(*, base_dir: Path, tenant_id: str, chat_id: str, conversation_id: str) -> None:
    run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="hola",
        ),
        base_dir=base_dir,
    )

    doc_path = base_dir / "ventas.xlsx"
    pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 80},
            {"producto": "B", "ventas": 50, "costo": 40},
        ]
    ).to_excel(doc_path, index=False)
    run_pymia_graph(
        PymIAEvent(
            event_type="document_received",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            document_path=doc_path,
            document_name="ventas.xlsx",
        ),
        base_dir=base_dir,
    )

    run_pymia_graph(
        PymIAEvent(
            event_type="diagnostic_request",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="diagnosticalo",
        ),
        base_dir=base_dir,
    )

    run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="gracias",
        ),
        base_dir=base_dir,
    )


def test_e2e_text_then_document_then_diagnostic(tmp_path: Path) -> None:
    tenant_id = "tenant_e2e"
    chat_id = "chat_e2e"
    conversation_id = "conv_e2e"

    response_first = run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="hola",
        ),
        base_dir=tmp_path,
    )
    state_after_text = replay_conversation(tenant_id, chat_id, tmp_path)
    assert state_after_text is not None
    assert state_after_text.progressive_context != {}
    assert any("Conversation adapter handled text_message" in d for d in state_after_text.decision_trail)
    assert "Entiendo tu consulta. Para ayudarte necesito un Excel con datos operativos." not in response_first

    doc_path = tmp_path / "ventas.xlsx"
    pd.DataFrame([{"producto": "A", "ventas": 100, "costo": 80}]).to_excel(doc_path, index=False)
    run_pymia_graph(
        PymIAEvent(
            event_type="document_received",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            document_path=doc_path,
            document_name="ventas.xlsx",
        ),
        base_dir=tmp_path,
    )
    state_after_doc = replay_conversation(tenant_id, chat_id, tmp_path)
    assert state_after_doc is not None
    assert state_after_doc.intake_id is not None
    assert len(state_after_doc.evidence_ids) >= 1

    run_pymia_graph(
        PymIAEvent(
            event_type="diagnostic_request",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="diagnosticalo",
        ),
        base_dir=tmp_path,
    )
    run_pymia_graph(
        PymIAEvent(
            event_type="text_message",
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id=conversation_id,
            text="gracias",
        ),
        base_dir=tmp_path,
    )
    final_state = replay_conversation(tenant_id, chat_id, tmp_path)
    assert final_state is not None
    assert final_state.phase in {"DELIVERED", "BLOCKED", "FAILED", "READY_TO_EXECUTE", "NEW", "WAITING_FOR_EVIDENCE"}


def test_e2e_replay_reconstructs_full_case(tmp_path: Path) -> None:
    tenant_id = "tenant_replay"
    chat_id = "chat_replay"
    conversation_id = "conv_replay"
    _run_longitudinal_flow(
        base_dir=tmp_path, tenant_id=tenant_id, chat_id=chat_id, conversation_id=conversation_id
    )

    state = replay_conversation(tenant_id, chat_id, tmp_path)
    assert state is not None
    assert state.progressive_context != {}
    assert isinstance(state.decision_trail, list)
    assert len(state.decision_trail) >= 4
    assert state.phase in {"NEW", "WAITING_FOR_EVIDENCE", "BLOCKED", "FAILED", "DELIVERED", "READY_TO_EXECUTE"}
    if state.intake_id is not None:
        assert len(state.evidence_ids) >= 1


def test_e2e_audit_storage_history_export(tmp_path: Path) -> None:
    tenant_id = "tenant_audit"
    chat_id = "chat_audit"
    conversation_id = "conv_audit"
    _run_longitudinal_flow(
        base_dir=tmp_path, tenant_id=tenant_id, chat_id=chat_id, conversation_id=conversation_id
    )

    history = get_conversation_history(tenant_id, chat_id, tmp_path)
    assert len(history) >= 4

    output = tmp_path / "exports" / "audit_history.jsonl"
    exported = export_conversation_jsonl(tenant_id, chat_id, tmp_path, output)
    assert exported == len(history)
    assert output.exists()

    text = output.read_text(encoding="utf-8")
    assert "delivery_package" not in text
    lines = [line for line in text.splitlines() if line.strip()]
    assert len(lines) == exported
    for line in lines:
        row = json.loads(line)
        assert row.get("chat_id") == chat_id
