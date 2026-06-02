from __future__ import annotations

from pathlib import Path

from .scenario import PipelineScenario, ScenarioEvidence, ScenarioExpectation


def _fixture_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "smartpyme"
        / "ventas_costos_margen.xlsx"
    )


def _margin_excel_happy_path() -> PipelineScenario:
    fixture_path = _fixture_path()
    return PipelineScenario(
        scenario_id="margin_excel_happy_path",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_ventas_costos",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="ventas_del_periodo",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="costos_directos",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="READY_TO_DELIVER",
            runtime_classification="excel_diagnostic",
            dispatch_status="EXECUTED",
            min_findings_count=1,
        ),
    )


def _margin_excel_missing_evidence() -> PipelineScenario:
    return PipelineScenario(
        scenario_id="margin_excel_missing_evidence",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(),
        expected=ScenarioExpectation(
            final_status="NEEDS_EVIDENCE",
            must_not_dispatch=True,
        ),
    )


def _evidence_type_mismatch() -> PipelineScenario:
    fixture_path = _fixture_path()
    return PipelineScenario(
        scenario_id="evidence_type_mismatch",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_proveedores",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="NEEDS_EVIDENCE",
            must_not_dispatch=True,
        ),
    )


def _unsupported_runtime_classification() -> PipelineScenario:
    fixture_path = _fixture_path()
    return PipelineScenario(
        scenario_id="unsupported_runtime_classification",
        tenant_id="tenant_demo",
        owner_message="Quiero revisar duplicados de proveedores",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_proveedores",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="BLOCKED",
            dispatch_status="UNSUPPORTED",
        ),
    )


def get_all_scenarios() -> list[PipelineScenario]:
    return [
        _margin_excel_happy_path(),
        _margin_excel_missing_evidence(),
        _evidence_type_mismatch(),
        _unsupported_runtime_classification(),
    ]


__all__ = ["get_all_scenarios"]
