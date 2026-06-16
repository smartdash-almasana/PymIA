from __future__ import annotations

from pathlib import Path

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.formula_rules_v1 import load_formula_rules
from pymia.services.diagnostic_pipeline import (
    formula_pathology_map_from_catalog_reconciliation,
    run_diagnostic_pipeline_from_structured_evidence,
)
from pymia.smartpyme.question_resolution import _build_owner_question


def _serializable_diagnostic_pipeline_result(result) -> dict:
    return {
        "core_input": result.core_input.model_dump(mode="json"),
        "gate_decisions": [item.model_dump(mode="json") for item in result.gate_decisions],
        "formula_results": [item.model_dump(mode="json") for item in result.formula_results],
        "pathology_findings": [item.model_dump(mode="json") for item in result.pathology_findings],
        "finding_records": [item.model_dump(mode="json") for item in result.finding_records],
        "report": result.report.model_dump(mode="json") if result.report else None,
    }


def _diagnostic_pipeline_result_for_report(
    *,
    path: Path,
    tenant_id: str,
    intake_id: str,
    cliente_id: str,
    structured_summary: dict,
) -> dict | None:
    from pymia.smartpyme.structured_evidence_builder import build_structured_evidence_context

    reconciliation = structured_summary.get("catalog_reconciliation") or []
    relevant_reconciliation = [
        entry for entry in reconciliation
        if isinstance(entry, dict) and str(entry.get("status") or "").lower() in ("calculable", "pending_data", "blocked")
    ]
    if not relevant_reconciliation:
        return None

    rules = load_formula_rules()
    rules_by_formula = rules.get("rules_by_formula", {})
    formula_to_pathology = {
        formula_id: pathology_code
        for formula_id, pathology_code in formula_pathology_map_from_catalog_reconciliation(relevant_reconciliation).items()
        if formula_id in rules_by_formula
    }
    if not formula_to_pathology:
        return None

    payload = build_structured_evidence_context(
        excel_path=path,
        tenant_id=tenant_id,
        intake_record={"evidence_requests": [{"formula_ids": list(formula_to_pathology.keys())}]},
    )
    evidence = StructuredEvidence.model_validate(payload["structured_evidence"])
    result = run_diagnostic_pipeline_from_structured_evidence(
        evidence,
        case_id=intake_id,
        cliente_id=cliente_id,
        formula_to_pathology=formula_to_pathology,
    )
    return _serializable_diagnostic_pipeline_result(result)


def _diagnostic_operator_summary_from_report(report: dict) -> dict | None:
    diagnostic = report.get("diagnostic_pipeline_result")
    if not isinstance(diagnostic, dict):
        return None

    diagnostic_report = diagnostic.get("report")
    if not isinstance(diagnostic_report, dict):
        return None

    gate_decisions = diagnostic.get("gate_decisions") or []
    pathology_findings = diagnostic.get("pathology_findings") or []
    structured_summary = report.get("structured_evidence_summary") or {}
    reconciliation = structured_summary.get("catalog_reconciliation") or []

    has_gate_block = any(
        isinstance(d, dict) and d.get("decision") == "BLOCK_MISSING_INPUTS"
        for d in gate_decisions
    )
    gate_status = "blocked" if has_gate_block else "ready"

    blocked_formulas = [
        str(d.get("formula_id"))
        for d in gate_decisions
        if isinstance(d, dict) and d.get("decision") == "BLOCK_MISSING_INPUTS"
    ]

    missing_variables = {}
    for d in gate_decisions:
        if isinstance(d, dict) and d.get("decision") == "BLOCK_MISSING_INPUTS":
            f_id = str(d.get("formula_id"))
            missing_vars = d.get("missing_variables") or []
            missing_variables[f_id] = list(missing_vars)

    pending_pathologies = []
    for f in pathology_findings:
        if isinstance(f, dict) and f.get("status") == "PENDING_DATA":
            p_id = f.get("pathology_id")
            if p_id and p_id not in pending_pathologies:
                pending_pathologies.append(p_id)

    unsupported_pathologies = []
    for f in pathology_findings:
        if isinstance(f, dict) and f.get("status") == "PENDING_DATA":
            meta = f.get("metadata") or {}
            if meta.get("blocking_reason") == "PATHOLOGY_NOT_SUPPORTED":
                p_id = f.get("pathology_id")
                if p_id and p_id not in unsupported_pathologies:
                    unsupported_pathologies.append(p_id)

    owner_safe_question_candidates = []
    for entry in reconciliation:
        if isinstance(entry, dict):
            owner_q, _ = _build_owner_question(entry)
            if owner_q and owner_q not in owner_safe_question_candidates:
                owner_safe_question_candidates.append(owner_q)

    suggested_operator_next_step = "Solicitar evidencia faltante antes de reintentar diagnóstico."

    return {
        "status": "available",
        "diagnosis_status": diagnostic_report.get("diagnosis_status"),
        "kernel_state": diagnostic_report.get("kernel_state"),
        "blocking_reason": diagnostic_report.get("blocking_reason"),
        "finding_types": [
            finding.get("finding_type")
            for finding in diagnostic_report.get("findings", [])
            if isinstance(finding, dict) and finding.get("finding_type")
        ],
        "formulas_used": list(diagnostic_report.get("formulas_used") or []),
        "evidence_used": list(diagnostic_report.get("evidence_used") or []),
        "gate_status": gate_status,
        "blocked_formulas": blocked_formulas,
        "missing_variables": missing_variables,
        "pending_pathologies": pending_pathologies,
        "unsupported_pathologies": unsupported_pathologies,
        "owner_safe_question_candidates": owner_safe_question_candidates,
        "suggested_operator_next_step": suggested_operator_next_step,
    }
