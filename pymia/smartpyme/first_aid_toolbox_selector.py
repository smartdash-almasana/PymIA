from __future__ import annotations

from typing import Any, Literal, TypedDict

from pymia.contracts.first_aid_toolbox_v1 import (
    get_first_aid_component,
    list_first_aid_components,
    list_first_aid_compositions,
)
from pymia.smartpyme.first_aid_entrypoint import FirstAidEntrypointVerdict

FirstAidToolboxSelectionStatus = Literal[
    "TOOLBOX_SELECTION_READY",
    "TOOLBOX_SELECTION_NEEDS_EVIDENCE",
    "TOOLBOX_SELECTION_NOT_ALLOWED",
]


class FirstAidToolboxComponent(TypedDict):
    id: str
    source: str
    component_type: str
    decision: str
    family: str
    owner_limit: str


class FirstAidToolboxComposition(TypedDict):
    id: str
    component_ids: list[str]
    output_limit: str
    components: list[FirstAidToolboxComponent]


class FirstAidToolboxSelection(TypedDict):
    status: FirstAidToolboxSelectionStatus
    tenant_id: str
    intake_id: str
    allowed_to_present_toolbox: bool
    next_allowed_action: str
    components: list[FirstAidToolboxComponent]
    compositions: list[FirstAidToolboxComposition]
    warnings: list[str]


def select_first_aid_toolbox(entrypoint_verdict: FirstAidEntrypointVerdict) -> FirstAidToolboxSelection:
    """Select candidate First Aid toolbox components after entrypoint gating.

    This selector is pure and contract-only. It does not execute toolbox components,
    calculate formulas, diagnose, read files, persist data, or call the vertical pipeline.
    """
    _validate_entrypoint_verdict(entrypoint_verdict)

    tenant_id = entrypoint_verdict["tenant_id"]
    intake_id = entrypoint_verdict["intake_id"]

    if entrypoint_verdict["status"] == "FIRST_AID_READY":
        components = _phase_1_components()
        compositions = _phase_1_compositions()
        return {
            "status": "TOOLBOX_SELECTION_READY",
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "allowed_to_present_toolbox": True,
            "next_allowed_action": "present_first_aid_toolbox_candidates",
            "components": components,
            "compositions": compositions,
            "warnings": [],
        }

    if entrypoint_verdict["status"] == "FIRST_AID_NEEDS_EVIDENCE":
        return {
            "status": "TOOLBOX_SELECTION_NEEDS_EVIDENCE",
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "allowed_to_present_toolbox": False,
            "next_allowed_action": "request_minimal_evidence",
            "components": [],
            "compositions": [],
            "warnings": ["FIRST_AID toolbox selection requires minimal evidence before presenting candidates."],
        }

    return {
        "status": "TOOLBOX_SELECTION_NOT_ALLOWED",
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "allowed_to_present_toolbox": False,
        "next_allowed_action": entrypoint_verdict["next_allowed_action"],
        "components": [],
        "compositions": [],
        "warnings": ["FIRST_AID toolbox selection is not allowed for this service depth."],
    }


def _phase_1_components() -> list[FirstAidToolboxComponent]:
    return [
        _component_view(component)
        for component in list_first_aid_components()
        if component.get("decision") in {"USE_IN_PHASE_1", "USE_IN_PHASE_1_WITH_GUARDRAILS"}
    ]


def _phase_1_compositions() -> list[FirstAidToolboxComposition]:
    selected_compositions: list[FirstAidToolboxComposition] = []
    for composition in list_first_aid_compositions():
        components = [_component_view(get_first_aid_component(component_id)) for component_id in composition["component_ids"]]
        selected_compositions.append(
            {
                "id": composition["id"],
                "component_ids": list(composition["component_ids"]),
                "output_limit": composition["output_limit"],
                "components": components,
            }
        )
    return selected_compositions


def _component_view(component: dict[str, Any] | None) -> FirstAidToolboxComponent:
    if component is None:
        raise ValueError("composition references an unknown First Aid component")
    return {
        "id": str(component["id"]),
        "source": str(component["source"]),
        "component_type": str(component["component_type"]),
        "decision": str(component["decision"]),
        "family": str(component["family"]),
        "owner_limit": str(component["owner_limit"]),
    }


def _validate_entrypoint_verdict(entrypoint_verdict: FirstAidEntrypointVerdict) -> None:
    if not isinstance(entrypoint_verdict, dict):
        raise ValueError("entrypoint_verdict must be a dict")
    for field in ["status", "tenant_id", "intake_id", "next_allowed_action"]:
        value = entrypoint_verdict.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"entrypoint_verdict.{field} is required")


__all__ = [
    "FirstAidToolboxComponent",
    "FirstAidToolboxComposition",
    "FirstAidToolboxSelection",
    "FirstAidToolboxSelectionStatus",
    "select_first_aid_toolbox",
]
