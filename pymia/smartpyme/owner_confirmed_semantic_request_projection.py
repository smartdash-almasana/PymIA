from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from pymia.smartpyme.owner_confirmed_semantic_request_flow import (
    OwnerConfirmedSemanticRequestFlowResult,
)

_BLOCKED_ACTIONABLE_STEP = (
    "El eje semántico confirmado permite pedir evidencia concreta, "
    "pero todavía no habilita diagnóstico."
)
_BLOCKED_ACTIONABLE_WARNING = (
    "La interpretación fue confirmada o corregida por el dueño, pero no reemplaza "
    "evidencia estructural faltante."
)
_PENDING_CONFIRMATION_STEP = (
    "Antes de pedir evidencia final, el dueño debe confirmar o corregir el eje semántico propuesto."
)
_NEEDS_REINTERPRETATION_STEP = (
    "El dueño rechazó el eje semántico propuesto; corresponde reformular la interpretación antes de pedir evidencia final."
)


def _as_report_dict(owner_facing_report: Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(owner_facing_report, Mapping):
        return dict(owner_facing_report)
    if hasattr(owner_facing_report, "to_dict") and callable(owner_facing_report.to_dict):
        data = owner_facing_report.to_dict()
        if not isinstance(data, dict):
            raise ValueError("owner_facing_report.to_dict() must return dict")
        return dict(data)
    if hasattr(owner_facing_report, "model_dump") and callable(owner_facing_report.model_dump):
        data = owner_facing_report.model_dump(mode="json")
        if not isinstance(data, dict):
            raise ValueError("owner_facing_report.model_dump() must return dict")
        return dict(data)
    raise ValueError("owner_facing_report must be mapping or expose to_dict()/model_dump()")


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def _append_unique(items: list[str], value: str) -> list[str]:
    text = str(value or "").strip()
    if text and text not in items:
        items.append(text)
    return items


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        _append_unique(result, value)
    return result


def project_confirmed_semantic_requests_to_owner_facing(
    *,
    owner_facing_report: Mapping[str, Any] | Any,
    flow_result: OwnerConfirmedSemanticRequestFlowResult,
) -> dict[str, Any]:
    """Project semantic evidence requests into an owner-facing report copy.

    This function does not change status, findings, evidence_used or missing_evidence.
    It only enriches owner-visible next steps/questions/warnings with traceable
    BLOCKED_ACTIONABLE guidance.
    """

    report = deepcopy(_as_report_dict(owner_facing_report))

    next_steps = _dedupe(_string_list(report.get("next_steps")))
    next_questions = _dedupe(_string_list(report.get("next_questions")))
    limit_warnings = _dedupe(_string_list(report.get("limit_warnings")))

    if flow_result.flow_status == "BLOCKED_ACTIONABLE":
        _append_unique(next_steps, _BLOCKED_ACTIONABLE_STEP)
        _append_unique(limit_warnings, _BLOCKED_ACTIONABLE_WARNING)
        for request in flow_result.semantic_evidence_requests:
            _append_unique(next_questions, request.refined_request_text)
    elif flow_result.flow_status == "PENDING_OWNER_CONFIRMATION":
        _append_unique(next_steps, _PENDING_CONFIRMATION_STEP)
    elif flow_result.flow_status == "NEEDS_REINTERPRETATION":
        _append_unique(next_steps, _NEEDS_REINTERPRETATION_STEP)

    report["next_steps"] = next_steps
    report["next_questions"] = next_questions
    report["limit_warnings"] = limit_warnings
    report["semantic_request_projection"] = {
        "flow_status": flow_result.flow_status,
        "requests_count": len(flow_result.semantic_evidence_requests),
        "unsupported_missing_keys": list(flow_result.unsupported_missing_keys),
        "does_resolve_structural_input": False,
        "produces_findings": False,
    }
    return report


__all__ = ["project_confirmed_semantic_requests_to_owner_facing"]
