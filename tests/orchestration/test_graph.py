"""Tests del grafo de orquestación.

CICLO 2: Integración con capas estáticas smartpyme.
"""

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
from pymia.smartpyme.storage import (
    load_intake_records,
    load_evidence_records_by_intake_id,
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


# ---------------------------------------------------------------------------
# CICLO 2: Tests de integración con capas estáticas
# ---------------------------------------------------------------------------


def test_execute_static_capability_creates_intake_and_evidence(tmp_path: Path) -> None:
    """CICLO 2: execute_static_capability crea IntakeRecord + EvidenceRecord reales."""
    doc_path = tmp_path / "test.xlsx"
    doc_path.write_bytes(b"fake excel content")
    
    state = PymIAState(
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=doc_path,
    )
    event = PymIAEvent(
        event_type="document_received",
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    
    new_state = execute_static_capability(state, event, base_dir=tmp_path)
    
    # Verificar que se crearon IDs
    assert new_state.intake_id is not None
    assert len(new_state.evidence_ids) == 1
    
    # Verificar que se persistieron en storage
    intakes = load_intake_records("test_tenant", base_dir=tmp_path)
    assert len(intakes) == 1
    assert intakes[0]["intake_id"] == new_state.intake_id
    
    evidences = load_evidence_records_by_intake_id("test_tenant", new_state.intake_id, base_dir=tmp_path)
    assert len(evidences) == 1
    assert evidences[0]["evidence_id"] == new_state.evidence_ids[0]
    assert evidences[0]["source_ref"] == str(doc_path)
    
    # Verificar decision trail
    assert any("Intake created" in d for d in new_state.decision_trail)
    assert any("Evidence registered" in d for d in new_state.decision_trail)


def test_execute_static_capability_evaluates_readiness(tmp_path: Path) -> None:
    """CICLO 2: execute_static_capability evalúa sufficiency + readiness + runtime."""
    # Primero crear intake + evidence vía document_received
    doc_path = tmp_path / "test.xlsx"
    doc_path.write_bytes(b"fake excel")
    
    state1 = PymIAState(
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=doc_path,
    )
    event1 = PymIAEvent(
        event_type="document_received",
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    state_after_doc = execute_static_capability(state1, event1, base_dir=tmp_path)
    
    # Ahora evaluar readiness vía diagnostic_request
    state2 = PymIAState(
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        phase="READY_TO_EXECUTE",
        intake_id=state_after_doc.intake_id,
        evidence_ids=list(state_after_doc.evidence_ids),
        latest_evidence_path=doc_path,
    )
    event2 = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test_tenant",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    new_state = execute_static_capability(state2, event2, base_dir=tmp_path)
    
    # Verificar que se evaluaron los gates
    assert new_state.sufficiency_status is not None
    assert new_state.readiness_status is not None
    assert new_state.runtime_candidate_status is not None
    
    # Verificar decision trail
    assert any("Evidence sufficiency" in d for d in new_state.decision_trail)
    assert any("Analysis readiness" in d for d in new_state.decision_trail)
    assert any("Runtime candidate" in d for d in new_state.decision_trail)


def test_execute_static_capability_blocks_when_no_intake(tmp_path: Path) -> None:
    """CICLO 2: execute_static_capability bloquea si no hay intake_id."""
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="READY_TO_EXECUTE",
        intake_id=None,  # Sin intake
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    
    new_state = execute_static_capability(state, event, base_dir=tmp_path)
    
    assert new_state.phase == "BLOCKED"
    assert new_state.runtime_candidate_status == "BLOCKED"
    assert new_state.pending_question is not None
    assert "intake" in new_state.pending_question.lower()


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
    
    # Verificar persistencia de estado
    state_file = tmp_path / "test" / "conversation_states.jsonl"
    assert state_file.exists()
    
    # CICLO 2: Verificar que se crearon intake + evidence en storage
    intakes = load_intake_records("test", base_dir=tmp_path)
    assert len(intakes) == 1


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
    """CICLO 2: run_pymia_graph recupera estado previo y evalúa readiness."""
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
    
    # Verificar que se creó intake + evidence
    intakes = load_intake_records("test", base_dir=tmp_path)
    assert len(intakes) == 1
    
    # Segundo mensaje: diagnostic_request (debería encontrar evidencia y evaluar readiness)
    event2 = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="diagnosticalo",
    )
    response = run_pymia_graph(event2, base_dir=tmp_path)
    
    # Debería estar listo para ejecutar o bloqueado (dependiendo de sufficiency)
    assert SENTINEL in response
    # No debería pedir evidencia de nuevo
    assert "Necesito un Excel" not in response


def test_run_pymia_graph_document_then_diagnostic_full_cycle(tmp_path: Path) -> None:
    """CICLO 2: Flujo completo document_received → diagnostic_request con integración real."""
    doc_path = tmp_path / "ventas.xlsx"
    doc_path.write_bytes(b"fake excel with ventas data")
    
    # Paso 1: document_received
    event_doc = PymIAEvent(
        event_type="document_received",
        tenant_id="tenant_abc",
        chat_id="chat_456",
        conversation_id="conv_789",
        document_path=doc_path,
        document_name="ventas.xlsx",
    )
    response1 = run_pymia_graph(event_doc, base_dir=tmp_path)
    
    assert SENTINEL in response1
    assert "Recibí tu archivo" in response1
    
    # Verificar intake + evidence creados
    intakes = load_intake_records("tenant_abc", base_dir=tmp_path)
    assert len(intakes) == 1
    intake_id = intakes[0]["intake_id"]
    
    evidences = load_evidence_records_by_intake_id("tenant_abc", intake_id, base_dir=tmp_path)
    assert len(evidences) == 1
    assert evidences[0]["original_filename"] == "ventas.xlsx"
    
    # Paso 2: diagnostic_request
    event_diag = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_abc",
        chat_id="chat_456",
        conversation_id="conv_789",
        text="diagnosticalo",
    )
    response2 = run_pymia_graph(event_diag, base_dir=tmp_path)
    
    assert SENTINEL in response2
    # Debería evaluar readiness (no pedir evidencia de nuevo)
    assert "Necesito un Excel" not in response2


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
