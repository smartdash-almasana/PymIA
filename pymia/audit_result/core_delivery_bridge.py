from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.scn_output_gateway import (
    build_render_contract_from_operational_audit_result,
)
from pymia.diagnostic_core.models import (
    DiagnosticCoreResult,
    DiagnosticCoreStatus,
    EvidenceGateDecision,
    EvidenceGateDecisionStatus,
    FormulaInputGateResult,
)
from pymia.orchestration.state import PymIAState
from pymia.smartpyme.delivery_package import DeliveryPackage, build_delivery_package
from pymia.smartpyme.execution_result_gate import (
    ExecutionResultGateVerdict,
    validate_execution_result,
)


RUNTIME_CLASSIFICATION_DIAGNOSTIC_CORE = "diagnostic_core_v1"
MICROSERVICE_NAME_DIAGNOSTIC_CORE_BRIDGE = "diagnostic_core_bridge"


@dataclass(frozen=True)
class CoreAuditDeliveryBundle:
    operational_audit_result: dict[str, Any]
    render_contract: dict[str, Any]
    execution_result: dict[str, Any]
    gate_verdict: ExecutionResultGateVerdict
    delivery_package: DeliveryPackage
    output_refs: list[str]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _collect_missing_evidence(
    formula_gate_results: list[FormulaInputGateResult],
    evidence_gate_decisions: list[EvidenceGateDecision],
    core_result: DiagnosticCoreResult,
) -> list[str]:
    missing: list[str] = []
    for item in formula_gate_results:
        missing.extend(item.missing_variables)
    for item in evidence_gate_decisions:
        if item.decision == EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS:
            missing.extend(item.missing_variables)
    missing.extend(core_result.missing_evidence)
    return _dedupe_preserve_order(sorted(missing))


def _collect_references(core_result: DiagnosticCoreResult) -> list[str]:
    refs: list[str] = []
    for item in core_result.formula_results:
        refs.extend(item.source_refs)
    for item in core_result.diagnostic_results:
        refs.extend(item.evidence_refs)
    for item in core_result.findings:
        refs.extend(item.evidence_refs)
    return _dedupe_preserve_order(refs)


def _resolve_operational_status(
    core_result: DiagnosticCoreResult,
    missing_evidence: list[str],
) -> str:
    if missing_evidence:
        return "pending_data"
    if core_result.status in {DiagnosticCoreStatus.BLOCKED, DiagnosticCoreStatus.INSUFFICIENT}:
        return "blocked"
    if core_result.status == DiagnosticCoreStatus.PARTIAL:
        return "candidate"
    return "ok"


def _build_forbidden_inferences() -> list[str]:
    return [
        "No inventar evidencia ni variables faltantes.",
        "No agregar findings fuera de DiagnosticCoreResult.",
        "No diagnosticar mas alla de los estados ya computados.",
        "No generar narrativa owner-facing.",
    ]


def _build_allowed_rendering(
    *,
    status: str,
    missing_evidence: list[str],
    references: list[str],
) -> dict[str, Any]:
    if status in {"pending_data", "blocked"}:
        return {
            "summary": "PymIA no puede completar este resultado sin evidencia adicional.",
            "next_questions": list(missing_evidence),
            "next_steps": [],
            "blocked_message": "Falta evidencia para avanzar al resultado operativo entregable.",
            "references": list(references),
            "must_not_diagnose": True,
            "must_not_create_findings": True,
        }

    return {
        "summary": "Resultado del core materializado para entrega operacional controlada.",
        "next_questions": [],
        "next_steps": ["Revisar referencias y salida soberana antes de cualquier canal externo."],
        "blocked_message": "",
        "references": list(references),
        "must_not_diagnose": True,
        "must_not_create_findings": True,
    }


def build_scn_operational_audit_result_from_core(
    *,
    evidence: StructuredEvidence,
    case_id: str,
    formula_gate_results: list[FormulaInputGateResult],
    evidence_gate_decisions: list[EvidenceGateDecision],
    core_result: DiagnosticCoreResult,
    audit_trail_ref: str,
) -> dict[str, Any]:
    missing_evidence = _collect_missing_evidence(
        formula_gate_results,
        evidence_gate_decisions,
        core_result,
    )
    references = _collect_references(core_result)
    status = _resolve_operational_status(core_result, missing_evidence)
    result_id = f"operational_audit_result_{case_id}"

    return {
        "schema_version": "scn.operational_audit_result.v1",
        "result_id": result_id,
        "tenant_id": evidence.tenant_id,
        "status": status,
        "findings": [item.model_dump(mode="json") for item in core_result.findings],
        "evidence_used": references,
        "missing_evidence": missing_evidence,
        "forbidden_inferences": _build_forbidden_inferences(),
        "allowed_rendering": _build_allowed_rendering(
            status=status,
            missing_evidence=missing_evidence,
            references=references,
        ),
        "audit_trail_ref": audit_trail_ref,
        "sovereign_mark": {
            "issuer": "pymia",
            "mark_type": "diagnostic_core_bridge",
            "mark_value": result_id,
        },
        "created_at": _utc_now_iso(),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_delivery_summary(path: Path, render_contract: dict[str, Any]) -> None:
    references = render_contract.get("references") or []
    next_questions = render_contract.get("next_questions") or []
    blocked_message = str(render_contract.get("blocked_message") or "")
    lines = [
        "# PymIA Delivery Summary",
        "",
        f"Summary: {render_contract.get('summary', '')}",
        f"Blocked message: {blocked_message or 'N/A'}",
        "",
        "Next questions:",
    ]
    if next_questions:
        lines.extend(f"- {item}" for item in next_questions)
    else:
        lines.append("- None")
    lines.extend(["", "References:"])
    if references:
        lines.extend(f"- {item}" for item in references)
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_execution_result(
    *,
    intake_id: str,
    core_result: DiagnosticCoreResult,
    operational_audit_result: dict[str, Any],
    render_contract: dict[str, Any],
    output_refs: list[str],
) -> dict[str, Any]:
    status = (
        "EXECUTED"
        if operational_audit_result["status"] in {"ok", "candidate"}
        else "BLOCKED"
    )
    return {
        "tenant_id": core_result.tenant_id,
        "intake_id": intake_id,
        "runtime_classification": RUNTIME_CLASSIFICATION_DIAGNOSTIC_CORE,
        "microservice_name": MICROSERVICE_NAME_DIAGNOSTIC_CORE_BRIDGE,
        "status": status,
        "output_refs": list(output_refs),
        "findings_count": len(core_result.findings),
        "raw_result": {
            "diagnostic_core_result": core_result.model_dump(mode="json"),
            "operational_audit_result": operational_audit_result,
            "render_contract": render_contract,
        },
        "warnings": [],
        "executed_at": _utc_now_iso(),
        "summary": render_contract.get("summary", ""),
    }


def build_core_audit_delivery_bundle(
    *,
    evidence: StructuredEvidence,
    case_id: str,
    intake_id: str,
    formula_gate_results: list[FormulaInputGateResult],
    evidence_gate_decisions: list[EvidenceGateDecision],
    core_result: DiagnosticCoreResult,
    output_dir: str | Path,
) -> CoreAuditDeliveryBundle:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    audit_path = target_dir / "operational_audit_result.json"
    render_path = target_dir / "render_contract.json"
    summary_path = target_dir / "delivery_summary.md"

    operational_audit_result = build_scn_operational_audit_result_from_core(
        evidence=evidence,
        case_id=case_id,
        formula_gate_results=formula_gate_results,
        evidence_gate_decisions=evidence_gate_decisions,
        core_result=core_result,
        audit_trail_ref=str(audit_path),
    )
    render_contract = build_render_contract_from_operational_audit_result(
        operational_audit_result,
    )

    _write_json(audit_path, operational_audit_result)
    _write_json(render_path, render_contract)
    _write_delivery_summary(summary_path, render_contract)

    output_refs = [str(summary_path), str(audit_path), str(render_path)]
    execution_result = _build_execution_result(
        intake_id=intake_id,
        core_result=core_result,
        operational_audit_result=operational_audit_result,
        render_contract=render_contract,
        output_refs=output_refs,
    )
    gate_verdict = validate_execution_result(execution_result)
    delivery_package = build_delivery_package(execution_result, gate_verdict)

    return CoreAuditDeliveryBundle(
        operational_audit_result=operational_audit_result,
        render_contract=render_contract,
        execution_result=execution_result,
        gate_verdict=gate_verdict,
        delivery_package=delivery_package,
        output_refs=output_refs,
    )


def project_bridge_result_to_state(
    state: PymIAState,
    bundle: CoreAuditDeliveryBundle,
) -> PymIAState:
    new_state = deepcopy(state)
    new_state.execution_status = str(bundle.execution_result.get("status") or "")
    new_state.gate_verdict = bundle.gate_verdict.verdict
    new_state.delivery_status = bundle.delivery_package.status
    new_state.delivery_summary = bundle.delivery_package.summary
    new_state.output_refs = list(bundle.delivery_package.output_refs)
    new_state.findings_count = int(bundle.execution_result.get("findings_count") or 0)

    if bundle.delivery_package.status == "READY_TO_DELIVER":
        new_state.phase = "DELIVERED"
    elif bundle.delivery_package.status == "BLOCKED":
        new_state.phase = "BLOCKED"
    else:
        new_state.phase = "FAILED"

    new_state.add_decision(
        f"M37 bridge projected audit status={bundle.operational_audit_result['status']}"
    )
    new_state.add_decision(
        f"M37 bridge delivery status={bundle.delivery_package.status}"
    )
    new_state.add_decision(
        f"M37 bridge gate verdict={bundle.gate_verdict.verdict}"
    )
    return new_state


__all__ = [
    "CoreAuditDeliveryBundle",
    "RUNTIME_CLASSIFICATION_DIAGNOSTIC_CORE",
    "MICROSERVICE_NAME_DIAGNOSTIC_CORE_BRIDGE",
    "build_scn_operational_audit_result_from_core",
    "build_core_audit_delivery_bundle",
    "project_bridge_result_to_state",
]
