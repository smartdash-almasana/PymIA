"""Grafo mínimo de orquestación dinámica.

4 nodos:
1. normalize_event - normaliza evento, actualiza estado inicial
2. decide_route - decide qué ruta tomar
3. execute_static_capability - ejecuta capacidad estática
4. render_response - renderiza respuesta final

SIN integración Telegram todavía.
SIN dispatch real todavía.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Optional

from pymia.orchestration.state import PymIAState, PymIAEvent
from pymia.orchestration.state_storage import save_state, load_state

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


def execute_static_capability(state: PymIAState, event: PymIAEvent) -> PymIAState:
    """Nodo 3: Ejecuta la capacidad estática correspondiente.
    
    En CICLO 1: solo simula ejecución (sin dispatch real).
    En CICLO 2: conectará con intake, evidence, storage, gates, readiness.
    En CICLO 4: ejecutará dispatch real.
    """
    new_state = deepcopy(state)
    
    if new_state.phase == "EVIDENCE_RECEIVED":
        # Simular registro de evidencia
        new_state.intake_id = f"intake_{new_state.chat_id}_{len(new_state.evidence_ids) + 1}"
        new_state.evidence_ids.append(f"evidence_{len(new_state.evidence_ids) + 1}")
        new_state.add_decision(f"Intake created: {new_state.intake_id}")
        new_state.add_decision(f"Evidence registered: evidence_{len(new_state.evidence_ids)}")
    
    elif new_state.phase == "READY_TO_EXECUTE":
        # Simular preparación de candidate (sin dispatch todavía)
        new_state.runtime_candidate_status = "READY_TO_EXECUTE"
        new_state.add_decision("Candidate prepared: READY_TO_EXECUTE")
        # En CICLO 4: aquí se ejecutará dispatch_candidate
    
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
        response = f"{SENTINEL} Listo para ejecutar diagnóstico. (CICLO 1: sin dispatch real todavía)"
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
    4. execute_static_capability
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
    
    # 4. execute_static_capability
    state = execute_static_capability(state, event)
    
    # 5. render_response
    state, response = render_response(state)
    
    # 6. Persistir estado
    save_state(event.tenant_id, event.chat_id, state, base_dir)
    
    # 7. Retornar respuesta
    return response
