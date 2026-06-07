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
