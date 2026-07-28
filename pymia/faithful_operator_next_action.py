from __future__ import annotations

from pydantic import BaseModel

from pymia.faithful_operator import OperatorPhase, OperatorState


class OperatorNextAction(BaseModel):
    owner_question: str
    required_evidence: str
    operator_decision: str
    stop_condition: str


def build_operator_next_action(state: OperatorState) -> OperatorNextAction:
    """Return the next concrete assisted-operator action for any operator state."""
    if state.current_state == OperatorPhase.BLOCKED:
        return OperatorNextAction(
            owner_question=state.next_question,
            required_evidence="clarificación del dueño o evidencia mínima faltante",
            operator_decision="no avanzar hasta resolver el bloqueo",
            stop_condition=state.blocked_reason or "blocked",
        )

    if state.current_state == OperatorPhase.EVIDENCE_REQUESTED:
        requested = ", ".join(state.evidence_requested) if state.evidence_requested else "evidencia mínima"
        return OperatorNextAction(
            owner_question=state.next_question,
            required_evidence=requested,
            operator_decision="esperar evidencia o corrección semántica antes de procesar",
            stop_condition="si no hay evidencia concreta, no diagnosticar",
        )

    if state.current_state == OperatorPhase.OWNER_CONFIRMATION_PENDING:
        return OperatorNextAction(
            owner_question=state.next_question,
            required_evidence="confirmación semántica del dueño sobre columnas, período y sentido de negocio",
            operator_decision="clasificar la respuesta como confirmación, corrección, incertidumbre o nueva evidencia",
            stop_condition="si el dueño no puede validar los datos, bloquear por incertidumbre semántica",
        )

    if state.current_state == OperatorPhase.CLOSED and state.owner_confirmation_status == "candidate_confirmed":
        return OperatorNextAction(
            owner_question="¿Querés revisar primero margen por producto, caja por período o costos directos?",
            required_evidence="NONE hasta que el dueño elija foco operativo",
            operator_decision="clasificar foco como MARGEN_PRODUCTO, CAJA_PERIODO o COSTOS_DIRECTOS",
            stop_condition="si no puede elegir foco ni validar datos, bloquear honestamente",
        )

    return OperatorNextAction(
        owner_question="¿Qué dato o decisión falta para continuar?",
        required_evidence="aclaración operativa concreta",
        operator_decision="no inventar el próximo paso; pedir precisión al dueño",
        stop_condition="si no hay claridad suficiente, bloquear honestamente",
    )
