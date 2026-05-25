"""
SmartPyme Intake Record and Evidence Request Slice.

Persistencia mínima determinística del flujo:
    raw_text + selectors
    -> InterrogationResult
    -> TankSelectionResult
    -> IntakeRecord con EvidenceRequests

NO diagnostica. NO ejecuta análisis. NO procesa archivos.
Produce un IntakeRecord serializable que documenta:
- qué se recibió;
- qué se interrogó;
- qué tanques quedaron activos/candidatos;
- qué evidencia se requiere;
- qué estado tiene el intake;
- qué se sugiere como próximo paso.

Ver: docs/smartpyme/SMARTPYME_INTAKE_RECORD_AND_EVIDENCE_REQUEST.md
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pymia.smartpyme.interrogation import (
    InterrogationResult,
    StructuredSelectors,
    run_interrogation,
    STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
)
from pymia.smartpyme.tank_selection import (
    TankSelectionResult,
    EvidenceRequest,
    select_tanks,
    NEXT_REQUEST_EVIDENCE,
    NEXT_READY_FOR_ANALYSIS,
    NEXT_ASK_CLARIFICATION,
    NEXT_CONFIRM_REFORMULATION,
    NEXT_BLOCKED,
)


# ---------------------------------------------------------------------------
# Estados del IntakeRecord
# ---------------------------------------------------------------------------
INTAKE_RECEIVED = "RECEIVED"
INTAKE_INTERROGATED = "INTERROGATED"
INTAKE_TANKS_SELECTED = "TANKS_SELECTED"
INTAKE_NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
INTAKE_READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
INTAKE_BLOCKED = "BLOCKED"
INTAKE_UNSUPPORTED = "UNSUPPORTED"

ALLOWED_INTAKE_STATES = (
    INTAKE_RECEIVED,
    INTAKE_INTERROGATED,
    INTAKE_TANKS_SELECTED,
    INTAKE_NEEDS_EVIDENCE,
    INTAKE_READY_FOR_ANALYSIS,
    INTAKE_BLOCKED,
    INTAKE_UNSUPPORTED,
)


# ---------------------------------------------------------------------------
# Estados del IntakeEvidenceRequest
# ---------------------------------------------------------------------------
EVIDENCE_STATUS_REQUESTED = "REQUESTED"
EVIDENCE_STATUS_RECEIVED = "RECEIVED"
EVIDENCE_STATUS_SATISFIED = "SATISFIED"
EVIDENCE_STATUS_WAIVED = "WAIVED"
EVIDENCE_STATUS_BLOCKED = "BLOCKED"

ALLOWED_EVIDENCE_STATUSES = (
    EVIDENCE_STATUS_REQUESTED,
    EVIDENCE_STATUS_RECEIVED,
    EVIDENCE_STATUS_SATISFIED,
    EVIDENCE_STATUS_WAIVED,
    EVIDENCE_STATUS_BLOCKED,
)


# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------
@dataclass
class IntakeEvidenceRequest:
    """Pedido de evidencia formal dentro de un IntakeRecord.

    Estado inicial: REQUESTED.
    No ejecuta análisis; solo registra qué se requiere y por qué.
    """
    request_id: str
    evidence_type: str
    description: str
    required_fields: List[str]
    reason: str
    blocks_analysis: bool
    enables_classification: Optional[str]
    source_tank: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IntakeRecord:
    """Registro completo del intake SmartPyme.

    Contiene:
    - input crudo y selectores
    - resultado del interrogatorio
    - resultado de la selección de tanques
    - pedidos de evidencia formales
    - estado del intake
    - advertencias y notas de auditoría
    """
    intake_id: str
    tenant_id: str
    raw_input: str
    structured_selectors: Dict[str, Any]
    interrogation_result: Dict[str, Any]
    tank_selection_result: Dict[str, Any]
    evidence_requests: List[IntakeEvidenceRequest]
    intake_state: str
    suggested_next_state: str
    warnings: List[str]
    audit_notes: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intake_id": self.intake_id,
            "tenant_id": self.tenant_id,
            "raw_input": self.raw_input,
            "structured_selectors": self.structured_selectors,
            "interrogation_result": self.interrogation_result,
            "tank_selection_result": self.tank_selection_result,
            "evidence_requests": [e.to_dict() for e in self.evidence_requests],
            "intake_state": self.intake_state,
            "suggested_next_state": self.suggested_next_state,
            "warnings": self.warnings,
            "audit_notes": self.audit_notes,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------
def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_tenant_id(tenant_id: str) -> None:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id must be a non-empty string")


def _validate_raw_text(raw_text: str) -> None:
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("raw_text must be a non-empty string")


def _convert_evidence_request(
    er: EvidenceRequest,
    index: int,
    intake_id: str,
) -> IntakeEvidenceRequest:
    """Convierte un EvidenceRequest del TankSelectionResult
    en un IntakeEvidenceRequest con ID propio y estado REQUESTED."""
    return IntakeEvidenceRequest(
        request_id=f"{intake_id}_ev_{index:03d}",
        evidence_type=er.evidence_type,
        description=er.description,
        required_fields=list(er.required_fields),
        reason=er.reason,
        blocks_analysis=er.blocks_analysis,
        enables_classification=er.enables_classification,
        source_tank=er.source_tank,
        status=EVIDENCE_STATUS_REQUESTED,
    )


def _resolve_intake_state(
    interrogation_result: InterrogationResult,
    tank_selection_result: TankSelectionResult,
) -> str:
    """Determina el estado del intake según reglas determinísticas.

    Reglas:
    - BLOCKED si interrogatorio bloqueado por contexto insuficiente.
    - NEEDS_EVIDENCE si tanques piden evidencia.
    - READY_FOR_ANALYSIS si todo está listo y hay evidencia suficiente.
    - INTERROGATED si se necesita desambiguación o confirmación.
    - BLOCKED como fallback fail-closed.
    """
    if interrogation_result.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT:
        return INTAKE_BLOCKED

    next_state = tank_selection_result.suggested_next_state

    if next_state == NEXT_REQUEST_EVIDENCE:
        return INTAKE_NEEDS_EVIDENCE
    if next_state == NEXT_READY_FOR_ANALYSIS:
        return INTAKE_READY_FOR_ANALYSIS
    if next_state in (NEXT_ASK_CLARIFICATION, NEXT_CONFIRM_REFORMULATION):
        return INTAKE_INTERROGATED
    if next_state == NEXT_BLOCKED:
        return INTAKE_BLOCKED

    # Fail-closed
    return INTAKE_BLOCKED


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def create_intake_record(
    *,
    tenant_id: str,
    raw_text: str,
    structured_selectors: Optional[StructuredSelectors] = None,
) -> IntakeRecord:
    """Crea un IntakeRecord completo para un caso SmartPyme.

    Flujo:
    1. Valida tenant_id y raw_text.
    2. Ejecuta run_interrogation(...).
    3. Ejecuta select_tanks(...).
    4. Convierte evidence_requests en IntakeEvidenceRequest.
    5. Determina intake_state.
    6. Devuelve IntakeRecord serializable.

    No diagnostica. No ejecuta análisis. No procesa archivos.
    """
    _validate_tenant_id(tenant_id)
    _validate_raw_text(raw_text)

    intake_id = _new_id("intake")

    # 1. Interrogatorio
    ir = run_interrogation(raw_text, structured_selectors)

    # 2. Selección de tanques
    tsr = select_tanks(ir)

    # 3. Conversión de evidence requests
    intake_evidence: List[IntakeEvidenceRequest] = [
        _convert_evidence_request(er, i, intake_id)
        for i, er in enumerate(tsr.evidence_requests)
    ]

    # 4. Estado del intake
    intake_state = _resolve_intake_state(ir, tsr)

    # 5. Audit notes
    audit: List[str] = [
        f"intake_id={intake_id}",
        f"tenant_id={tenant_id}",
        f"interrogation.status={ir.status}",
        f"interrogation.candidate_symptoms={ir.candidate_symptoms}",
        f"tank_selection.suggested_next_state={tsr.suggested_next_state}",
        f"intake_state={intake_state}",
        f"evidence_requests_count={len(intake_evidence)}",
    ]

    # 6. Selectores como dict
    selectors_dict: Dict[str, Any] = (
        structured_selectors.to_dict()
        if structured_selectors is not None
        else {}
    )

    return IntakeRecord(
        intake_id=intake_id,
        tenant_id=tenant_id,
        raw_input=raw_text,
        structured_selectors=selectors_dict,
        interrogation_result=ir.to_dict(),
        tank_selection_result=tsr.to_dict(),
        evidence_requests=intake_evidence,
        intake_state=intake_state,
        suggested_next_state=tsr.suggested_next_state,
        warnings=list(tsr.warnings),
        audit_notes=audit,
        created_at=_now_iso(),
    )


__all__ = [
    "IntakeEvidenceRequest",
    "IntakeRecord",
    "create_intake_record",
    "ALLOWED_INTAKE_STATES",
    "ALLOWED_EVIDENCE_STATUSES",
    "INTAKE_RECEIVED",
    "INTAKE_INTERROGATED",
    "INTAKE_TANKS_SELECTED",
    "INTAKE_NEEDS_EVIDENCE",
    "INTAKE_READY_FOR_ANALYSIS",
    "INTAKE_BLOCKED",
    "INTAKE_UNSUPPORTED",
    "EVIDENCE_STATUS_REQUESTED",
    "EVIDENCE_STATUS_RECEIVED",
    "EVIDENCE_STATUS_SATISFIED",
    "EVIDENCE_STATUS_WAIVED",
    "EVIDENCE_STATUS_BLOCKED",
]
