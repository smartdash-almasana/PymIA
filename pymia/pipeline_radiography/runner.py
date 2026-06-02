from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from pymia.smartpyme.delivery_package import build_delivery_package
from pymia.smartpyme.evidence import (
    EVIDENCE_STATUS_RECEIVED,
    SOURCE_KIND_UPLOADED_FILE,
    create_evidence_record,
)
from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
from pymia.smartpyme.execution_result_gate import validate_execution_result
from pymia.smartpyme.intake import create_intake_record
from pymia.smartpyme.microservice_dispatcher import dispatch_candidate
from pymia.smartpyme.readiness import evaluate_analysis_readiness
from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

from .scenario import PipelineScenario, ScenarioEvidence
from .trace import PipelineStageTrace, PipelineTrace


@dataclass
class PipelineRunResult:
    trace: PipelineTrace
    intake_record: dict[str, Any]
    evidence_records: list[dict[str, Any]]
    sufficiency_result: dict[str, Any]
    readiness_result: dict[str, Any]
    runtime_candidate: dict[str, Any]
    execution_result: dict[str, Any] | None
    execution_gate_verdict: dict[str, Any] | None
    delivery_package: dict[str, Any] | None


def _scenario_metadata_for_request(
    evidence_item: ScenarioEvidence,
    request: dict[str, Any],
) -> dict[str, Any]:
    # Metadata sintetica de escenario para M19 v0; no reemplaza un extractor real.
    metadata = dict(evidence_item.metadata)
    required_fields = list(request.get("required_fields") or [])
    for field in required_fields:
        metadata.setdefault(field, f"provided_{field}")
    if "fields" not in metadata:
        fields = list(dict.fromkeys(
            [*required_fields, *metadata.get("columns", [])]
        ))
        if fields:
            metadata["fields"] = fields
    return metadata


def _build_evidence_records(
    *,
    scenario: PipelineScenario,
    intake_record: dict[str, Any],
) -> list[dict[str, Any]]:
    requests = [
        dict(item)
        for item in (intake_record.get("evidence_requests") or [])
        if isinstance(item, dict) and item.get("blocks_analysis")
    ]
    evidence_records: list[dict[str, Any]] = []
    available_items = list(scenario.evidence_items)
    for request in requests:
        match = next(
            (
                item for item in available_items
                if item.evidence_type == str(request.get("evidence_type") or "")
            ),
            None,
        )
        if match is None:
            continue
        evidence = create_evidence_record(
            tenant_id=scenario.tenant_id,
            intake_id=str(intake_record["intake_id"]),
            evidence_type=match.evidence_type,
            source_kind=match.source_kind or SOURCE_KIND_UPLOADED_FILE,
            source_ref=match.source_ref,
            request_id=str(request.get("request_id") or "") or None,
            status=EVIDENCE_STATUS_RECEIVED,
            metadata=_scenario_metadata_for_request(match, request),
        )
        evidence_records.append(evidence.to_dict())
    return evidence_records


def _stage_summary_intake(intake_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "intake_state": intake_record.get("intake_state"),
        "suggested_next_state": intake_record.get("suggested_next_state"),
        "evidence_request_count": len(intake_record.get("evidence_requests") or []),
    }


def _stage_summary_evidence(evidence_records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "evidence_count": len(evidence_records),
        "evidence_types": [str(item.get("evidence_type") or "") for item in evidence_records],
    }


def run_pipeline_scenario(
    scenario: PipelineScenario,
    *,
    output_root: str | Path | None = None,
) -> PipelineRunResult:
    trace = PipelineTrace(
        trace_id=f"trace_{uuid4().hex[:12]}",
        scenario_id=scenario.scenario_id,
    )
    intake = create_intake_record(
        tenant_id=scenario.tenant_id,
        raw_text=scenario.owner_message,
    ).to_dict()
    trace.add_stage(
        PipelineStageTrace(
            name="intake",
            status=str(intake.get("intake_state") or ""),
            input_type="owner_message",
            output_type="IntakeRecord",
            summary=_stage_summary_intake(intake),
        )
    )

    evidence_records = _build_evidence_records(scenario=scenario, intake_record=intake)
    trace.add_stage(
        PipelineStageTrace(
            name="evidence",
            status="REGISTERED" if evidence_records else "MISSING",
            input_type="ScenarioEvidence",
            output_type="EvidenceRecordList",
            summary=_stage_summary_evidence(evidence_records),
        )
    )

    sufficiency = evaluate_evidence_sufficiency(intake, evidence_records).to_dict()
    trace.add_stage(
        PipelineStageTrace(
            name="evidence_gate",
            status=str(sufficiency.get("status") or ""),
            input_type="IntakeRecord+EvidenceRecordList",
            output_type="EvidenceSufficiencyResult",
            summary={
                "suggested_next_state": sufficiency.get("suggested_next_state"),
                "missing_request_ids": list(sufficiency.get("missing_request_ids") or []),
                "matched_evidence_ids": list(sufficiency.get("matched_evidence_ids") or []),
            },
        )
    )

    readiness = evaluate_analysis_readiness(intake, sufficiency).to_dict()
    trace.add_stage(
        PipelineStageTrace(
            name="readiness",
            status=str(readiness.get("status") or ""),
            input_type="IntakeRecord+EvidenceSufficiencyResult",
            output_type="AnalysisReadinessResult",
            summary={
                "runtime_classification": readiness.get("runtime_classification"),
                "can_execute": readiness.get("can_execute"),
                "blocking_reasons": list(readiness.get("blocking_reasons") or []),
            },
        )
    )

    candidate = prepare_runtime_execution(readiness).to_dict()
    trace.add_stage(
        PipelineStageTrace(
            name="runtime_bridge",
            status=str(candidate.get("status") or ""),
            input_type="AnalysisReadinessResult",
            output_type="RuntimeExecutionCandidate",
            summary={
                "runtime_classification": candidate.get("runtime_classification"),
                "microservice_name": candidate.get("microservice_name"),
                "can_dispatch": candidate.get("can_dispatch"),
                "blocking_reasons": list(candidate.get("blocking_reasons") or []),
            },
        )
    )

    execution_result: dict[str, Any] | None = None
    execution_gate_verdict: dict[str, Any] | None = None
    delivery_package: dict[str, Any] | None = None

    if candidate.get("can_dispatch"):
        matched_ids = set(str(item) for item in (candidate.get("evidence_ids") or []))
        evidence_path = ""
        for record in evidence_records:
            if str(record.get("evidence_id") or "") in matched_ids:
                evidence_path = str(record.get("source_ref") or "")
                break
        if not evidence_path and evidence_records:
            evidence_path = str(evidence_records[0].get("source_ref") or "")

        if output_root is None:
            output_dir = Path.cwd() / ".pipeline_radiography" / trace.trace_id
        else:
            output_dir = Path(output_root) / trace.trace_id
        output_dir.mkdir(parents=True, exist_ok=True)

        execution_result = dispatch_candidate(
            candidate,
            evidence_path=evidence_path,
            output_dir=output_dir,
        ).to_dict()
        trace.add_stage(
            PipelineStageTrace(
                name="microservice_dispatcher",
                status=str(execution_result.get("status") or ""),
                input_type="RuntimeExecutionCandidate",
                output_type="MicroserviceExecutionResult",
                summary={
                    "output_refs": list(execution_result.get("output_refs") or []),
                    "findings_count": execution_result.get("findings_count"),
                    "warnings": list(execution_result.get("warnings") or []),
                },
            )
        )

        execution_gate_verdict = validate_execution_result(execution_result).to_dict()
        trace.add_stage(
            PipelineStageTrace(
                name="execution_result_gate",
                status=str(execution_gate_verdict.get("verdict") or ""),
                input_type="MicroserviceExecutionResult",
                output_type="ExecutionResultGateVerdict",
                summary={
                    "reasons": list(execution_gate_verdict.get("reasons") or []),
                    "warnings": list(execution_gate_verdict.get("warnings") or []),
                },
            )
        )

        delivery_package = build_delivery_package(
            execution_result,
            execution_gate_verdict,
        ).to_dict()
        trace.add_stage(
            PipelineStageTrace(
                name="delivery_package",
                status=str(delivery_package.get("status") or ""),
                input_type="MicroserviceExecutionResult+ExecutionResultGateVerdict",
                output_type="DeliveryPackage",
                summary={
                    "gate_verdict": delivery_package.get("gate_verdict"),
                    "output_refs": list(delivery_package.get("output_refs") or []),
                },
            )
        )
    else:
        blocked_at = "readiness"
        if sufficiency.get("status") != "READY":
            blocked_at = "evidence_gate"
        trace.set_final(
            overall_status="BLOCKED_EXPECTED",
            blocked_at=blocked_at,
            final_summary={
                "final_status": str(readiness.get("status") or ""),
                "runtime_classification": readiness.get("runtime_classification"),
                "dispatch_status": None,
                "findings_count": 0,
                "must_not_dispatch": True,
            },
        )
        return PipelineRunResult(
            trace=trace,
            intake_record=intake,
            evidence_records=evidence_records,
            sufficiency_result=sufficiency,
            readiness_result=readiness,
            runtime_candidate=candidate,
            execution_result=None,
            execution_gate_verdict=None,
            delivery_package=None,
        )

    final_status = str((delivery_package or {}).get("status") or "")
    dispatch_status = str((execution_result or {}).get("status") or "")
    runtime_classification = (
        (delivery_package or {}).get("runtime_classification")
        or (execution_result or {}).get("runtime_classification")
        or candidate.get("runtime_classification")
    )
    findings_count = int((execution_result or {}).get("findings_count") or 0)

    overall_status = "PASS"
    if final_status != scenario.expected.final_status:
        overall_status = "FAIL"
    if scenario.expected.runtime_classification and (
        runtime_classification != scenario.expected.runtime_classification
    ):
        overall_status = "FAIL"
    if scenario.expected.dispatch_status and (
        dispatch_status != scenario.expected.dispatch_status
    ):
        overall_status = "FAIL"
    if findings_count < scenario.expected.min_findings_count:
        overall_status = "FAIL"

    trace.set_final(
        overall_status=overall_status,
        blocked_at=None,
        final_summary={
            "final_status": final_status,
            "runtime_classification": runtime_classification,
            "dispatch_status": dispatch_status,
            "findings_count": findings_count,
            "must_not_dispatch": False,
        },
    )
    return PipelineRunResult(
        trace=trace,
        intake_record=intake,
        evidence_records=evidence_records,
        sufficiency_result=sufficiency,
        readiness_result=readiness,
        runtime_candidate=candidate,
        execution_result=execution_result,
        execution_gate_verdict=execution_gate_verdict,
        delivery_package=delivery_package,
    )


__all__ = [
    "PipelineRunResult",
    "run_pipeline_scenario",
]
