from __future__ import annotations

from typing import Final, Literal, TypedDict

CAPABILITY_REF: Final[str] = "service_1_accounting_workpaper_draft_packet_v1"
SERVICE_NAME: Final[str] = "SERVICE_1"

Status = Literal["READY", "BLOCKED", "INVALID_INPUT"]
BlockedReason = Literal[
    "workpaper_contract_not_ready",
    "manifest_model_not_valid",
    "human_review_gate_not_passed",
    "runtime_authorization_forbidden",
    "production_use_forbidden",
    "invalid_packet_input",
    "invalid_packet_components",
]

_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No genera papel de trabajo final.",
    "No certifica evidencia suficiente.",
    "No certifica conclusión contable o fiscal.",
    "No ejecuta plantilla.",
    "No lee archivos soporte.",
    "No genera asientos contables.",
)
_PACKET_SECTIONS: Final[tuple[str, ...]] = (
    "owner_summary",
    "operator_summary",
    "packet_sections",
    "readiness_flags",
    "blocked_reasons",
    "forbidden_claims",
    "next_allowed_action",
)


class WorkpaperDraftPacketInputV1(TypedDict):
    workpaper_contract_result: dict[str, object]
    manifest_model_result: dict[str, object]
    human_review_gate_result: dict[str, object]


class WorkpaperDraftPacketResultV1(TypedDict):
    capability_ref: str
    status: Status
    runtime_authorized: Literal[False]
    production_allowed: Literal[False]
    owner_summary: str
    operator_summary: str
    packet_sections: list[str]
    readiness_flags: dict[str, bool]
    blocked_reasons: list[BlockedReason]
    forbidden_claims: list[str]
    next_allowed_action: str
    delivery_input: dict[str, object]


def build_accounting_workpaper_draft_packet_v1(*, packet_input: WorkpaperDraftPacketInputV1) -> WorkpaperDraftPacketResultV1:
    if not isinstance(packet_input, dict):
        return _packet("INVALID_INPUT", {}, {}, {}, ["invalid_packet_input"], "fix_invalid_workpaper_draft_packet_input")

    contract = packet_input.get("workpaper_contract_result")
    manifest = packet_input.get("manifest_model_result")
    gate = packet_input.get("human_review_gate_result")

    if not isinstance(contract, dict) or not isinstance(manifest, dict) or not isinstance(gate, dict):
        return _packet("INVALID_INPUT", {}, {}, {}, ["invalid_packet_components"], "fix_invalid_workpaper_draft_packet_components")

    blocked: list[BlockedReason] = []
    if contract.get("status") != "READY_FOR_REVIEW":
        blocked.append("workpaper_contract_not_ready")
    if manifest.get("status") != "VALID":
        blocked.append("manifest_model_not_valid")
    if gate.get("status") != "PASS":
        blocked.append("human_review_gate_not_passed")
    if _is_true_flag(contract, "runtime_authorized") or _is_true_flag(manifest, "runtime_authorized") or _is_true_flag(gate, "runtime_authorized"):
        blocked.append("runtime_authorization_forbidden")
    if _is_true_flag(contract, "production_allowed") or _is_true_flag(manifest, "production_allowed") or _is_true_flag(gate, "production_allowed"):
        blocked.append("production_use_forbidden")

    if blocked:
        return _packet("BLOCKED", contract, manifest, gate, blocked, "resolve_blocked_workpaper_draft_packet_inputs")

    return _packet("READY", contract, manifest, gate, [], "prepare_owner_operator_workpaper_draft_review")


def _packet(
    status: Status,
    contract: dict[str, object],
    manifest: dict[str, object],
    gate: dict[str, object],
    blocked_reasons: list[BlockedReason],
    next_allowed_action: str,
) -> WorkpaperDraftPacketResultV1:
    runtime_clear = not (
        _is_true_flag(contract, "runtime_authorized")
        or _is_true_flag(manifest, "runtime_authorized")
        or _is_true_flag(gate, "runtime_authorized")
    )
    production_clear = not (
        _is_true_flag(contract, "production_allowed")
        or _is_true_flag(manifest, "production_allowed")
        or _is_true_flag(gate, "production_allowed")
    )
    readiness_flags = {
        "workpaper_contract_ready": contract.get("status") == "READY_FOR_REVIEW",
        "manifest_model_valid": manifest.get("status") == "VALID",
        "human_review_gate_passed": gate.get("status") == "PASS",
        "runtime_authorization_clear": runtime_clear,
        "production_use_clear": production_clear,
        "ready_for_owner_operator_review": status == "READY",
    }
    owner_summary = _owner_summary(status, blocked_reasons)
    operator_summary = _operator_summary(status, contract, manifest, gate)
    packet_sections = list(_PACKET_SECTIONS)
    forbidden_claims = list(_FORBIDDEN_CLAIMS)
    delivery_input = {
        "service_name": SERVICE_NAME,
        "capability_ref": CAPABILITY_REF,
        "status": status,
        "owner_summary": owner_summary,
        "inputs_used": {
            "workpaper_contract_status": contract.get("status"),
            "manifest_model_status": manifest.get("status"),
            "human_review_gate_status": gate.get("status"),
            "workpaper_contract_ref": contract.get("contract_ref"),
            "evidence_manifest_id": manifest.get("evidence_manifest_id"),
            "template_ref": manifest.get("template_ref"),
            "period_ref": manifest.get("period_ref"),
            "area_revision": manifest.get("area_revision"),
            "human_review_next_action": gate.get("next_allowed_action"),
        },
        "computed_results": {
            "readiness_flags": readiness_flags,
            "packet_sections": packet_sections,
            "blocked_reasons": blocked_reasons,
            "next_allowed_action": next_allowed_action,
        },
        "missing_inputs": blocked_reasons,
        "limitations": [
            "Draft packet only; no final workpaper is generated.",
            "No source files were read and no support files were parsed.",
            "No template runtime was executed.",
            "Human accounting review remains mandatory before any owner-facing interpretation.",
        ],
        "forbidden_claims": forbidden_claims,
        "technical_notes": [operator_summary],
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


def _owner_summary(status: str, blocked_reasons: list[BlockedReason]) -> str:
    if status == "READY":
        return "El paquete borrador de papel de trabajo está listo para revisión owner/operator; no genera un papel final ni certificado."
    if status == "BLOCKED":
        return "El paquete borrador de papel de trabajo está bloqueado por: " + ", ".join(blocked_reasons) + "."
    return "El input del paquete borrador de papel de trabajo es inválido."


def _operator_summary(status: str, contract: dict[str, object], manifest: dict[str, object], gate: dict[str, object]) -> str:
    return (
        "status="
        + status
        + "; workpaper_contract="
        + str(contract.get("status"))
        + "; manifest_model="
        + str(manifest.get("status"))
        + "; human_gate="
        + str(gate.get("status"))
        + "; manifest_id="
        + str(manifest.get("evidence_manifest_id"))
        + "; template_ref="
        + str(manifest.get("template_ref"))
    )


def _is_true_flag(component: dict[str, object], key: str) -> bool:
    return component.get(key) is True
