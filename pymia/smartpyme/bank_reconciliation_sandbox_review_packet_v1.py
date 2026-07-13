from __future__ import annotations

from typing import Literal, TypedDict

CAPABILITY_REF = "service_1_bank_reconciliation_sandbox_review_packet_v1"

Status = Literal["READY", "BLOCKED", "INVALID_INPUT"]


class ReviewPacketInput(TypedDict):
    fixture_model_result: dict[str, object]
    fixture_handoff_result: dict[str, object]
    sandbox_contract_result: dict[str, object]


class ReviewPacketResult(TypedDict):
    capability_ref: str
    status: Status
    runtime_authorized: Literal[False]
    production_allowed: Literal[False]
    owner_summary: str
    operator_summary: str
    packet_sections: list[str]
    readiness_flags: dict[str, bool]
    blocked_reasons: list[str]
    forbidden_claims: list[str]
    next_allowed_action: str
    delivery_input: dict[str, object]


def build_bank_reconciliation_sandbox_review_packet_v1(*, packet_input: ReviewPacketInput) -> ReviewPacketResult:
    if not isinstance(packet_input, dict):
        return _packet("INVALID_INPUT", {}, {}, {}, ["Invalid packet input."], "fix_invalid_review_packet_input")

    fixture_model = packet_input.get("fixture_model_result")
    handoff = packet_input.get("fixture_handoff_result")
    sandbox_contract = packet_input.get("sandbox_contract_result")

    if not isinstance(fixture_model, dict) or not isinstance(handoff, dict) or not isinstance(sandbox_contract, dict):
        return _packet("INVALID_INPUT", {}, {}, {}, ["Invalid packet components."], "fix_invalid_review_packet_components")

    blocked: list[str] = []
    if fixture_model.get("status") != "VALID":
        blocked.append("fixture_model_not_valid")
    if handoff.get("status") != "READY":
        blocked.append("fixture_handoff_not_ready")
    if sandbox_contract.get("status") != "READY_FOR_SANDBOX_CONTRACT":
        blocked.append("sandbox_contract_not_ready")

    if blocked:
        return _packet("BLOCKED", fixture_model, handoff, sandbox_contract, blocked, "resolve_blocked_review_packet_inputs")

    return _packet("READY", fixture_model, handoff, sandbox_contract, [], "prepare_owner_operator_review")


def _packet(
    status: Status,
    fixture_model: dict[str, object],
    handoff: dict[str, object],
    sandbox_contract: dict[str, object],
    blocked_reasons: list[str],
    next_allowed_action: str,
) -> ReviewPacketResult:
    readiness_flags = {
        "fixture_model_valid": fixture_model.get("status") == "VALID",
        "handoff_ready": handoff.get("status") == "READY",
        "sandbox_contract_ready": sandbox_contract.get("status") == "READY_FOR_SANDBOX_CONTRACT",
        "runtime_authorized": False,
        "production_allowed": False,
    }
    packet_sections = [
        "owner_summary",
        "operator_summary",
        "readiness_flags",
        "fixture_refs",
        "limitations",
        "forbidden_claims",
        "next_allowed_action",
    ]
    owner_summary = _owner_summary(status, blocked_reasons)
    operator_summary = _operator_summary(status, fixture_model, handoff, sandbox_contract)
    forbidden_claims = [
        "No confirma saldo conciliado.",
        "No confirma diferencia final.",
        "No genera asientos contables.",
        "No certifica exactitud contable o fiscal.",
    ]
    delivery_input = {
        "service_name": "SERVICE_1",
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": owner_summary,
        "inputs_used": {
            "fixture_model_status": fixture_model.get("status"),
            "fixture_handoff_status": handoff.get("status"),
            "sandbox_contract_status": sandbox_contract.get("status"),
        },
        "computed_results": {
            "readiness_flags": readiness_flags,
            "packet_sections": packet_sections,
            "next_allowed_action": next_allowed_action,
        },
        "missing_inputs": blocked_reasons,
        "limitations": ["Review packet only. No movement comparison or execution."],
        "forbidden_claims": forbidden_claims,
        "technical_notes": ["Pure deterministic owner/operator packet over existing sandbox outputs."],
        "runtime_authorized": False,
    }
    return {
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "runtime_authorized": False,
        "production_allowed": False,
        "owner_summary": owner_summary,
        "operator_summary": operator_summary,
        "packet_sections": packet_sections,
        "readiness_flags": readiness_flags,
        "blocked_reasons": blocked_reasons,
        "forbidden_claims": forbidden_claims,
        "next_allowed_action": next_allowed_action,
        "delivery_input": delivery_input,
    }


def _owner_summary(status: str, blocked_reasons: list[str]) -> str:
    if status == "READY":
        return "El paquete de revisión sandbox está listo; no ejecuta conciliación ni confirma saldos."
    if status == "BLOCKED":
        return "El paquete de revisión sandbox está bloqueado por: " + ", ".join(blocked_reasons) + "."
    return "El input del paquete de revisión sandbox es inválido."


def _operator_summary(
    status: str,
    fixture_model: dict[str, object],
    handoff: dict[str, object],
    sandbox_contract: dict[str, object],
) -> str:
    return (
        "status="
        + status
        + "; fixture_model="
        + str(fixture_model.get("status"))
        + "; handoff="
        + str(handoff.get("status"))
        + "; sandbox_contract="
        + str(sandbox_contract.get("status"))
    )
