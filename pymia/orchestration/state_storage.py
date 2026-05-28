"""Persistencia de estado conversacional en JSONL."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pymia.orchestration.state import PymIAState


def save_state(
    tenant_id: str,
    chat_id: str,
    state: PymIAState,
    base_dir: Path,
) -> None:
    """Persiste estado conversacional en JSONL.
    
    Append-only: cada estado se agrega como nueva línea.
    """
    state_file = base_dir / tenant_id / "conversation_states.jsonl"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convertir estado a dict serializable
    state_dict = {
        "tenant_id": state.tenant_id,
        "chat_id": chat_id,
        "conversation_id": state.conversation_id,
        "phase": state.phase,
        "last_user_message": state.last_user_message,
        "pending_question": state.pending_question,
        "intake_id": state.intake_id,
        "evidence_ids": state.evidence_ids,
        "sufficiency_status": state.sufficiency_status,
        "readiness_status": state.readiness_status,
        "runtime_candidate_status": state.runtime_candidate_status,
        "execution_status": state.execution_status,
        "delivery_status": state.delivery_status,
        "latest_evidence_path": str(state.latest_evidence_path) if state.latest_evidence_path else None,
        "decision_trail": state.decision_trail,
        "errors": state.errors,
        "created_at": state.created_at.isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with state_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(state_dict, ensure_ascii=False) + "\n")


def load_state(
    tenant_id: str,
    chat_id: str,
    base_dir: Path,
) -> Optional[PymIAState]:
    """Carga estado conversacional más reciente para un chat_id.
    
    Retorna None si no existe estado.
    """
    state_file = base_dir / tenant_id / "conversation_states.jsonl"
    if not state_file.exists():
        return None
    
    with state_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Buscar última línea con este chat_id (scan reverso)
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        
        state_dict = json.loads(line)
        if state_dict.get("chat_id") == chat_id:
            # Reconstruir PymIAState
            latest_evidence_path = state_dict.get("latest_evidence_path")
            
            return PymIAState(
                tenant_id=state_dict["tenant_id"],
                chat_id=state_dict["chat_id"],
                conversation_id=state_dict["conversation_id"],
                phase=state_dict["phase"],
                last_user_message=state_dict.get("last_user_message", ""),
                pending_question=state_dict.get("pending_question"),
                intake_id=state_dict.get("intake_id"),
                evidence_ids=state_dict.get("evidence_ids", []),
                sufficiency_status=state_dict.get("sufficiency_status"),
                readiness_status=state_dict.get("readiness_status"),
                runtime_candidate_status=state_dict.get("runtime_candidate_status"),
                execution_status=state_dict.get("execution_status"),
                delivery_status=state_dict.get("delivery_status"),
                latest_evidence_path=Path(latest_evidence_path) if latest_evidence_path else None,
                decision_trail=state_dict.get("decision_trail", []),
                errors=state_dict.get("errors", []),
                created_at=datetime.fromisoformat(state_dict["created_at"]),
                updated_at=datetime.fromisoformat(state_dict["updated_at"]),
            )
    
    return None
