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
