"""Tests del grafo de orquestación.

CICLO 2: Integración con capas estáticas smartpyme.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pandas as pd

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
from pymia.orchestration.state_storage import load_state

TEXTILE_FIXTURE = Path(__file__).resolve().parents[2] / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


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


def test_graph_text_message_invokes_adapter_and_updates_context() -> None:
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        progressive_context={"old": "value"},
    )
    event = PymIAEvent(
        event_type="text_message",
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        text="hola",
    )
    with patch("pymia.orchestration.graph.adapt_text_message") as adapter_mock:
        from pymia.orchestration.conversation_adapter import ConversationAdapterResult

        adapter_mock.return_value = ConversationAdapterResult(
            reply_text="respuesta adapter",
            updated_progressive_context={"new": "ctx"},
            phase_hint="CONVERSATIONAL",
            decision_trail_entry="adapter-ok",
        )
        new_state = decide_route(state, event)

    adapter_mock.assert_called_once()
    assert new_state.progressive_context == {"new": "ctx"}
    assert new_state.pending_question == "respuesta adapter"
    assert new_state.phase == "NEW"


def test_graph_text_message_phase_hint_mapping() -> None:
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
        text="hola",
    )
    from pymia.orchestration.conversation_adapter import ConversationAdapterResult

    with patch("pymia.orchestration.graph.adapt_text_message") as adapter_mock:
        adapter_mock.return_value = ConversationAdapterResult(
            reply_text="need evidence",
            updated_progressive_context={},
            phase_hint="NEEDS_EVIDENCE",
            decision_trail_entry="adapter-needs-evidence",
        )
        needs_evidence_state = decide_route(state, event)
    assert needs_evidence_state.phase == "WAITING_FOR_EVIDENCE"

    with patch("pymia.orchestration.graph.adapt_text_message") as adapter_mock:
        adapter_mock.return_value = ConversationAdapterResult(
            reply_text="blocked",
            updated_progressive_context={},
            phase_hint="BLOCKED",
            decision_trail_entry="adapter-blocked",
        )
        blocked_state = decide_route(state, event)
    assert blocked_state.phase == "BLOCKED"


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


def test_execute_static_capability_fail_closed_without_runtime_candidate(tmp_path: Path) -> None:
    state = PymIAState(
        tenant_id="test",
        chat_id="123",
        conversation_id="conv_1",
        phase="READY_TO_EXECUTE",
        intake_id=None,
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
    assert new_state.execution_status == "BLOCKED"
    assert any("Blocked: no intake_id" in d for d in new_state.decision_trail)


def test_decision_trail_includes_dispatch_gate_delivery(tmp_path: Path) -> None:
    doc_path = tmp_path / "test.xlsx"
    pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 80},
            {"producto": "B", "ventas": 50, "costo": 40},
        ]
    ).to_excel(doc_path, index=False)

    state_doc = PymIAState(
        tenant_id="tenant_x",
        chat_id="chat_x",
        conversation_id="conv_x",
        phase="EVIDENCE_RECEIVED",
        latest_evidence_path=doc_path,
    )
    event_doc = PymIAEvent(
        event_type="document_received",
        tenant_id="tenant_x",
        chat_id="chat_x",
        conversation_id="conv_x",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    state_after_doc = execute_static_capability(state_doc, event_doc, base_dir=tmp_path)

    state_diag = PymIAState(
        tenant_id="tenant_x",
        chat_id="chat_x",
        conversation_id="conv_x",
        phase="READY_TO_EXECUTE",
        intake_id=state_after_doc.intake_id,
        evidence_ids=list(state_after_doc.evidence_ids),
        latest_evidence_path=doc_path,
    )
    event_diag = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_x",
        chat_id="chat_x",
        conversation_id="conv_x",
        text="diagnosticalo",
    )
    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_x",
                "intake_id": state_after_doc.intake_id,
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    class _DispatchResult:
        status = "EXECUTED"
        findings_count = 2
        output_refs = [str(tmp_path / "diagnostic_report.md")]

        def to_dict(self):
            return {
                "tenant_id": "tenant_x",
                "intake_id": state_after_doc.intake_id,
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "EXECUTED",
                "output_refs": self.output_refs,
                "findings_count": self.findings_count,
                "raw_result": {"ok": True},
                "warnings": [],
            }

    class _Gate:
        verdict = "PASS"
        reasons = ["ok"]
        warnings = []

        def to_dict(self):
            return {"verdict": "PASS", "reasons": self.reasons, "warnings": self.warnings}

    class _Delivery:
        status = "READY_TO_DELIVER"
        summary = "Execution validated and ready to deliver."
        output_refs = [str(tmp_path / "diagnostic_report.md")]

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {"intake_id": state_after_doc.intake_id},
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev1"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: _DispatchResult(),
        "validate_execution_result": lambda *args, **kwargs: _Gate(),
        "build_delivery_package": lambda *args, **kwargs: _Delivery(),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        state_after_diag = execute_static_capability(state_diag, event_diag, base_dir=tmp_path)
    joined = "\n".join(state_after_diag.decision_trail)
    assert "Dispatch executed" in joined
    assert "Execution result gate evaluated" in joined
    assert "Delivery package built" in joined


def test_execute_static_capability_consumes_core_delivery_bridge_and_updates_state(tmp_path: Path) -> None:
    doc_path = tmp_path / "core_bridge.xlsx"
    doc_path.write_bytes(b"fake excel bridge")

    state = PymIAState(
        tenant_id="tenant_bridge",
        chat_id="chat_bridge",
        conversation_id="conv_bridge",
        phase="READY_TO_EXECUTE",
        intake_id="intake_bridge",
        evidence_ids=["ev_bridge"],
        latest_evidence_path=doc_path,
        progressive_context={
            "core_delivery_bridge_payload": {
                "case_id": "case_bridge",
                "intake_id": "intake_bridge",
                "structured_evidence": {
                    "tenant_id": "tenant_bridge",
                    "document_type": "xlsx_operational_evidence",
                    "source": "xlsx_upload",
                    "file_name": "core_bridge.xlsx",
                    "computed_variables": {
                        "ventas_total": 120000.0,
                        "costos_total": 60000.0,
                    },
                    "metadata": {},
                },
                "formula_gate_results": [
                    {
                        "formula_id": "PYME_026_rotacion_inventario",
                        "required_variables": ["ventas_total", "costos_total"],
                        "available_variables": ["costos_total", "ventas_total"],
                        "missing_variables": [],
                        "status": "READY",
                    }
                ],
                "evidence_gate_decisions": [
                    {
                        "formula_id": "PYME_026_rotacion_inventario",
                        "decision": "ALLOW_EXECUTION",
                        "missing_variables": [],
                    }
                ],
                "diagnostic_core_result": {
                    "case_id": "case_bridge",
                    "tenant_id": "tenant_bridge",
                    "status": "READY",
                    "formula_results": [
                        {
                            "formula_id": "PYME_026_rotacion_inventario",
                            "status": "READY",
                            "value": 2.5,
                            "source_refs": ["sheet://ventas", "sheet://costos"],
                            "blocking_reason": None,
                        }
                    ],
                    "diagnostic_results": [
                        {
                            "pathology_code": "INV_001",
                            "status": "CANDIDATE",
                            "formula_id": "PYME_026_rotacion_inventario",
                            "reason": "Low inventory rotation signal.",
                            "evidence_refs": ["sheet://ventas", "sheet://costos"],
                        }
                    ],
                    "findings": [
                        {
                            "finding_id": "finding-bridge-1",
                            "pathology_code": "INV_001",
                            "formula_id": "PYME_026_rotacion_inventario",
                            "status": "CANDIDATE",
                            "summary": "Inventory rotation below threshold.",
                            "evidence_refs": ["sheet://ventas", "sheet://costos"],
                        }
                    ],
                    "missing_evidence": [],
                    "blocked_reasons": [],
                },
            }
        },
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_bridge",
        chat_id="chat_bridge",
        conversation_id="conv_bridge",
        text="diagnosticalo",
    )

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_bridge",
                "intake_id": "intake_bridge",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {"intake_id": "intake_bridge"},
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev_bridge"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy dispatch should not run when core delivery bridge payload exists")
        ),
        "validate_execution_result": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy execution gate should not run when core delivery bridge payload exists")
        ),
        "build_delivery_package": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy delivery package should not run when core delivery bridge payload exists")
        ),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        new_state = execute_static_capability(state, event, base_dir=tmp_path)

    assert new_state.phase == "DELIVERED"
    assert new_state.gate_verdict == "PASS"
    assert new_state.delivery_status == "READY_TO_DELIVER"
    assert len(new_state.output_refs) >= 3
    assert new_state.findings_count == 1
    assert any("Core delivery bridge consumed" in d for d in new_state.decision_trail)
    assert all(Path(ref).exists() for ref in new_state.output_refs)


def test_execute_static_capability_produces_and_consumes_core_delivery_bridge_payload(tmp_path: Path) -> None:
    doc_path = tmp_path / "core_bridge_auto.xlsx"
    doc_path.write_bytes(b"fake excel bridge auto")

    state = PymIAState(
        tenant_id="tenant_bridge_auto",
        chat_id="chat_bridge_auto",
        conversation_id="conv_bridge_auto",
        phase="READY_TO_EXECUTE",
        intake_id="intake_bridge_auto",
        evidence_ids=["ev_bridge_auto"],
        latest_evidence_path=doc_path,
        progressive_context={
            "structured_evidence": {
                "tenant_id": "tenant_bridge_auto",
                "document_type": "xlsx_operational_evidence",
                "source": "xlsx_upload",
                "file_name": "core_bridge_auto.xlsx",
                "computed_variables": {
                    "main_sku_sales": 80000.0,
                    "total_sales": 120000.0,
                },
                "metadata": {
                    "variable_source_refs": {
                        "main_sku_sales": ["sheet://ventas!A:A"],
                        "total_sales": ["sheet://ventas!B:B"],
                    }
                },
            },
            "formula_ids": ["PYME_033_concentracion_sku"],
            "hypothesis_codes": ["PYME_033"],
        },
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_bridge_auto",
        chat_id="chat_bridge_auto",
        conversation_id="conv_bridge_auto",
        text="diagnosticalo",
    )

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_bridge_auto",
                "intake_id": "intake_bridge_auto",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {"intake_id": "intake_bridge_auto"},
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev_bridge_auto"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy dispatch should not run when M39 produces bridge payload")
        ),
        "validate_execution_result": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy execution gate should not run when M39 produces bridge payload")
        ),
        "build_delivery_package": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy delivery package should not run when M39 produces bridge payload")
        ),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        new_state = execute_static_capability(state, event, base_dir=tmp_path)

    payload = new_state.progressive_context.get("core_delivery_bridge_payload")
    assert isinstance(payload, dict)
    assert payload["formula_gate_results"][0]["status"] == "READY"
    assert new_state.phase == "DELIVERED"
    assert new_state.gate_verdict == "PASS"
    assert new_state.delivery_status == "READY_TO_DELIVER"
    assert new_state.output_refs
    assert new_state.findings_count == 1
    assert all(Path(ref).exists() for ref in new_state.output_refs)


def test_execute_static_capability_produces_blocking_bridge_payload_when_evidence_is_insufficient(tmp_path: Path) -> None:
    doc_path = tmp_path / "core_bridge_blocked.xlsx"
    doc_path.write_bytes(b"fake excel bridge blocked")

    state = PymIAState(
        tenant_id="tenant_bridge_blocked",
        chat_id="chat_bridge_blocked",
        conversation_id="conv_bridge_blocked",
        phase="READY_TO_EXECUTE",
        intake_id="intake_bridge_blocked",
        evidence_ids=["ev_bridge_blocked"],
        latest_evidence_path=doc_path,
        progressive_context={
            "structured_evidence": {
                "tenant_id": "tenant_bridge_blocked",
                "document_type": "xlsx_operational_evidence",
                "source": "xlsx_upload",
                "file_name": "core_bridge_blocked.xlsx",
                "computed_variables": {
                    "sale_price": 1000.0,
                    "costs": 700.0,
                },
                "metadata": {},
            },
            "formula_ids": ["REN_001_margen_neto_real"],
            "hypothesis_codes": ["REN_001"],
        },
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_bridge_blocked",
        chat_id="chat_bridge_blocked",
        conversation_id="conv_bridge_blocked",
        text="diagnosticalo",
    )

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_bridge_blocked",
                "intake_id": "intake_bridge_blocked",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {"intake_id": "intake_bridge_blocked"},
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev_bridge_blocked"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy dispatch should not run when M39 produces blocking bridge payload")
        ),
        "validate_execution_result": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy execution gate should not run when M39 produces blocking bridge payload")
        ),
        "build_delivery_package": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy delivery package should not run when M39 produces blocking bridge payload")
        ),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        new_state = execute_static_capability(state, event, base_dir=tmp_path)

    payload = new_state.progressive_context.get("core_delivery_bridge_payload")
    assert isinstance(payload, dict)
    assert payload["formula_gate_results"][0]["status"] == "MISSING_INPUTS"
    assert payload["formula_gate_results"][0]["missing_variables"] == ["taxes"]
    assert payload["diagnostic_core_result"]["formula_results"] == []
    assert payload["diagnostic_core_result"]["missing_evidence"] == ["taxes"]
    assert new_state.phase == "BLOCKED"
    assert new_state.gate_verdict == "BLOCKED"
    assert new_state.delivery_status == "BLOCKED"
    assert new_state.findings_count == 0
    assert new_state.output_refs


def test_graph_populates_progressive_context_with_structured_evidence_and_formula_ids(tmp_path: Path) -> None:
    doc_path = tmp_path / "structured_context.xlsx"
    doc_path.write_bytes(b"fake excel context")

    state = PymIAState(
        tenant_id="tenant_m40",
        chat_id="chat_m40",
        conversation_id="conv_m40",
        phase="READY_TO_EXECUTE",
        intake_id="intake_m40",
        evidence_ids=["ev_m40"],
        latest_evidence_path=doc_path,
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_m40",
        chat_id="chat_m40",
        conversation_id="conv_m40",
        text="diagnosticalo",
    )

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_m40",
                "intake_id": "intake_m40",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {
            "intake_id": "intake_m40",
            "evidence_requests": [
                {"formula_ids": ["PYME_033_concentracion_sku"]},
            ],
        },
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev_m40"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy dispatch should not run when M40+M39 path is available")
        ),
        "validate_execution_result": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy execution gate should not run when M40+M39 path is available")
        ),
        "build_delivery_package": lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy delivery package should not run when M40+M39 path is available")
        ),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        with patch("pymia.orchestration.graph._structured_evidence_builder_deps") as builder_deps:
            builder_deps.return_value = {
                "build_structured_evidence_context": lambda **kwargs: {
                    "structured_evidence": {
                        "tenant_id": "tenant_m40",
                        "document_type": "xlsx_operational_evidence",
                        "source": "xlsx_upload",
                        "file_name": "structured_context.xlsx",
                        "computed_variables": {
                            "main_sku_sales": 80000.0,
                            "total_sales": 120000.0,
                        },
                        "metadata": {},
                    },
                    "formula_ids": ["PYME_033_concentracion_sku"],
                }
            }
            new_state = execute_static_capability(state, event, base_dir=tmp_path)

    assert isinstance(new_state.progressive_context.get("structured_evidence"), dict)
    assert new_state.progressive_context.get("formula_ids") == ["PYME_033_concentracion_sku"]
    assert new_state.phase == "DELIVERED"
    assert new_state.gate_verdict == "PASS"
    assert new_state.delivery_status == "READY_TO_DELIVER"
    assert new_state.output_refs
    assert new_state.findings_count == 1


def test_graph_does_not_collapse_when_structured_evidence_population_fails(tmp_path: Path) -> None:
    doc_path = tmp_path / "structured_context_fail.xlsx"
    doc_path.write_bytes(b"fake excel context fail")
    legacy_report = tmp_path / "diagnostic_report.md"
    legacy_report.write_text("legacy ok", encoding="utf-8")

    state = PymIAState(
        tenant_id="tenant_m40_fail",
        chat_id="chat_m40_fail",
        conversation_id="conv_m40_fail",
        phase="READY_TO_EXECUTE",
        intake_id="intake_m40_fail",
        evidence_ids=["ev_m40_fail"],
        latest_evidence_path=doc_path,
    )
    event = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_m40_fail",
        chat_id="chat_m40_fail",
        conversation_id="conv_m40_fail",
        text="diagnosticalo",
    )

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_m40_fail",
                "intake_id": "intake_m40_fail",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    class _DispatchResult:
        status = "EXECUTED"
        findings_count = 2
        output_refs = [str(legacy_report)]

        def to_dict(self):
            return {
                "tenant_id": "tenant_m40_fail",
                "intake_id": "intake_m40_fail",
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "EXECUTED",
                "output_refs": self.output_refs,
                "findings_count": self.findings_count,
                "raw_result": {"ok": True},
                "warnings": [],
            }

    class _Gate:
        verdict = "PASS"
        reasons = ["ok"]
        warnings = []

        def to_dict(self):
            return {"verdict": self.verdict, "reasons": self.reasons, "warnings": self.warnings}

    class _Delivery:
        status = "READY_TO_DELIVER"
        summary = "Execution validated and ready to deliver."
        output_refs = [str(legacy_report)]

    deps = {
        "load_intake_record_by_id": lambda *args, **kwargs: {
            "intake_id": "intake_m40_fail",
            "evidence_requests": [{"formula_ids": ["PYME_033_concentracion_sku"]}],
        },
        "load_evidence_records_by_intake_id": lambda *args, **kwargs: [{"evidence_id": "ev_m40_fail"}],
        "evaluate_evidence_sufficiency": lambda *args, **kwargs: type("S", (), {"status": "READY"})(),
        "evaluate_analysis_readiness": lambda *args, **kwargs: type("R", (), {"status": "READY"})(),
        "prepare_runtime_execution": lambda *args, **kwargs: _Candidate(),
        "dispatch_candidate": lambda *args, **kwargs: _DispatchResult(),
        "validate_execution_result": lambda *args, **kwargs: _Gate(),
        "build_delivery_package": lambda *args, **kwargs: _Delivery(),
    }

    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        with patch("pymia.orchestration.graph._structured_evidence_builder_deps") as builder_deps:
            builder_deps.return_value = {
                "build_structured_evidence_context": lambda **kwargs: (_ for _ in ()).throw(
                    RuntimeError("parse failed")
                )
            }
            new_state = execute_static_capability(state, event, base_dir=tmp_path)

    assert "structured_evidence" not in new_state.progressive_context
    assert "formula_ids" not in new_state.progressive_context
    assert new_state.phase == "DELIVERED"
    assert new_state.gate_verdict == "PASS"
    assert new_state.delivery_status == "READY_TO_DELIVER"
    assert new_state.output_refs == [str(legacy_report)]
    assert any("Structured evidence context population failed" in d for d in new_state.decision_trail)


def test_run_pymia_graph_real_fixture_replays_core_delivery_bridge_end_to_end(tmp_path: Path) -> None:
    assert TEXTILE_FIXTURE.exists()

    event_doc = PymIAEvent(
        event_type="document_received",
        tenant_id="tenant_m41",
        chat_id="chat_m41",
        conversation_id="conv_m41",
        document_path=TEXTILE_FIXTURE,
        document_name=TEXTILE_FIXTURE.name,
        text="Necesito analizar margen, cobranzas y stock de este Excel.",
    )
    response_doc = run_pymia_graph(event_doc, base_dir=tmp_path)
    assert SENTINEL in response_doc

    state_after_doc = load_state("tenant_m41", "chat_m41", tmp_path)
    assert state_after_doc is not None
    assert state_after_doc.intake_id is not None
    assert state_after_doc.evidence_ids

    real_deps = __import__("pymia.orchestration.graph", fromlist=["_smartpyme_deps"])._smartpyme_deps()

    class _Candidate:
        status = "READY_TO_EXECUTE"
        blocking_reasons: list[str] = []

        def to_dict(self):
            return {
                "tenant_id": "tenant_m41",
                "intake_id": state_after_doc.intake_id,
                "runtime_classification": "excel_diagnostic",
                "microservice_name": "excel_diagnostic_worker",
                "status": "READY_TO_EXECUTE",
                "can_dispatch": True,
            }

    deps = dict(real_deps)
    deps["evaluate_evidence_sufficiency"] = lambda *args, **kwargs: type("S", (), {"status": "READY"})()
    deps["evaluate_analysis_readiness"] = lambda *args, **kwargs: type("R", (), {"status": "READY"})()
    deps["prepare_runtime_execution"] = lambda *args, **kwargs: _Candidate()
    deps["dispatch_candidate"] = lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("legacy dispatch should not run when M40+M39+M38 path is available")
    )
    deps["validate_execution_result"] = lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("legacy execution gate should not run when M40+M39+M38 path is available")
    )
    deps["build_delivery_package"] = lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("legacy delivery package should not run when M40+M39+M38 path is available")
    )

    event_diag = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_m41",
        chat_id="chat_m41",
        conversation_id="conv_m41",
        text="diagnosticalo",
    )
    with patch("pymia.orchestration.graph._smartpyme_deps", return_value=deps):
        response_diag = run_pymia_graph(event_diag, base_dir=tmp_path)

    assert SENTINEL in response_diag
    final_state = load_state("tenant_m41", "chat_m41", tmp_path)
    assert final_state is not None

    structured_evidence = final_state.progressive_context.get("structured_evidence")
    formula_ids = final_state.progressive_context.get("formula_ids")
    bridge_payload = final_state.progressive_context.get("core_delivery_bridge_payload")

    assert isinstance(structured_evidence, dict)
    assert structured_evidence["file_name"] == TEXTILE_FIXTURE.name
    assert structured_evidence["computed_variables"]
    assert isinstance(formula_ids, list)
    assert formula_ids
    assert isinstance(bridge_payload, dict)

    gate_results = bridge_payload["formula_gate_results"]
    diagnostic_core_result = bridge_payload["diagnostic_core_result"]
    executed_formula_ids = [
        item["formula_id"] for item in diagnostic_core_result["formula_results"]
    ]
    blocked_formula_ids = [
        item["formula_id"]
        for item in gate_results
        if item["status"] == "MISSING_INPUTS"
    ]

    for formula_id in blocked_formula_ids:
        assert formula_id not in executed_formula_ids

    assert final_state.phase in {"DELIVERED", "BLOCKED"}
    assert final_state.gate_verdict in {"PASS", "BLOCKED"}
    assert final_state.delivery_status in {"READY_TO_DELIVER", "BLOCKED"}
    assert isinstance(final_state.delivery_summary, str) and final_state.delivery_summary
    assert isinstance(final_state.output_refs, list)
    assert all(Path(ref).exists() for ref in final_state.output_refs)
    assert isinstance(final_state.findings_count, int)
    assert any("Structured evidence context populated" in d for d in final_state.decision_trail)
    assert any("Core delivery bridge payload produced" in d for d in final_state.decision_trail)
    assert any("Core delivery bridge consumed" in d for d in final_state.decision_trail)
    if final_state.phase == "DELIVERED":
        assert final_state.delivery_summary in response_diag
    if final_state.phase == "BLOCKED":
        assert final_state.pending_question
        assert final_state.pending_question in response_diag


def test_state_serializable_runtime_fields() -> None:
    state = PymIAState(
        tenant_id="tenant_s",
        chat_id="chat_s",
        conversation_id="conv_s",
        execution_status="EXECUTED",
        gate_verdict="PASS",
        delivery_status="READY_TO_DELIVER",
        delivery_summary="Execution validated and ready to deliver.",
        output_refs=["/tmp/report.md"],
        findings_count=3,
    )
    payload = {
        "execution_status": state.execution_status,
        "gate_verdict": state.gate_verdict,
        "delivery_status": state.delivery_status,
        "delivery_summary": state.delivery_summary,
        "output_refs": state.output_refs,
        "findings_count": state.findings_count,
    }
    json.dumps(payload)


def test_graph_module_has_no_telegram_or_hermes_imports() -> None:
    from pymia.orchestration import graph as graph_module

    source = Path(graph_module.__file__).read_text(encoding="utf-8").lower()
    assert "import hermes" not in source
    assert "from hermes" not in source
    assert "import telegram" not in source
    assert "from telegram" not in source


def test_graph_has_no_direct_smartpyme_imports() -> None:
    from pymia.orchestration import graph as graph_module

    source = Path(graph_module.__file__).read_text(encoding="utf-8")
    assert "from pymia.smartpyme" not in source


def test_delivered_state_has_no_delivery_package_and_jsonl_omits_it(tmp_path: Path) -> None:
    doc_path = tmp_path / "test.xlsx"
    pd.DataFrame(
        [
            {"producto": "A", "ventas": 100, "costo": 80},
            {"producto": "B", "ventas": 50, "costo": 40},
        ]
    ).to_excel(doc_path, index=False)

    event_doc = PymIAEvent(
        event_type="document_received",
        tenant_id="tenant_c4b",
        chat_id="chat_c4b",
        conversation_id="conv_c4b",
        document_path=doc_path,
        document_name="test.xlsx",
    )
    run_pymia_graph(event_doc, base_dir=tmp_path)

    event_diag = PymIAEvent(
        event_type="diagnostic_request",
        tenant_id="tenant_c4b",
        chat_id="chat_c4b",
        conversation_id="conv_c4b",
        text="diagnosticalo",
    )
    run_pymia_graph(event_diag, base_dir=tmp_path)

    state = load_state("tenant_c4b", "chat_c4b", tmp_path)
    assert state is not None
    # Contrato 4B: no atributo delivery_package
    assert not hasattr(state, "delivery_package")

    # Estado serializable mínimo presente
    assert state.phase in {"DELIVERED", "BLOCKED", "FAILED"}
    if state.phase == "DELIVERED":
        assert isinstance(state.delivery_summary, str) and state.delivery_summary
        assert isinstance(state.output_refs, list)
        assert all(isinstance(x, str) for x in state.output_refs)
        assert isinstance(state.findings_count, int)

    state_file = tmp_path / "tenant_c4b" / "conversation_states.jsonl"
    raw = state_file.read_text(encoding="utf-8")
    assert "delivery_package" not in raw
