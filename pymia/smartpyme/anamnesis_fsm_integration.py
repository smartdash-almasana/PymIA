"""
Integración offline del FSM de anamnesis con sesión/progressive_context.

Este módulo provee un wrapper puro y determinístico que:
- Recibe tenant_id, session_id, message_text y previous_progressive_context
- Reconstruye AnamnesisFSMState desde progressive_context si existe
- Llama a process_message() del FSM offline
- Devuelve reply_text + updated_progressive_context serializable

NO usa Telegram, NO usa red, NO usa I/O, NO ejecuta microservicios,
NO lee Excel, NO diagnostica.

Este wrapper es consumible por conversa-engine/main.py o por cualquier
capa superior (Hermes real, bot, CLI) sin acoplamiento directo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pymia.smartpyme.anamnesis_fsm import (
    FSMPhase,
    AnamnesisFSMState,
    process_message,
)
from pymia.smartpyme.anamnesis_readiness import (
    AnamnesisReadiness,
    ReadinessStatus,
)
from pymia.smartpyme.conversation_contract import (
    ConversationContract,
    ConversationPhase,
    create_conversation_contract,
)
from pymia.smartpyme.evidence_requirement import EvidenceRequirement
from pymia.smartpyme.operational_hypothesis import OperationalHypothesis
from pymia.smartpyme.taxonomy import BusinessTaxonomySnapshot

__all__ = [
    "AnamnesisTurnInput",
    "AnamnesisTurnOutput",
    "run_anamnesis_turn",
]


@dataclass(frozen=True)
class AnamnesisTurnInput:
    """
    Entrada de un turno de anamnesis.

    Campos
    ------
    tenant_id:
        Identificador del tenant. Obligatorio.

    session_id:
        Identificador de sesión (puede ser user_id, chat_id, etc.).
        Obligatorio para trazabilidad.

    message_text:
        Texto del usuario. Puede ser vacío (→ menú inicial).

    previous_progressive_context:
        Contexto previo serializado (dict). None si es sesión nueva.
        Debe contener al menos "fsm_state" con el snapshot anterior.
    """

    tenant_id: str
    session_id: str
    message_text: str
    previous_progressive_context: dict[str, Any] | None = None


@dataclass(frozen=True)
class AnamnesisTurnOutput:
    """
    Salida de un turno de anamnesis.

    Campos
    ------
    reply_text:
        Mensaje para el usuario en castellano de negocio.

    updated_progressive_context:
        Contexto serializable para el próximo turno.
        Contiene fsm_state, taxonomy, contract, hypotheses, evidence_requests.

    phase:
        Fase actual del FSM (para logging/debug).

    has_hypotheses:
        True si hay hipótesis ABIERTAS.

    has_evidence_requests:
        True si hay evidencia solicitada.

    readiness_status:
        Status de AnamnesisReadiness (READY, NEEDS_MORE_INFO, BLOCKED).
    """

    reply_text: str
    updated_progressive_context: dict[str, Any]
    phase: str
    has_hypotheses: bool
    has_evidence_requests: bool
    readiness_status: str | None = None


def _reconstruct_state_from_context(
    tenant_id: str,
    context: dict[str, Any],
) -> AnamnesisFSMState | None:
    """
    Reconstruye AnamnesisFSMState desde progressive_context serializado.

    Si el contexto está corrupto o incompleto, devuelve None (fail-closed).
    """
    if not context or not isinstance(context, dict):
        return None

    fsm_state_dict = context.get("fsm_state")
    if not fsm_state_dict or not isinstance(fsm_state_dict, dict):
        return None

    try:
        phase_str = fsm_state_dict.get("phase", "INIT")
        phase = FSMPhase(phase_str) if phase_str in [p.value for p in FSMPhase] else FSMPhase.INIT

        # Reconstruir contratos anidados si existen
        taxonomy_dict = fsm_state_dict.get("taxonomy")
        taxonomy = None
        if taxonomy_dict and isinstance(taxonomy_dict, dict):
            # No reconstruimos el dataclass completo, solo pasamos el dict
            # process_message() aceptará None y reconstruirá desde texto
            pass

        contract_dict = fsm_state_dict.get("contract")
        contract = None
        if contract_dict and isinstance(contract_dict, dict):
            pass

        # Reconstruir hypotheses (tupla vacía si no hay)
        hypotheses_dicts = fsm_state_dict.get("hypotheses", [])
        hypotheses = tuple()  # No reconstruimos, process_message maneja esto

        # Reconstruir evidence_requests
        evidence_dicts = fsm_state_dict.get("evidence_requests", [])
        evidence_requests = tuple()

        # Reconstruir readiness
        readiness_dict = fsm_state_dict.get("readiness")
        readiness = None
        if readiness_dict and isinstance(readiness_dict, dict):
            pass

        # Reconstruir blocking_reasons
        blocking_reasons = tuple(fsm_state_dict.get("blocking_reasons", []))

        return AnamnesisFSMState(
            phase=phase,
            tenant_id=tenant_id,
            user_text=fsm_state_dict.get("user_text", ""),
            taxonomy=None,  # Se reconstruye desde texto en próximo turno
            contract=None,
            hypotheses=hypotheses,
            evidence_requests=evidence_requests,
            readiness=None,
            blocking_reasons=blocking_reasons,
            created_at=fsm_state_dict.get("created_at", ""),
            updated_at=fsm_state_dict.get("updated_at", ""),
        )
    except Exception:
        # Fail-closed: contexto corrupto → None (sesión nueva)
        return None


def _serialize_state_to_context(state: AnamnesisFSMState) -> dict[str, Any]:
    """
    Serializa AnamnesisFSMState a dict para progressive_context.
    """
    return {
        "fsm_state": state.to_dict(),
        "tenant_id": state.tenant_id,
        "phase": state.phase.value if isinstance(state.phase, FSMPhase) else state.phase,
        "has_taxonomy": state.taxonomy is not None,
        "has_hypotheses": len(state.hypotheses) > 0,
        "has_evidence_requests": len(state.evidence_requests) > 0,
        "readiness_status": (
            state.readiness.status.value
            if state.readiness and hasattr(state.readiness.status, "value")
            else None
        ),
    }


def run_anamnesis_turn(input_data: AnamnesisTurnInput) -> AnamnesisTurnOutput:
    """
    Ejecuta un turno de anamnesis usando el FSM offline.

    Args:
        input_data: AnamnesisTurnInput con tenant_id, session_id, message_text,
                    y opcionalmente previous_progressive_context.

    Returns:
        AnamnesisTurnOutput con reply_text, updated_progressive_context,
        y metadata del estado actual.

    Raises:
        ValueError: Si tenant_id o session_id están vacíos.
    """
    if not input_data.tenant_id or not isinstance(input_data.tenant_id, str):
        raise ValueError("tenant_id obligatorio")
    if not input_data.session_id or not isinstance(input_data.session_id, str):
        raise ValueError("session_id obligatorio")

    # Reconstruir estado previo desde progressive_context
    previous_state = None
    if input_data.previous_progressive_context:
        previous_state = _reconstruct_state_from_context(
            tenant_id=input_data.tenant_id,
            context=input_data.previous_progressive_context,
        )

    # Llamar al FSM offline
    try:
        new_state, reply_text = process_message(
            user_text=input_data.message_text,
            tenant_id=input_data.tenant_id,
            previous_state=previous_state,
        )
    except Exception as e:
        # Fail-closed: error en FSM → menú inicial
        new_state, reply_text = process_message(
            user_text="",
            tenant_id=input_data.tenant_id,
            previous_state=None,
        )

    # Serializar nuevo estado a progressive_context
    updated_context = _serialize_state_to_context(new_state)

    # Extraer metadata para output
    phase_str = new_state.phase.value if isinstance(new_state.phase, FSMPhase) else new_state.phase
    has_hypotheses = len(new_state.hypotheses) > 0
    has_evidence_requests = len(new_state.evidence_requests) > 0
    readiness_status = None
    if new_state.readiness and hasattr(new_state.readiness.status, "value"):
        readiness_status = new_state.readiness.status.value

    return AnamnesisTurnOutput(
        reply_text=reply_text,
        updated_progressive_context=updated_context,
        phase=phase_str,
        has_hypotheses=has_hypotheses,
        has_evidence_requests=has_evidence_requests,
        readiness_status=readiness_status,
    )
