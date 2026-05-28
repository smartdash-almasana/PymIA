"""Tests de persistencia de estado conversacional."""

from pathlib import Path

from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import save_state, load_state


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
