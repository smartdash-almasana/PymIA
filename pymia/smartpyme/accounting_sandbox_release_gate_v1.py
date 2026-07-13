from __future__ import annotations

from typing import Literal, TypedDict

GATE_REF = "service_1_accounting_sandbox_release_gate_v1"

Status = Literal["PASS", "PENDING", "REJECTED", "BLOCKED", "INVALID_INPUT"]


class GateInput(TypedDict):
    capability_ref: str
    responsible_role: str
    decision: str
    scope_ok: bool
    evidence_ok: bool
    forbidden_claims: list[str]
    live_use: bool


class GateResult(TypedDict):
    gate_ref: str
    status: Status
    runtime_authorized: Literal[False]
    sandbox_candidate_allowed: bool
    next_allowed_action: str
    reasons: list[str]


def evaluate_accounting_sandbox_release_gate_v1(*, gate_input: GateInput) -> GateResult:
    if not isinstance(gate_input.get("forbidden_claims"), list):
        return _build_result("INVALID_INPUT", False, "fix_invalid_gate_input", ["Invalid forbidden_claims."])
    if gate_input.get("live_use") is True:
        return _build_result("BLOCKED", False, "downgrade_to_sandbox_candidate_scope", ["Live accounting use is blocked."])
    if any(str(claim).strip() for claim in gate_input.get("forbidden_claims", [])):
        return _build_result("BLOCKED", False, "remove_forbidden_accounting_claims", ["Forbidden accounting claims are present."])
    if gate_input.get("scope_ok") is not True:
        return _build_result("BLOCKED", False, "validate_accounting_scope", ["Scope is not validated."])
    if gate_input.get("evidence_ok") is not True:
        return _build_result("BLOCKED", False, "request_missing_accounting_evidence", ["Evidence is insufficient."])
    if gate_input.get("decision") == "REJECTED":
        return _build_result("REJECTED", False, "revise_accounting_sandbox_candidate", ["Sandbox release gate rejected the candidate."])
    if gate_input.get("decision") == "APPROVED":
        return _build_result("PASS", True, "prepare_accounting_sandbox_contract", ["Sandbox release gate passed for sandbox candidate only."])
    return _build_result("PENDING", False, "request_accounting_sandbox_release_decision", ["Sandbox release decision is pending."])


def _build_result(status: Status, sandbox_candidate_allowed: bool, next_allowed_action: str, reasons: list[str]) -> GateResult:
    return {
        "gate_ref": GATE_REF,
        "status": status,
        "runtime_authorized": False,
        "sandbox_candidate_allowed": sandbox_candidate_allowed,
        "next_allowed_action": next_allowed_action,
        "reasons": reasons,
    }
