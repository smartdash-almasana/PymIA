from __future__ import annotations

from typing import Literal, TypedDict

from pymia.smartpyme.first_aid_entrypoint import FirstAidEntrypointVerdict

FirstAidOwnerOutputStatus = Literal["REQUEST_EVIDENCE", "READY_FOR_REVIEW", "REDIRECT_TO_DEEPER_INTAKE"]


class FirstAidOwnerOutput(TypedDict):
    status: FirstAidOwnerOutputStatus
    message: str
    next_step_hint: str
    required_artifacts: list[str]
    next_question: str
    limits: list[str]


def build_first_aid_owner_view(*, verdict: FirstAidEntrypointVerdict) -> FirstAidOwnerOutput:
    """Translate a FIRST_AID entrypoint verdict into owner-facing language.

    This helper is intentionally pure and presentation-light. It only translates
    the verdict into owner-facing guidance without exposing technical identifiers
    or causing side effects.
    """
    status = verdict["status"]

    if status == "FIRST_AID_NEEDS_EVIDENCE":
        return {
            "status": "REQUEST_EVIDENCE",
            "message": (
                "Puedo ayudarte a hacer una primera revisión, pero antes necesito que me compartas "
                "la planilla, archivo o fuente mínima que querés ordenar."
            ),
            "next_step_hint": "Adjuntar una fuente concreta para una revisión inicial.",
            "required_artifacts": list(verdict.get("required_evidence") or ["minimal_file_or_source"]),
            "next_question": "¿Qué archivo o fuente querés que revisemos primero?",
            "limits": [_first_aid_limit_text()],
        }

    if status == "FIRST_AID_READY":
        return {
            "status": "READY_FOR_REVIEW",
            "message": (
                "Con esta fuente puedo hacer una revisión inicial y ayudarte a separar qué se puede "
                "leer, qué está desordenado y cuál sería el próximo dato útil."
            ),
            "next_step_hint": "Ejecutar una revisión inicial de una sola fuente.",
            "required_artifacts": [],
            "next_question": "¿Querés que empecemos por ordenar esta fuente y marcar el próximo dato útil?",
            "limits": [_first_aid_limit_text()],
        }

    if status == "NOT_FIRST_AID":
        return {
            "status": "REDIRECT_TO_DEEPER_INTAKE",
            "message": (
                "Esto parece necesitar más contexto que una revisión inicial de una sola fuente. "
                "Conviene ordenar primero el tipo de negocio, el dolor principal y la evidencia disponible."
            ),
            "next_step_hint": "Completar una anamnesis mínima antes de avanzar.",
            "required_artifacts": [],
            "next_question": "¿Cuál es el dolor principal que querés ordenar primero y qué evidencia tenés para contrastarlo?",
            "limits": [_first_aid_limit_text()],
        }

    raise ValueError(f"Unsupported FIRST_AID entrypoint status: {status}")


def _first_aid_limit_text() -> str:
    return "Esto es una revisión inicial de una fuente; no reemplaza una evaluación integral de la empresa."


__all__ = [
    "FirstAidOwnerOutput",
    "FirstAidOwnerOutputStatus",
    "build_first_aid_owner_view",
]
