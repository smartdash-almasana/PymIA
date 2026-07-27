from pymia.contracts.diagnostic_report_contract import (
    DiagnosisStatus,
    KernelState,
    QuantifiedImpact,
)
from pymia.contracts.formula_contract import FormulaInput, FormulaStatus
from pymia.contracts.pathology_contract import PathologyEvaluationInput, PathologySeverity, PathologyStatus
from pymia.services.diagnostic_report_service import DiagnosticReportService
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.services.pathology_adapters import pathology_finding_to_finding_record
from pymia.services.pathology_engine_service import PathologyEngineService


def test_chip1_end_to_end_passes_with_negative_margin():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
    )
    assert formula_result.status == FormulaStatus.OK

    pathology = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=formula_result,
        ),
    )
    assert pathology.status == PathologyStatus.ACTIVE

    finding = pathology_finding_to_finding_record(pathology)
    report = DiagnosticReportService().create_report(
        case_id="case-1",
        cliente_id="pyme_A",
        hypothesis="Investigar si el margen bruto es negativo.",
        findings=[finding],
        evidence_used=finding.evidence_used,
        formulas_used=[formula_result.formula_id],
        quantified_impact=QuantifiedImpact(
            percentage=formula_result.value,
            risk_level=PathologySeverity.HIGH,
        ),
        reasoning_summary=pathology.explanation,
        references_used=formula_result.source_refs,
    )

    assert report.kernel_state == KernelState.PASS
    assert report.diagnosis_status == DiagnosisStatus.CONFIRMED
    assert report.findings[0].finding_type == "margen_bruto_negativo"
    assert report.evidence_used == ["ventas:1", "costos:1"]


def test_chip1_blocks_when_formula_cannot_calculate():
    formula_result = FormulaEngineService().calculate(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=0, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
    )
    assert formula_result.status == FormulaStatus.BLOCKED

    pathology = PathologyEngineService().evaluate(
        "margen_bruto_negativo",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr-blocked",
            formula_result=formula_result,
        ),
    )

    assert pathology.status == PathologyStatus.PENDING_DATA
    assert pathology.metadata["blocking_reason"] == "DIVISION_BY_ZERO: ventas"
