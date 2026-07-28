import json

from pymia.diagnostic_core import DiagnosticCoreInput, DiagnosticCoreV1


def test_calculates_ren001_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-1",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_001"],
            formula_ids=["REN_001_margen_neto_real"],
            variables={"sale_price": 1000, "costs": 700, "taxes": 50},
            evidence_refs={
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:compras"],
                "taxes": ["sheet:impuestos"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 25.0
    assert result.formula_results[0].blocking_reason is None
    assert set(result.formula_results[0].source_refs) == {
        "sheet:ventas",
        "sheet:compras",
        "sheet:impuestos",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_supported_formula_and_preserves_source_refs():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-2",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_001"],
            formula_ids=["margen_bruto"],
            variables={"ventas": 1000, "costos": 700},
            evidence_refs={"ventas": ["sheet:ventas"], "costos": ["sheet:compras"]},
        )
    )

    formula = result.formula_results[0]
    assert result.status == "PARTIAL"
    assert formula.status == "OK"
    assert formula.value == 0.3
    assert set(formula.source_refs) == {"sheet:ventas", "sheet:compras"}


def test_does_not_invent_missing_inputs():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-3",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_001"],
            formula_ids=["margen_bruto"],
            variables={"ventas": 1000},
            evidence_refs={"ventas": ["sheet:ventas"]},
        )
    )

    formula = result.formula_results[0]
    assert result.status == "BLOCKED"
    assert formula.status == "BLOCKED"
    assert formula.blocking_reason == "MISSING_INPUTS: costos"
    assert result.missing_evidence == ["costos"]
    assert result.findings == []


def test_result_is_serializable_to_json():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-4",
            tenant_id="tenant-1",
            formula_ids=["ganancia_bruta"],
            variables={"ventas": 1000, "costos": 700},
            evidence_refs={"ventas": ["sheet:ventas"], "costos": ["sheet:compras"]},
        )
    )

    payload = result.model_dump()
    dumped = json.dumps(payload, sort_keys=True)
    assert "ganancia_bruta" in dumped


def test_calculates_liq001_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-5",
            tenant_id="tenant-1",
            hypothesis_codes=["LIQ_001"],
            formula_ids=["LIQ_001_vendido_cobrado"],
            variables={"sold_amount": 1000, "collected_amount": 650},
            evidence_refs={
                "sold_amount": ["sheet:ventas"],
                "collected_amount": ["sheet:cobranzas"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 350.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:ventas",
        "sheet:cobranzas",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.diagnostic_results[0].formula_id == "LIQ_001_vendido_cobrado"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_inv002_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-6",
            tenant_id="tenant-1",
            hypothesis_codes=["INV_002"],
            formula_ids=["INV_002_rotacion_stock"],
            variables={"cost_of_goods_sold": 12000, "average_stock": 3000},
            evidence_refs={
                "cost_of_goods_sold": ["sheet:cogs"],
                "average_stock": ["sheet:stock"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 4.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:cogs",
        "sheet:stock",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_scopes_source_refs_per_formula_when_multiple_formulas_share_input_pool():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-6c",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_001", "LIQ_001", "INV_002"],
            formula_ids=[
                "REN_001_margen_neto_real",
                "LIQ_001_vendido_cobrado",
                "INV_002_rotacion_stock",
            ],
            variables={
                "sale_price": 1000,
                "costs": 700,
                "taxes": 100,
                "sold_amount": 1000,
                "collected_amount": 650,
                "cost_of_goods_sold": 12000,
                "average_stock": 3000,
            },
            evidence_refs={
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
                "taxes": ["sheet:impuestos"],
                "sold_amount": ["sheet:ventas_emitidas"],
                "collected_amount": ["sheet:cobranzas"],
                "cost_of_goods_sold": ["sheet:cogs"],
                "average_stock": ["sheet:stock"],
            },
        )
    )

    assert result.formula_results[0].source_refs == ["sheet:ventas", "sheet:costos", "sheet:impuestos"]
    assert result.formula_results[1].source_refs == ["sheet:ventas_emitidas", "sheet:cobranzas"]
    assert result.formula_results[2].source_refs == ["sheet:cogs", "sheet:stock"]


def test_calculates_inv001_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-6b",
            tenant_id="tenant-1",
            hypothesis_codes=["INV_001"],
            formula_ids=["INV_001_punto_reposicion"],
            variables={"average_sales": 20, "lead_time": 5, "safety_stock": 30},
            evidence_refs={
                "average_sales": ["sheet:avg_sales"],
                "lead_time": ["sheet:lead_time"],
                "safety_stock": ["sheet:safety_stock"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 130.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:avg_sales",
        "sheet:lead_time",
        "sheet:safety_stock",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme011_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-7",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_011"],
            formula_ids=["PYME_011_dso"],
            variables={"accounts_receivable": 3000, "sales": 12000, "days": 30},
            evidence_refs={
                "accounts_receivable": ["sheet:ar"],
                "sales": ["sheet:sales"],
                "days": ["sheet:days"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 7.5
    assert set(result.formula_results[0].source_refs) == {
        "sheet:ar",
        "sheet:sales",
        "sheet:days",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme013_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-8",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_013"],
            formula_ids=["PYME_013_dso_dpo_gap"],
            variables={"dso": 45, "dpo": 30},
            evidence_refs={
                "dso": ["sheet:dso"],
                "dpo": ["sheet:dpo"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 15.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:dso",
        "sheet:dpo",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_liq002_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-9",
            tenant_id="tenant-1",
            hypothesis_codes=["LIQ_002"],
            formula_ids=["LIQ_002_saldo_final_proyectado"],
            variables={
                "initial_balance": 5000,
                "expected_collections": 2000,
                "expected_payments": 3000,
            },
            evidence_refs={
                "initial_balance": ["sheet:saldo"],
                "expected_collections": ["sheet:cobranzas"],
                "expected_payments": ["sheet:pagos"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 4000.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:saldo",
        "sheet:cobranzas",
        "sheet:pagos",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme024_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-10",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_024"],
            formula_ids=["PYME_024_liquidez_corriente"],
            variables={"current_assets": 15000, "current_liabilities": 10000},
            evidence_refs={
                "current_assets": ["sheet:assets"],
                "current_liabilities": ["sheet:liabilities"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 1.5
    assert set(result.formula_results[0].source_refs) == {
        "sheet:assets",
        "sheet:liabilities",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme017_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-11",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_017"],
            formula_ids=["PYME_017_pricing_drift"],
            variables={"own_price": 120, "market_price": 100},
            evidence_refs={
                "own_price": ["sheet:own"],
                "market_price": ["sheet:market"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 20.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:own",
        "sheet:market",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_punto_equilibrio_ventas_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-12",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_002"],
            formula_ids=["punto_equilibrio_ventas"],
            variables={"fixed_costs": 5000, "contribution_margin_rate": 0.25},
            evidence_refs={
                "fixed_costs": ["sheet:fixed_costs"],
                "contribution_margin_rate": ["sheet:cmr"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 20000.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:fixed_costs",
        "sheet:cmr",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme026_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-13",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_026"],
            formula_ids=["PYME_026_flujo_operativo"],
            variables={
                "net_income": 1000,
                "depreciation": 200,
                "amortization": 50,
                "working_capital_change": 150,
            },
            evidence_refs={
                "net_income": ["sheet:ni"],
                "depreciation": ["sheet:dep"],
                "amortization": ["sheet:amort"],
                "working_capital_change": ["sheet:wcc"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 1100.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:ni",
        "sheet:dep",
        "sheet:amort",
        "sheet:wcc",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme027_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-14",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_027"],
            formula_ids=["PYME_027_intereses_ebitda"],
            variables={
                "interest_expense": 500,
                "ebitda": 2500,
            },
            evidence_refs={
                "interest_expense": ["sheet:interest"],
                "ebitda": ["sheet:ebitda"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 0.2
    assert set(result.formula_results[0].source_refs) == {
        "sheet:interest",
        "sheet:ebitda",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme044_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-15",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_044"],
            formula_ids=["PYME_044_margen_cliente"],
            variables={
                "client_revenue": 5000,
                "client_direct_costs": 3000,
                "client_service_costs": 500,
            },
            evidence_refs={
                "client_revenue": ["sheet:revenue"],
                "client_direct_costs": ["sheet:direct"],
                "client_service_costs": ["sheet:service"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 1500.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:revenue",
        "sheet:direct",
        "sheet:service",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_pyme033_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-16",
            tenant_id="tenant-1",
            hypothesis_codes=["PYME_033"],
            formula_ids=["PYME_033_concentracion_sku"],
            variables={
                "main_sku_sales": 4000,
                "total_sales": 10000,
            },
            evidence_refs={
                "main_sku_sales": ["sheet:main"],
                "total_sales": ["sheet:total"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 40.0
    assert set(result.formula_results[0].source_refs) == {
        "sheet:main",
        "sheet:total",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"


def test_calculates_ren002_formula_without_confirmed_finding():
    result = DiagnosticCoreV1().run(
        DiagnosticCoreInput(
            case_id="case-17",
            tenant_id="tenant-1",
            hypothesis_codes=["REN_002"],
            formula_ids=["REN_002_coeficiente_reposicion"],
            variables={
                "closing_index": 130,
                "origin_index": 100,
            },
            evidence_refs={
                "closing_index": ["sheet:closing"],
                "origin_index": ["sheet:origin"],
            },
        )
    )

    assert result.status == "PARTIAL"
    assert result.formula_results[0].status == "OK"
    assert result.formula_results[0].value == 1.3
    assert set(result.formula_results[0].source_refs) == {
        "sheet:closing",
        "sheet:origin",
    }
    assert result.diagnostic_results[0].status == "CANDIDATE"
    assert result.findings[0].status == "CANDIDATE"
