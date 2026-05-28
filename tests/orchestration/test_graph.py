"""Tests del grafo de orquestación."""

from pathlib import Path

from pymia.orchestration.state import PymIAEvent
from pymia.orchestration.graph import (
    run_pymia_graph,
    normalize_event,
    decide_route,
    execute_static_capability,
    render_response,
    PymIAState,
    SENTINEL,
)


def test_normalize_event_updates_last_message() -> None:
    """normalize_event actualiza last_user_message."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
    )
    event = PymIAEvent(
        event_type="text_message",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="Hola",
    )
    
    new_state = normalize_event(state, event)
    
    assert new_state.last_user_message == "Hola"
    assert len(new_state.decision_trail) == 1


def test_normalize_event_handles_document() -> None:
    """normalize_event actualiza latest_evidence_path para documentos."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
    )
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        document_path=Path("/tmp/test.xlsx"),
        document_name="test.xlsx",
    )
    
    new_state = normalize_event(state, event)
    
    assert new_state.latest_evidence_path == Path("/tmp/test.xlsx")
    assert new_state.phase == "EVIDENCE_RECEIVED"
    assert "Document received" in new_state.decision_trail[0]


def test_decide_route_document_received() -> None:
    """decide_route para document_received."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
    )
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        document_path=Path("/tmp/test.xlsx"),
        document_name="test.xlsx",
    )
    
    new_state = decide_route(state, event)
    
    assert new_state.phase == "EVIDENCE_RECEIVED"
    assert "register_evidence" in new_state.decision_trail[-1]


def test_decide_route_diagnostic_with_evidence(tmp_path: Path) -> None:
    """decide_route para diagnostic_request con evidencia."""
    doc_path = tmp_path / "test.xlsx"
    doc_path.write_bytes(b"fake excel")
    
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=doc_path,
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    new_state = decide_route(state, event)
    
    assert new_state.phase == "READY_TO_EXECUTE"
    assert "check_readiness" in new_state.decision_trail[-1]


def test_decide_route_diagnostic_without_evidence() -> None:
    """decide_route para diagnostic_request sin evidencia."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="NEW",
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    new_state = decide_route(state, event)
    
    assert new_state.phase == "WAITING_FOR_EVIDENCE"
    assert "ask_evidence" in new_state.decision_trail[-1]


def test_execute_static_capability_register_evidence() -> None:
    """execute_static_capability crea intake + evidence."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=Path("/tmp/test.xlsx"),
    )
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        document_path=Path("/tmp/test.xlsx"),
        document_name="test.xlsx",
    )
    
    new_state = execute_static_capability(state, event)
    
    assert new_state.intake_id is not None
    assert len(new_state.evidence_ids) == 1
    assert "Intake created" in new_state.decision_trail[-2]
    assert "Evidence registered" in new_state.decision_trail[-1]


def test_execute_static_capability_check_readiness() -> None:
    """execute_static_capability prepara candidate."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="READY_TO_EXECUTE",
        latest_evidence_path=Path("/tmp/test.xlsx"),
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    new_state = execute_static_capability(state, event)
    
    assert new_state.runtime_candidate_status == "READY_TO_EXECUTE"
    assert "Candidate prepared" in new_state.decision_trail[-1]


def test_render_response_evidence_received() -> None:
    """render_response para EVIDENCE_RECEIVED."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
        pending_question="¿Querés que analice este Excel?",
    )
    
    new_state, response = render_response(state)
    
    assert SENTINEL in response
    assert "Recibí tu archivo" in response
    assert "¿Querés que analice este Excel?" in response


def test_render_response_ready_to_execute() -> None:
    """render_response para READY_TO_EXECUTE."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="READY_TO_EXECUTE",
    )
    
    new_state, response = render_response(state)
    
    assert SENTINEL in response
    assert "Listo para ejecutar" in response


def test_render_response_waiting_for_evidence() -> None:
    """render_response para WAITING_FOR_EVIDENCE."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="WAITING_FOR_EVIDENCE",
        pending_question="Necesito un Excel para analizar.",
    )
    
    new_state, response = render_response(state)
    
    assert SENTINEL in response
    assert "Necesito un Excel" in response


def test_run_pymia_graph_full_flow_document(tmp_path: Path) -> None:
    """run_pymia_graph flujo completo: document_received."""
    doc_path = tmp_path / "test.xlsx"
    doc_path.write_bytes(b"fake excel")
    
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    
    response = run_pymia_graph(event, base_dir=tmp_path)
    
    assert SENTINEL in response
    assert "Recibí tu archivo" in response
    
    # Verificar persistencia
    state_file = tmp_path / "test" / "conversation_states.jsonl"
    assert state_file.exists()


def test_run_pymia_graph_full_flow_diagnostic_without_evidence(tmp_path: Path) -> None:
    """run_pymia_graph flujo completo: diagnostic_request sin evidencia."""
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    response = run_pymia_graph(event, base_dir=tmp_path)
    
    assert SENTINEL in response
    assert "Necesito un Excel" in response


def test_run_pymia_graph_persists_state(tmp_path: Path) -> None:
    """run_pymia_graph persiste estado."""
    event = PymIAEvent(
        event_type="text_message",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="hola",
    )
    
    run_pymia_graph(event, base_dir=tmp_path)
    
    state_file = tmp_path / "test" / "conversation_states.jsonl"
    assert state_file.exists()
    
    lines = state_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1


def test_run_pymia_graph_recovers_state(tmp_path: Path) -> None:
    """run_pymia_graph recupera estado previo."""
    # Primer mensaje: document_received
    doc_path = tmp_path / "test.xlsx"
    doc_path.write_bytes(b"fake excel")
    
    event1 = PymIAEvent(
        event_type="document_received",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    run_pymia_graph(event1, base_dir=tmp_path)
    
    # Segundo mensaje: diagnostic_request (debería encontrar evidencia)
    event2 = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    response = run_pymia_graph(event2, base_dir=tmp_path)
    
    # Debería estar listo para ejecutar (no pedir evidencia)
    assert "Listo para ejecutar" in response
    assert "Necesito un Excel" not in response
