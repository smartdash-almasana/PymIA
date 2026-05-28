"""Adapter entre Orchestration OS y anamnesis SmartPyme."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal

from pymia.smartpyme.anamnesis_fsm_integration import (
    AnamnesisTurnInput,
    run_anamnesis_turn,
)

_ALLOWED_PHASE_HINTS = ("CONVERSATIONAL", "NEEDS_EVIDENCE", "BLOCKED")


@dataclass(frozen=True)
class ConversationAdapterResult:
    reply_text: str
    updated_progressive_context: dict[str, Any]
    phase_hint: Literal["CONVERSATIONAL", "NEEDS_EVIDENCE", "BLOCKED"]
    decision_trail_entry: str


def _map_phase_hint(*, has_evidence_requests: bool, readiness_status: str | None) -> str:
    if readiness_status == "BLOCKED":
        return "BLOCKED"
    if has_evidence_requests:
        return "NEEDS_EVIDENCE"
    return "CONVERSATIONAL"


def adapt_text_message(
    *,
    text: str,
    tenant_id: str,
    user_id: str,
    progressive_context: dict[str, Any],
) -> ConversationAdapterResult:
    """Ejecuta turno de anamnesis offline detrás del adapter."""
    input_context = deepcopy(progressive_context if isinstance(progressive_context, dict) else {})

    try:
        turn_output = run_anamnesis_turn(
            AnamnesisTurnInput(
                tenant_id=tenant_id,
                session_id=user_id,
                message_text=text,
                previous_progressive_context=input_context,
            )
        )
        phase_hint = _map_phase_hint(
            has_evidence_requests=turn_output.has_evidence_requests,
            readiness_status=turn_output.readiness_status,
        )
        if phase_hint not in _ALLOWED_PHASE_HINTS:
            phase_hint = "BLOCKED"
        return ConversationAdapterResult(
            reply_text=turn_output.reply_text,
            updated_progressive_context=deepcopy(turn_output.updated_progressive_context),
            phase_hint=phase_hint,
            decision_trail_entry=f"Conversation adapter handled text_message: phase_hint={phase_hint}",
        )
    except Exception as exc:
        return ConversationAdapterResult(
            reply_text=(
                "No pude procesar tu mensaje en este momento. "
                "¿Podés reformularlo o compartir un poco más de contexto operativo?"
            ),
            updated_progressive_context=deepcopy(input_context),
            phase_hint="BLOCKED",
            decision_trail_entry=f"Conversation adapter error (controlled): {exc}",
        )
