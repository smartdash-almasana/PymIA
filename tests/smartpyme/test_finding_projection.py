"""Tests for pymia.smartpyme.finding_projection.

Covers the fail-closed contract and the deterministic projection from
MicroserviceExecutionResult-like dicts to ActionableFinding.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from pymia.smartpyme.finding_projection import (
    ActionableFinding,
    GENERIC_METRIC,
    GENERIC_RECOMMENDATION,
    project_actionable_findings,
)


MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "pymia"
    / "smartpyme"
    / "finding_projection.py"
)


def _base_raw_findings() -> list[dict]:
    return [
        {
            "code": "LOW_MARGIN",
            "severity": "medium",
            "message": "Margen bajo (<10%).",
            "count": 5,
            "sheet_name": "ventas",
        }
    ]


def _base_execution(
    *,
    status: str = "EXECUTED",
    findings_count: int = 1,
    findings: list[dict] | None = None,
    output_refs: list[str] | None = None,
    raw_result_extra: dict | None = None,
    include_raw: bool = True,
) -> dict:
    raw: dict = {
        "evidence": {
            "tenant_id": "tenant_1",
            "source_file": "/tmp/ventas.xlsx",
            "total_rows": 150,
            "sheets_processed": 2,
        },
        "findings": list(findings) if findings is not None else _base_raw_findings(),
    }
    if raw_result_extra:
        raw.update(raw_result_extra)
    return {
        "tenant_id": "tenant_1",
        "intake_id": "intake_1",
        "runtime_classification": "excel_diagnostic",
        "microservice_name": "excel_diagnostic_worker",
        "status": status,
        "output_refs": list(output_refs) if output_refs is not None else ["/tmp/report.md"],
        "findings_count": findings_count,
        "raw_result": raw if include_raw else {},
        "executed_at": "2026-06-01T19:45:32+00:00",
        "warnings": [],
    }


@dataclass
class _FakeExecutionResult:
    data: dict
    extra_attr: str = "smoke"

    def to_dict(self) -> dict:
        return dict(self.data)


def test_blocked_status_returns_empty_findings() -> None:
    result = _base_execution(status="BLOCKED")
    assert project_actionable_findings(result) == []


def test_failed_status_returns_empty_findings() -> None:
    result = _base_execution(status="FAILED")
    assert project_actionable_findings(result) == []


def test_unsupported_status_returns_empty_findings() -> None:
    result = _base_execution(status="UNSUPPORTED")
    assert project_actionable_findings(result) == []


def test_unknown_status_returns_empty_findings() -> None:
    result = _base_execution(status="WHATEVER")
    assert project_actionable_findings(result) == []


def test_zero_findings_count_returns_empty_findings() -> None:
    result = _base_execution(findings_count=0)
    assert project_actionable_findings(result) == []


def test_negative_findings_count_returns_empty_findings() -> None:
    result = _base_execution(findings_count=-1)
    assert project_actionable_findings(result) == []


def test_raw_result_without_findings_returns_empty() -> None:
    result = _base_execution()
    result["raw_result"] = {"evidence": {}, "markdown": "..."}
    assert project_actionable_findings(result) == []


def test_raw_result_findings_not_list_returns_empty() -> None:
    result = _base_execution()
    result["raw_result"]["findings"] = "not-a-list"
    assert project_actionable_findings(result) == []


def test_missing_raw_result_returns_empty() -> None:
    result = _base_execution(include_raw=False)
    assert project_actionable_findings(result) == []


def test_low_margin_projects_metric_margen_and_preserves_severity() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "LOW_MARGIN",
                "severity": "medium",
                "message": "Margen bajo (<10%).",
                "count": 5,
                "sheet_name": "ventas",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    f = findings[0]
    assert f.metric == "margen"
    assert f.severity == "medium"
    assert "5" in f.difference
    assert "ventas" in f.difference
    assert f.recommendation  # non-empty deterministic recommendation
    assert f.source_comparison == "/tmp/ventas.xlsx"


def test_product_without_cost_projects_metric_costo() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "PRODUCT_WITHOUT_COST",
                "severity": "high",
                "message": "Productos con costo faltante o no positivo.",
                "count": 3,
                "sheet_name": "productos",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    assert findings[0].metric == "costo"
    assert findings[0].severity == "high"
    assert "3" in findings[0].difference
    assert "productos" in findings[0].difference


def test_empty_product_projects_metric_producto() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "EMPTY_PRODUCT",
                "severity": "high",
                "message": "Columna relevante ausente.",
                "count": 1,
                "sheet_name": "productos",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    assert findings[0].metric == "producto"
    assert findings[0].severity == "high"


def test_empty_sales_projects_metric_ventas() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "EMPTY_SALES",
                "severity": "medium",
                "message": "Celdas vacias.",
                "count": 4,
                "sheet_name": "ventas",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert findings[0].metric == "ventas"


def test_empty_cost_projects_metric_costo() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "EMPTY_COST",
                "severity": "medium",
                "message": "Celdas vacias.",
                "count": 2,
                "sheet_name": "costos",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert findings[0].metric == "costo"


def test_duplicate_rows_projects_metric_filas() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "DUPLICATE_ROWS",
                "severity": "medium",
                "message": "Filas duplicadas.",
                "count": 7,
                "sheet_name": "ventas",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert findings[0].metric == "filas"
    assert "7" in findings[0].difference


def test_margin_not_calculable_projects_metric_margen() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "MARGIN_NOT_CALCULABLE",
                "severity": "high",
                "message": "Margen no calculable.",
                "count": 2,
                "sheet_name": "ventas",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert findings[0].metric == "margen"
    assert findings[0].severity == "high"


def test_output_refs_are_propagated_to_evidence_refs() -> None:
    refs = ["/tmp/report.md", "/tmp/slice.json"]
    result = _base_execution(output_refs=refs)
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    assert findings[0].evidence_refs == refs


def test_unknown_code_produces_generic_finding() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "SOMETHING_WEIRD",
                "severity": "low",
                "message": "Cosa rara.",
                "count": 1,
                "sheet_name": "misc",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    f = findings[0]
    assert f.metric == GENERIC_METRIC
    assert f.recommendation == GENERIC_RECOMMENDATION
    assert f.severity == "low"


def test_empty_code_produces_generic_finding() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "",
                "severity": "medium",
                "message": "mensaje",
                "count": 1,
                "sheet_name": "x",
            }
        ]
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    assert findings[0].metric == GENERIC_METRIC


def test_to_dict_is_json_serializable() -> None:
    result = _base_execution(
        findings=[
            {
                "code": "LOW_MARGIN",
                "severity": "medium",
                "message": "Margen bajo (<10%).",
                "count": 5,
                "sheet_name": "ventas",
            },
            {
                "code": "PRODUCT_WITHOUT_COST",
                "severity": "high",
                "message": "Sin costo.",
                "count": 3,
                "sheet_name": "productos",
            },
        ],
        output_refs=["/tmp/report.md"],
    )
    findings = project_actionable_findings(result)
    assert len(findings) == 2
    for f in findings:
        payload = f.to_dict()
        serialized = json.dumps(payload, ensure_ascii=False)
        assert isinstance(serialized, str)
        round_trip = json.loads(serialized)
        assert round_trip["metric"] == payload["metric"]
        assert round_trip["evidence_refs"] == payload["evidence_refs"]


def test_accepts_object_with_to_dict() -> None:
    obj = _FakeExecutionResult(data=_base_execution())
    findings = project_actionable_findings(obj)
    assert len(findings) == 1
    assert findings[0].metric == "margen"


def test_accepts_microservice_execution_result_like_dataclass() -> None:
    @dataclass
    class MicroserviceExecutionResultLike:
        tenant_id: str
        intake_id: str
        runtime_classification: str
        microservice_name: str
        status: str
        output_refs: list[str] = field(default_factory=list)
        findings_count: int = 0
        raw_result: dict = field(default_factory=dict)
        executed_at: str = ""
        warnings: list[str] = field(default_factory=list)

        def to_dict(self) -> dict:
            return {
                "tenant_id": self.tenant_id,
                "intake_id": self.intake_id,
                "runtime_classification": self.runtime_classification,
                "microservice_name": self.microservice_name,
                "status": self.status,
                "output_refs": list(self.output_refs),
                "findings_count": self.findings_count,
                "raw_result": dict(self.raw_result),
                "executed_at": self.executed_at,
                "warnings": list(self.warnings),
            }

    obj = MicroserviceExecutionResultLike(
        tenant_id="tenant_1",
        intake_id="intake_1",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        status="EXECUTED",
        output_refs=["/tmp/report.md"],
        findings_count=1,
        raw_result={
            "evidence": {
                "tenant_id": "tenant_1",
                "source_file": "/tmp/ventas.xlsx",
                "total_rows": 150,
                "sheets_processed": 2,
            },
            "findings": _base_raw_findings(),
        },
        executed_at="2026-06-01T19:45:32+00:00",
        warnings=[],
    )
    findings = project_actionable_findings(obj)
    assert len(findings) == 1
    assert findings[0].metric == "margen"


def test_module_does_not_import_excel_diagnostic() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {
        "pymia.smartpyme.excel_diagnostic",
        "excel_diagnostic",
        "pymia.smartpyme.microservice_dispatcher",
        "microservice_dispatcher",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module not in forbidden, (
                f"finding_projection must not import {node.module}"
            )
            for alias in node.names:
                assert alias.name not in forbidden
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden


def test_module_does_not_import_llm_or_telegram() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_fragments = {
        "openai",
        "llm",
        "hermes",
        "telegram",
        "landing",
        "conversa_engine",
        "conversa-engine",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            lowered = node.module.lower()
            for fragment in forbidden_fragments:
                assert fragment not in lowered, (
                    f"finding_projection must not import module containing {fragment!r}"
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                lowered = alias.name.lower()
                for fragment in forbidden_fragments:
                    assert fragment not in lowered


def test_finding_projection_does_not_generate_report_or_findings_final() -> None:
    """The projection returns a list, never a report or a final 'hallazgo' wrapper."""
    result = _base_execution()
    findings = project_actionable_findings(result)
    assert isinstance(findings, list)
    for f in findings:
        assert isinstance(f, ActionableFinding)
        # No report/findings-wrapper keys leak into the finding payload.
        payload = f.to_dict()
        assert "report" not in payload
        assert "markdown" not in payload
        assert "findings" not in payload


def test_source_comparison_uses_evidence_source_file() -> None:
    result = _base_execution()
    findings = project_actionable_findings(result)
    assert findings[0].source_comparison == "/tmp/ventas.xlsx"


def test_source_comparison_empty_when_evidence_missing() -> None:
    result = _base_execution()
    result["raw_result"] = {"findings": _base_raw_findings()}
    findings = project_actionable_findings(result)
    assert findings[0].source_comparison == ""


def test_non_dict_finding_entry_is_skipped() -> None:
    result = _base_execution(
        findings=[
            "not-a-dict",
            {
                "code": "LOW_MARGIN",
                "severity": "medium",
                "message": "Margen bajo.",
                "count": 2,
                "sheet_name": "ventas",
            },
            None,
        ]
    )
    result["findings_count"] = 3
    findings = project_actionable_findings(result)
    assert len(findings) == 1
    assert findings[0].metric == "margen"


def test_invalid_execution_input_returns_empty() -> None:
    assert project_actionable_findings(None) == []
    assert project_actionable_findings(42) == []
    assert project_actionable_findings("EXECUTED") == []


@pytest.mark.parametrize("status", ["BLOCKED", "FAILED", "UNSUPPORTED", "PENDING", ""])
def test_non_executed_statuses_return_empty(status: str) -> None:
    result = _base_execution(status=status)
    assert project_actionable_findings(result) == []
