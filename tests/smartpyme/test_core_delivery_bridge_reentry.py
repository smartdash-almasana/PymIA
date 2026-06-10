from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import pytest

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.contracts.owner_questions import OwnerQuestion, OwnerQuestionsBundle
from pymia.diagnostic_core.models import (
    CoreDiagnosticResult,
    CoreDiagnosticStatus,
    CoreFinding,
    CoreFormulaResult,
    DiagnosticCoreResult,
    DiagnosticCoreStatus,
    EvidenceGateDecision,
    EvidenceGateDecisionStatus,
    FormulaInputGateResult,
    FormulaInputGateStatus,
)


def _sample_evidence() -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant-reentry",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="tenant_reentry.xlsx",
        computed_variables={
            "ventas_total": 120000.0,
            "costos_total": 60000.0,
        },
        metadata={},
    )


def _build_delivery_bundle(tmp_path):
    from pymia.audit_result.core_delivery_bridge import build_core_audit_delivery_bundle

    return build_core_audit_delivery_bundle(
        evidence=_sample_evidence(),
        case_id="case-reentry",
        intake_id="intake-reentry",
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
            case_id="case-reentry",
            tenant_id="tenant-reentry",
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


def _build_questions_bundle() -> OwnerQuestionsBundle:
    return OwnerQuestionsBundle(
        bundle_id="questions-reentry",
        questions=[
            OwnerQuestion(
                question_id="q_dias_periodo",
                question_text="¿Cuántos días tiene el período analizado?",
                reason="missing_evidence",
                missing_key="dias_periodo",
                source_ref="operational_audit_result://missing_evidence/0",
                expected_answer_type="number",
                metadata={"missing_input_type": "STRUCTURAL_INPUT"},
            ),
            OwnerQuestion(
                question_id="q_evidencia_ventas",
                question_text="¿Hay evidencia de ventas que no se registró?",
                reason="blocked_message",
                missing_key="evidencia_ventas",
                source_ref="render_contract://blocked_message",
                expected_answer_type="text",
            ),
        ],
    )


def test_project_owner_answers_into_delivery_bundle_happy_path(tmp_path) -> None:
    from pymia.audit_result.core_delivery_bridge import (
        project_owner_answers_into_delivery_bundle,
    )

    delivery_bundle = _build_delivery_bundle(tmp_path)
    original_render_contract = deepcopy(delivery_bundle.render_contract)
    original_owner_report = deepcopy(delivery_bundle.owner_facing_report)
    original_execution_result = deepcopy(delivery_bundle.execution_result)
    original_findings = deepcopy(delivery_bundle.operational_audit_result["findings"])
    questions_bundle = _build_questions_bundle()

    projected = project_owner_answers_into_delivery_bundle(
        delivery_bundle=delivery_bundle,
        questions_bundle=questions_bundle,
        answers_payload=[
            {"question_id": "q_dias_periodo", "answer_text": "30"},
            {
                "question_id": "q_evidencia_ventas",
                "answer_text": "Sí, hay ventas manuales no registradas",
            },
        ],
        source_ref="sandbox://reentry",
        tenant_id="tenant-reentry",
    )

    assert projected is not delivery_bundle
    assert projected.render_contract is not delivery_bundle.render_contract
    assert projected.owner_facing_report is not delivery_bundle.owner_facing_report
    assert projected.execution_result is not delivery_bundle.execution_result
    assert projected.delivery_package is not delivery_bundle.delivery_package
    assert projected.operational_audit_result["findings"] == original_findings
    assert projected.operational_audit_result["findings"] == delivery_bundle.operational_audit_result["findings"]
    assert projected.render_contract["next_questions"] == [
        "¿Hay evidencia de ventas que no se registró?"
    ]
    assert (
        projected.render_contract["blocked_message"]
        == "¿Hay evidencia de ventas que no se registró?"
    )
    assert projected.owner_facing_report["next_questions"] == [
        "¿Hay evidencia de ventas que no se registró?"
    ]
    assert (
        projected.owner_facing_report["blocked_message"]
        == "¿Hay evidencia de ventas que no se registró?"
    )
    assert projected.owner_facing_report["summary"] == "¿Hay evidencia de ventas que no se registró?"
    assert projected.execution_result["raw_result"]["render_contract"] == projected.render_contract
    assert projected.owner_questions_bundle == questions_bundle.model_dump(mode="json")

    assert delivery_bundle.render_contract == original_render_contract
    assert delivery_bundle.owner_facing_report == original_owner_report
    assert delivery_bundle.execution_result == original_execution_result


def test_project_owner_answers_into_delivery_bundle_acknowledges_declared_answer_without_evidence_promotion(
    tmp_path,
) -> None:
    from pymia.audit_result.core_delivery_bridge import (
        project_owner_answers_into_delivery_bundle,
    )

    delivery_bundle = _build_delivery_bundle(tmp_path)
    questions_bundle = _build_questions_bundle()

    projected = project_owner_answers_into_delivery_bundle(
        delivery_bundle=delivery_bundle,
        questions_bundle=questions_bundle,
        answers_payload=[{"question_id": "q_dias_periodo", "answer_text": "30"}],
        source_ref="sandbox://reentry",
        tenant_id="tenant-reentry",
    )

    acknowledgement = (
        "La respuesta queda registrada como declaración del dueño, no como evidencia validada."
    )
    warning = (
        "Advertencia trazable: la respuesta queda como declaración del dueño y no como evidencia validada."
    )
    structural_message = (
        "Tu respuesta fue considerada, pero todavía falta evidencia o dato estructurado "
        "para resolver este punto."
    )
    structural_warning = (
        "Advertencia trazable: la respuesta del dueño fue considerada, pero no reemplaza "
        "evidencia estructurada faltante."
    )

    assert acknowledgement in projected.render_contract["next_steps"]
    assert acknowledgement in projected.owner_facing_report["next_steps"]
    assert structural_message in projected.render_contract["next_steps"]
    assert structural_message in projected.owner_facing_report["next_steps"]
    render_warnings = projected.render_contract.get("limit_warnings") or projected.render_contract.get("forbidden_inferences") or []
    assert warning in render_warnings
    assert structural_warning in render_warnings
    assert warning in projected.owner_facing_report["limit_warnings"]
    assert structural_warning in projected.owner_facing_report["limit_warnings"]
    assert projected.delivery_package.status == delivery_bundle.delivery_package.status
    assert projected.operational_audit_result == delivery_bundle.operational_audit_result
    assert projected.operational_audit_result["findings"] == delivery_bundle.operational_audit_result["findings"]
    assert "evidence_candidate" not in str(projected.execution_result)


def test_project_owner_answers_into_delivery_bundle_fail_closed(tmp_path) -> None:
    from pymia.audit_result.core_delivery_bridge import (
        project_owner_answers_into_delivery_bundle,
    )

    with pytest.raises(ValueError) as exc:
        project_owner_answers_into_delivery_bundle(
            delivery_bundle=_build_delivery_bundle(tmp_path),
            questions_bundle=_build_questions_bundle(),
            answers_payload=[{"question_id": "q_missing", "answer_text": "30"}],
            source_ref="sandbox://reentry",
            tenant_id="tenant-reentry",
        )

    assert "unknown question_id" in str(exc.value)


def test_bridge_reentry_does_not_import_sandbox_formatter() -> None:
    source = Path("pymia/audit_result/core_delivery_bridge.py").read_text(encoding="utf-8")
    lowered = source.lower()

    assert "owner_answer_replay_formatter" not in lowered


def test_bridge_reentry_has_no_runtime_imports() -> None:
    source = Path("pymia/audit_result/core_delivery_bridge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.orchestration.graph",
        "pymia.orchestration.state",
        "pymia.telegram",
        "pymia.telegram_",
        "llm",
        "runtime",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)
