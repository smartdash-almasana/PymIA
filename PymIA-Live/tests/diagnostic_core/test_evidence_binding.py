from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core.evidence_binding import build_diagnostic_core_input_from_structured_evidence


def test_binding_preserves_explicit_refs():
    evidence = StructuredEvidence(
        tenant_id="tenant_test",
        document_type="xlsx_operational_evidence",
        file_name="caso.xlsx",
        computed_variables={"ventas_total": 1000.0, "costos_total": 900.0, "impuestos_total": 200.0},
        metadata={"variable_source_refs": {"ventas_total": ["sheet:ventas"], "costos_total": ["sheet:costos"], "impuestos_total": ["sheet:impuestos"]}},
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-1",
        tenant_id="tenant_test",
        formula_ids=["REN_001_margen_neto_real"],
    )

    assert core_input.evidence_refs["sale_price"] == ["sheet:ventas"]
    assert core_input.evidence_refs["costs"] == ["sheet:costos"]
    assert core_input.evidence_refs["taxes"] == ["sheet:impuestos"]


def test_binding_adds_document_refs_when_explicit_refs_are_missing():
    evidence = StructuredEvidence(
        tenant_id="tenant_test",
        document_type="xlsx_operational_evidence",
        file_name="caso.xlsx",
        computed_variables={"ventas_total": 1000.0, "costos_total": 900.0},
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-1",
        tenant_id="tenant_test",
        formula_ids=["LIQ_001_vendido_cobrado", "INV_002_rotacion_stock"],
    )

    assert core_input.evidence_refs["sold_amount"] == ["caso.xlsx:ventas_total"]
    assert core_input.evidence_refs["cost_of_goods_sold"] == ["caso.xlsx:costos_total"]
