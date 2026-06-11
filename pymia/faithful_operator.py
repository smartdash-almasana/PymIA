from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class OperatorPhase(StrEnum):
    LISTENING = "LISTENING"
    EVIDENCE_REQUESTED = "EVIDENCE_REQUESTED"
    PROCESSING = "PROCESSING"
    CANDIDATE_DELIVERED = "CANDIDATE_DELIVERED"
    OWNER_CONFIRMATION_PENDING = "OWNER_CONFIRMATION_PENDING"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"


class OperatorState(BaseModel):
    tenant_id: str
    intake_id: str
    owner_message: str
    current_state: OperatorPhase
    problem_summary: str
    evidence_requested: list[str] = Field(default_factory=list)
    next_question: str
    blocked_reason: str | None = None
    evidence_path: str | None = None
    evidence_id: str | None = None
    evidence_hash: str | None = None
    run_id: str | None = None
    output_hash: str | None = None
    candidate_markdown: str | None = None
    candidate_response: str | None = None
    limit: str | None = None
    owner_confirmation_status: str | None = None
    owner_confirmation_message: str | None = None
    catalog_reconciliation: list[dict] = Field(default_factory=list)


def _build_intake_id(tenant_id: str, owner_message: str) -> str:
    digest = hashlib.sha256(f"{tenant_id}:{owner_message}".encode("utf-8")).hexdigest()[:16]
    return f"intake_{digest}"


def _summarize_owner_message(owner_message: str) -> str:
    return " ".join(owner_message.strip().split())


def handle_owner_message(
    owner_message: str,
    *,
    tenant_id: str = "tenant_operator_local",
    intake_id: str | None = None,
) -> OperatorState:
    """Create the first faithful-operator state from an owner message.

    This V1 path is deterministic: it never diagnoses, never invokes tools,
    and only asks for minimum evidence.
    """
    summary = _summarize_owner_message(owner_message)
    resolved_intake_id = intake_id or _build_intake_id(tenant_id, summary)

    if not summary:
        return OperatorState(
            tenant_id=tenant_id,
            intake_id=resolved_intake_id,
            owner_message=owner_message,
            current_state=OperatorPhase.BLOCKED,
            problem_summary="",
            evidence_requested=[],
            next_question="Necesito que me cuentes el problema operativo en una frase para poder pedir la evidencia mínima.",
            blocked_reason="empty_owner_message",
        )

    return OperatorState(
        tenant_id=tenant_id,
        intake_id=resolved_intake_id,
        owner_message=owner_message,
        current_state=OperatorPhase.EVIDENCE_REQUESTED,
        problem_summary=summary,
        evidence_requested=["ventas", "costos", "productos", "periodo"],
        next_question=(
            "Entiendo. Puede ser caja, margen, costos o plazos, pero todavía no puedo afirmar la causa. "
            "Para avanzar necesito evidencia mínima: ventas, costos, productos y período. "
            "Si tenés un Excel, lo registro como evidencia inicial y te devuelvo una lectura candidata con límites."
        ),
    )


def receive_excel_and_build_candidate(
    state: OperatorState,
    excel_path: Path | str,
    *,
    storage_dir: Path | str | None = None,
) -> OperatorState:
    if state.current_state != OperatorPhase.EVIDENCE_REQUESTED:
        return state.model_copy(
            update={
                "current_state": OperatorPhase.BLOCKED,
                "blocked_reason": "evidence_not_requested",
                "next_question": "Primero necesito formar el pedido de evidencia antes de procesar un Excel.",
            }
        )

    path = Path(excel_path)
    if not path.exists() or not path.is_file():
        return state.model_copy(
            update={
                "current_state": OperatorPhase.BLOCKED,
                "evidence_path": str(path),
                "blocked_reason": "evidence_file_not_found",
                "next_question": "No pude leer el Excel indicado. Necesito un archivo existente para registrarlo como evidencia.",
            }
        )

    from pymia.cli.vertical_slice import build_pipeline
 
    pipeline = build_pipeline(
        path,
        state.owner_message,
        tenant_id=state.tenant_id,
        intake_id=state.intake_id,
        storage_dir=Path(storage_dir) if storage_dir is not None else None,
    )
    catalog_reconciliation = pipeline.get("catalog_reconciliation", [])
    reconciled_count = len(catalog_reconciliation)

    limit = "Resultado candidato: no declara verdad final sin confirmación del dueño."
    next_question = "¿Estas columnas representan realmente ventas, costos, productos y período del proceso que querés revisar?"
    candidate_response = (
        f"Estado: {pipeline['status']}\n"
        f"Evidence ID: {pipeline['evidence_id']}\n"
        f"Evidence SHA-256: {pipeline['evidence_hash']}\n"
        f"Run ID: {pipeline['run_id']}\n"
        f"Output hash: {pipeline['output_hash']}\n"
        f"Reconciliación de catálogos: {reconciled_count} fórmulas\n"
        f"Límite: {limit}\n"
        f"Próxima pregunta: {next_question}"
    )

    return state.model_copy(
        update={
            "current_state": OperatorPhase.OWNER_CONFIRMATION_PENDING,
            "evidence_path": str(path),
            "evidence_id": pipeline["evidence_id"],
            "evidence_hash": pipeline["evidence_hash"],
            "run_id": pipeline["run_id"],
            "output_hash": pipeline["output_hash"],
            "candidate_markdown": pipeline["markdown"],
            "candidate_response": candidate_response,
            "limit": limit,
            "next_question": next_question,
            "blocked_reason": None,
            "owner_confirmation_status": "pending",
            "catalog_reconciliation": catalog_reconciliation,
        }
    )


def handle_owner_confirmation(
    state: OperatorState,
    owner_reply: str,
    *,
    new_evidence_path: Path | str | None = None,
) -> OperatorState:
    """Handle owner feedback after candidate delivery.

    This deterministic loop preserves traceability and does not promote a
    candidate to final diagnosis.
    """
    reply = _summarize_owner_message(owner_reply).lower()
    if state.current_state != OperatorPhase.OWNER_CONFIRMATION_PENDING:
        return state.model_copy(
            update={
                "current_state": OperatorPhase.BLOCKED,
                "blocked_reason": "confirmation_not_expected",
                "owner_confirmation_message": owner_reply,
                "next_question": "Todavía no hay un resultado candidato pendiente de confirmación del dueño.",
            }
        )

    base_update = {"owner_confirmation_message": owner_reply}

    if new_evidence_path is not None:
        return state.model_copy(
            update={
                **base_update,
                "current_state": OperatorPhase.EVIDENCE_REQUESTED,
                "owner_confirmation_status": "new_evidence_provided",
                "evidence_path": str(new_evidence_path),
                "next_question": "Recibí nueva evidencia. Necesito reprocesarla antes de sostener el resultado candidato.",
                "blocked_reason": None,
            }
        )

    uncertainty_markers = ("no se", "no estoy seguro", "no estoy segura", "dudo", "ni idea")
    correction_markers = ("correg", "esta mal", "no representa", "mezcla", "faltan", "falto")
    confirmation_markers = ("si", "correcto", "confirmo", "representa", "esta bien", "ok")

    if any(marker in reply for marker in uncertainty_markers):
        return state.model_copy(
            update={
                **base_update,
                "current_state": OperatorPhase.BLOCKED,
                "owner_confirmation_status": "blocked_by_owner_uncertainty",
                "blocked_reason": "owner_uncertain_about_business_semantics",
                "next_question": "No cierro el resultado como confirmado. Necesito validación del dueño o nueva evidencia.",
            }
        )

    if any(marker in reply for marker in correction_markers):
        return state.model_copy(
            update={
                **base_update,
                "current_state": OperatorPhase.EVIDENCE_REQUESTED,
                "owner_confirmation_status": "correction_requested",
                "evidence_requested": ["ventas", "costos", "productos", "periodo", "correccion_semantica"],
                "next_question": "Entendido. No cierro el resultado. Necesito la corrección concreta o nueva evidencia.",
                "blocked_reason": None,
            }
        )

    if any(marker in reply for marker in confirmation_markers):
        return state.model_copy(
            update={
                **base_update,
                "current_state": OperatorPhase.CLOSED,
                "owner_confirmation_status": "candidate_confirmed",
                "next_question": "Resultado candidato confirmado por el dueño. No se declara diagnóstico final automático.",
                "blocked_reason": None,
            }
        )

    return state.model_copy(
        update={
            **base_update,
            "current_state": OperatorPhase.BLOCKED,
            "owner_confirmation_status": "unclear_confirmation",
            "blocked_reason": "unclear_owner_confirmation",
            "next_question": "Necesito una confirmación clara, una corrección concreta o nueva evidencia para continuar.",
        }
    )


def build_confirmed_candidate_next_actions(state: OperatorState) -> str:
    """Build deterministic operational next actions for a confirmed candidate."""
    if state.current_state != OperatorPhase.CLOSED or state.owner_confirmation_status != "candidate_confirmed":
        return (
            "BLOQUEADO: no hay candidato confirmado por el dueño. "
            "Necesito confirmación explícita antes de proponer próximos pasos operativos."
        )

    evidence_id = state.evidence_id or "sin_evidence_id"
    run_id = state.run_id or "sin_run_id"
    output_hash = state.output_hash or "sin_output_hash"
    limit = state.limit or "Resultado candidato confirmado; no declara verdad final automática."

    return "\n".join(
        [
            "Resultado de trabajo posterior a confirmación",
            f"Caso: {state.problem_summary}",
            f"Evidencia usada: {evidence_id}",
            f"Run ID: {run_id}",
            f"Output hash: {output_hash}",
            f"Límite: {limit}",
            "Próximos pasos operativos:",
            "1. Revisar con el dueño si las ventas y costos cargados cubren el período completo.",
            "2. Separar productos o líneas con margen dudoso para lectura focalizada.",
            "3. Pedir al dueño una decisión operativa concreta sobre qué variable quiere ajustar primero.",
            "Pregunta de seguimiento: ¿Querés que revisemos primero margen por producto, caja por período o costos directos?",
        ]
    )


def run_local_operator_flow(
    owner_message: str,
    *,
    excel_path: Path | str | None = None,
    owner_confirmation: str | None = None,
    tenant_id: str = "tenant_operator_local",
    intake_id: str | None = None,
    storage_dir: Path | str | None = None,
) -> dict[str, object]:
    """Run the deterministic local operator flow without channels or external orchestration."""
    states: list[OperatorState] = []
    state = handle_owner_message(owner_message, tenant_id=tenant_id, intake_id=intake_id)
    states.append(state)

    final_response = state.next_question
    if state.current_state == OperatorPhase.BLOCKED:
        return {"status": state.current_state.value, "state": state, "states": states, "response": final_response}

    if excel_path is None:
        return {"status": state.current_state.value, "state": state, "states": states, "response": final_response}

    state = receive_excel_and_build_candidate(state, excel_path, storage_dir=storage_dir)
    states.append(state)
    final_response = state.candidate_response or state.next_question
    if state.current_state != OperatorPhase.OWNER_CONFIRMATION_PENDING:
        return {"status": state.current_state.value, "state": state, "states": states, "response": final_response}

    if owner_confirmation is None:
        return {"status": state.current_state.value, "state": state, "states": states, "response": final_response}

    state = handle_owner_confirmation(state, owner_confirmation)
    states.append(state)
    if state.current_state == OperatorPhase.CLOSED and state.owner_confirmation_status == "candidate_confirmed":
        final_response = build_confirmed_candidate_next_actions(state)
    else:
        final_response = state.next_question

    return {"status": state.current_state.value, "state": state, "states": states, "response": final_response}
