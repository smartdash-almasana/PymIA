from __future__ import annotations

import ast
from pathlib import Path

from pymia.narrative.actionable_findings_adapter import (
    build_evidence_pool_from_actionable_findings,
    build_narrative_report_from_actionable_findings,
)
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.markdown_exporter import render_markdown
from pymia.smartpyme.finding_projection import ActionableFinding


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
        ),
        ActionableFinding(
            entity="Productos en ventas",
            metric="costo",
            difference="2 productos sin costo valido en ventas",
            source_comparison="ventas_costos_margen.xlsx",
            severity="medium",
            evidence_refs=["diagnostic_result.json"],
            recommendation="Asignar costo unitario positivo a productos afectados.",
        ),
    ]


def test_build_evidence_pool_from_actionable_findings_preserves_traceable_fields() -> None:
    pool = build_evidence_pool_from_actionable_findings(_sample_findings())

    assert [item.id for item in pool] == [
        "actionable_finding:1:margen",
        "actionable_finding:2:costo",
    ]
    assert pool[0].source == "actionable_findings"
    assert pool[0].metric == "margen"
    assert pool[0].value == "high"
    assert pool[0].details["evidence_refs"] == ["diagnostic_result.json"]


def test_build_narrative_report_from_actionable_findings_is_grounded_and_legible() -> None:
    findings = _sample_findings()
    pool = build_evidence_pool_from_actionable_findings(findings)
    report = build_narrative_report_from_actionable_findings(findings)

    result = validate_grounding(report, pool)
    plain = render_markdown(report, include_trace_ids=False)
    traced = render_markdown(report, include_trace_ids=True)

    assert result.ok is True
    assert [section.title for section in report.sections] == [
        "Hallazgos principales",
        "Acciones sugeridas",
    ]
    assert "Productos en ventas" in plain
    assert "3 productos con margen bajo" in plain
    assert "actionable_finding:1:margen" not in plain
    assert "actionable_finding:1:margen" in traced
    assert report.trace["status"] == "OK"


def test_build_narrative_report_from_empty_findings_fails_closed() -> None:
    report = build_narrative_report_from_actionable_findings([])

    assert report.sections == []
    assert report.trace["status"] == "EMPTY"
    assert report.trace["findings_count"] == 0


def test_actionable_findings_adapter_has_no_forbidden_runtime_imports() -> None:
    path = Path("pymia/narrative/actionable_findings_adapter.py")
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
