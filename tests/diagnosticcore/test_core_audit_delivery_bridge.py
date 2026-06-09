from __future__ import annotations

import ast
import json
from pathlib import Path

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.diagnostic_core.models import (
    CoreDiagnosticResult,
    CoreFinding,
    CoreFormulaResult,
    CoreDiagnosticStatus,
    DiagnosticCoreResult,
    DiagnosticCoreStatus,
    EvidenceGateDecision,
    EvidenceGateDecisionStatus,
    FormulaInputGateResult,
    FormulaInputGateStatus,
)
from pymia.orchestration.state import PymIAState


def _sample_evidence() -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant-m37",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="tenant_m37_operational.xlsx",
        computed_variables={
            "ventas_total": 120000.0,
            "costos_total": 60000.0,
            "margen_bruto": 60000.0,
            "margen_bruto_pct": 0.5,
        },
        metadata={},
    )


def test_bridge_blocks_when_missing_inputs_and_projects_state(tmp_path):
    from pymia.audit_result.core_delivery_bridge import (
        build_core_audit_delivery_bundle,
        project_bridge_result_to_state,
    )

    bundle = build_core_audit_delivery_bundle(
        evidence=_sample_evidence(),
        case_id="case-m37-blocked",
        intake_id="intake-m37-blocked",
        formula_gate_results=[
            FormulaInputGateResult(
                formula_id="PYME_001_ventas_totales",
                required_variables=["ventas_total", "dias_periodo"],
                available_variables=["ventas_total"],
                missing_variables=["dias_periodo"],
                status=FormulaInputGateStatus.MISSING_INPUTS,
            )
        ],
        evidence_gate_decisions=[
            EvidenceGateDecision(
                formula_id="PYME_001_ventas_totales",
                decision=EvidenceGateDecisionStatus.BLOCK_MISSING_INPUTS,
                missing_variables=["dias_periodo"],
            )
        ],
        core_result=DiagnosticCoreResult(
            case_id="case-m37-blocked",
            tenant_id="tenant-m37",
            status=DiagnosticCoreStatus.BLOCKED,
            formula_results=[],
            diagnostic_results=[],
            findings=[],
            missing_evidence=["dias_periodo"],
            blocked_reasons=["Missing required variables for execution."],
        ),
        output_dir=tmp_path,
    )

    assert bundle.operational_audit_result["status"] == "pending_data"
    assert "dias_periodo" in bundle.operational_audit_result["missing_evidence"]
    assert bundle.render_contract["next_questions"]
    assert bundle.execution_result["status"] == "BLOCKED"
    assert bundle.gate_verdict.verdict == "BLOCKED"
    assert bundle.delivery_package.status == "BLOCKED"
    assert bundle.owner_facing_report["status"] == "BLOCKED"
    assert bundle.owner_questions_bundle["questions"]
    assert any(
        item["reason"] == "missing_evidence" and item["missing_key"] == "dias_periodo"
        for item in bundle.owner_questions_bundle["questions"]
    )
    assert any(
        item["reason"] == "next_question" and item["question_text"] == "dias_periodo"
        for item in bundle.owner_questions_bundle["questions"]
    )
    assert any(
        item["reason"] == "blocked_message"
        and item["metadata"]["blocked_message"]
        == "Falta evidencia para avanzar al resultado operativo entregable."
        for item in bundle.owner_questions_bundle["questions"]
    )
    assert bundle.owner_facing_report["missing_evidence"] == ["dias_periodo"]
    assert bundle.render_contract["next_questions"] == [
        "¿Cuál es la cantidad de días del período analizado?",
        "dias_periodo",
        "El caso está bloqueado. ¿Podés aportar la evidencia o aclaración necesaria para destrabarlo?",
    ]
    assert bundle.render_contract["blocked_message"] == (
        "¿Cuál es la cantidad de días del período analizado?"
    )
    assert bundle.owner_facing_report["next_questions"] == bundle.render_contract["next_questions"]
    assert bundle.owner_facing_report["blocked_message"] == bundle.render_contract["blocked_message"]
    assert str(tmp_path / "owner_facing_report.json") in bundle.delivery_package.output_refs
    assert str(tmp_path / "owner_questions_bundle.json") in bundle.delivery_package.output_refs
    assert Path(bundle.output_refs[0]).exists()
    assert (tmp_path / "owner_facing_report.json").exists()
    assert (tmp_path / "owner_questions_bundle.json").exists()
    assert json.loads((tmp_path / "owner_facing_report.json").read_text(encoding="utf-8")) == (
        bundle.owner_facing_report
    )
    assert json.loads(
        (tmp_path / "owner_questions_bundle.json").read_text(encoding="utf-8")
    ) == bundle.owner_questions_bundle

    state = PymIAState(
        tenant_id="tenant-m37",
        chat_id="chat-1",
        conversation_id="conv-1",
    )
    updated = project_bridge_result_to_state(state, bundle)

    assert updated.phase == "BLOCKED"
    assert updated.gate_verdict == "BLOCKED"
    assert updated.delivery_status == "BLOCKED"
    assert updated.delivery_summary == bundle.owner_facing_report["summary"]
    assert updated.delivery_summary == "¿Cuál es la cantidad de días del período analizado?"
    assert updated.findings_count == 0
    assert updated.output_refs


def test_bridge_builds_sovereign_audit_render_delivery_and_state_when_ready(tmp_path):
    from pymia.audit_result.core_delivery_bridge import (
        build_core_audit_delivery_bundle,
        project_bridge_result_to_state,
    )

    bundle = build_core_audit_delivery_bundle(
        evidence=_sample_evidence(),
        case_id="case-m37-ready",
        intake_id="intake-m37-ready",
        formula_gate_results=[
            FormulaInputGateResult(
                formula_id="PYME_026_rotacion_inventario",
                required_variables=["ventas_total", "costos_total"],
                available_variables=["costos_total", "ventas_total"],
                missing_variables=[],
                status=FormulaInputGateStatus.READY,
            )
        ],
        evidence_gate_decisions=[
            EvidenceGateDecision(
                formula_id="PYME_026_rotacion_inventario",
                decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION,
                missing_variables=[],
            )
        ],
        core_result=DiagnosticCoreResult(
            case_id="case-m37-ready",
            tenant_id="tenant-m37",
            status=DiagnosticCoreStatus.PARTIAL,
            formula_results=[
                CoreFormulaResult(
                    formula_id="PYME_026_rotacion_inventario",
                    status="READY",
                    value=2.5,
                    source_refs=["sheet://ventas", "sheet://costos"],
                )
            ],
            diagnostic_results=[
                CoreDiagnosticResult(
                    pathology_code="INV_001",
                    status=CoreDiagnosticStatus.CANDIDATE,
                    formula_id="PYME_026_rotacion_inventario",
                    reason="Low inventory rotation signal.",
                    evidence_refs=["sheet://ventas", "sheet://costos"],
                )
            ],
            findings=[
                CoreFinding(
                    finding_id="finding-1",
                    pathology_code="INV_001",
                    formula_id="PYME_026_rotacion_inventario",
                    status="CANDIDATE",
                    summary="Inventory rotation below expected threshold.",
                    evidence_refs=["sheet://ventas", "sheet://costos"],
                )
            ],
            missing_evidence=[],
            blocked_reasons=[],
        ),
        output_dir=tmp_path,
    )

    assert bundle.operational_audit_result["status"] == "candidate"
    assert bundle.operational_audit_result["findings"]
    assert bundle.operational_audit_result["allowed_rendering"]["references"]
    assert bundle.render_contract["result_ref"] == bundle.operational_audit_result["result_id"]
    assert bundle.execution_result["status"] == "EXECUTED"
    assert bundle.gate_verdict.verdict == "PASS"
    assert bundle.delivery_package.status == "READY_TO_DELIVER"
    assert bundle.owner_facing_report["status"] == "DELIVERED_CANDIDATE"
    assert bundle.owner_questions_bundle["questions"] == []
    assert "confirm" not in bundle.owner_facing_report["summary"].lower()
    assert bundle.owner_facing_report["limit_warnings"][-1] == (
        "Estado candidato: el resultado sigue siendo no confirmado."
    )
    assert str(tmp_path / "owner_facing_report.json") in bundle.delivery_package.output_refs
    assert str(tmp_path / "owner_questions_bundle.json") in bundle.delivery_package.output_refs
    assert len(bundle.output_refs) >= 5
    for ref in bundle.output_refs:
        assert Path(ref).exists()

    state = PymIAState(
        tenant_id="tenant-m37",
        chat_id="chat-1",
        conversation_id="conv-1",
    )
    updated = project_bridge_result_to_state(state, bundle)

    assert updated.phase == "DELIVERED"
    assert updated.gate_verdict == "PASS"
    assert updated.delivery_status == "READY_TO_DELIVER"
    assert updated.delivery_summary == bundle.owner_facing_report["summary"]
    assert updated.findings_count == 1
    assert updated.output_refs == bundle.delivery_package.output_refs


def test_project_bridge_result_to_state_falls_back_to_delivery_package_summary_when_owner_summary_is_empty(
    tmp_path,
):
    from pymia.audit_result.core_delivery_bridge import (
        CoreAuditDeliveryBundle,
        build_core_audit_delivery_bundle,
        project_bridge_result_to_state,
    )

    bundle = build_core_audit_delivery_bundle(
        evidence=_sample_evidence(),
        case_id="case-m44-fallback",
        intake_id="intake-m44-fallback",
        formula_gate_results=[
            FormulaInputGateResult(
                formula_id="PYME_026_rotacion_inventario",
                required_variables=["ventas_total", "costos_total"],
                available_variables=["costos_total", "ventas_total"],
                missing_variables=[],
                status=FormulaInputGateStatus.READY,
            )
        ],
        evidence_gate_decisions=[
            EvidenceGateDecision(
                formula_id="PYME_026_rotacion_inventario",
                decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION,
                missing_variables=[],
            )
        ],
        core_result=DiagnosticCoreResult(
            case_id="case-m44-fallback",
            tenant_id="tenant-m37",
            status=DiagnosticCoreStatus.READY,
            formula_results=[],
            diagnostic_results=[],
            findings=[],
            missing_evidence=[],
            blocked_reasons=[],
        ),
        output_dir=tmp_path,
    )

    bundle_with_empty_owner_summary = CoreAuditDeliveryBundle(
        operational_audit_result=bundle.operational_audit_result,
        render_contract=bundle.render_contract,
        owner_facing_report={**bundle.owner_facing_report, "summary": ""},
        owner_questions_bundle=bundle.owner_questions_bundle,
        execution_result=bundle.execution_result,
        gate_verdict=bundle.gate_verdict,
        delivery_package=bundle.delivery_package,
        output_refs=bundle.output_refs,
    )

    state = PymIAState(
        tenant_id="tenant-m37",
        chat_id="chat-fallback",
        conversation_id="conv-fallback",
    )
    updated = project_bridge_result_to_state(state, bundle_with_empty_owner_summary)

    assert updated.delivery_summary == bundle.delivery_package.summary


def test_project_bridge_result_to_state_falls_back_to_delivery_package_summary_when_owner_summary_is_absent(
    tmp_path,
):
    from pymia.audit_result.core_delivery_bridge import (
        CoreAuditDeliveryBundle,
        build_core_audit_delivery_bundle,
        project_bridge_result_to_state,
    )

    bundle = build_core_audit_delivery_bundle(
        evidence=_sample_evidence(),
        case_id="case-m44-absent-summary",
        intake_id="intake-m44-absent-summary",
        formula_gate_results=[
            FormulaInputGateResult(
                formula_id="PYME_026_rotacion_inventario",
                required_variables=["ventas_total", "costos_total"],
                available_variables=["costos_total", "ventas_total"],
                missing_variables=[],
                status=FormulaInputGateStatus.READY,
            )
        ],
        evidence_gate_decisions=[
            EvidenceGateDecision(
                formula_id="PYME_026_rotacion_inventario",
                decision=EvidenceGateDecisionStatus.ALLOW_EXECUTION,
                missing_variables=[],
            )
        ],
        core_result=DiagnosticCoreResult(
            case_id="case-m44-absent-summary",
            tenant_id="tenant-m37",
            status=DiagnosticCoreStatus.READY,
            formula_results=[],
            diagnostic_results=[],
            findings=[],
            missing_evidence=[],
            blocked_reasons=[],
        ),
        output_dir=tmp_path,
    )

    owner_report_without_summary = dict(bundle.owner_facing_report)
    owner_report_without_summary.pop("summary", None)
    bundle_with_absent_owner_summary = CoreAuditDeliveryBundle(
        operational_audit_result=bundle.operational_audit_result,
        render_contract=bundle.render_contract,
        owner_facing_report=owner_report_without_summary,
        owner_questions_bundle=bundle.owner_questions_bundle,
        execution_result=bundle.execution_result,
        gate_verdict=bundle.gate_verdict,
        delivery_package=bundle.delivery_package,
        output_refs=bundle.output_refs,
    )

    state = PymIAState(
        tenant_id="tenant-m37",
        chat_id="chat-absent-summary",
        conversation_id="conv-absent-summary",
    )
    updated = project_bridge_result_to_state(state, bundle_with_absent_owner_summary)

    assert updated.delivery_summary == bundle.delivery_package.summary


def test_bridge_module_does_not_import_telegram_or_runtime_ast():
    source = Path("pymia/audit_result/core_delivery_bridge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.telegram",
        "pymia.telegram_",
        "pymia.smartpyme.runtime_bridge",
        "pymia.orchestration.graph",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)


def test_payload_producer_does_not_execute_blocked_formulas_and_keeps_missing_inputs():
    from pymia.audit_result.core_delivery_bridge import (
        build_core_delivery_bridge_payload_from_structured_evidence,
    )

    payload = build_core_delivery_bridge_payload_from_structured_evidence(
        evidence=_sample_evidence(),
        case_id="case-payload-blocked",
        intake_id="intake-payload-blocked",
        formula_ids=["REN_001_margen_neto_real"],
        hypothesis_codes=["REN_001"],
    )

    assert payload["formula_ids"] == ["REN_001_margen_neto_real"]
    assert payload["formula_gate_results"][0]["status"] == "MISSING_INPUTS"
    assert payload["formula_gate_results"][0]["missing_variables"] == ["taxes"]
    assert payload["evidence_gate_decisions"][0]["decision"] == "BLOCK_MISSING_INPUTS"
    assert payload["diagnostic_core_result"]["formula_results"] == []
    assert payload["diagnostic_core_result"]["missing_evidence"] == ["taxes"]
