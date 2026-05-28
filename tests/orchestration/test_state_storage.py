"""Tests de persistencia de estado conversacional."""

import json
from pathlib import Path

from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import (
    export_conversation_jsonl,
    find_conversations_by_tenant,
    get_conversation_history,
    load_state,
    replay_conversation,
    save_state,
)


def test_save_state_creates_file(tmp_path: Path) -> None:
    """save_state crea archivo JSONL."""
    tenant_id = "test_tenant"
    chat_id = "12345"
    
    state = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="NEW",
    )
    
    save_state(tenant_id, chat_id, state, tmp_path)
    
    state_file = tmp_path / tenant_id / "conversation_states.jsonl"
    assert state_file.exists()


def test_save_state_appends(tmp_path: Path) -> None:
    """save_state hace append a archivo existente."""
    tenant_id = "test_tenant"
    chat_id = "12345"
    
    state1 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="NEW",
    )
    save_state(tenant_id, chat_id, state1, tmp_path)
    
    state2 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="EVIDENCE_RECEIVED",
    )
    save_state(tenant_id, chat_id, state2, tmp_path)
    
    state_file = tmp_path / tenant_id / "conversation_states.jsonl"
    lines = state_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2


def test_load_state_returns_latest(tmp_path: Path) -> None:
    """load_state retorna estado más reciente para chat_id."""
    tenant_id = "test_tenant"
    chat_id = "12345"
    
    state1 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="NEW",
    )
    save_state(tenant_id, chat_id, state1, tmp_path)
    
    state2 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="EVIDENCE_RECEIVED",
        intake_id="intake_001",
    )
    save_state(tenant_id, chat_id, state2, tmp_path)
    
    loaded = load_state(tenant_id, chat_id, tmp_path)
    
    assert loaded is not None
    assert loaded.phase == "EVIDENCE_RECEIVED"
    assert loaded.intake_id == "intake_001"


def test_load_state_returns_none_if_not_found(tmp_path: Path) -> None:
    """load_state retorna None si no existe estado."""
    loaded = load_state("nonexistent_tenant", "nonexistent_chat", tmp_path)
    assert loaded is None


def test_load_state_filters_by_chat_id(tmp_path: Path) -> None:
    """load_state filtra por chat_id correcto."""
    tenant_id = "test_tenant"
    chat_id_1 = "12345"
    chat_id_2 = "67890"
    
    state1 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id_1,
        conversation_id="conv_001",
        phase="NEW",
    )
    save_state(tenant_id, chat_id_1, state1, tmp_path)
    
    state2 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id_2,
        conversation_id="conv_002",
        phase="EVIDENCE_RECEIVED",
    )
    save_state(tenant_id, chat_id_2, state2, tmp_path)
    
    loaded1 = load_state(tenant_id, chat_id_1, tmp_path)
    loaded2 = load_state(tenant_id, chat_id_2, tmp_path)
    
    assert loaded1 is not None
    assert loaded1.phase == "NEW"
    assert loaded1.chat_id == chat_id_1
    
    assert loaded2 is not None
    assert loaded2.phase == "EVIDENCE_RECEIVED"
    assert loaded2.chat_id == chat_id_2


def test_save_state_preserves_decision_trail(tmp_path: Path) -> None:
    """save_state preserva decision_trail."""
    tenant_id = "test_tenant"
    chat_id = "12345"
    
    state = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="NEW",
    )
    state.add_decision("Test decision 1")
    state.add_decision("Test decision 2")
    
    save_state(tenant_id, chat_id, state, tmp_path)
    
    loaded = load_state(tenant_id, chat_id, tmp_path)
    
    assert loaded is not None
    assert len(loaded.decision_trail) == 2
    assert "Test decision 1" in loaded.decision_trail[0]
    assert "Test decision 2" in loaded.decision_trail[1]


def test_save_state_preserves_evidence_path(tmp_path: Path) -> None:
    """save_state preserva latest_evidence_path."""
    tenant_id = "test_tenant"
    chat_id = "12345"
    
    state = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id="conv_001",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=Path("/tmp/test.xlsx"),
    )
    
    save_state(tenant_id, chat_id, state, tmp_path)
    
    loaded = load_state(tenant_id, chat_id, tmp_path)
    
    assert loaded is not None
    assert loaded.latest_evidence_path == Path("/tmp/test.xlsx")


def test_replay_conversation_returns_latest(tmp_path: Path) -> None:
    tenant_id = "test_tenant"
    chat_id = "12345"

    save_state(
        tenant_id,
        chat_id,
        PymIAState(tenant_id=tenant_id, chat_id=chat_id, conversation_id="conv", phase="NEW"),
        tmp_path,
    )
    save_state(
        tenant_id,
        chat_id,
        PymIAState(
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id="conv",
            phase="READY_TO_EXECUTE",
        ),
        tmp_path,
    )

    loaded = replay_conversation(tenant_id, chat_id, tmp_path)
    assert loaded is not None
    assert loaded.phase == "READY_TO_EXECUTE"


def test_get_conversation_history_sorted_and_filtered(tmp_path: Path) -> None:
    tenant_id = "test_tenant"
    chat_id = "12345"
    other_chat_id = "99999"

    save_state(
        tenant_id,
        chat_id,
        PymIAState(tenant_id=tenant_id, chat_id=chat_id, conversation_id="conv_a", phase="NEW"),
        tmp_path,
    )
    save_state(
        tenant_id,
        other_chat_id,
        PymIAState(
            tenant_id=tenant_id,
            chat_id=other_chat_id,
            conversation_id="conv_b",
            phase="NEW",
        ),
        tmp_path,
    )
    save_state(
        tenant_id,
        chat_id,
        PymIAState(
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id="conv_a",
            phase="DELIVERED",
        ),
        tmp_path,
    )

    history = get_conversation_history(tenant_id, chat_id, tmp_path)
    assert len(history) == 2
    assert all(item["chat_id"] == chat_id for item in history)
    assert [item["phase"] for item in history] == ["NEW", "DELIVERED"]


def test_find_conversations_by_tenant_groups_by_conversation(tmp_path: Path) -> None:
    tenant_id = "test_tenant"
    chat_id_a = "chat_a"
    chat_id_b = "chat_b"

    first_state = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id_a,
        conversation_id="conv_1",
        phase="NEW",
    )
    save_state(tenant_id, chat_id_a, first_state, tmp_path)

    second_state = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id_b,
        conversation_id="conv_2",
        phase="EVIDENCE_RECEIVED",
        evidence_ids=["ev1", "ev2"],
    )
    save_state(tenant_id, chat_id_b, second_state, tmp_path)

    latest_conv_1 = PymIAState(
        tenant_id=tenant_id,
        chat_id=chat_id_a,
        conversation_id="conv_1",
        phase="DELIVERED",
        evidence_ids=["ev3"],
    )
    save_state(tenant_id, chat_id_a, latest_conv_1, tmp_path)

    conversations = find_conversations_by_tenant(tenant_id, tmp_path)
    assert len(conversations) == 2
    assert conversations[0]["last_updated"] >= conversations[1]["last_updated"]

    conv_1 = next(item for item in conversations if item["conversation_id"] == "conv_1")
    assert conv_1["last_phase"] == "DELIVERED"
    assert conv_1["chat_id"] == chat_id_a
    assert conv_1["evidence_count"] == 1


def test_export_conversation_jsonl_exports_filtered_history(tmp_path: Path) -> None:
    tenant_id = "test_tenant"
    chat_id = "12345"
    other_chat_id = "67890"

    save_state(
        tenant_id,
        chat_id,
        PymIAState(tenant_id=tenant_id, chat_id=chat_id, conversation_id="conv", phase="NEW"),
        tmp_path,
    )
    save_state(
        tenant_id,
        other_chat_id,
        PymIAState(
            tenant_id=tenant_id,
            chat_id=other_chat_id,
            conversation_id="conv_2",
            phase="NEW",
        ),
        tmp_path,
    )
    save_state(
        tenant_id,
        chat_id,
        PymIAState(
            tenant_id=tenant_id,
            chat_id=chat_id,
            conversation_id="conv",
            phase="DELIVERED",
        ),
        tmp_path,
    )

    output_path = tmp_path / "exports" / "chat_12345.jsonl"
    exported_count = export_conversation_jsonl(tenant_id, chat_id, tmp_path, output_path)

    assert exported_count == 2
    assert output_path.exists()
    lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert all(item["chat_id"] == chat_id for item in parsed)
    assert all("delivery_package" not in item for item in parsed)


def test_conversation_queries_return_empty_when_storage_missing(tmp_path: Path) -> None:
    assert replay_conversation("tenant", "chat", tmp_path) is None
    assert get_conversation_history("tenant", "chat", tmp_path) == []
    assert find_conversations_by_tenant("tenant", tmp_path) == []
    assert export_conversation_jsonl(
        "tenant",
        "chat",
        tmp_path,
        tmp_path / "exports" / "missing.jsonl",
    ) == 0


def test_get_conversation_history_raises_on_corrupt_jsonl(tmp_path: Path) -> None:
    tenant_id = "test_tenant"
    state_file = tmp_path / tenant_id / "conversation_states.jsonl"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("{bad json}\n", encoding="utf-8")

    try:
        get_conversation_history(tenant_id, "chat", tmp_path)
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert "Invalid JSONL" in str(exc)
