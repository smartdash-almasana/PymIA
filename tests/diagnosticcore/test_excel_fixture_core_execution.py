from __future__ import annotations

import json
from pathlib import Path

from pymia.diagnostic_core import DiagnosticCoreV1, build_diagnostic_core_input_from_structured_evidence
from tools.excel_evidence import build_excel_structured_evidence


_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"
)
_FORMULA_IDS = [
    "REN_001_margen_neto_real",
    "LIQ_001_vendido_cobrado",
    "INV_002_rotacion_stock",
]


def test_excel_fixture_builds_structured_evidence() -> None:
    assert _FIXTURE_PATH.exists()

    evidence = build_excel_structured_evidence(
        excel_path=_FIXTURE_PATH,
        tenant_id="tenant-fixture",
    )

    assert evidence.tenant_id == "tenant-fixture"
    assert evidence.file_name == _FIXTURE_PATH.name
    assert isinstance(evidence.computed_variables, dict)
    assert isinstance(evidence.metadata, dict)
    assert evidence.computed_variables["ventas_total"] > 0
    assert evidence.computed_variables["costos_total"] > 0


def test_excel_fixture_executes_through_binder_and_core() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=_FIXTURE_PATH,
        tenant_id="tenant-fixture",
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-fixture",
        tenant_id="tenant-fixture",
        formula_ids=_FORMULA_IDS,
        hypothesis_codes=["REN_001", "LIQ_001", "INV_002"],
    )
    result = DiagnosticCoreV1().run(core_input)

    dumped = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    assert "formula_results" in dumped
    assert result.status == "BLOCKED"
    assert [formula.formula_id for formula in result.formula_results] == _FORMULA_IDS
    assert [formula.status for formula in result.formula_results] == ["BLOCKED", "BLOCKED", "BLOCKED"]
    assert result.formula_results[0].blocking_reason == "MISSING_INPUTS: taxes"
    assert result.formula_results[1].blocking_reason == "MISSING_INPUTS: collected_amount"
    assert result.formula_results[2].blocking_reason == "MISSING_INPUTS: average_stock"
    assert all(item.status != "CONFIRMED" for item in result.diagnostic_results)
    assert result.findings == []


def test_excel_fixture_does_not_invent_missing_variables_in_binding() -> None:
    evidence = build_excel_structured_evidence(
        excel_path=_FIXTURE_PATH,
        tenant_id="tenant-fixture",
    )

    core_input = build_diagnostic_core_input_from_structured_evidence(
        evidence,
        case_id="case-fixture-missing",
        tenant_id="tenant-fixture",
        formula_ids=_FORMULA_IDS,
        hypothesis_codes=["REN_001", "LIQ_001", "INV_002"],
    )

    assert core_input.variables["sale_price"] == evidence.computed_variables["ventas_total"]
    assert core_input.variables["costs"] == evidence.computed_variables["costos_total"]
    assert core_input.variables["sold_amount"] == evidence.computed_variables["ventas_total"]
    assert core_input.variables["cost_of_goods_sold"] == evidence.computed_variables["costos_total"]
    assert "taxes" not in core_input.variables
    assert "collected_amount" not in core_input.variables
    assert "average_stock" not in core_input.variables
