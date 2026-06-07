from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core import (
    DiagnosticCoreV1,
    build_diagnostic_core_input_from_structured_evidence,
)


def test_binds_ren001_from_structured_evidence() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        file_name="ren.xlsx",
        computed_variables={"sale_price": 1000, "costs": 700, "taxes": 100},
        metadata={
            "variable_source_refs": {
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
                "taxes": ["sheet:impuestos"],
            }
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-ren",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
        hypothesis_codes=["REN_001"],
    )

    assert core_input.formula_ids == ["REN_001_margen_neto_real"]
    assert core_input.variables == {"sale_price": 1000, "costs": 700, "taxes": 100}
    assert core_input.evidence_refs == {
        "sale_price": ["sheet:ventas"],
        "costs": ["sheet:costos"],
        "taxes": ["sheet:impuestos"],
    }


def test_binds_liq001_from_structured_evidence() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"sold_amount": 1000, "collected_amount": 650},
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-liq",
        tenant_id="tenant-1",
        formula_ids=["LIQ_001_vendido_cobrado"],
        hypothesis_codes=["LIQ_001"],
    )

    assert core_input.variables == {"sold_amount": 1000, "collected_amount": 650}


def test_binds_inv002_from_structured_evidence() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"cost_of_goods_sold": 12000, "average_stock": 3000},
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-inv",
        tenant_id="tenant-1",
        formula_ids=["INV_002_rotacion_stock"],
        hypothesis_codes=["INV_002"],
    )

    assert core_input.variables == {"cost_of_goods_sold": 12000, "average_stock": 3000}


def test_does_not_invent_missing_structured_evidence_variables() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"sale_price": 1000, "costs": 700},
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-missing",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
        hypothesis_codes=["REN_001"],
    )

    assert core_input.variables == {"sale_price": 1000, "costs": 700}
    assert "taxes" not in core_input.variables


def test_binding_integrates_with_diagnostic_core_v1() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"sale_price": 1000, "costs": 700, "taxes": 100},
        metadata={
            "variable_source_refs": {
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
                "taxes": ["sheet:impuestos"],
            }
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-core",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
        hypothesis_codes=["REN_001"],
    )
    result = DiagnosticCoreV1().run(core_input)

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 20.0
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"
