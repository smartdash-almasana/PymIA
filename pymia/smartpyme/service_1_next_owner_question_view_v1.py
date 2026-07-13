from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "SERVICE_1_NEXT_OWNER_QUESTION_VIEW_V1"
SERVICE_NAME = "SERVICE_1"
FILENAME = "next_owner_question.md"


def build_service_1_next_owner_question_view_v1(packet: dict[str, Any]) -> dict[str, Any]:
    """Build a readable next-question view for the PyME owner.

    The view is generated only when the owner reentry projection has a next
    pending question ref and the canonical question bundle is available in the
    packet. It does not authorize tools, delivery, recalculation or runtime.
    """
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")

    bridge = packet.get("owner_reentry_bridge")
    bundle = packet.get("question_bundle")
    if not isinstance(bridge, dict):
        return _blocked("OWNER_REENTRY_BRIDGE_MISSING")
    if not isinstance(bundle, dict):
        return _blocked("QUESTION_BUNDLE_MISSING")

    next_ref = bridge.get("selected_next_pending_question_ref")
    if not next_ref:
        return {
            "schema_version": SCHEMA_VERSION,
            "service_name": SERVICE_NAME,
            "status": "NO_NEXT_PENDING_QUESTION",
            "filename": None,
            "selected_next_pending_question_ref": None,
            "markdown": None,
            "runtime_authorized": False,
            "delivery_authorized": False,
            "blocked_reason": None,
        }

    questions = bundle.get("questions")
    if not isinstance(questions, list):
        return _blocked("QUESTION_BUNDLE_QUESTIONS_INVALID")

    selected = None
    for question in questions:
        if isinstance(question, dict) and question.get("question_ref") == next_ref:
            selected = question
            break
    if selected is None:
        return _blocked("NEXT_QUESTION_REF_NOT_FOUND")

    text = str(selected.get("text") or "").strip()
    if not text:
        return _blocked("NEXT_QUESTION_TEXT_EMPTY")

    markdown = _render_markdown(
        question_ref=str(next_ref),
        question_text=text,
        target_ref=str(selected.get("target_ref") or ""),
        answer_type=str(selected.get("answer_type") or "free_text"),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": "READY",
        "filename": FILENAME,
        "selected_next_pending_question_ref": str(next_ref),
        "question_text": text,
        "markdown": markdown,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "blocked_reason": None,
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "status": "BLOCKED",
        "filename": None,
        "selected_next_pending_question_ref": None,
        "markdown": None,
        "runtime_authorized": False,
        "delivery_authorized": False,
        "blocked_reason": reason,
    }


def _render_markdown(*, question_ref: str, question_text: str, target_ref: str, answer_type: str) -> str:
    lines = [
        "# Próxima pregunta para el dueño",
        "",
        "PymIA necesita una respuesta concreta antes de seguir procesando evidencia.",
        "",
        f"**Pregunta:** {question_text}",
        "",
        f"**Referencia:** `{question_ref}`",
        f"**Tipo de respuesta esperado:** `{answer_type}`",
    ]
    if target_ref:
        lines.append(f"**Evidencia o punto relacionado:** `{target_ref}`")
    lines.extend(
        [
            "",
            "## Regla",
            "",
            "Si el dueño no puede responder, el caso debe quedar pendiente o bloqueado. No se inventa evidencia.",
        ]
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "FILENAME",
    "build_service_1_next_owner_question_view_v1",
]
