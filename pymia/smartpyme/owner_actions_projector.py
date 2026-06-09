from __future__ import annotations

from copy import deepcopy

from pymia.contracts.owner_resolved_actions import OwnerResolvedNextActionBundle


KEEP_AS_DECLARED_STEP = (
    "La respuesta queda registrada como declaración del dueño, no como evidencia validada."
)
REJECT_ANSWER_MESSAGE = (
    "No puedo usar esa respuesta sin una aclaración o respaldo adicional."
)
REJECT_WARNING = (
    "Advertencia trazable: la respuesta fue rechazada y requiere aclaración o respaldo adicional."
)
DECLARED_WARNING = (
    "Advertencia trazable: la respuesta queda como declaración del dueño y no como evidencia validada."
)


def project_resolved_owner_actions_to_render_contract(
    render_contract: dict,
    resolved_action_bundle: OwnerResolvedNextActionBundle,
) -> dict:
    projected = deepcopy(render_contract)
    if not resolved_action_bundle.resolved_actions:
        return projected

    action = resolved_action_bundle.resolved_actions[0]
    resolved_questions = list(action.resolved_questions)

    if action.action_type == "ask_clarification":
        projected["next_questions"] = resolved_questions
        if resolved_questions:
            projected["blocked_message"] = resolved_questions[0]
        return projected

    if action.action_type == "reject_answer":
        projected["next_questions"] = resolved_questions
        projected["blocked_message"] = REJECT_ANSWER_MESSAGE
        _append_warning(projected, REJECT_WARNING)
        return projected

    if action.action_type == "keep_as_declared":
        next_steps = _string_list(projected.get("next_steps"))
        if KEEP_AS_DECLARED_STEP not in next_steps:
            next_steps.append(KEEP_AS_DECLARED_STEP)
        projected["next_steps"] = next_steps
        _append_warning(projected, DECLARED_WARNING)
        return projected

    return projected


def _append_warning(projected: dict, warning: str) -> None:
    warning_key = "forbidden_inferences" if "forbidden_inferences" in projected else "limit_warnings"
    warnings = _string_list(projected.get(warning_key))
    if warning not in warnings:
        warnings.append(warning)
    projected[warning_key] = warnings


def _string_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]
