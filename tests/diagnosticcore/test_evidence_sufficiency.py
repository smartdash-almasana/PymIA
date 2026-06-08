from __future__ import annotations

import pytest

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core.evidence_sufficiency import (
    build_evidence_sufficiency_report_from_structured_evidence,
)


def test_returns_ready_with_complete_evidence() -> None:
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

    report = build_evidence_sufficiency_report_from_structured_evidence(
        evidence,
        case_id="case-ready",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
    )

    assert len(report) == 1
    assert report[0].formula_id == "REN_001_margen_neto_real"
    assert report[0].required_variables == ["sale_price", "costs", "taxes"]
    assert report[0].available_variables == ["sale_price", "costs", "taxes"]
    assert report[0].missing_variables == []
    assert report[0].source_refs == ["sheet:ventas", "sheet:costos", "sheet:impuestos"]
    assert report[0].status == "READY"


def test_returns_missing_inputs_with_incomplete_evidence() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"sale_price": 1000, "costs": 700},
        metadata={
            "variable_source_refs": {
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
            }
        },
    )

    report = build_evidence_sufficiency_report_from_structured_evidence(
        evidence,
        case_id="case-missing",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
    )

    assert report[0].available_variables == ["sale_price", "costs"]
    assert report[0].missing_variables == ["taxes"]
    assert report[0].source_refs == ["sheet:ventas", "sheet:costos"]
    assert report[0].status == "MISSING_INPUTS"


def test_source_refs_are_scoped_per_formula() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "sale_price": 1000,
            "costs": 700,
            "taxes": 100,
            "sold_amount": 1500,
            "collected_amount": 800,
        },
        metadata={
            "variable_source_refs": {
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
                "taxes": ["sheet:impuestos"],
                "sold_amount": ["sheet:ventas_emitidas"],
                "collected_amount": ["sheet:cobranzas"],
            }
        },
    )

    report = build_evidence_sufficiency_report_from_structured_evidence(
        evidence,
        case_id="case-refs",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real", "LIQ_001_vendido_cobrado"],
    )

    assert report[0].source_refs == ["sheet:ventas", "sheet:costos", "sheet:impuestos"]
    assert report[1].source_refs == ["sheet:ventas_emitidas", "sheet:cobranzas"]


def test_supports_multiple_formulas_with_deterministic_order() -> None:
    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={
            "cost_of_goods_sold": 12000,
            "average_stock": 3000,
            "sale_price": 1000,
            "costs": 700,
        },
        metadata={
            "variable_source_refs": {
                "cost_of_goods_sold": ["sheet:cogs"],
                "average_stock": ["sheet:stock"],
                "sale_price": ["sheet:ventas"],
                "costs": ["sheet:costos"],
            }
        },
    )

    report = build_evidence_sufficiency_report_from_structured_evidence(
        evidence,
        case_id="case-multi",
        tenant_id="tenant-1",
        formula_ids=["INV_002_rotacion_stock", "REN_001_margen_neto_real"],
    )

    assert [item.formula_id for item in report] == [
        "INV_002_rotacion_stock",
        "REN_001_margen_neto_real",
    ]
    assert report[0].available_variables == ["cost_of_goods_sold", "average_stock"]
    assert report[0].missing_variables == []
    assert report[0].status == "READY"
    assert report[1].available_variables == ["sale_price", "costs"]
    assert report[1].missing_variables == ["taxes"]
    assert report[1].status == "MISSING_INPUTS"


def test_does_not_invoke_diagnostic_core_v1(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("DiagnosticCoreV1.run should not be called")

    monkeypatch.setattr("pymia.diagnostic_core.core.DiagnosticCoreV1.run", fail_if_called)

    evidence = StructuredEvidence(
        tenant_id="tenant-1",
        document_type="xlsx_operational_evidence",
        computed_variables={"sale_price": 1000, "costs": 700, "taxes": 100},
    )

    report = build_evidence_sufficiency_report_from_structured_evidence(
        evidence,
        case_id="case-no-core",
        tenant_id="tenant-1",
        formula_ids=["REN_001_margen_neto_real"],
    )

    assert report[0].status == "READY"
