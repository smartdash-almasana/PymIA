from __future__ import annotations

from typing import Literal, TypedDict

CAPABILITY_REF = "service_1_bank_reconciliation_sandbox_contract_v1"

Status = Literal[
    "READY_FOR_SANDBOX_CONTRACT",
    "BLOCKED_BANK_CONTRACT_NOT_READY",
    "BLOCKED_HUMAN_REVIEW_NOT_PASSED",
    "MISSING_FIXTURES",
    "BLOCKED_LIVE_USE",
    "INVALID_INPUT",
]


class SandboxInput(TypedDict):
    bank_contract: dict[str, object]
    human_review_gate: dict[str, object]
    fixture_refs: list[str]
    live_use_requested: bool


class SandboxResult(TypedDict):
    capability_ref: str
    status: Status
    required_fixture_refs: list[str]
    fixture_refs: list[str]
    missing_fixture_refs: list[str]
    runtime_authorized: Literal[False]
    sandbox_candidate_allowed: bool
    production_allowed: Literal[False]
    next_allowed_action: str
    reasons: list[str]
    delivery_input: dict[str, object]


def build_bank_reconciliation_sandbox_contract_v1(*, sandbox_input: SandboxInput) -> SandboxResult:
    required_fixtures = ["bank_statement_fixture", "internal_ledger_fixture"]
    fixture_refs = sandbox_input.get("fixture_refs")
    if not isinstance(fixture_refs, list) or not all(isinstance(item, str) for item in fixture_refs):
        return _result("INVALID_INPUT", [], required_fixtures, False, "fix_invalid_sandbox_contract_input", ["Invalid fixture refs."])

    clean_fixtures = [item.strip() for item in fixture_refs if item.strip()]
    missing_fixtures = [item for item in required_fixtures if item not in clean_fixtures]
    bank_contract = sandbox_input.get("bank_contract")
    human_review_gate = sandbox_input.get("human_review_gate")

    if sandbox_input.get("live_use_requested") is True:
        return _result("BLOCKED_LIVE_USE", clean_fixtures, missing_fixtures, False, "downgrade_to_fixture_scope", ["Live use is blocked."])
    if not isinstance(bank_contract, dict) or bank_contract.get("status") != "READY_FOR_REVIEW":
        return _result("BLOCKED_BANK_CONTRACT_NOT_READY", clean_fixtures, missing_fixtures, False, "complete_bank_contract_first", ["Bank contract is not ready."])
    if not isinstance(human_review_gate, dict) or human_review_gate.get("status") != "PASS":
        return _result("BLOCKED_HUMAN_REVIEW_NOT_PASSED", clean_fixtures, missing_fixtures, False, "complete_human_review_gate_first", ["Human review gate has not passed."])
    if missing_fixtures:
        return _result("MISSING_FIXTURES", clean_fixtures, missing_fixtures, False, "provide_required_fixtures", ["Required fixtures are missing."])

    return _result("READY_FOR_SANDBOX_CONTRACT", clean_fixtures, [], True, "prepare_fixture_sandbox", ["Sandbox contract is ready for fixture-only preparation."])


def _result(
    status: Status,
    fixture_refs: list[str],
    missing_fixture_refs: list[str],
    sandbox_candidate_allowed: bool,
    next_allowed_action: str,
    reasons: list[str],
) -> SandboxResult:
    delivery_input = {
        "service_name": "SERVICE_1",
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": _owner_summary(status, missing_fixture_refs),
        "inputs_used": {
            "fixture_refs": fixture_refs,
            "required_fixture_refs": ["bank_statement_fixture", "internal_ledger_fixture"],
        },
        "computed_results": {
            "sandbox_candidate_allowed": sandbox_candidate_allowed,
            "production_allowed": False,
            "next_allowed_action": next_allowed_action,
        },
        "missing_inputs": missing_fixture_refs,
        "limitations": ["Fixture-only sandbox contract. No live execution."],
        "forbidden_claims": [
            "No confirma saldo conciliado.",
            "No confirma diferencia final.",
            "No genera asientos contables.",
            "No certifica exactitud contable o fiscal.",
        ],
        "technical_notes": ["Pure deterministic sandbox contract boundary."],
        "runtime_authorized": False,
    }
    return {
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "required_fixture_refs": ["bank_statement_fixture", "internal_ledger_fixture"],
        "fixture_refs": fixture_refs,
        "missing_fixture_refs": missing_fixture_refs,
        "runtime_authorized": False,
        "sandbox_candidate_allowed": sandbox_candidate_allowed,
        "production_allowed": False,
        "next_allowed_action": next_allowed_action,
        "reasons": reasons,
        "delivery_input": delivery_input,
    }


def _owner_summary(status: str, missing_fixture_refs: list[str]) -> str:
    if status == "READY_FOR_SANDBOX_CONTRACT":
        return "El contrato sandbox quedó listo para preparación con fixtures; no ejecuta conciliación real."
    if status == "MISSING_FIXTURES":
        return "Faltan fixtures obligatorios: " + ", ".join(missing_fixture_refs) + "."
    if status == "BLOCKED_BANK_CONTRACT_NOT_READY":
        return "Primero debe quedar listo el contrato base de conciliación bancaria."
    if status == "BLOCKED_HUMAN_REVIEW_NOT_PASSED":
        return "Primero debe aprobarse la puerta humana contable."
    if status == "BLOCKED_LIVE_USE":
        return "El uso con datos reales está bloqueado para este contrato sandbox."
    return "El input del contrato sandbox es inválido."
