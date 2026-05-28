"""Grafo mínimo de orquestación dinámica.

4 nodos:
1. normalize_event - normaliza evento, actualiza estado inicial
2. decide_route - decide qué ruta tomar
3. execute_static_capability - ejecuta capacidad estática
4. render_response - renderiza respuesta final

CICLO 2: Integración con capas estáticas (intake, evidence, storage, gates, readiness, runtime_bridge).
SIN integración Telegram todavía.
SIN dispatch real todavía (eso es CICLO 4).

"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Optional

from pymia.orchestration.state import PymIAState, PymIAEvent
from pymia.orchestration.state_storage import save_state, load_state

# Capas estáticas smartpyme (CICLO 2)
from pymia.smartpyme.intake import create_intake_record
from pymia.smartpyme.evidence import create_evidence_record, SOURCE_KIND_UPLOADED_FILE
from pymia.smartpyme.storage import (
    save_intake_record,
    save_evidence_record,
    load_intake_record_by_id,
    load_evidence_records_by_intake_id,
)
from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
from pymia.smartpyme.readiness import evaluate_analysis_readiness
from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

SENTINEL = "[PymIA:TELEGRAM_RUNTIME]"
STORAGE_BASE_DIR = Path(".runtime/telegram_storage")


def normalize_event(state: PymIAState, event: PymIAEvent) -> PymIAState:
    """Nodo 1: Normaliza el evento y actualiza estado inicial.
    
    - Actualiza last_user_message
    - Si document_received: actualiza latest_evidence_path
    - Agrega entrada al decision_trail
    
    """
    new_state = deepcopy(state)
    new_state.last_user_message = event.text or f"[{event.event_type}]"
    
    if event.event_type == "document_received" and event.document_path:
        new_state.latest_evidence_path = event.document_path
        new_state.phase = "EVIDENCE_RECEIVED"
        new_state.add_decision(f"Document received: {event.document_name}")
    
    elif event.event_type == "diagnostic_request":
        new_state.add_decision("Diagnostic requested")
    
    elif event.event_type == "text_message":
        new_state.add_decision(f"Text message: {event.text[:50] if event.text else ''}")
    
    elif event.event_type == "system_error":
        new_state.phase = "FAILED"
        new_state.add_error(event.error_message or "Unknown error")
        new_state.add_decision(f"System error: {event.error_message}")
    
    return new_state


def decide_route(state: PymIAState, event: PymIAEvent) -> PymIAState:
    """Nodo 2: Decide qué ruta tomar basado en estado + evento.
    
    Rutas:
    - document_received → register_evidence
    - diagnostic_request + evidence → check_readiness
    - diagnostic_request + no evidence → ask_evidence
    - text_message → fallback_text
    
    """
    new_state = deepcopy(state)
    
    if event.event_type == "document_received":
        new_state.add_decision("Route: register_evidence")
        new_state.phase = "EVIDENCE_RECEIVED"
        new_state.pending_question = "¿Querés que analice este Excel?"
    
    elif event.event_type == "diagnostic_request":
        if new_state.latest_evidence_path and new_state.latest_evidence_path.exists():
            new_state.add_decision("Route: check_readiness (evidence available)")
            new_state.phase = "READY_TO_EXECUTE"
        else:
            new_state.add_decision("Route: ask_evidence (no evidence)")
            new_state.phase = "WAITING_FOR_EVIDENCE"
            new_state.pending_question = "Necesito un Excel para analizar. ¿Podés subirlo?"
    
    elif event.event_type == "text_message":
        new_state.add_decision("Route: fallback_text")
        new_state.phase = "NEW"
        new_state.pending_question = "Entiendo tu consulta. Para ayudarte necesito un Excel con datos operativos."
    
    elif event.event_type == "system_error":
        new_state.add_decision("Route: error_response")
        new_state.phase = "FAILED"
    
    return new_state


def execute_static_capability(state: PymIAState, event: PymIAEvent, base_dir: Path = STORAGE_BASE_DIR) -> PymIAState:
    """Nodo 3: Ejecuta la capacidad estática correspondiente.
    
    CICLO 2: Integración real con capas estáticas smartpyme:
    - document_received: create_intake_record + create_evidence_record + save
    - diagnostic_request + evidence: load_intake + load_evidences + evaluate_sufficiency + evaluate_readiness + prepare_runtime
    
    CICLO 4: ejecutará dispatch real.
    
    """
    new_state = deepcopy(state)
    
    if new_state.phase == "EVIDENCE_RECEIVED":
        # CICLO 2: Integración real con intake + evidence + storage
        try:
            # 1. Crear IntakeRecord
            raw_text = event.text or f"Documento recibido: {event.document_name or 'archivo'}"
            intake = create_intake_record(
                tenant_id=new_state.tenant_id,
                raw_text=raw_text,
            )
            save_intake_record(new_state.tenant_id, intake, base_dir=base_dir)
            new_state.intake_id = intake.intake_id
            new_state.add_decision(f"Intake created: {intake.intake_id}")
            
            # 2. Crear EvidenceRecord
            if event.document_path:
                evidence = create_evidence_record(
                    tenant_id=new_state.tenant_id,
                    intake_id=intake.intake_id,
                    evidence_type="excel_file",
                    source_kind=SOURCE_KIND_UPLOADED_FILE,
                    source_ref=str(event.document_path),
                    original_filename=event.document_name,
                )
                save_evidence_record(new_state.tenant_id, evidence, base_dir=base_dir)
                new_state.evidence_ids.append(evidence.evidence_id)
                new_state.add_decision(f"Evidence registered: {evidence.evidence_id}")
            
        except Exception as exc:
            new_state.phase = "FAILED"
            new_state.add_error(f"Intake/Evidence creation failed: {exc}")
            new_state.add_decision(f"Failed to create intake/evidence: {exc}")
    
    elif new_state.phase == "READY_TO_EXECUTE":
        # CICLO 2: Integración real con gates + readiness + runtime_bridge
        try:
            if not new_state.intake_id:
                new_state.phase = "BLOCKED"
                new_state.runtime_candidate_status = "BLOCKED"
                new_state.pending_question = "No hay intake registrado. Subí un archivo primero."
                new_state.add_decision("Blocked: no intake_id")
                new_state.add_decision("Runtime candidate: BLOCKED (no intake_id)")
                return new_state
            
            # 1. Cargar intake y evidences
            intake_dict = load_intake_record_by_id(new_state.tenant_id, new_state.intake_id, base_dir=base_dir)
            if intake_dict is None:
                new_state.phase = "BLOCKED"
                new_state.runtime_candidate_status = "BLOCKED"
                new_state.pending_question = f"Intake {new_state.intake_id} no encontrado."
                new_state.add_decision(f"Blocked: intake not found")
                new_state.add_decision("Runtime candidate: BLOCKED (intake not found)")
                return new_state
            
            evidence_dicts = load_evidence_records_by_intake_id(new_state.tenant_id, new_state.intake_id, base_dir=base_dir)
            
            # 2. Evaluar sufficiency
            sufficiency = evaluate_evidence_sufficiency(intake_dict, evidence_dicts)
            new_state.sufficiency_status = sufficiency.status
            new_state.add_decision(f"Evidence sufficiency: {sufficiency.status}")
            
            # 3. Evaluar readiness
            readiness = evaluate_analysis_readiness(intake_dict, sufficiency)
            new_state.readiness_status = readiness.status
            new_state.add_decision(f"Analysis readiness: {readiness.status}")
            
            # 4. Preparar runtime candidate
            candidate = prepare_runtime_execution(readiness)
            new_state.runtime_candidate_status = candidate.status
            new_state.add_decision(f"Runtime candidate: {candidate.status}")
            
            if candidate.status == "READY_TO_EXECUTE":
                new_state.phase = "READY_TO_EXECUTE"
                # En CICLO 4: aquí se ejecutará dispatch_candidate
            else:
                new_state.phase = "BLOCKED"
                reason = candidate.blocking_reasons[0] if candidate.blocking_reasons else "candidato no listo"
                new_state.pending_question = f"Diagnóstico bloqueado: {reason}"
                new_state.add_decision(f"Blocked: {reason}")
        
        except Exception as exc:
            new_state.phase = "FAILED"
            new_state.runtime_candidate_status = "FAILED"
            new_state.add_error(f"Readiness/Runtime preparation failed: {exc}")
            new_state.add_decision(f"Failed readiness/runtime: {exc}")
            new_state.add_decision("Runtime candidate: FAILED (exception)")
    
    elif new_state.phase == "WAITING_FOR_EVIDENCE":
        new_state.add_decision("Asking for evidence")
    
    elif new_state.phase == "NEW":
        new_state.add_decision("Fallback text response")
    
    elif new_state.phase == "FAILED":
        new_state.add_decision("Error response")
    
    return new_state


def render_response(state: PymIAState) -> tuple[PymIAState, str]:
    """Nodo 4: Renderiza respuesta final basada en estado.
    
    Retorna: (new_state, response_text)
    
    """
    new_state = deepcopy(state)
    
    if new_state.phase == "EVIDENCE_RECEIVED":
        response = f"{SENTINEL} Recibí tu archivo. {new_state.pending_question or ''}"
    
    elif new_state.phase == "READY_TO_EXECUTE":
        # En CICLO 4: aquí se ejecutará dispatch y se renderizará resultado real
        response = f"{SENTINEL} Listo para ejecutar diagnóstico. (CICLO 2: candidate preparado, sin dispatch real todavía)"
        new_state.add_decision("Response rendered: ready_to_execute")
    
    elif new_state.phase == "WAITING_FOR_EVIDENCE":
        response = f"{SENTINEL} {new_state.pending_question or 'Necesito evidencia.'}"
    
    elif new_state.phase == "NEW":
        response = f"{SENTINEL} {new_state.pending_question or 'Mensaje recibido.'}"
    
    elif new_state.phase == "BLOCKED":
        response = f"{SENTINEL} Bloqueado: {new_state.pending_question or 'motivo desconocido'}"
    
    elif new_state.phase == "FAILED":
        error_msg = new_state.errors[-1] if new_state.errors else "error desconocido"
        response = f"{SENTINEL} Error: {error_msg}"
    
    else:
        response = f"{SENTINEL} {new_state.pending_question or 'Mensaje recibido.'}"
    
    new_state.add_decision(f"Response rendered: {response[:50]}")
    
    return new_state, response


def run_pymia_graph(
    event: PymIAEvent,
    base_dir: Path = STORAGE_BASE_DIR,
) -> str:
    """Orquesta los 4 nodos del grafo y retorna respuesta final.
    
    Flujo:
    1. Cargar estado previo (si existe)
    2. normalize_event
    3. decide_route
    4. execute_static_capability (CICLO 2: integra capas estáticas)
    5. render_response
    6. Persistir estado
    7. Retornar respuesta
    
    """
    # 1. Cargar estado previo
    state = load_state(event.tenant_id, event.chat_id, base_dir)
    if state is None:
        state = PymIAState(
            tenant_id=event.tenant_id,
            chat_id=event.chat_id,
            conversation_id=event.conversation_id,
        )
    
    # 2. normalize_event
    state = normalize_event(state, event)
    
    # 3. decide_route
    state = decide_route(state, event)
    
    # 4. execute_static_capability (CICLO 2: con base_dir)
    state = execute_static_capability(state, event, base_dir)
    
    # 5. render_response
    state, response = render_response(state)
    
    # 6. Persistir estado
    save_state(event.tenant_id, event.chat_id, state, base_dir)
    
    # 7. Retornar respuesta
    return response
