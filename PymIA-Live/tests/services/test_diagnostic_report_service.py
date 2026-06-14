from pymia.contracts.diagnostic_report_contract import (
    DiagnosisStatus,
    FindingRecord,
    KernelState,
    QuantifiedImpact,
)
from pymia.contracts.pathology_contract import PathologySeverity
from pymia.services.diagnostic_report_service import DiagnosticReportService


def _finding() -> FindingRecord:
    return FindingRecord(
        entity="pyme_A",
        finding_type="margen_bruto_negativo",
        measured_difference={"margen_bruto": -0.2},
        compared_sources=["ventas:1", "costos:1"],
        evidence_used=["ventas:1", "costos:1"],
        severity=PathologySeverity.HIGH,
        recommendation="Revisar costos o precios.",
        explanation="Margen negativo.",
    )


def test_service_confirms_report_with_traceable_finding():
    report = DiagnosticReportService().create_report(
        case_id="case-1",
        cliente_id="pyme_A",
        hypothesis="Investigar si el margen bruto es negativo.",
        findings=[_finding()],
        evidence_used=["ventas:1", "costos:1"],
        formulas_used=["margen_bruto"],
        quantified_impact=QuantifiedImpact(percentage=-0.2, risk_level=PathologySeverity.HIGH),
        reasoning_summary="El margen bruto calculado es negativo con evidencia trazable.",
    )

    assert report.diagnosis_status == DiagnosisStatus.CONFIRMED
    assert report.kernel_state == KernelState.PASS
    assert report.blocking_reason is None
    assert not hasattr(report, "job_id")
    assert not hasattr(report, "owner_question")
    assert not hasattr(report, "proposed_next_actions")


def test_service_blocks_without_evidence_used():
    report = DiagnosticReportService().create_report(
        case_id="case-1",
        cliente_id="pyme_A",
        hypothesis="Investigar si el margen bruto es negativo.",
        findings=[_finding()],
        evidence_used=[],
        formulas_used=["margen_bruto"],
        quantified_impact=QuantifiedImpact(percentage=-0.2),
        reasoning_summary="El margen bruto calculado es negativo.",
    )

    assert report.diagnosis_status == DiagnosisStatus.INSUFFICIENT_EVIDENCE
    assert report.kernel_state == KernelState.BLOCKED
    assert report.blocking_reason == "EVIDENCE_USED_REQUIRED"


def test_service_blocks_without_findings():
    report = DiagnosticReportService().create_report(
        case_id="case-1",
        cliente_id="pyme_A",
        hypothesis="Investigar si el margen bruto es negativo.",
        findings=[],
        evidence_used=["ventas:1"],
        formulas_used=["margen_bruto"],
        quantified_impact=QuantifiedImpact(percentage=-0.2),
        reasoning_summary="No hay hallazgos trazables.",
    )

    assert report.diagnosis_status == DiagnosisStatus.INSUFFICIENT_EVIDENCE
    assert report.kernel_state == KernelState.BLOCKED
    assert report.blocking_reason == "FINDINGS_REQUIRED"
