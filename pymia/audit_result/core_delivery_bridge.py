from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.owner_questions import OwnerQuestionsBundle
from pymia.contracts.scn_output_gateway import (
    build_render_contract_from_operational_audit_result,
)
from pymia.diagnostic_core import (
    DiagnosticCoreV1,
    build_diagnostic_core_input_from_structured_evidence,
    build_evidence_gate_decisions_from_formula_input_results,
    build_formula_input_gate_results_from_structured_evidence,
)
from pymia.diagnostic_core.models import (
    DiagnosticCoreResult,
    DiagnosticCoreInput,
    DiagnosticCoreStatus,
    EvidenceGateDecision,
    FormulaInputGateStatus,
    EvidenceGateDecisionStatus,
    FormulaInputGateResult,
)
from pymia.smartpyme.delivery_package import DeliveryPackage, build_delivery_package
from pymia.smartpyme.execution_result_gate import (
    ExecutionResultGateVerdict,
    validate_execution_result,
)
from pymia.smartpyme.owner_facing_report import build_owner_facing_report
from pymia.smartpyme.owner_answers_composer import compose_owner_answers_to_actions
from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle
from pymia.smartpyme.owner_semantic_confirmation_reentry_projection import (
    project_semantic_confirmation_reentry_to_owner_facing,
)


RUNTIME_CLASSIFICATION_DIAGNOSTIC_CORE = "diagnostic_core_v1"
MICROSERVICE_NAME_DIAGNOSTIC_CORE_BRIDGE = "diagnostic_core_bridge"
STILL_BLOCKED_REQUIRES_STRUCTURED_EVIDENCE = "still_blocked_requires_structured_evidence"
STRUCTURAL_INPUT_OWNER_MESSAGE = (
    "Tu respuesta fue considerada, pero todavía falta evidencia o dato estructurado "
    "para resolver este punto."
)
STRUCTURAL_INPUT_OWNER_WARNING = (
    "Advertencia trazable: la respuesta del dueño fue considerada, pero no reemplaza "
    "evidencia estructurada faltante."
)


@dataclass(frozen=True)
class CoreAuditDeliveryBundle:
    operational_audit_result: dict[str, Any]
    render_contract: dict[str, Any]
    owner_facing_report: dict[str, Any]
    owner_questions_bundle: dict[str, Any]
    execution_result: dict[str, Any]
    gate_verdict: ExecutionResultGateVerdict
    delivery_package: DeliveryPackage
    output_refs: list[str]


def _empty_core_result(
    *,
    case_id: str,
    tenant_id: str,
    missing_evidence: list[str],
) -> DiagnosticCoreResult:
    return DiagnosticCoreResult(
        case_id=case_id,
        tenant_id=tenant_id,
        status=DiagnosticCoreStatus.INSUFFICIENT,
        formula_results=[],
        diagnostic_results=[],
        findings=[],
        missing_evidence=list(missing_evidence),
        blocked_reasons=[],
    )


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


def _append_unique_text(container: dict[str, Any], key: str, value: str) -> None:
    items = list(container.get(key) or [])
    if value not in items:
        items.append(value)
    container[key] = items


def _apply_missing_input_resolution_trace(
    *,
    render_contract: dict[str, Any],
    evaluation_bundle: Any,
) -> None:
    evaluations = list(getattr(evaluation_bundle, "evaluations", []) or [])
    has_structural_gap = any(
        getattr(evaluation, "metadata", {}).get("missing_input_resolution_status")
        == STILL_BLOCKED_REQUIRES_STRUCTURED_EVIDENCE
        for evaluation in evaluations
    )
    if not has_structural_gap:
        return

    _append_unique_text(render_contract, "next_steps", STRUCTURAL_INPUT_OWNER_MESSAGE)
    warning_key = (
        "forbidden_inferences"
        if isinstance(render_contract.get("forbidden_inferences"), list)
        else "limit_warnings"
    )
    _append_unique_text(render_contract, warning_key, STRUCTURAL_INPUT_OWNER_WARNING)


def _apply_semantic_confirmation_reentry_projection(
    *,
    owner_facing_report: dict[str, Any],
    composed: Any,
    missing_keys: list[str],
    source_ref: str,
) -> dict[str, Any]:
    projected = deepcopy(owner_facing_report)
    for owner_answer in getattr(composed.owner_answers_bundle, "answers", []) or []:
        metadata = getattr(owner_answer, "metadata", {}) or {}
        if not isinstance(metadata, dict) or not metadata.get("semantic_confirmation_status"):
            continue
        projected = project_semantic_confirmation_reentry_to_owner_facing(
            owner_answer=owner_answer,
            owner_facing_report=projected,
            missing_keys=list(missing_keys),
            source_ref=source_ref,
        )
    return projected


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


def _filter_formula_ids_for_execution(
    formula_gate_results: list[FormulaInputGateResult],
) -> list[str]:
    return [
        item.formula_id
        for item in formula_gate_results
        if item.status == FormulaInputGateStatus.READY
    ]


def _filter_hypothesis_codes_for_execution(
    formula_ids: list[str],
    hypothesis_codes: list[str],
) -> list[str]:
    if not hypothesis_codes:
        return []
    if len(hypothesis_codes) == len(formula_ids):
        return list(hypothesis_codes)
    return list(hypothesis_codes)


def build_core_delivery_bridge_payload_from_structured_evidence(
    *,
    evidence: StructuredEvidence,
    case_id: str,
    intake_id: str,
    formula_ids: list[str],
    hypothesis_codes: list[str] | None = None,
    core: DiagnosticCoreV1 | None = None,
) -> dict[str, Any]:
    formula_gate_results = build_formula_input_gate_results_from_structured_evidence(
        evidence,
        case_id=case_id,
        tenant_id=evidence.tenant_id,
        formula_ids=formula_ids,
    )
    evidence_gate_decisions = build_evidence_gate_decisions_from_formula_input_results(
        formula_gate_results
    )

    executable_formula_ids = _filter_formula_ids_for_execution(formula_gate_results)
    executable_hypothesis_codes = _filter_hypothesis_codes_for_execution(
        executable_formula_ids,
        list(hypothesis_codes or []),
    )

    if executable_formula_ids:
        core_input: DiagnosticCoreInput = build_diagnostic_core_input_from_structured_evidence(
            evidence,
            case_id=case_id,
            tenant_id=evidence.tenant_id,
            formula_ids=executable_formula_ids,
            hypothesis_codes=executable_hypothesis_codes,
        )
        core_result = (core or DiagnosticCoreV1()).run(core_input)
    else:
        missing_evidence = _collect_missing_evidence(
            formula_gate_results,
            evidence_gate_decisions,
            _empty_core_result(
                case_id=case_id,
                tenant_id=evidence.tenant_id,
                missing_evidence=[],
            ),
        )
        core_result = _empty_core_result(
            case_id=case_id,
            tenant_id=evidence.tenant_id,
            missing_evidence=missing_evidence,
        )

    return {
        "case_id": case_id,
        "intake_id": intake_id,
        "structured_evidence": evidence.model_dump(mode="json"),
        "formula_ids": list(formula_ids),
        "hypothesis_codes": list(hypothesis_codes or []),
        "formula_gate_results": [
            item.model_dump(mode="json") for item in formula_gate_results
        ],
        "evidence_gate_decisions": [
            item.model_dump(mode="json") for item in evidence_gate_decisions
        ],
        "diagnostic_core_result": core_result.model_dump(mode="json"),
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


def _with_output_ref(output_refs: list[str], new_ref: str) -> list[str]:
    refs = list(output_refs)
    if new_ref not in refs:
        refs.append(new_ref)
    return refs


def _question_texts_from_owner_questions_bundle(bundle: dict[str, Any]) -> list[str]:
    questions_raw = bundle.get("questions") or []
    if not isinstance(questions_raw, list):
        return []

    texts: list[str] = []
    seen: set[str] = set()
    for item in questions_raw:
        if not isinstance(item, dict):
            continue
        text = str(item.get("question_text") or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        texts.append(text)
    return texts


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
    owner_report_path = target_dir / "owner_facing_report.json"
    owner_questions_path = target_dir / "owner_questions_bundle.json"

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
    owner_questions_bundle = build_owner_questions_bundle(
        source_ref=str(audit_path),
        missing_evidence=list(operational_audit_result.get("missing_evidence") or []),
        next_questions=list(render_contract.get("next_questions") or []),
        blocked_message=str(render_contract.get("blocked_message") or ""),
        metadata={
            "operational_audit_result_ref": str(audit_path),
            "render_contract_ref": str(render_path),
        },
    ).model_dump(mode="json")
    owner_question_texts = _question_texts_from_owner_questions_bundle(owner_questions_bundle)
    render_contract["next_questions"] = list(owner_question_texts)
    render_contract["blocked_message"] = owner_question_texts[0] if owner_question_texts else ""

    _write_json(render_path, render_contract)
    _write_delivery_summary(summary_path, render_contract)
    _write_json(owner_questions_path, owner_questions_bundle)

    output_refs = [str(summary_path), str(audit_path), str(render_path)]
    output_refs = _with_output_ref(output_refs, str(owner_questions_path))
    execution_result = _build_execution_result(
        intake_id=intake_id,
        core_result=core_result,
        operational_audit_result=operational_audit_result,
        render_contract=render_contract,
        output_refs=output_refs,
    )
    gate_verdict = validate_execution_result(execution_result)
    delivery_package = build_delivery_package(execution_result, gate_verdict)
    delivery_package = DeliveryPackage(
        tenant_id=delivery_package.tenant_id,
        intake_id=delivery_package.intake_id,
        runtime_classification=delivery_package.runtime_classification,
        output_refs=list(output_refs),
        summary=delivery_package.summary,
        warnings=list(delivery_package.warnings),
        reasons=list(delivery_package.reasons),
        gate_verdict=delivery_package.gate_verdict,
        status=delivery_package.status,
        created_at=delivery_package.created_at,
    )
    owner_facing_report = build_owner_facing_report(
        operational_audit_result=operational_audit_result,
        render_contract=render_contract,
        delivery_package=delivery_package,
    ).to_dict()
    _write_json(owner_report_path, owner_facing_report)
    output_refs = _with_output_ref(output_refs, str(owner_report_path))
    execution_result["output_refs"] = list(output_refs)
    delivery_package = DeliveryPackage(
        tenant_id=delivery_package.tenant_id,
        intake_id=delivery_package.intake_id,
        runtime_classification=delivery_package.runtime_classification,
        output_refs=list(output_refs),
        summary=delivery_package.summary,
        warnings=list(delivery_package.warnings),
        reasons=list(delivery_package.reasons),
        gate_verdict=delivery_package.gate_verdict,
        status=delivery_package.status,
        created_at=delivery_package.created_at,
    )

    return CoreAuditDeliveryBundle(
        operational_audit_result=operational_audit_result,
        render_contract=render_contract,
        owner_facing_report=owner_facing_report,
        owner_questions_bundle=owner_questions_bundle,
        execution_result=execution_result,
        gate_verdict=gate_verdict,
        delivery_package=delivery_package,
        output_refs=output_refs,
    )


def project_owner_answers_into_delivery_bundle(
    *,
    delivery_bundle: CoreAuditDeliveryBundle,
    questions_bundle: OwnerQuestionsBundle,
    answers_payload: list[dict[str, Any]],
    source_ref: str,
    tenant_id: str | None = None,
) -> CoreAuditDeliveryBundle:
    bundle_tenant_id = str(delivery_bundle.delivery_package.tenant_id or "").strip()
    if tenant_id is not None and str(tenant_id).strip() != bundle_tenant_id:
        raise ValueError("tenant_id mismatch for delivery bundle reentry")

    composed = compose_owner_answers_to_actions(
        questions_bundle=questions_bundle,
        answers_payload=deepcopy(answers_payload),
        source_ref=source_ref,
        render_contract=deepcopy(delivery_bundle.render_contract),
        tenant_id=tenant_id or bundle_tenant_id,
    )
    projected_render_contract = deepcopy(composed.projected_render_contract)
    _apply_missing_input_resolution_trace(
        render_contract=projected_render_contract,
        evaluation_bundle=composed.evaluation_bundle,
    )
    delivery_package = DeliveryPackage(
        tenant_id=delivery_bundle.delivery_package.tenant_id,
        intake_id=delivery_bundle.delivery_package.intake_id,
        runtime_classification=delivery_bundle.delivery_package.runtime_classification,
        output_refs=list(delivery_bundle.delivery_package.output_refs),
        summary=delivery_bundle.delivery_package.summary,
        warnings=list(delivery_bundle.delivery_package.warnings),
        reasons=list(delivery_bundle.delivery_package.reasons),
        gate_verdict=delivery_bundle.delivery_package.gate_verdict,
        status=delivery_bundle.delivery_package.status,
        created_at=delivery_bundle.delivery_package.created_at,
    )
    execution_result = deepcopy(delivery_bundle.execution_result)
    raw_result = dict(execution_result.get("raw_result") or {})
    raw_result["render_contract"] = deepcopy(projected_render_contract)
    execution_result["raw_result"] = raw_result

    owner_facing_report = build_owner_facing_report(
        operational_audit_result=deepcopy(delivery_bundle.operational_audit_result),
        render_contract=projected_render_contract,
        delivery_package=delivery_package,
    ).to_dict()

    return CoreAuditDeliveryBundle(
        operational_audit_result=deepcopy(delivery_bundle.operational_audit_result),
        render_contract=projected_render_contract,
        owner_facing_report=_apply_semantic_confirmation_reentry_projection(
            owner_facing_report=owner_facing_report,
            composed=composed,
            missing_keys=list(deepcopy(delivery_bundle.operational_audit_result.get("missing_evidence") or [])),
            source_ref=source_ref,
        ),
        owner_questions_bundle=questions_bundle.model_dump(mode="json"),
        execution_result=execution_result,
        gate_verdict=delivery_bundle.gate_verdict,
        delivery_package=delivery_package,
        output_refs=list(delivery_bundle.output_refs),
    )


def project_bridge_result_to_state(
    state: PymIAState,
    bundle: CoreAuditDeliveryBundle,
) -> PymIAState:
    new_state = deepcopy(state)
    owner_summary = str(bundle.owner_facing_report.get("summary") or "").strip()
    new_state.execution_status = str(bundle.execution_result.get("status") or "")
    new_state.gate_verdict = bundle.gate_verdict.verdict
    new_state.delivery_status = bundle.delivery_package.status
    new_state.delivery_summary = owner_summary or bundle.delivery_package.summary
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
    "project_owner_answers_into_delivery_bundle",
    "project_bridge_result_to_state",
]
