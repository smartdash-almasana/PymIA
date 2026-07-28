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


def test_binding_maps_pyme044_client_margin() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "client_revenue": 1000,
            "client_direct_costs": 600,
            "client_service_costs": 150,
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-p044",
        tenant_id="tenant-1",
        formula_ids=["PYME_044_margen_cliente"],
        hypothesis_codes=["PYME_044"],
    )

    assert core_input.variables == {
        "client_revenue": 1000,
        "client_direct_costs": 600,
        "client_service_costs": 150,
    }


def test_binding_maps_pyme033_sku_concentration() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "main_sku_sales": 400,
            "total_sales": 1000,
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-p033",
        tenant_id="tenant-1",
        formula_ids=["PYME_033_concentracion_sku"],
        hypothesis_codes=["PYME_033"],
    )

    assert core_input.variables == {
        "main_sku_sales": 400,
        "total_sales": 1000,
    }


def test_binding_maps_ren002_replacement_coefficient() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "closing_index": 150,
            "origin_index": 100,
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-r002",
        tenant_id="tenant-1",
        formula_ids=["REN_002_coeficiente_reposicion"],
        hypothesis_codes=["REN_002"],
    )

    assert core_input.variables == {
        "closing_index": 150,
        "origin_index": 100,
    }


def test_binding_aliases_for_new_formulas() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "ingresos_cliente": 1000,
            "costos_directos_cliente": 600,
            "costos_servicio_cliente": 150,
            "ventas_sku_principal": 400,
            "ventas_total": 1000,
            "indice_cierre": 150,
            "indice_origen": 100,
        },
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-alias-new",
        tenant_id="tenant-1",
        formula_ids=[
            "PYME_044_margen_cliente",
            "PYME_033_concentracion_sku",
            "REN_002_coeficiente_reposicion",
        ],
        hypothesis_codes=["PYME_044", "PYME_033", "REN_002"],
    )

    assert core_input.variables == {
        "client_revenue": 1000,
        "client_direct_costs": 600,
        "client_service_costs": 150,
        "main_sku_sales": 400,
        "total_sales": 1000,
        "closing_index": 150,
        "origin_index": 100,
    }
