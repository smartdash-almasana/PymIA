"""Grafo mínimo de orquestación dinámica.

4 nodos:
1. normalize_event - normaliza evento, actualiza estado inicial
2. decide_route - decide qué ruta tomar
3. execute_static_capability - ejecuta capacidad estática
4. render_response - renderiza respuesta final

CICLO 2: Integración con capas estáticas (intake, evidence, storage, gates, readiness, runtime_bridge).
CICLO 4: Integración de ejecución y entrega (dispatch, execution_result_gate, delivery_package).
SIN integración Telegram todavía.

"""

from __future__ import annotations

from copy import deepcopy
from importlib import import_module
from pathlib import Path
from typing import Any, Optional

from pymia.orchestration.state import PymIAState, PymIAEvent
from pymia.orchestration.state_storage import save_state, load_state
from pymia.orchestration.conversation_adapter import adapt_text_message

SENTINEL = "[PymIA:TELEGRAM_RUNTIME]"
STORAGE_BASE_DIR = Path(".runtime/telegram_storage")


def _smartpyme_deps() -> dict[str, Any]:
    """Carga lazy de dependencias SmartPyme para evitar acoplamiento en imports de módulo."""
    intake = import_module("pymia.smartpyme.intake")
    evidence = import_module("pymia.smartpyme.evidence")
    storage = import_module("pymia.smartpyme.storage")
    evidence_gate = import_module("pymia.smartpyme.evidence_gate")
    readiness = import_module("pymia.smartpyme.readiness")
    runtime_bridge = import_module("pymia.smartpyme.runtime_bridge")
    dispatcher = import_module("pymia.smartpyme.microservice_dispatcher")
    exec_gate = import_module("pymia.smartpyme.execution_result_gate")
    delivery = import_module("pymia.smartpyme.delivery_package")
    return {
        "create_intake_record": intake.create_intake_record,
        "create_evidence_record": evidence.create_evidence_record,
        "SOURCE_KIND_UPLOADED_FILE": evidence.SOURCE_KIND_UPLOADED_FILE,
        "save_intake_record": storage.save_intake_record,
        "save_evidence_record": storage.save_evidence_record,
        "load_intake_record_by_id": storage.load_intake_record_by_id,
        "load_evidence_records_by_intake_id": storage.load_evidence_records_by_intake_id,
        "evaluate_evidence_sufficiency": evidence_gate.evaluate_evidence_sufficiency,
        "evaluate_analysis_readiness": readiness.evaluate_analysis_readiness,
        "prepare_runtime_execution": runtime_bridge.prepare_runtime_execution,
        "dispatch_candidate": dispatcher.dispatch_candidate,
        "validate_execution_result": exec_gate.validate_execution_result,
        "build_delivery_package": delivery.build_delivery_package,
    }


def _core_delivery_bridge_deps() -> dict[str, Any]:
    """Carga lazy del bridge M37 para evitar acoplamiento de import en módulo."""
    evidence_contract = import_module("pymia.contracts.evidence_v1")
    diagnostic_models = import_module("pymia.diagnostic_core.models")
    bridge = import_module("pymia.audit_result.core_delivery_bridge")
    return {
        "StructuredEvidence": evidence_contract.StructuredEvidence,
        "FormulaInputGateResult": diagnostic_models.FormulaInputGateResult,
        "EvidenceGateDecision": diagnostic_models.EvidenceGateDecision,
        "DiagnosticCoreResult": diagnostic_models.DiagnosticCoreResult,
        "build_core_audit_delivery_bundle": bridge.build_core_audit_delivery_bundle,
        "project_bridge_result_to_state": bridge.project_bridge_result_to_state,
    }


def _consume_core_delivery_bridge_if_available(
    state: PymIAState,
    *,
    base_dir: Path,
) -> Optional[PymIAState]:
    """Consume M37 bridge only when progressive_context provides a serialized payload.

    This keeps graph integration minimal and fail-closed:
    - if payload is absent, graph falls back to the existing legacy path;
    - if payload is invalid, graph raises and the caller handles the failure.
    """
    payload = state.progressive_context.get("core_delivery_bridge_payload")
    if not isinstance(payload, dict):
        return None

    deps = _core_delivery_bridge_deps()
    structured_evidence_raw = payload.get("structured_evidence")
    formula_gate_results_raw = payload.get("formula_gate_results") or []
    evidence_gate_decisions_raw = payload.get("evidence_gate_decisions") or []
    core_result_raw = payload.get("diagnostic_core_result")

    if not isinstance(structured_evidence_raw, dict):
        raise ValueError("core_delivery_bridge_payload.structured_evidence must be a mapping")
    if not isinstance(core_result_raw, dict):
        raise ValueError("core_delivery_bridge_payload.diagnostic_core_result must be a mapping")
    if not isinstance(formula_gate_results_raw, list):
        raise ValueError("core_delivery_bridge_payload.formula_gate_results must be a list")
    if not isinstance(evidence_gate_decisions_raw, list):
        raise ValueError("core_delivery_bridge_payload.evidence_gate_decisions must be a list")

    structured_evidence = deps["StructuredEvidence"].model_validate(structured_evidence_raw)
    formula_gate_results = [
        deps["FormulaInputGateResult"].model_validate(item)
        for item in formula_gate_results_raw
    ]
    evidence_gate_decisions = [
        deps["EvidenceGateDecision"].model_validate(item)
        for item in evidence_gate_decisions_raw
    ]
    core_result = deps["DiagnosticCoreResult"].model_validate(core_result_raw)

    case_id = str(payload.get("case_id") or state.conversation_id)
    intake_id = str(payload.get("intake_id") or state.intake_id or "")
    if not intake_id:
        raise ValueError("core_delivery_bridge_payload requires intake_id or state.intake_id")

    out_dir = base_dir / state.tenant_id / "core_delivery_bridge" / state.conversation_id
    bundle = deps["build_core_audit_delivery_bundle"](
        evidence=structured_evidence,
        case_id=case_id,
        intake_id=intake_id,
        formula_gate_results=formula_gate_results,
        evidence_gate_decisions=evidence_gate_decisions,
        core_result=core_result,
        output_dir=out_dir,
    )
    new_state = deps["project_bridge_result_to_state"](state, bundle)
    new_state.add_decision("Core delivery bridge consumed")

    if new_state.phase == "BLOCKED":
        blocked_message = str(bundle.render_contract.get("blocked_message") or "").strip()
        next_questions = bundle.render_contract.get("next_questions") or []
        if blocked_message:
            new_state.pending_question = blocked_message
        elif next_questions:
            new_state.pending_question = str(next_questions[0])

    return new_state


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
        adapter_result = adapt_text_message(
            text=event.text or "",
            tenant_id=new_state.tenant_id,
            user_id=new_state.chat_id,
            progressive_context=new_state.progressive_context,
        )
        new_state.progressive_context = dict(adapter_result.updated_progressive_context)
        new_state.pending_question = adapter_result.reply_text
        new_state.add_decision(adapter_result.decision_trail_entry)
        if adapter_result.phase_hint == "NEEDS_EVIDENCE":
            new_state.phase = "WAITING_FOR_EVIDENCE"
        elif adapter_result.phase_hint == "BLOCKED":
            new_state.phase = "BLOCKED"
        else:
            new_state.phase = "NEW"
    
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
        deps = _smartpyme_deps()
        # CICLO 2: Integración real con intake + evidence + storage
        try:
            # 1. Crear IntakeRecord
            raw_text = event.text or f"Documento recibido: {event.document_name or 'archivo'}"
            intake = deps["create_intake_record"](
                tenant_id=new_state.tenant_id,
                raw_text=raw_text,
            )
            deps["save_intake_record"](new_state.tenant_id, intake, base_dir=base_dir)
            new_state.intake_id = intake.intake_id
            new_state.add_decision(f"Intake created: {intake.intake_id}")
            
            # 2. Crear EvidenceRecord
            if event.document_path:
                evidence = deps["create_evidence_record"](
                    tenant_id=new_state.tenant_id,
                    intake_id=intake.intake_id,
                    evidence_type="excel_file",
                    source_kind=deps["SOURCE_KIND_UPLOADED_FILE"],
                    source_ref=str(event.document_path),
                    original_filename=event.document_name,
                )
                deps["save_evidence_record"](new_state.tenant_id, evidence, base_dir=base_dir)
                new_state.evidence_ids.append(evidence.evidence_id)
                new_state.add_decision(f"Evidence registered: {evidence.evidence_id}")
            
        except Exception as exc:
            new_state.phase = "FAILED"
            new_state.add_error(f"Intake/Evidence creation failed: {exc}")
            new_state.add_decision(f"Failed to create intake/evidence: {exc}")
    
    elif new_state.phase == "READY_TO_EXECUTE":
        deps = _smartpyme_deps()
        # CICLO 4: Integración real con dispatch + gate + delivery
        try:
            if not new_state.intake_id:
                new_state.phase = "BLOCKED"
                new_state.runtime_candidate_status = "BLOCKED"
                new_state.execution_status = "BLOCKED"
                new_state.pending_question = "No hay intake registrado. Subí un archivo primero."
                new_state.add_decision("Blocked: no intake_id")
                new_state.add_decision("Runtime candidate: BLOCKED (no intake_id)")
                return new_state
            
            # 1. Cargar intake y evidences
            intake_dict = deps["load_intake_record_by_id"](
                new_state.tenant_id, new_state.intake_id, base_dir=base_dir
            )
            if intake_dict is None:
                new_state.phase = "BLOCKED"
                new_state.runtime_candidate_status = "BLOCKED"
                new_state.execution_status = "BLOCKED"
                new_state.pending_question = f"Intake {new_state.intake_id} no encontrado."
                new_state.add_decision(f"Blocked: intake not found")
                new_state.add_decision("Runtime candidate: BLOCKED (intake not found)")
                return new_state
            
            evidence_dicts = deps["load_evidence_records_by_intake_id"](
                new_state.tenant_id, new_state.intake_id, base_dir=base_dir
            )
            
            # 2. Evaluar sufficiency
            sufficiency = deps["evaluate_evidence_sufficiency"](intake_dict, evidence_dicts)
            new_state.sufficiency_status = sufficiency.status
            new_state.add_decision(f"Evidence sufficiency: {sufficiency.status}")
            
            # 3. Evaluar readiness
            readiness = deps["evaluate_analysis_readiness"](intake_dict, sufficiency)
            new_state.readiness_status = readiness.status
            new_state.add_decision(f"Analysis readiness: {readiness.status}")
            
            # 4. Preparar runtime candidate
            candidate = deps["prepare_runtime_execution"](readiness)
            new_state.runtime_candidate_status = candidate.status
            new_state.add_decision(f"Runtime candidate: {candidate.status}")

            if candidate.status != "READY_TO_EXECUTE":
                new_state.phase = "BLOCKED"
                reason = candidate.blocking_reasons[0] if candidate.blocking_reasons else "candidato no listo"
                new_state.execution_status = "BLOCKED"
                new_state.pending_question = f"Diagnóstico bloqueado: {reason}"
                new_state.add_decision(f"Blocked: {reason}")
                return new_state

            if not new_state.latest_evidence_path or not new_state.latest_evidence_path.exists():
                new_state.phase = "BLOCKED"
                new_state.execution_status = "BLOCKED"
                new_state.pending_question = "No hay evidencia disponible para ejecutar el diagnóstico."
                new_state.add_decision("Blocked: no evidence path for dispatch")
                return new_state

            bridge_state = _consume_core_delivery_bridge_if_available(
                new_state,
                base_dir=base_dir,
            )
            if bridge_state is not None:
                return bridge_state

            out_dir = base_dir / new_state.tenant_id / "dispatch" / new_state.conversation_id
            dispatch_result = deps["dispatch_candidate"](
                candidate.to_dict(),
                evidence_path=new_state.latest_evidence_path,
                output_dir=out_dir,
            )
            new_state.execution_status = dispatch_result.status
            new_state.findings_count = int(dispatch_result.findings_count)
            new_state.output_refs = list(dispatch_result.output_refs)
            new_state.add_decision(f"Dispatch executed: status={dispatch_result.status}")

            gate = deps["validate_execution_result"](dispatch_result)
            new_state.gate_verdict = gate.verdict
            new_state.add_decision(f"Execution result gate evaluated: verdict={gate.verdict}")

            if gate.verdict != "PASS":
                new_state.phase = "BLOCKED" if gate.verdict == "BLOCKED" else "FAILED"
                new_state.delivery_status = "BLOCKED" if gate.verdict == "BLOCKED" else "FAILED"
                reason = gate.reasons[0] if gate.reasons else "resultado no entregable"
                new_state.pending_question = f"Diagnóstico bloqueado: {reason}"
                return new_state

            try:
                delivery = deps["build_delivery_package"](dispatch_result, gate)
            except Exception as exc:
                new_state.phase = "FAILED"
                new_state.delivery_status = "FAILED"
                new_state.add_error(f"Delivery package build failed: {exc}")
                new_state.add_decision(f"Delivery package build failed: {exc}")
                return new_state

            new_state.delivery_status = delivery.status
            new_state.delivery_summary = delivery.summary
            new_state.output_refs = list(delivery.output_refs)
            new_state.phase = "DELIVERED" if delivery.status == "READY_TO_DELIVER" else "BLOCKED"
            new_state.add_decision(f"Delivery package built: status={delivery.status}")
        
        except Exception as exc:
            new_state.phase = "FAILED"
            new_state.runtime_candidate_status = "FAILED"
            new_state.execution_status = "FAILED"
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
        response = f"{SENTINEL} Listo para ejecutar diagnóstico."
        new_state.add_decision("Response rendered: ready_to_execute")

    elif new_state.phase == "DELIVERED":
        response = f"{SENTINEL} {new_state.delivery_summary or 'Diagnóstico ejecutado y listo para entregar.'}"
        new_state.add_decision("Response rendered: delivered")
    
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
