from __future__ import annotations

import json

from pymia.pipeline_radiography import (
    ALLOWED_RADIOGRAPHY_VERDICTS,
    PipelineScenario,
    PipelineStageTrace,
    PipelineTrace,
    ScenarioEvidence,
    ScenarioExpectation,
)


def test_scenario_is_json_serializable() -> None:
    scenario = PipelineScenario(
        scenario_id="margin_excel_happy_path",
        tenant_id="tenant_demo",
        owner_message="No se si vendo con margen",
        evidence_items=(
            ScenarioEvidence(
                evidence_type="excel_ventas_costos",
                source_kind="uploaded_file",
                source_ref="tests/fixtures/smartpyme/ventas_costos_margen.xlsx",
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="ventas_del_periodo",
                source_kind="uploaded_file",
                source_ref="tests/fixtures/smartpyme/ventas_costos_margen.xlsx",
                metadata={"columns": ["producto", "ventas", "costo"]},
            ),
            ScenarioEvidence(
                evidence_type="costos_directos",
                source_kind="uploaded_file",
                source_ref="tests/fixtures/smartpyme/ventas_costos_margen.xlsx",
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

    payload = scenario.to_dict()
    assert payload["scenario_id"] == "margin_excel_happy_path"
    assert payload["expected"]["final_status"] == "READY_TO_DELIVER"
    assert len(payload["evidence_items"]) == 3
    assert payload["evidence_items"][0]["metadata"]["columns"] == ["producto", "ventas", "costo"]
    json.dumps(payload)


def test_trace_appends_stages_and_serializes() -> None:
    trace = PipelineTrace(
        trace_id="trace_001",
        scenario_id="margin_excel_happy_path",
    )
    trace.add_stage(
        PipelineStageTrace(
            name="intake",
            status="NEEDS_EVIDENCE",
            input_type="owner_message",
            output_type="IntakeRecord",
            summary={"evidence_request_count": 1},
        )
    )
    trace.add_stage(
        PipelineStageTrace(
            name="evidence_gate",
            status="READY",
            output_type="EvidenceSufficiencyResult",
            summary={"matched_evidence_ids": ["ev_1"]},
        )
    )
    trace.set_final(
        overall_status="PASS",
        final_summary={"final_status": "READY_TO_DELIVER"},
    )

    payload = trace.to_dict()
    assert len(payload["stages"]) == 2
    assert payload["overall_status"] == "PASS"
    assert payload["final_summary"]["final_status"] == "READY_TO_DELIVER"
    json.dumps(payload)


def test_allowed_verdicts_are_explicit() -> None:
    assert ALLOWED_RADIOGRAPHY_VERDICTS == (
        "PASS",
        "BLOCKED_EXPECTED",
        "FAIL",
        "AMBIGUOUS",
    )
