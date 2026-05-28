"""Tests de PymIAState y PymIAEvent."""

from datetime import datetime
from pathlib import Path

from pymia.orchestration.state import PymIAState, PymIAEvent


def test_pymia_state_creation() -> None:
    """Creación de PymIAState con campos mínimos."""
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
    )
    
    assert state.tenant_id == "test_tenant"
    assert state.chat_id == "12345"
    assert state.conversation_id == "conv_001"
    assert state.phase == "NEW"
    assert state.evidence_ids == []
    assert state.progressive_context == {}
    assert state.decision_trail == []
    assert state.errors == []


def test_pymia_state_progressive_context_default_is_empty_dict() -> None:
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
    )
    assert state.progressive_context == {}


def test_pymia_state_add_decision() -> None:
    """Agregar entrada al decision trail."""
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
    )
    
    state.add_decision("Document received: test.xlsx")
    
    assert len(state.decision_trail) == 1
    assert "Document received: test.xlsx" in state.decision_trail[0]
    assert state.decision_trail[0].startswith("[")


def test_pymia_state_add_error() -> None:
    """Agregar error."""
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
    )
    
    state.add_error("File not found")
    
    assert len(state.errors) == 1
    assert "File not found" in state.errors[0]
    assert state.errors[0].startswith("[")


def test_pymia_event_creation_text_message() -> None:
    """Creación de evento text_message."""
    event = PymIAEvent(
        event_type="text_message",
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
        text="Hola",
    )
    
    assert event.event_type == "text_message"
    assert event.text == "Hola"
    assert event.document_path is None
    assert isinstance(event.timestamp, datetime)


def test_pymia_event_creation_document_received() -> None:
    """Creación de evento document_received."""
    doc_path = Path("/tmp/test.xlsx")
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    
    assert event.event_type == "document_received"
    assert event.document_path == doc_path
    assert event.document_name == "test.xlsx"
    assert event.text is None


def test_pymia_state_with_evidence() -> None:
    """Estado con evidencia registrada."""
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
        phase="EVIDENCE_RECEIVED",
        intake_id="intake_001",
        evidence_ids=["evidence_001", "evidence_002"],
        latest_evidence_path=Path("/tmp/test.xlsx"),
    )
    
    assert state.phase == "EVIDENCE_RECEIVED"
    assert state.intake_id == "intake_001"
    assert len(state.evidence_ids) == 2
    assert state.latest_evidence_path == Path("/tmp/test.xlsx")


def test_pymia_state_serialization_roundtrip() -> None:
    """Estado puede serializarse a dict y reconstruirse."""
    original = PymIAState(
        tenant_id="test_tenant",
        chat_id="12345",
        conversation_id="conv_001",
        phase="EVIDENCE_RECEIVED",
        last_user_message="Test message",
        intake_id="intake_001",
        evidence_ids=["evidence_001"],
        latest_evidence_path=Path("/tmp/test.xlsx"),
    )
    original.add_decision("Test decision")
    
    # Serializar a dict (simulando lo que hace state_storage)
    state_dict = {
        "tenant_id": original.tenant_id,
        "chat_id": original.chat_id,
        "conversation_id": original.conversation_id,
        "phase": original.phase,
        "last_user_message": original.last_user_message,
        "progressive_context": {"step": "intake", "questions_done": 2},
        "intake_id": original.intake_id,
        "evidence_ids": original.evidence_ids,
        "latest_evidence_path": str(original.latest_evidence_path),
        "decision_trail": original.decision_trail,
        "errors": original.errors,
    }
    
    # Reconstruir
    reconstructed = PymIAState(
        tenant_id=state_dict["tenant_id"],
        chat_id=state_dict["chat_id"],
        conversation_id=state_dict["conversation_id"],
        phase=state_dict["phase"],
        last_user_message=state_dict["last_user_message"],
        progressive_context=state_dict["progressive_context"],
        intake_id=state_dict["intake_id"],
        evidence_ids=state_dict["evidence_ids"],
        latest_evidence_path=Path(state_dict["latest_evidence_path"]),
        decision_trail=state_dict["decision_trail"],
        errors=state_dict["errors"],
    )
    
    assert reconstructed.tenant_id == original.tenant_id
    assert reconstructed.chat_id == original.chat_id
    assert reconstructed.phase == original.phase
    assert reconstructed.progressive_context == {"step": "intake", "questions_done": 2}
    assert reconstructed.intake_id == original.intake_id
    assert reconstructed.evidence_ids == original.evidence_ids
    assert reconstructed.decision_trail == original.decision_trail


def test_state_source_does_not_reintroduce_complex_delivery_fields() -> None:
    source = Path("pymia/orchestration/state.py").read_text(encoding="utf-8")
    assert "delivery_package" not in source
    assert "Optional[object]" not in source
