from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core import (
    DiagnosticCoreV1,
    build_diagnostic_core_input_from_structured_evidence,
)


def test_executes_three_formulas_from_structured_evidence_fixture() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        file_name="fixture.xlsx",
        computed_variables={
            "sale_price": 1000,
            "costs": 700,
            "taxes": 100,
            "sold_amount": 1000,
            "collected_amount": 650,
            "cost_of_goods_sold": 12000,
            "average_stock": 3000,
        },
        metadata={
            "variable_source_refs": {
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
                "taxes": ["sheet:impuestos"],
                "sold_amount": ["sheet:ventas_emitidas"],
                "collected_amount": ["sheet:cobranzas"],
                "cost_of_goods_sold": ["sheet:cogs"],
                "average_stock": ["sheet:stock"],
            }
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-all",
        tenant_id="tenant-1",
        formula_ids=[
            "REN_001_margen_neto_real",
            "LIQ_001_vendido_cobrado",
            "INV_002_rotacion_stock",
        ],
        hypothesis_codes=["REN_001", "LIQ_001", "INV_002"],
    )
    result = DiagnosticCoreV1().run(core_input)

    assert result.status == "PARTIAL"
    assert [formula.value for formula in result.formula_results] == [20.0, 350.0, 4.0]
    assert [formula.status for formula in result.formula_results] == ["OK", "OK", "OK"]
    assert all(item.status == "CANDIDATE" for item in result.diagnostic_results)
    assert all(finding.status == "CANDIDATE" for finding in result.findings)
    expected_refs = {
        "sheet:ventas",
        "sheet:costos",
        "sheet:impuestos",
        "sheet:ventas_emitidas",
        "sheet:cobranzas",
        "sheet:cogs",
        "sheet:stock",
    }
    assert set(core_input.evidence_refs["sale_price"]) == {"sheet:ventas"}
    assert set(core_input.evidence_refs["costs"]) == {"sheet:costos"}
    assert set(core_input.evidence_refs["taxes"]) == {"sheet:impuestos"}
    assert set(core_input.evidence_refs["sold_amount"]) == {"sheet:ventas_emitidas"}
    assert set(core_input.evidence_refs["collected_amount"]) == {"sheet:cobranzas"}
    assert set(core_input.evidence_refs["cost_of_goods_sold"]) == {"sheet:cogs"}
    assert set(core_input.evidence_refs["average_stock"]) == {"sheet:stock"}
    assert all(set(formula.source_refs) == expected_refs for formula in result.formula_results)


def test_partial_execution_blocks_only_incomplete_formula() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "sale_price": 1000,
            "costs": 700,
            "sold_amount": 1000,
            "collected_amount": 650,
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-partial",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real", "LIQ_001_vendido_cobrado"],
        hypothesis_codes=["REN_001", "LIQ_001"],
    )
    result = DiagnosticCoreV1().run(core_input)

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "BLOCKED"
    assert result.formula_results[0].blocking_reason == "MISSING_INPUTS: taxes"
    assert result.formula_results[1].status == "OK"
    assert result.formula_results[1].value == 350.0
    assert result.diagnostic_results[0].status == "BLOCKED"
    assert result.diagnostic_results[1].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_executes_supported_aliases_from_parser_like_variables() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "ventas_total": 1000,
            "costos_total": 700,
            "impuestos_total": 100,
            "cobranzas_total": 650,
            "stock_promedio": 3000,
        },
        metadata={
            "variable_source_refs": {
                "ventas_total": ["sheet:ventas_total"],
                "costos_total": ["sheet:costos_total"],
                "impuestos_total": ["sheet:impuestos_total"],
                "cobranzas_total": ["sheet:cobranzas_total"],
                "stock_promedio": ["sheet:stock_promedio"],
            }
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-alias",
        tenant_id="tenant-1",
        formula_ids=[
            "REN_001_margen_neto_real",
            "LIQ_001_vendido_cobrado",
            "INV_002_rotacion_stock",
        ],
        hypothesis_codes=["REN_001", "LIQ_001", "INV_002"],
    )
    result = DiagnosticCoreV1().run(core_input)

    assert result.status == "PARTIAL"
    assert [formula.value for formula in result.formula_results] == [20.0, 350.0, 700 / 3000]
    assert [formula.status for formula in result.formula_results] == ["OK", "OK", "OK"]
    expected_refs = {
        "sheet:ventas_total",
        "sheet:costos_total",
        "sheet:impuestos_total",
        "sheet:cobranzas_total",
        "sheet:stock_promedio",
    }
    assert set(core_input.evidence_refs["sale_price"]) == {"sheet:ventas_total"}
    assert set(core_input.evidence_refs["costs"]) == {"sheet:costos_total"}
    assert set(core_input.evidence_refs["taxes"]) == {"sheet:impuestos_total"}
    assert set(core_input.evidence_refs["sold_amount"]) == {"sheet:ventas_total"}
    assert set(core_input.evidence_refs["collected_amount"]) == {"sheet:cobranzas_total"}
    assert set(core_input.evidence_refs["cost_of_goods_sold"]) == {"sheet:costos_total"}
    assert set(core_input.evidence_refs["average_stock"]) == {"sheet:stock_promedio"}
    assert all(set(formula.source_refs) == expected_refs for formula in result.formula_results)
