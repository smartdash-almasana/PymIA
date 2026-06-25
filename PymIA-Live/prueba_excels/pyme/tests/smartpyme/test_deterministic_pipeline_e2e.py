from __future__ import annotations

from pathlib import Path

import pandas as pd


def _write_excel(path: Path) -> None:
    df = pd.DataFrame(
        {
            "producto": ["Cafe", "Medialuna", "Tostado", "Cafe"],
            "ventas": [120000, 85000, 65000, 120000],
            "costo": [70000, 40000, 36000, 70000],
        }
    )
    df.to_excel(path, index=False)


def _create_excel_intake_and_evidence(tmp_path):
    from pymia.smartpyme.evidence import (
        EVIDENCE_STATUS_RECEIVED,
        SOURCE_KIND_UPLOADED_FILE,
        create_evidence_record,
    )
    from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
    from pymia.smartpyme.intake import create_intake_record
    from pymia.smartpyme.readiness import evaluate_analysis_readiness

    tenant_id = "tenant_m18_2_excel"
    excel_path = tmp_path / "ventas_costos_margen.xlsx"
    _write_excel(excel_path)

    intake = create_intake_record(
        tenant_id=tenant_id,
        raw_text="Tengo un Excel con ventas, costos y margen, y necesito entender por que no me cierra la plata.",
    )
    assert intake.evidence_requests

    evidence_records = []
    for req in [request for request in intake.evidence_requests if request.blocks_analysis]:
        metadata = {field: f"value_{field}" for field in (req.required_fields or [])}
        evidence_records.append(
            create_evidence_record(
                tenant_id=tenant_id,
                intake_id=intake.intake_id,
                evidence_type=req.evidence_type,
                source_kind=SOURCE_KIND_UPLOADED_FILE,
                source_ref=str(excel_path),
                request_id=req.request_id,
                original_filename=excel_path.name,
                mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                status=EVIDENCE_STATUS_RECEIVED,
                metadata=metadata,
            )
        )

    sufficiency = evaluate_evidence_sufficiency(intake.to_dict(), evidence_records)
    readiness = evaluate_analysis_readiness(intake.to_dict(), sufficiency.to_dict())
    return intake, evidence_records, sufficiency, readiness, excel_path


def test_m18_2_excel_diagnostic_pipeline_happy_path_ready_to_deliver(tmp_path) -> None:
    from pymia.smartpyme.delivery_package import STATUS_READY_TO_DELIVER, build_delivery_package
    from pymia.smartpyme.execution_result_gate import VERDICT_PASS, validate_execution_result
    from pymia.smartpyme.microservice_dispatcher import EXECUTION_EXECUTED, dispatch_candidate
    from pymia.smartpyme.readiness import (
        READINESS_READY_FOR_ANALYSIS,
        RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC,
    )
    from pymia.smartpyme.runtime_bridge import EXECUTION_READY_TO_EXECUTE, prepare_runtime_execution

    intake, evidence_records, sufficiency, readiness, excel_path = _create_excel_intake_and_evidence(tmp_path)

    assert sufficiency.status == "READY"
    assert sufficiency.matched_evidence_ids
    assert readiness.status == READINESS_READY_FOR_ANALYSIS
    assert readiness.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC
    assert readiness.can_execute is True

    candidate = prepare_runtime_execution(readiness)
    assert candidate.status == EXECUTION_READY_TO_EXECUTE
    assert candidate.can_dispatch is True
    assert candidate.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC
    assert candidate.evidence_ids == sufficiency.matched_evidence_ids

    execution_result = dispatch_candidate(
        candidate,
        evidence_path=excel_path,
        output_dir=tmp_path / "out",
    )
    assert execution_result.status == EXECUTION_EXECUTED
    assert execution_result.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC
    assert execution_result.findings_count > 0
    assert execution_result.output_refs
    for output_ref in execution_result.output_refs:
        assert Path(output_ref).exists()

    gate_verdict = validate_execution_result(execution_result)
    assert gate_verdict.verdict == VERDICT_PASS

    delivery_package = build_delivery_package(execution_result, gate_verdict)
    assert delivery_package.status == STATUS_READY_TO_DELIVER
    assert delivery_package.runtime_classification == RUNTIME_CLASSIFICATION_EXCEL_DIAGNOSTIC
    assert delivery_package.output_refs
    assert delivery_package.output_refs == execution_result.output_refs
    assert delivery_package.tenant_id == intake.tenant_id
    assert delivery_package.intake_id == intake.intake_id


def test_m18_2_missing_evidence_blocks_before_runtime(tmp_path) -> None:
    from pymia.smartpyme.evidence_gate import evaluate_evidence_sufficiency
    from pymia.smartpyme.intake import create_intake_record
    from pymia.smartpyme.readiness import READINESS_NEEDS_EVIDENCE, evaluate_analysis_readiness
    from pymia.smartpyme.runtime_bridge import EXECUTION_BLOCKED, prepare_runtime_execution

    intake = create_intake_record(
        tenant_id="tenant_m18_2_missing_evidence",
        raw_text="Tengo un Excel con ventas y costos pero no adjunte el archivo.",
    )

    sufficiency = evaluate_evidence_sufficiency(intake.to_dict(), [])
    readiness = evaluate_analysis_readiness(intake.to_dict(), sufficiency.to_dict())
    candidate = prepare_runtime_execution(readiness)

    assert sufficiency.status == "NEEDS_MORE_EVIDENCE"
    assert readiness.status == READINESS_NEEDS_EVIDENCE
    assert readiness.can_execute is False
    assert candidate.status == EXECUTION_BLOCKED
    assert candidate.can_dispatch is False


def test_m18_2_unknown_runtime_classification_is_unsupported() -> None:
    from pymia.smartpyme.runtime_bridge import EXECUTION_UNSUPPORTED, prepare_runtime_execution

    candidate = prepare_runtime_execution(
        {
            "tenant_id": "tenant_m18_2_unknown",
            "intake_id": "intake_unknown",
            "status": "READY_FOR_ANALYSIS",
            "runtime_classification": "unknown_classification",
            "can_execute": True,
            "matched_evidence_ids": ["evidence_1"],
            "blocking_reasons": [],
            "warnings": [],
            "audit_notes": [],
        }
    )

    assert candidate.status == EXECUTION_UNSUPPORTED
    assert candidate.can_dispatch is False
    assert "Unsupported runtime_classification" in candidate.blocking_reasons[0]


def test_m18_2_candidate_not_ready_is_blocked_by_dispatcher(tmp_path) -> None:
    from pymia.smartpyme.microservice_dispatcher import EXECUTION_BLOCKED, dispatch_candidate

    excel_path = tmp_path / "ventas_costos_margen.xlsx"
    _write_excel(excel_path)
    result = dispatch_candidate(
        {
            "tenant_id": "tenant_m18_2_candidate_blocked",
            "intake_id": "intake_candidate_blocked",
            "runtime_classification": "excel_diagnostic",
            "microservice_name": "excel_diagnostic_worker",
            "evidence_ids": ["evidence_1"],
            "status": "BLOCKED",
            "can_dispatch": False,
        },
        evidence_path=excel_path,
        output_dir=tmp_path / "out",
    )

    assert result.status == EXECUTION_BLOCKED
    assert result.output_refs == []
    assert result.findings_count == 0


def test_m18_2_plugin_failure_yields_failed_delivery(tmp_path) -> None:
    from pymia.smartpyme.delivery_package import STATUS_FAILED, build_delivery_package
    from pymia.smartpyme.execution_result_gate import VERDICT_FAILED, validate_execution_result
    from pymia.smartpyme.microservice_dispatcher import EXECUTION_FAILED, dispatch_candidate
    from pymia.smartpyme.runtime_bridge import RuntimeExecutionCandidate

    candidate = RuntimeExecutionCandidate(
        tenant_id="tenant_m18_2_plugin_failure",
        intake_id="intake_plugin_failure",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        evidence_ids=["evidence_1"],
        status="READY_TO_EXECUTE",
        can_dispatch=True,
    )

    result = dispatch_candidate(
        candidate,
        evidence_path=tmp_path / "missing.xlsx",
        output_dir=tmp_path / "out",
    )
    gate_verdict = validate_execution_result(result)
    delivery_package = build_delivery_package(result, gate_verdict)

    assert result.status == EXECUTION_FAILED
    assert gate_verdict.verdict == VERDICT_FAILED
    assert delivery_package.status == STATUS_FAILED


def test_m18_2_gate_rejects_undeliverable_execution_result() -> None:
    from pymia.smartpyme.delivery_package import STATUS_FAILED, build_delivery_package
    from pymia.smartpyme.execution_result_gate import VERDICT_UNDELIVERABLE, validate_execution_result

    result = {
        "tenant_id": "tenant_m18_2_undeliverable",
        "intake_id": "intake_undeliverable",
        "runtime_classification": "excel_diagnostic",
        "microservice_name": "excel_diagnostic_worker",
        "status": "EXECUTED",
        "output_refs": [],
        "findings_count": 1,
        "raw_result": {"findings": [{"message": "synthetic"}]},
        "warnings": [],
    }

    gate_verdict = validate_execution_result(result)
    delivery_package = build_delivery_package(result, gate_verdict)

    assert gate_verdict.verdict == VERDICT_UNDELIVERABLE
    assert delivery_package.status == STATUS_FAILED
