from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, TypedDict

ActivationStatus = Literal[
    "ELIGIBLE",
    "BLOCKED_MISSING_EVIDENCE",
    "BLOCKED_COLUMN_CONFIRMATION",
    "BLOCKED_RESTRICTED_FORMULA",
    "BLOCKED_FORBIDDEN_CLAIM",
    "BLOCKED_SCOPE_MISMATCH",
    "BLOCKED_COMPONENT_NOT_ALIGNED",
    "BLOCKED_RUNTIME_NOT_AUTHORIZED",
]


class FirstAidToolActivationInput(TypedDict, total=False):
    tool_ref: str
    owner_problem: str
    service_depth: str
    available_evidence: dict[str, Any]
    column_confirmation_status: dict[str, str]
    requested_formula_refs: list[str]
    requested_claims: list[str]
    pack_seed_status: str
    runtime_authorized: bool


class FirstAidToolActivationResult(TypedDict):
    tool_ref: str
    activation_status: ActivationStatus
    blocking_reasons: list[str]
    missing_inputs: list[str]
    owner_questions: list[str]
    limitations: list[str]
    escalation_hint: str | None
    runtime_authorized: bool


def evaluate_first_aid_tool_activation(
    activation_input: FirstAidToolActivationInput,
    *,
    activation_contract: dict[str, Any] | None = None,
    pack_seed: dict[str, Any] | None = None,
) -> FirstAidToolActivationResult:
    """Evaluate conceptual First Aid tool activation.

    Pure evaluator. It does not execute tools, calculate formulas, generate XLSX,
    call LLMs, persist data, authorize runtime, or wire into the vertical pipeline.
    """
    contract = activation_contract or load_first_aid_tool_activation_contract()
    seed = pack_seed or load_first_aid_toolbox_pack_seed()

    if contract.get("status") != "CONTRACT_ONLY":
        raise ValueError("activation_contract.status must be CONTRACT_ONLY")

    if seed.get("status") != "CANDIDATE_SEED":
        raise ValueError("pack_seed.status must be CANDIDATE_SEED")

    input_seed_status = activation_input.get("pack_seed_status")
    if input_seed_status != "CANDIDATE_SEED":
        raise ValueError("activation_input.pack_seed_status must be CANDIDATE_SEED")

    tool_ref = _required_str(activation_input, "tool_ref")
    tool_contract = _find_tool_contract(contract, tool_ref)
    limitations = list(tool_contract.get("limitations", [])) if tool_contract else []

    if tool_contract is None or not _tool_exists_in_seed(seed, tool_ref):
        return _blocked(
            tool_ref,
            "BLOCKED_COMPONENT_NOT_ALIGNED",
            [f"tool_ref {tool_ref} is not present in the First Aid pack"],
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="seed_audit_required",
        )

    mapping = _seed_mapping(seed, tool_ref)
    if mapping is None or mapping.get("mapping_status") != "ALIGNED":
        return _blocked(
            tool_ref,
            "BLOCKED_COMPONENT_NOT_ALIGNED",
            [f"tool_ref {tool_ref} has no ALIGNED component mapping"],
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="seed_audit_required",
        )

    if tool_contract.get("component_required") != mapping.get("component_id"):
        return _blocked(
            tool_ref,
            "BLOCKED_COMPONENT_NOT_ALIGNED",
            ["tool component required by activation contract does not match seed mapping"],
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="seed_audit_required",
        )

    service_depth = _required_str(activation_input, "service_depth")
    if service_depth not in set(contract.get("allowed_service_depth", [])):
        return _blocked(
            tool_ref,
            "BLOCKED_SCOPE_MISMATCH",
            [f"service_depth {service_depth} is not allowed for First Aid activation"],
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint=service_depth,
        )

    column_status = activation_input.get("column_confirmation_status", {}) or {}
    unconfirmed_columns = [
        column
        for column, status in column_status.items()
        if str(status).lower() in {"unconfirmed", "ambiguous"}
    ]
    if unconfirmed_columns:
        return _blocked(
            tool_ref,
            "BLOCKED_COLUMN_CONFIRMATION",
            ["computational columns require owner confirmation"],
            missing_inputs=unconfirmed_columns,
            owner_questions=["Confirmá qué significa cada columna computacional dudosa antes de calcular."],
            limitations=limitations,
            runtime_authorized=False,
        )

    requested_formulas = set(activation_input.get("requested_formula_refs", []) or [])
    allowed_formulas = set(tool_contract.get("allowed_formulas", []) or [])
    requested_not_allowed = sorted(requested_formulas - allowed_formulas)
    restricted_formulas = set(tool_contract.get("restricted_formulas", []) or [])
    requested_restricted = sorted(requested_formulas & restricted_formulas)
    if requested_restricted:
        return _blocked(
            tool_ref,
            "BLOCKED_RESTRICTED_FORMULA",
            ["requested formula requires deeper diagnostic sufficiency"],
            missing_inputs=requested_restricted,
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="DETERMINISTIC_DIAGNOSIS",
        )
    if requested_not_allowed:
        return _blocked(
            tool_ref,
            "BLOCKED_RESTRICTED_FORMULA",
            ["requested formula is not allowed for this First Aid tool"],
            missing_inputs=requested_not_allowed,
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="tool_contract_audit_required",
        )

    requested_claims = set(_normalize_items(activation_input.get("requested_claims", []) or []))
    forbidden_claims = set(_normalize_items(tool_contract.get("forbidden_claims", []) or []))
    forbidden_claims.update(_global_forbidden_claims(seed))
    forbidden_requested = sorted(requested_claims & forbidden_claims)
    if forbidden_requested:
        return _blocked(
            tool_ref,
            "BLOCKED_FORBIDDEN_CLAIM",
            ["requested claim is forbidden for this First Aid tool"],
            missing_inputs=forbidden_requested,
            limitations=limitations,
            runtime_authorized=False,
            escalation_hint="reformulate_or_escalate",
        )

    evidence = activation_input.get("available_evidence", {}) or {}
    minimum_evidence = list(tool_contract.get("minimum_evidence", []) or [])
    missing_evidence = [field for field in minimum_evidence if not _has_value(evidence.get(field))]
    if missing_evidence:
        return _blocked(
            tool_ref,
            "BLOCKED_MISSING_EVIDENCE",
            ["minimum evidence is missing"],
            missing_inputs=missing_evidence,
            owner_questions=list(tool_contract.get("owner_questions_if_missing", []) or []),
            limitations=limitations,
            runtime_authorized=False,
        )

    return _blocked(
        tool_ref,
        "BLOCKED_RUNTIME_NOT_AUTHORIZED",
        ["tool is conceptually eligible but runtime execution is not authorized"],
        limitations=limitations,
        runtime_authorized=False,
    )


def load_first_aid_tool_activation_contract() -> dict[str, Any]:
    return _load_contract_json("first_aid_tool_activation_v1.json")


def load_first_aid_toolbox_pack_seed() -> dict[str, Any]:
    return _load_contract_json("first_aid_toolbox_pack_seed_v1.json")


def _load_contract_json(filename: str) -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "contracts" / filename
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{filename} must contain a JSON object")
    return data


def _find_tool_contract(contract: dict[str, Any], tool_ref: str) -> dict[str, Any] | None:
    for tool in contract.get("tool_activation_matrix", []) or []:
        if tool.get("tool_ref") == tool_ref:
            return tool
    return None


def _tool_exists_in_seed(seed: dict[str, Any], tool_ref: str) -> bool:
    return tool_ref in {tool.get("id") for tool in seed.get("tool_refs", []) or []}


def _seed_mapping(seed: dict[str, Any], tool_ref: str) -> dict[str, Any] | None:
    for mapping in seed.get("tool_component_mapping", []) or []:
        if mapping.get("tool_ref") == tool_ref:
            return mapping
    return None


def _required_str(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"activation_input.{field} is required")
    return value


def _normalize_items(items: list[Any]) -> list[str]:
    return [str(item).strip().lower() for item in items if str(item).strip()]


def _global_forbidden_claims(seed: dict[str, Any]) -> set[str]:
    claims: list[Any] = []
    owner_language = seed.get("owner_language", {}) or {}
    claims.extend(owner_language.get("forbidden_claims", []) or [])
    claims.extend(seed.get("forbidden_claims", []) or [])
    return set(_normalize_items(claims))


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _blocked(
    tool_ref: str,
    status: ActivationStatus,
    blocking_reasons: list[str],
    *,
    missing_inputs: list[str] | None = None,
    owner_questions: list[str] | None = None,
    limitations: list[str] | None = None,
    escalation_hint: str | None = None,
    runtime_authorized: bool,
) -> FirstAidToolActivationResult:
    return {
        "tool_ref": tool_ref,
        "activation_status": status,
        "blocking_reasons": blocking_reasons,
        "missing_inputs": missing_inputs or [],
        "owner_questions": owner_questions or [],
        "limitations": limitations or [],
        "escalation_hint": escalation_hint,
        "runtime_authorized": runtime_authorized,
    }


__all__ = [
    "ActivationStatus",
    "FirstAidToolActivationInput",
    "FirstAidToolActivationResult",
    "evaluate_first_aid_tool_activation",
    "load_first_aid_tool_activation_contract",
    "load_first_aid_toolbox_pack_seed",
]
