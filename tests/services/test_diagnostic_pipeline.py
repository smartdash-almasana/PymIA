from pymia.contracts.diagnostic_report_contract import DiagnosisStatus, KernelState
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.formula_contract import FormulaStatus
from pymia.contracts.pathology_contract import PathologyStatus
from pymia.diagnostic_core.models import EvidenceGateDecisionStatus
from pymia.services.diagnostic_pipeline import (
    formula_pathology_map_from_catalog_reconciliation,
    run_diagnostic_pipeline_from_structured_evidence,
)


_FORMULA_ID = "REN_001_margen_neto_real"
_PATHOLOGY_CODE = "REN_001"


def _structured_evidence(*, sale_price: float, costs: float, taxes: float) -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant_test",
        document_type="xlsx_operacional",
        file_name="margen.xlsx",
        computed_variables={
            "ventas_total": sale_price,
            "costos_total": costs,
            "impuestos_total": taxes,
        },
        metadata={
            "variable_source_refs": {
                "ventas_total": ["sheet:ventas"],
                "costos_total": ["sheet:costos"],
                "impuestos_total": ["sheet:impuestos"],
            }
        },
    )


def test_pipeline_e2e_produces_confirmed_report_for_active_ren_001():
    result = run_diagnostic_pipeline_from_structured_evidence(
        _structured_evidence(sale_price=1000, costs=900, taxes=200),
        case_id="case-1",
        cliente_id="pyme_A",
        formula_to_pathology={_FORMULA_ID: _PATHOLOGY_CODE},
    )

    assert result.core_input.variables == {
        "sale_price": 1000.0,
        "costs": 900.0,
        "taxes": 200.0,
    }
    assert result.gate_decisions[0].decision == EvidenceGateDecisionStatus.ALLOW_EXECUTION
    assert result.formula_results[0].formula_id == _FORMULA_ID
    assert result.formula_results[0].status == FormulaStatus.OK
    assert result.formula_results[0].value == -10.0
    assert result.pathology_findings[0].pathology_id == _PATHOLOGY_CODE
    assert result.pathology_findings[0].status == PathologyStatus.PENDING_DATA
    assert result.finding_records == []
    assert result.report is not None
    assert result.report.kernel_state == KernelState.BLOCKED
    assert result.report.diagnosis_status == DiagnosisStatus.INSUFFICIENT_EVIDENCE
    assert result.report.evidence_used == ["sheet:ventas", "sheet:costos", "sheet:impuestos"]


def test_pipeline_fail_closed_when_formula_blocks():
    result = run_diagnostic_pipeline_from_structured_evidence(
        _structured_evidence(sale_price=0, costs=900, taxes=200),
        case_id="case-2",
        cliente_id="pyme_A",
        formula_to_pathology={_FORMULA_ID: _PATHOLOGY_CODE},
    )

    assert result.formula_results[0].status == FormulaStatus.BLOCKED
    assert result.formula_results[0].blocking_reason == "DIVISION_BY_ZERO: sale_price"
    assert result.pathology_findings[0].status == PathologyStatus.PENDING_DATA
    assert result.finding_records == []
    assert result.report is not None
    assert result.report.kernel_state == KernelState.BLOCKED
    assert result.report.diagnosis_status == DiagnosisStatus.INSUFFICIENT_EVIDENCE
    assert result.report.blocking_reason == "FINDINGS_REQUIRED"


def test_formula_pathology_map_from_catalog_reconciliation():
    mapping = formula_pathology_map_from_catalog_reconciliation(
        [
            {
                "formula_id": _FORMULA_ID,
                "pathology_code": _PATHOLOGY_CODE,
                "status": "calculable",
            },
            {
                "formula_id": "",
                "pathology_code": "IGNORED",
            },
        ]
    )

    assert mapping == {_FORMULA_ID: _PATHOLOGY_CODE}
