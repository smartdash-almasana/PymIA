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


def _supplier_fixture_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "smartpyme"
        / "proveedores_duplicados.xlsx"
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
    return PipelineScenario(
        scenario_id="unsupported_runtime_classification",
        tenant_id="tenant_demo",
        owner_message="Quiero analizar este archivo",
        evidence_items=(),
        expected=ScenarioExpectation(
            final_status="BLOCKED",
            must_not_dispatch=True,
        ),
    )


def _supplier_duplicate_check_happy_path() -> PipelineScenario:
    fixture_path = _supplier_fixture_path()
    return PipelineScenario(
        scenario_id="supplier_duplicate_check_happy_path",
        tenant_id="tenant_demo",
        owner_message="Quiero revisar duplicados de proveedores",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_proveedores",
                source_kind="uploaded_file",
                source_ref=str(fixture_path),
                metadata={"columns": ["proveedor", "cuit", "razon_social"]},
            ),
        ),
        expected=ScenarioExpectation(
            final_status="READY_TO_DELIVER",
            runtime_classification="supplier_duplicate_check",
            dispatch_status="EXECUTED",
            min_findings_count=1,
        ),
    )


def get_all_scenarios() -> list[PipelineScenario]:
    return [
        _margin_excel_happy_path(),
        _margin_excel_missing_evidence(),
        _evidence_type_mismatch(),
        _unsupported_runtime_classification(),
        _supplier_duplicate_check_happy_path(),
    ]


__all__ = ["get_all_scenarios"]
