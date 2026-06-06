from __future__ import annotations

from pathlib import Path

from pymia.mcp_server.first_clinical_interview import invoke_first_clinical_interview
from pymia.narrative.minimal_delivery_report import render_minimal_delivery_report
from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import (
    find_conversations_by_tenant,
    load_state,
    save_state,
)
from pymia.smartpyme.finding_projection import ActionableFinding
from pymia.smartpyme.intake import INTAKE_NEEDS_EVIDENCE, create_intake_record
from pymia.smartpyme.post_ficha_evidence_gate import apply_post_ficha_evidence_turn
from tools.document_ingestion import build_structured_evidence_from_xlsx


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXTILE_FIXTURE = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"

TENANT_ID = "depth-textil-001"
CASE_ID = "depth-case-textil-001"
CHAT_ID = CASE_ID
TURN_1_TEXT = "Estoy confundido con la rentabilidad."
TURN_2_TEXT = (
    "Somos una fábrica textil. Fabricamos prendas y también revendemos algunos "
    "productos. Vendemos por local y WhatsApp. Somos 8 personas."
)
FORBIDDEN_FINAL_DIAGNOSIS = (
    "gana plata",
    "no gana plata",
    "ganando plata",
    "perdiendo plata",
    "rentabilidad final",
    "diagnóstico financiero final",
)
FORBIDDEN_PRODUCT_CLAIMS = (
    "producto digital",
    "software as a service",
    "saas",
    "plataforma",
    "mvp",
)


def _evidence_metadata_for(evidence_type: str) -> dict[str, list[str]]:
    metadata_by_type = {
        "excel_ventas_costos": {"fields": ["producto", "venta_neta", "costo_directo"]},
        "ventas_del_periodo": {"fields": ["periodo", "ventas"]},
        "costos_directos": {"fields": ["periodo", "costos"]},
    }
    return metadata_by_type[evidence_type]


def _assert_no_unsupported_claims(text: str) -> None:
    lowered = text.lower()
    for forbidden in FORBIDDEN_FINAL_DIAGNOSIS:
        assert forbidden not in lowered
    for forbidden in FORBIDDEN_PRODUCT_CLAIMS:
        assert forbidden not in lowered


def _finding_models(rows: list[dict]) -> list[ActionableFinding]:
    return [ActionableFinding(**row) for row in rows]


def _assisted_case_context(
    *,
    intake_id: str,
    owner_message: str,
    evidence_refs: list[str],
    report_ref: str,
    findings: list[dict],
    next_step: str,
    gate_status: str,
    delivery_summary: str,
) -> dict:
    return {
        "assisted_case": {
            "case_id": CASE_ID,
            "intake_id": intake_id,
            "owner_message": owner_message,
            "evidence_refs": list(evidence_refs),
            "finding_codes": [row["metric"] for row in findings],
            "minimal_report_ref": report_ref,
            "next_step": next_step,
            "case_status": "DELIVERY_READY",
            "gate_status": gate_status,
            "delivery_summary": delivery_summary,
        }
    }


def test_depth_e2e_textile_owner_excel_flow(tmp_path: Path) -> None:
    assert TEXTILE_FIXTURE.exists(), f"Fixture inexistente: {TEXTILE_FIXTURE}"

    turn_1 = invoke_first_clinical_interview(
        tenant_id=TENANT_ID,
        channel="test",
        text=TURN_1_TEXT,
        previous_progressive_context=None,
    )

    assert turn_1["status"] == "ok"
    assert turn_1["estado_conversacional"] == "encuadre_taxonomico_inicial"
    assert turn_1["anamnesis"]["hipotesis_iniciales"] == []
    assert turn_1["laboratorio"]["evidencia_requerida"] == []
    assert turn_1["progressive_context"]["business_identity"]["taxonomy_phase"] is None
    assert "comercio" in turn_1["message"].lower()
    assert "excel" not in turn_1["message"].lower()
    _assert_no_unsupported_claims(turn_1["message"])

    turn_2 = invoke_first_clinical_interview(
        tenant_id=TENANT_ID,
        channel="test",
        text=TURN_2_TEXT,
        previous_progressive_context=turn_1["progressive_context"],
    )

    assert turn_2["status"] == "ok"
    assert turn_2["estado_conversacional"] != "encuadre_taxonomico_inicial"
    assert turn_2["progressive_context"]["business_identity"]["taxonomy_phase"] == "FASE_0_IDENTIDAD"
    assert turn_2["progressive_context"]["business_identity"]["industry_hint"] is not None
    assert "incertidumbre de rentabilidad" in turn_2["progressive_context"]["symptom_summary"]
    assert turn_2["laboratorio"]["evidencia_requerida"]
    assert any(
        "venta" in item.lower() or "costo" in item.lower()
        for item in turn_2["laboratorio"]["evidencia_requerida"]
    )
    _assert_no_unsupported_claims(turn_2["message"])

    intake = create_intake_record(
        tenant_id=TENANT_ID,
        raw_text=TURN_1_TEXT,
    )
    assert intake.intake_state == INTAKE_NEEDS_EVIDENCE

    blocking_requests = [request for request in intake.evidence_requests if request.blocks_analysis]
    blocking_types = [request.evidence_type for request in blocking_requests]
    assert blocking_types[:3] == ["excel_ventas_costos", "ventas_del_periodo", "costos_directos"]

    evidence = build_structured_evidence_from_xlsx(
        excel_path=TEXTILE_FIXTURE,
        tenant_id=TENANT_ID,
    )
    assert evidence.file_name == TEXTILE_FIXTURE.name
    assert evidence.tables
    assert evidence.computed_variables
    assert evidence.metadata["sheet_reports"]

    context: dict = {
        "post_ficha_routing": {
            "intake_id": intake.intake_id,
            "evidence_requests": [request.to_dict() for request in intake.evidence_requests],
        }
    }
    previous_context: dict | None = None

    for evidence_type in ("excel_ventas_costos", "ventas_del_periodo", "costos_directos"):
        context, _reply = apply_post_ficha_evidence_turn(
            tenant_id=TENANT_ID,
            message_text=f"EVIDENCE::uploaded_file::{evidence_type}::{TEXTILE_FIXTURE}",
            previous_context=previous_context,
            updated_context=context,
            evidence_metadata=_evidence_metadata_for(evidence_type),
        )
        previous_context = context

    readiness = context["post_ficha_readiness"]
    analysis = context["analysis_readiness"]
    candidate = context["runtime_execution_candidate"]
    execution = context["microservice_execution_result"]
    actionable_rows = context["actionable_findings"]

    assert readiness["readiness_state"] == "READY_FOR_ANALYSIS"
    assert readiness["ready_for_analysis"] is True
    assert readiness["missing_evidence_types"] == []
    assert readiness["requested_count"] == 3
    assert readiness["received_count"] == 3
    assert readiness["satisfied_count"] == 3

    assert analysis["tenant_id"] == TENANT_ID
    assert analysis["intake_id"] == intake.intake_id
    assert analysis["status"] == "READY_FOR_ANALYSIS"
    assert analysis["runtime_classification"] == "excel_diagnostic"
    assert analysis["matched_evidence_ids"]

    assert candidate["status"] == "READY_TO_EXECUTE"
    assert candidate["can_dispatch"] is True
    assert candidate["runtime_classification"] == "excel_diagnostic"
    assert candidate["microservice_name"] == "excel_diagnostic_worker"

    assert execution["status"] == "EXECUTED"
    assert execution["findings_count"] >= 1
    assert actionable_rows
    assert context["minimal_business_report"]["status"] == "HAS_FINDINGS"

    findings = _finding_models(actionable_rows)
    report_text = render_minimal_delivery_report(
        tenant_id=TENANT_ID,
        case_id=CASE_ID,
        owner_message=TURN_1_TEXT,
        evidence_refs=[str(TEXTILE_FIXTURE)],
        findings=findings,
        include_trace_ids=False,
    )

    assert "## Problema declarado" in report_text
    assert TURN_1_TEXT in report_text
    assert "## Evidencia usada" in report_text
    assert str(TEXTILE_FIXTURE) in report_text
    assert "## Hallazgos principales" in report_text
    assert "## Límites del análisis" in report_text
    assert "filas duplicadas" in report_text.lower() or "margen" in report_text.lower()
    _assert_no_unsupported_claims(report_text)

    report_path = tmp_path / "reports" / CASE_ID / "minimal_delivery.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")

    delivery_summary = context["minimal_business_report"]["summary"]
    next_step = findings[0].recommendation
    progressive_context = _assisted_case_context(
        intake_id=intake.intake_id,
        owner_message=TURN_1_TEXT,
        evidence_refs=[str(TEXTILE_FIXTURE)],
        report_ref=str(report_path),
        findings=actionable_rows,
        next_step=next_step,
        gate_status=analysis["status"],
        delivery_summary=delivery_summary,
    )

    state_ready = PymIAState(
        tenant_id=TENANT_ID,
        chat_id=CHAT_ID,
        conversation_id=CASE_ID,
        phase="DELIVERY_READY",
        last_user_message=TURN_2_TEXT,
        progressive_context=progressive_context,
        intake_id=intake.intake_id,
        evidence_ids=analysis["matched_evidence_ids"],
        sufficiency_status=readiness["readiness_state"],
        readiness_status=analysis["status"],
        runtime_candidate_status=candidate["status"],
        execution_status=execution["status"],
        delivery_status="READY_TO_DELIVER",
        delivery_summary=delivery_summary,
        output_refs=[str(report_path)],
        findings_count=len(findings),
        latest_evidence_path=TEXTILE_FIXTURE,
    )
    state_ready.add_decision("depth_e2e_textile_flow_ready_for_delivery")
    save_state(TENANT_ID, CHAT_ID, state_ready, tmp_path)

    loaded_ready = load_state(TENANT_ID, CHAT_ID, tmp_path)
    assert loaded_ready is not None
    assert loaded_ready.tenant_id == TENANT_ID
    assert loaded_ready.chat_id == CHAT_ID
    assert loaded_ready.conversation_id == CASE_ID
    assert loaded_ready.progressive_context["assisted_case"]["case_id"] == CASE_ID
    assert loaded_ready.progressive_context["assisted_case"]["owner_message"] == TURN_1_TEXT
    assert loaded_ready.progressive_context["assisted_case"]["evidence_refs"] == [str(TEXTILE_FIXTURE)]
    assert loaded_ready.progressive_context["assisted_case"]["minimal_report_ref"] == str(report_path)
    assert loaded_ready.progressive_context["assisted_case"]["next_step"] == next_step
    assert loaded_ready.progressive_context["assisted_case"]["delivery_summary"] == delivery_summary
    assert loaded_ready.evidence_ids == analysis["matched_evidence_ids"]
    assert loaded_ready.output_refs == [str(report_path)]
    assert loaded_ready.findings_count == len(findings)

    state_delivered = PymIAState(
        tenant_id=TENANT_ID,
        chat_id=CHAT_ID,
        conversation_id=CASE_ID,
        phase="DELIVERED",
        last_user_message="Quiero seguir con el próximo paso.",
        progressive_context={
            "assisted_case": {
                **loaded_ready.progressive_context["assisted_case"],
                "case_status": "DELIVERED",
                "last_follow_up": "Quiero seguir con el próximo paso.",
            }
        },
        intake_id=loaded_ready.intake_id,
        evidence_ids=loaded_ready.evidence_ids,
        sufficiency_status=loaded_ready.sufficiency_status,
        readiness_status=loaded_ready.readiness_status,
        runtime_candidate_status=loaded_ready.runtime_candidate_status,
        execution_status=loaded_ready.execution_status,
        delivery_status="DELIVERED",
        delivery_summary=loaded_ready.delivery_summary,
        output_refs=loaded_ready.output_refs,
        findings_count=loaded_ready.findings_count,
        latest_evidence_path=loaded_ready.latest_evidence_path,
    )
    state_delivered.add_decision("depth_e2e_textile_flow_delivered_and_continued")
    save_state(TENANT_ID, CHAT_ID, state_delivered, tmp_path)

    loaded_delivered = load_state(TENANT_ID, CHAT_ID, tmp_path)
    assert loaded_delivered is not None
    assert loaded_delivered.phase == "DELIVERED"
    assert loaded_delivered.progressive_context["assisted_case"]["case_id"] == CASE_ID
    assert loaded_delivered.progressive_context["assisted_case"]["evidence_refs"] == [str(TEXTILE_FIXTURE)]
    assert loaded_delivered.progressive_context["assisted_case"]["last_follow_up"] == "Quiero seguir con el próximo paso."
    assert loaded_delivered.progressive_context["assisted_case"]["case_status"] == "DELIVERED"

    conversations = find_conversations_by_tenant(TENANT_ID, tmp_path)
    assert len(conversations) == 1
    assert conversations[0]["conversation_id"] == CASE_ID
    assert conversations[0]["chat_id"] == CHAT_ID
    assert conversations[0]["last_phase"] == "DELIVERED"
    assert conversations[0]["evidence_count"] == 3
