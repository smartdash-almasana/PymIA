from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

FirstAidDecision = Literal[
    "USE_IN_PHASE_1",
    "USE_IN_PHASE_1_WITH_GUARDRAILS",
    "NOT_FOR_PHASE_1_PHASE_2",
    "REVIEW_REQUIRED",
    "DO_NOT_MIGRATE",
]


@lru_cache(maxsize=1)
def load_first_aid_toolbox_contract() -> dict[str, Any]:
    """Load the declarative First Aid Toolbox candidate contract.

    This loader is contract-only. It does not execute tools, load runtime plugins,
    calculate formulas, diagnose, or mutate state.
    """
    contract_path = Path(__file__).resolve().parent / "first_aid_toolbox_v1.json"
    if not contract_path.exists():
        return {}
    return json.loads(contract_path.read_text(encoding="utf-8"))


def list_first_aid_components(*, decision: FirstAidDecision | None = None) -> list[dict[str, Any]]:
    contract = load_first_aid_toolbox_contract()
    components = contract.get("components", [])
    if decision is None:
        return list(components)
    return [component for component in components if component.get("decision") == decision]


def get_first_aid_component(component_id: str) -> dict[str, Any] | None:
    normalized_component_id = _required_component_id(component_id)
    for component in list_first_aid_components():
        if component.get("id") == normalized_component_id:
            return component
    return None


def is_allowed_for_first_aid(component_id: str) -> bool:
    component = get_first_aid_component(component_id)
    if component is None:
        return False
    return component.get("decision") in {"USE_IN_PHASE_1", "USE_IN_PHASE_1_WITH_GUARDRAILS"}


def requires_guardrails(component_id: str) -> bool:
    component = get_first_aid_component(component_id)
    if component is None:
        return False
    return component.get("decision") == "USE_IN_PHASE_1_WITH_GUARDRAILS"


def list_first_aid_compositions() -> list[dict[str, Any]]:
    contract = load_first_aid_toolbox_contract()
    return list(contract.get("compositions", []))


def _required_component_id(component_id: str) -> str:
    if not isinstance(component_id, str) or not component_id.strip():
        raise ValueError("component_id is required and must be a non-empty string")
    return component_id.strip()


__all__ = [
    "FirstAidDecision",
    "get_first_aid_component",
    "is_allowed_for_first_aid",
    "list_first_aid_components",
    "list_first_aid_compositions",
    "load_first_aid_toolbox_contract",
    "requires_guardrails",
]
