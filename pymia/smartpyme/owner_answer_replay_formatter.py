from __future__ import annotations

from typing import Any

from pymia.smartpyme.owner_answers_composer import OwnerAnswerToActionCompositionResult


_EMPTY_WARNING = "Información incompleta en replay sandbox."


def _safe_text(value: Any, *, fallback: str = "N/D") -> str:
    text = str(value or "").strip()
    return text or fallback


def _append_section(lines: list[str], title: str) -> None:
    lines.extend(["", f"## {title}"])


def _append_bullets(lines: list[str], values: list[str]) -> None:
    if not values:
        lines.append("- N/D")
        return
    for value in values:
        lines.append(f"- {value}")


def _answer_lines(result: OwnerAnswerToActionCompositionResult) -> list[str]:
    out: list[str] = []
    for answer in result.owner_answers_bundle.answers:
        question = _safe_text(answer.question_text)
        value = _safe_text(answer.answer_text)
        out.append(f"Pregunta: {question} | Respuesta: {value}")
    return out


def _evaluation_lines(result: OwnerAnswerToActionCompositionResult) -> list[str]:
    answers_by_id = {
        answer.answer_id: answer for answer in result.owner_answers_bundle.answers
    }
    out: list[str] = []
    for evaluation in result.evaluation_bundle.evaluations:
        answer = answers_by_id.get(evaluation.source_answer_id)
        question = _safe_text(answer.question_text if answer else None)
        verdict = _safe_text(evaluation.verdict)
        notes = "; ".join(evaluation.notes or evaluation.warnings or [])
        suffix = f" | Notas: {notes}" if notes else ""
        out.append(f"Pregunta: {question} | Evaluación: {verdict}{suffix}")
    return out


def _action_lines(result: OwnerAnswerToActionCompositionResult) -> list[str]:
    out: list[str] = []
    for action in result.resolved_action_bundle.resolved_actions:
        action_type = _safe_text(action.action_type)
        questions = "; ".join(action.resolved_questions) or "N/D"
        out.append(f"Acción: {action_type} | Preguntas: {questions}")
    return out


def _projected_render_lines(result: OwnerAnswerToActionCompositionResult) -> list[str]:
    render_contract = result.projected_render_contract or {}
    out: list[str] = []
    blocked_message = str(render_contract.get("blocked_message") or "").strip()
    if blocked_message:
        out.append(f"Bloqueo visible técnico: {blocked_message}")
    next_questions = render_contract.get("next_questions") or []
    if next_questions:
        out.append("Preguntas proyectadas:")
        out.extend(f"  - {_safe_text(item)}" for item in next_questions)
    next_steps = render_contract.get("next_steps") or []
    if next_steps:
        out.append("Próximos pasos proyectados:")
        out.extend(f"  - {_safe_text(item)}" for item in next_steps)
    return out


def format_composition_result_for_human_review(
    result: OwnerAnswerToActionCompositionResult,
) -> str:
    """Build a human-readable sandbox review from a composition result.

    This formatter is pure: it does not mutate the result, write files, call
    delivery boundaries, or reinterpret answers as evidence.
    """

    lines: list[str] = [
        "# Revisión sandbox de respuestas del dueño",
        "",
        "Tipo: sandbox_owner_answer_replay_review",
        "Estado: revisión técnica no productiva",
        "Límite: no diagnostica y no convierte declaraciones en evidencia dura.",
    ]

    warnings: list[str] = []
    if not result.owner_answers_bundle.answers:
        warnings.append(_EMPTY_WARNING)
    if not result.evaluation_bundle.evaluations:
        warnings.append(_EMPTY_WARNING)
    if not result.resolved_action_bundle.resolved_actions:
        warnings.append(_EMPTY_WARNING)
    if not result.projected_render_contract:
        warnings.append(_EMPTY_WARNING)

    _append_section(lines, "Respuestas capturadas")
    _append_bullets(lines, _answer_lines(result))

    _append_section(lines, "Evaluación de respuestas")
    _append_bullets(lines, _evaluation_lines(result))

    _append_section(lines, "Próxima acción resuelta")
    _append_bullets(lines, _action_lines(result))

    _append_section(lines, "Cambios proyectados en render_contract")
    _append_bullets(lines, _projected_render_lines(result))

    _append_section(lines, "Advertencias y límites")
    base_warnings = [
        "Salida de revisión sandbox, no salida productiva.",
        "No reemplaza la frontera visible soberana.",
        "No agrega diagnóstico ni findings.",
    ]
    _append_bullets(lines, base_warnings + warnings)

    return "\n".join(lines).strip() + "\n"
