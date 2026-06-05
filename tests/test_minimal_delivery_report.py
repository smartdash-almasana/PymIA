from __future__ import annotations

import ast
from pathlib import Path

import pytest

from pymia.smartpyme.finding_projection import ActionableFinding
from pymia.narrative.minimal_delivery_report import render_minimal_delivery_report


def _sample_findings() -> list[ActionableFinding]:
    return [
        ActionableFinding(
            entity="Productos en ventas",
            metric="margen",
            difference="3 productos con margen bajo (<10%) en ventas",
            source_comparison="ventas_costos_margen.xlsx",
            severity="high",
            evidence_refs=["diagnostic_result.json"],
            recommendation="Revisar estructura de precios y costos de productos afectados.",
        )
    ]


def test_minimal_delivery_report_full_structure_without_traces() -> None:
    report = render_minimal_delivery_report(
        tenant_id="t1",
        case_id="c1",
        owner_message="Mis margenes son malos",
        evidence_refs=["ventas_costos.xlsx"],
        findings=_sample_findings(),
        include_trace_ids=False,
    )
    
    assert "# Reporte operativo mínimo" in report
    assert "## Problema declarado" in report
    assert "Mis margenes son malos" in report
    assert "## Evidencia usada" in report
    assert "- ventas_costos.xlsx" in report
    assert "## Hallazgos principales" in report
    assert "## Acciones sugeridas" in report
    assert "## Límites del análisis" in report
    assert "actionable_finding:1:margen" not in report


def test_minimal_delivery_report_with_traces() -> None:
    report = render_minimal_delivery_report(
        tenant_id="t1",
        case_id="c1",
        owner_message="Mis margenes son malos",
        evidence_refs=["ventas_costos.xlsx"],
        findings=_sample_findings(),
        include_trace_ids=True,
    )
    
    assert "actionable_finding:1:margen" in report


def test_minimal_delivery_report_empty_findings_fails_closed() -> None:
    report = render_minimal_delivery_report(
        tenant_id="t1",
        case_id="c1",
        owner_message="Mis margenes son malos",
        evidence_refs=["ventas_costos.xlsx"],
        findings=[],
    )
    
    assert report == "El caso fue evaluado pero no arrojó hallazgos operativos."


def test_minimal_delivery_report_validates_inputs() -> None:
    findings = _sample_findings()
    
    with pytest.raises(ValueError, match="tenant_id"):
        render_minimal_delivery_report(
            tenant_id="",
            case_id="c1",
            owner_message="msg",
            evidence_refs=["file"],
            findings=findings,
        )
        
    with pytest.raises(ValueError, match="case_id"):
        render_minimal_delivery_report(
            tenant_id="t1",
            case_id=" ",
            owner_message="msg",
            evidence_refs=["file"],
            findings=findings,
        )
        
    with pytest.raises(ValueError, match="owner_message"):
        render_minimal_delivery_report(
            tenant_id="t1",
            case_id="c1",
            owner_message="",
            evidence_refs=["file"],
            findings=findings,
        )
        
    with pytest.raises(ValueError, match="evidence_refs"):
        render_minimal_delivery_report(
            tenant_id="t1",
            case_id="c1",
            owner_message="msg",
            evidence_refs=[],
            findings=findings,
        )


def test_minimal_delivery_report_has_no_forbidden_runtime_imports() -> None:
    path = Path("pymia/narrative/minimal_delivery_report.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_roots = {"requests", "httpx", "openai", "telegram", "pandas"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = {node.module.split(".")[0]}
        else:
            continue
        assert imported.isdisjoint(forbidden_roots)
