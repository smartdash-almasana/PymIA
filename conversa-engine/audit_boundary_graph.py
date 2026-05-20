from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import TypedDict, Optional, Any, Dict

# Ensure conversa-engine is on path for relative imports when executed from elsewhere
conversa_dir = Path(__file__).resolve().parent
if str(conversa_dir) not in sys.path:
    sys.path.insert(0, str(conversa_dir))


class AuditState(TypedDict):
    tenant_id: str
    user_id: str
    session_id: str
    graph_thread_id: str
    message_text: str
    file_path: Optional[str]
    file_name: Optional[str]
    mime_type: Optional[str]
    expected_schema: str
    entropy_level: float
    base_path: Optional[str]
    fallback_path: Optional[str]
    route_label: Optional[str]
    intake_message: Optional[str]
    audit_output_path: Optional[str]
    audit_found: bool
    routing_decision: Optional[Dict[str, Any]]
    reply_text: Optional[str]
    error: Optional[str]


def _session_id(tenant_id: str, user_id: str) -> str:
    return f"{tenant_id}/{user_id}"


def _encoded_session_id(session_id: str) -> str:
    session_bytes = str(session_id).encode("utf-8")
    return base64.urlsafe_b64encode(session_bytes).decode("ascii").rstrip("=")


def _audit_path_for_state(state: Dict[str, Any]) -> Optional[Path]:
    session_id = state.get("session_id") or _session_id(state["tenant_id"], state["user_id"])
    encoded_id = _encoded_session_id(session_id)
    
    paths_to_try = []
    
    if state.get("base_path"):
        paths_to_try.append(Path(state["base_path"]))
    else:
        paths_to_try.append(conversa_dir / ".intake_state")
        
    if state.get("fallback_path"):
        paths_to_try.append(Path(state["fallback_path"]))
    else:
        paths_to_try.append(Path.home() / ".cache" / "pymia" / "conversa-intake-state")
        
    for bp in paths_to_try:
        candidate = bp / "audits" / encoded_id / "operational_audit_result.json"
        if candidate.exists():
            return candidate
            
    # Default path if none found
    primary_bp = Path(state["base_path"]) if state.get("base_path") else conversa_dir / ".intake_state"
    return primary_bp / "audits" / encoded_id / "operational_audit_result.json"


def intake_node(state: Dict[str, Any]) -> Dict[str, Any]:
    from document_intake import intake_document
    
    updates = {}
    file_path = state.get("file_path")
    
    session_id = state.get("session_id") or _session_id(state["tenant_id"], state["user_id"])
    updates["session_id"] = session_id
    
    if file_path:
        try:
            base_path = Path(state["base_path"]) if state.get("base_path") else None
            fallback_path = Path(state["fallback_path"]) if state.get("fallback_path") else None
            
            msg = intake_document(
                tenant_id=state["tenant_id"],
                user_id=state["user_id"],
                file_path=file_path,
                file_name=state.get("file_name") or Path(file_path).name,
                mime_type=state.get("mime_type"),
                expected_schema=state.get("expected_schema") or "unknown",
                entropy_level=state.get("entropy_level", 0.5),
                base_path=base_path,
                fallback_path=fallback_path,
            )
            updates["intake_message"] = msg
            
            # Infer route_label
            if "Clasificación de ingesta: BEM_AI" in msg:
                updates["route_label"] = "BEM_AI"
            elif "Clasificación de ingesta: INTERNAL_FACT" in msg:
                updates["route_label"] = "INTERNAL_FACT"
            elif "Clasificación de ingesta: NARRATIVE" in msg:
                updates["route_label"] = "NARRATIVE"
            else:
                updates["route_label"] = None
                
        except Exception as e:
            updates["error"] = str(e)
            updates["reply_text"] = f"Error en ingesta de documentos: {e}"
    else:
        updates["intake_message"] = None
        updates["route_label"] = None
        
    return updates


def locate_audit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    updates = {}
    try:
        path = _audit_path_for_state(state)
        if path and path.exists():
            updates["audit_output_path"] = str(path)
            updates["audit_found"] = True
        else:
            updates["audit_output_path"] = None
            updates["audit_found"] = False
    except Exception as e:
        updates["error"] = str(e)
        updates["audit_output_path"] = None
        updates["audit_found"] = False
    return updates


def routing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    import json
    from pymia.audit_result.models import OperationalAuditResult
    from operational_audit_router import route_operational_audit_message
    
    updates = {}
    message_text = state.get("message_text") or ""
    intake_message = state.get("intake_message")
    
    if not message_text.strip():
        if intake_message:
            updates["reply_text"] = intake_message
        else:
            updates["reply_text"] = "No se proporcionó ningún mensaje ni archivo válido."
        updates["routing_decision"] = None
        return updates
        
    if not state.get("audit_found") or not state.get("audit_output_path"):
        updates["reply_text"] = "Todavía no tengo una auditoría operacional activa para esta conversación. Subí una planilla estructurada primero."
        updates["routing_decision"] = None
        return updates
        
    try:
        path_str = state["audit_output_path"]
        with open(path_str, "r", encoding="utf-8") as f:
            payload = json.load(f)
            
        # Reconcile date fields for model validation
        if "business_context" in payload and "period_analyzed" in payload["business_context"]:
            pa = payload["business_context"]["period_analyzed"]
            if "from_date" in pa:
                pa["from"] = pa.pop("from_date")
            if "to_date" in pa:
                pa["to"] = pa.pop("to_date")
            
        audit = OperationalAuditResult.model_validate(payload)
        decision = route_operational_audit_message(message_text, audit)
        
        updates["routing_decision"] = {
            "pathology_code": decision.pathology_code,
            "thread_id": decision.thread_id,
            "missing_evidence": decision.missing_evidence,
            "next_question": decision.next_question,
            "reply_text": decision.reply_text,
            "options": decision.options,
        }
        updates["reply_text"] = decision.reply_text
        
        # Clean up to help GC
        del audit
        
    except Exception as e:
        updates["error"] = str(e)
        updates["reply_text"] = f"Error al procesar la auditoría operacional: {e}"
        updates["routing_decision"] = None
        
    return updates


def build_audit_boundary_graph() -> Any:
    """
    Attempts to compile and build the LangGraph StateGraph workflow if langgraph is installed.
    Otherwise, returns None.
    """
    try:
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import MemorySaver
        
        workflow = StateGraph(AuditState)
        workflow.add_node("intake", intake_node)
        workflow.add_node("locate_audit", locate_audit_node)
        workflow.add_node("routing", routing_node)
        
        workflow.add_edge(START, "intake")
        workflow.add_edge("intake", "locate_audit")
        workflow.add_edge("locate_audit", "routing")
        workflow.add_edge("routing", END)
        
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    except ImportError:
        return None


def run_audit_boundary_graph_v1(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronously runs the AuditBoundaryGraph v1 sequential workflow as a fallback
    or standard pure Python execution of the nodes.
    """
    state: Dict[str, Any] = {
        "tenant_id": "",
        "user_id": "",
        "session_id": "",
        "graph_thread_id": "",
        "message_text": "",
        "file_path": None,
        "file_name": None,
        "mime_type": None,
        "expected_schema": "unknown",
        "entropy_level": 0.5,
        "base_path": None,
        "fallback_path": None,
        "route_label": None,
        "intake_message": None,
        "audit_output_path": None,
        "audit_found": False,
        "routing_decision": None,
        "reply_text": None,
        "error": None,
    }
    state.update(initial_state)
    
    if not state.get("session_id"):
        state["session_id"] = _session_id(state["tenant_id"], state["user_id"])
        
    # Node 1: Ingest document if provided
    intake_updates = intake_node(state)
    state.update(intake_updates)
    
    if state.get("error"):
        return state
        
    # Node 2: Locate pre-computed audit json
    locate_updates = locate_audit_node(state)
    state.update(locate_updates)
    
    if state.get("error"):
        return state
        
    # Node 3: Route user query against the audit if found
    routing_updates = routing_node(state)
    state.update(routing_updates)
    
    return state
