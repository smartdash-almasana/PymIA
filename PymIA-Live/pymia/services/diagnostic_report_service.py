from __future__ import annotations

import uuid

from pymia.contracts.diagnostic_report_contract import (
    DiagnosisStatus,
    DiagnosticReport,
    FindingRecord,
    KernelState,
    QuantifiedImpact,
)


class DiagnosticReportService:
    """Construye reportes diagnósticos mínimos del kernel.

    No emite owner_question, proposed_next_actions ni job_id.
    """

    def create_report(
        self,
        *,
        case_id: str,
        cliente_id: str,
        hypothesis: str,
        findings: list[FindingRecord],
        evidence_used: list[str],
        formulas_used: list[str],
        quantified_impact: QuantifiedImpact | None,
        reasoning_summary: str,
        references_used: list[str] | None = None,
    ) -> DiagnosticReport:
        blocking_reason = self._blocking_reason(
            findings=findings,
            evidence_used=evidence_used,
            quantified_impact=quantified_impact,
            reasoning_summary=reasoning_summary,
        )

        if blocking_reason:
            return DiagnosticReport(
                report_id=str(uuid.uuid4()),
                case_id=case_id,
                cliente_id=cliente_id,
                hypothesis=hypothesis,
                diagnosis_status=DiagnosisStatus.INSUFFICIENT_EVIDENCE,
                kernel_state=KernelState.BLOCKED,
                findings=findings,
                evidence_used=evidence_used,
                formulas_used=formulas_used,
                quantified_impact=quantified_impact,
                reasoning_summary=reasoning_summary or "Evidencia insuficiente para confirmar el diagnóstico.",
                references_used=references_used or [],
                blocking_reason=blocking_reason,
            )

        return DiagnosticReport(
            report_id=str(uuid.uuid4()),
            case_id=case_id,
            cliente_id=cliente_id,
            hypothesis=hypothesis,
            diagnosis_status=DiagnosisStatus.CONFIRMED,
            kernel_state=KernelState.PASS,
            findings=findings,
            evidence_used=evidence_used,
            formulas_used=formulas_used,
            quantified_impact=quantified_impact,
            reasoning_summary=reasoning_summary,
            references_used=references_used or [],
        )

    def _blocking_reason(
        self,
        *,
        findings: list[FindingRecord],
        evidence_used: list[str],
        quantified_impact: QuantifiedImpact | None,
        reasoning_summary: str,
    ) -> str | None:
        if not evidence_used:
            return "EVIDENCE_USED_REQUIRED"
        if not findings:
            return "FINDINGS_REQUIRED"
        for finding in findings:
            if not finding.compared_sources:
                return "COMPARED_SOURCES_REQUIRED"
            if not finding.measured_difference:
                return "MEASURED_DIFFERENCE_REQUIRED"
            if not finding.evidence_used:
                return "FINDING_EVIDENCE_USED_REQUIRED"
        if quantified_impact is None:
            return "QUANTIFIED_IMPACT_REQUIRED"
        if not reasoning_summary.strip():
            return "REASONING_SUMMARY_REQUIRED"
        return None
