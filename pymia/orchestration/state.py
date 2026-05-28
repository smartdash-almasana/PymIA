"""Estado conversacional dinámico de PymIA."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


@dataclass
class PymIAState:
    """Estado conversacional dinámico de PymIA.
    
    Mantiene contexto conversacional, evidencia registrada, resultados de gates,
    y trazabilidad de decisiones.
    """
    
    # Identificación
    tenant_id: str
    chat_id: str
    conversation_id: str
    
    # Fase actual
    phase: Literal[
        "NEW",                      # mensaje nuevo, sin contexto
        "WAITING_FOR_EVIDENCE",     # esperando archivo
        "EVIDENCE_RECEIVED",        # archivo recibido, listo para diagnosticar
        "READY_TO_EXECUTE",         # candidato listo para ejecutar
        "EXECUTING",                # ejecutando microservicio
        "EXECUTED",                 # ejecución completada
        "DELIVERY_READY",           # paquete listo para entregar
        "DELIVERED",                # entrega lista para responder
        "BLOCKED",                  # bloqueado (falta evidencia, error, etc.)
        "FAILED",                   # fallo controlado
    ] = "NEW"
    
    # Contexto conversacional
    last_user_message: str = ""
    pending_question: Optional[str] = None
    progressive_context: dict[str, Any] = field(default_factory=dict)
    
    # Registros formales
    intake_id: Optional[str] = None
    evidence_ids: list[str] = field(default_factory=list)
    
    # Resultados de gates
    sufficiency_status: Optional[str] = None  # READY, NEEDS_MORE, BLOCKED
    readiness_status: Optional[str] = None    # READY, NEEDS_EVIDENCE, BLOCKED
    
    # Ejecución
    runtime_candidate_status: Optional[str] = None  # READY_TO_EXECUTE, BLOCKED
    execution_status: Optional[str] = None          # EXECUTED, FAILED
    delivery_status: Optional[str] = None           # READY_TO_DELIVER, BLOCKED
    gate_verdict: Optional[str] = None
    delivery_summary: Optional[str] = None
    output_refs: list[str] = field(default_factory=list)
    findings_count: int = 0
    
    # Paths
    latest_evidence_path: Optional[Path] = None
    
    # Trazabilidad
    decision_trail: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_decision(self, decision: str) -> None:
        """Agrega entrada al decision trail."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.decision_trail.append(f"[{timestamp}] {decision}")
        self.updated_at = datetime.now(timezone.utc)
    
    def add_error(self, error: str) -> None:
        """Agrega error."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.errors.append(f"[{timestamp}] {error}")
        self.updated_at = datetime.now(timezone.utc)


@dataclass(frozen=True)
class PymIAEvent:
    """Evento de entrada al grafo de orquestación."""
    
    event_type: Literal[
        "text_message",      # mensaje de texto del usuario
        "document_received", # documento subido
        "diagnostic_request", # usuario pide diagnóstico
        "system_error",      # error interno
    ]
    
    # Metadata del evento
    tenant_id: str
    chat_id: str
    conversation_id: str
    
    # Payload según event_type
    text: Optional[str] = None
    document_path: Optional[Path] = None
    document_name: Optional[str] = None
    error_message: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
