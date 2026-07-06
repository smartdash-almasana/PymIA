from __future__ import annotations

from typing import Literal, TypedDict

CAPABILITY_REF = "service_1_bank_reconciliation_sandbox_fixture_handoff_v1"

Status = Literal[
    "READY",
    "BLOCKED_FIXTURE_MODEL",
    "BLOCKED_BASE_CONTRACT",
    "BLOCKED_SANDBOX_RELEASE_GATE",
    "BLOCKED_LIVE_USE",
    "INVALID_INPUT",
]


class HandoffInput(TypedDict):
    fixture_model_result: dict[str, object]
    base_contract: dict[str, object]
    sandbox_release_gate: dict[str, object]
    live_use_requested: bool


class HandoffResult(TypedDict):
    capability_ref: str
    status: Status
    runtime_authorized: Literal[False]
    production_allowed: Literal[False]
    sandbox_input_ready: bool
    sandbox_input: dict[str, object] | None
    next_allowed_action: str
    reasons: list[str]


def build_bank_reconciliation_sandbox_fixture_handoff_v1(*, handoff_input: HandoffInput) -> HandoffResult:
    if not isinstance(handoff_input, dict):
        return _result("INVALID_INPUT", None, "fix_invalid_handoff_input", ["Invalid handoff input."])

    fixture_model = handoff_input.get("fixture_model_result")
    base_contract = handoff_input.get("base_contract")
    sandbox_release_gate = handoff_input.get("sandbox_release_gate")

    if not isinstance(fixture_model, dict) or not isinstance(base_contract, dict) or not isinstance(sandbox_release_gate, dict):
        return _result("INVALID_INPUT", None, "fix_invalid_handoff_components", ["Invalid handoff components."])
    if handoff_input.get("live_use_requested") is True:
        return _result("BLOCKED_LIVE_USE", None, "downgrade_to_fixture_scope", ["Live use is blocked."])
    if fixture_model.get("status") != "VALID" or fixture_model.get("valid_for_sandbox_contract") is not True:
        return _result("BLOCKED_FIXTURE_MODEL", None, "complete_fixture_model_first", ["Fixture model is not valid."])
    if base_contract.get("status") != "READY_FOR_REVIEW":
        return _result("BLOCKED_BASE_CONTRACT", None, "complete_base_contract_first", ["Base contract is not ready."])
    if sandbox_release_gate.get("status") != "PASS":
        return _result("BLOCKED_SANDBOX_RELEASE_GATE", None, "complete_sandbox_release_gate_first", ["Sandbox release gate has not passed."])

    refs = fixture_model.get("handoff_refs")
    if not isinstance(refs, list) or not all(isinstance(item, str) for item in refs):
        return _result("INVALID_INPUT", None, "fix_invalid_handoff_refs", ["Invalid handoff refs."])

    sandbox_input = {
        "bank_contract": base_contract,
        "sandbox_release_gate": sandbox_release_gate,
        "fixture_refs": [item.strip() for item in refs if item.strip()],
        "live_use_requested": False,
    }
    return _result("READY", sandbox_input, "call_sandbox_contract", ["Handoff is ready."])


def _result(status: Status, sandbox_input: dict[str, object] | None, next_allowed_action: str, reasons: list[str]) -> HandoffResult:
    return {
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "runtime_authorized": False,
        "production_allowed": False,
        "sandbox_input_ready": status == "READY",
        "sandbox_input": sandbox_input,
        "next_allowed_action": next_allowed_action,
        "reasons": reasons,
    }