from __future__ import annotations

from dataclasses import dataclass, field

from pymia.contracts.diagnostic_report_contract import DiagnosticReport, FindingRecord, QuantifiedImpact
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.formula_contract import FormulaResult
from pymia.contracts.pathology_contract import PathologyEvaluationInput, PathologyFinding, PathologySeverity, PathologyStatus
from pymia.diagnostic_core.evidence_binding import build_diagnostic_core_input_from_structured_evidence
from pymia.diagnostic_core.evidence_sufficiency import (
    build_evidence_gate_decisions_from_structured_evidence,
    execute_allowed_formulas_from_gate_decisions,
)
from pymia.diagnostic_core.models import DiagnosticCoreInput, EvidenceGateDecision
from pymia.services.diagnostic_report_service import DiagnosticReportService
from pymia.services.pathology_adapters import PathologyAdapterError, pathology_finding_to_finding_record
from pymia.services.pathology_engine_service import PathologyEngineService


@dataclass(frozen=True)
class DiagnosticPipelineResult:
    core_input: DiagnosticCoreInput
    gate_decisions: list[EvidenceGateDecision] = field(default_factory=list)
    formula_results: list[FormulaResult] = field(default_factory=list)
    pathology_findings: list[PathologyFinding] = field(default_factory=list)
    finding_records: list[FindingRecord] = field(default_factory=list)
    report: DiagnosticReport | None = None


def run_diagnostic_pipeline_from_structured_evidence(
    evidence: StructuredEvidence,
    *,
    case_id: str,
    cliente_id: str,
    formula_to_pathology: dict[str, str],
    hypothesis: str = "Contraste diagnóstico desde evidencia estructurada.",
) -> DiagnosticPipelineResult:
    """Orquesta evidencia estructurada hasta reporte diagnóstico sin tocar CLI/storage.

    La ejecución de fórmulas se delega al gate existente para no duplicar binding,
    aliases ni source_refs. El mapeo fórmula → patología entra explícito desde la
    reconciliación de catálogo o desde un test focal.
    """

    if not isinstance(evidence, StructuredEvidence):
        raise ValueError("evidence must be a StructuredEvidence")
    if not formula_to_pathology:
        raise ValueError("formula_to_pathology is required")

    formula_ids = list(formula_to_pathology.keys())
    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id=case_id,
        tenant_id=evidence.tenant_id,
        formula_ids=formula_ids,
        hypothesis_codes=list(formula_to_pathology.values()),
    )
    gate_decisions = build_evidence_gate_decisions_from_structured_evidence(
        evidence,
        case_id=case_id,
        tenant_id=evidence.tenant_id,
        formula_ids=formula_ids,
    )
    formula_results = execute_allowed_formulas_from_gate_decisions(core_input, gate_decisions)
    pathology_findings = _evaluate_pathologies(
        formula_results=formula_results,
        formula_to_pathology=formula_to_pathology,
        cliente_id=cliente_id,
        case_id=case_id,
    )
    finding_records = _active_finding_records(pathology_findings)
    report = _build_report(
        case_id=case_id,
        cliente_id=cliente_id,
        hypothesis=hypothesis,
        finding_records=finding_records,
        formula_results=formula_results,
        pathology_findings=pathology_findings,
    )
    return DiagnosticPipelineResult(
        core_input=core_input,
        gate_decisions=gate_decisions,
        formula_results=formula_results,
        pathology_findings=pathology_findings,
        finding_records=finding_records,
        report=report,
    )


def formula_pathology_map_from_catalog_reconciliation(
    catalog_reconciliation: list[dict],
) -> dict[str, str]:
    """Extrae formula_id → pathology_code sin recalcular suficiencia."""

    mapping: dict[str, str] = {}
    for entry in catalog_reconciliation:
        if not isinstance(entry, dict):
            continue
        formula_id = str(entry.get("formula_id") or "").strip()
        pathology_code = str(entry.get("pathology_code") or "").strip()
        if formula_id and pathology_code:
            mapping[formula_id] = pathology_code
    return mapping


def _evaluate_pathologies(
    *,
    formula_results: list[FormulaResult],
    formula_to_pathology: dict[str, str],
    cliente_id: str,
    case_id: str,
) -> list[PathologyFinding]:
    service = PathologyEngineService()
    findings: list[PathologyFinding] = []
    for formula_result in formula_results:
        pathology_id = formula_to_pathology.get(formula_result.formula_id)
        if not pathology_id:
            continue
        findings.append(
            service.evaluate(
                pathology_id,
                PathologyEvaluationInput(
                    cliente_id=cliente_id,
                    formula_result_id=f"{case_id}:{formula_result.formula_id}",
                    formula_result=formula_result,
                ),
            )
        )
    return findings


def _active_finding_records(pathology_findings: list[PathologyFinding]) -> list[FindingRecord]:
    records: list[FindingRecord] = []
    for pathology_finding in pathology_findings:
        if pathology_finding.status != PathologyStatus.ACTIVE:
            continue
        try:
            records.append(pathology_finding_to_finding_record(pathology_finding))
        except PathologyAdapterError:
            continue
    return records


def _build_report(
    *,
    case_id: str,
    cliente_id: str,
    hypothesis: str,
    finding_records: list[FindingRecord],
    formula_results: list[FormulaResult],
    pathology_findings: list[PathologyFinding],
) -> DiagnosticReport:
    evidence_used = _unique_refs([ref for finding in finding_records for ref in finding.evidence_used])
    if not evidence_used:
        evidence_used = _unique_refs([ref for result in formula_results for ref in result.source_refs])

    formulas_used = [result.formula_id for result in formula_results]
    active_findings = [finding for finding in pathology_findings if finding.status == PathologyStatus.ACTIVE]
    quantified_impact = _quantified_impact_from(active_findings)
    reasoning_summary = _reasoning_summary_from(pathology_findings)

    return DiagnosticReportService().create_report(
        case_id=case_id,
        cliente_id=cliente_id,
        hypothesis=hypothesis,
        findings=finding_records,
        evidence_used=evidence_used,
        formulas_used=formulas_used,
        quantified_impact=quantified_impact,
        reasoning_summary=reasoning_summary,
        references_used=evidence_used,
    )


def _quantified_impact_from(active_findings: list[PathologyFinding]) -> QuantifiedImpact | None:
    severity = _highest_severity([finding.severity for finding in active_findings if finding.severity is not None])
    if severity is None:
        return None
    return QuantifiedImpact(risk_level=severity)


def _highest_severity(severities: list[PathologySeverity]) -> PathologySeverity | None:
    if not severities:
        return None
    rank = {
        PathologySeverity.LOW: 1,
        PathologySeverity.MEDIUM: 2,
        PathologySeverity.HIGH: 3,
        PathologySeverity.CRITICAL: 4,
    }
    return max(severities, key=lambda item: rank[item])


def _reasoning_summary_from(pathology_findings: list[PathologyFinding]) -> str:
    explanations = [finding.explanation.strip() for finding in pathology_findings if finding.explanation.strip()]
    if explanations:
        return " ".join(explanations)
    return "No hay hallazgos activos trazables para confirmar diagnóstico."


def _unique_refs(refs: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        result.append(ref)
    return result
