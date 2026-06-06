from __future__ import annotations

from pathlib import Path

from pymia.mcp_server.first_clinical_interview import invoke_first_clinical_interview
from pymia.smartpyme.intake import INTAKE_NEEDS_EVIDENCE, create_intake_record
from pymia.smartpyme.post_ficha_evidence_gate import apply_post_ficha_evidence_turn


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXTILE_FIXTURE = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"

TENANT_ID = "tenant_m27_a_textile"
TURN_1_TEXT = "Estoy confundido con la rentabilidad."
TURN_2_TEXT = (
    "Somos una fábrica textil. Fabricamos prendas y también revendemos algunos "
    "productos. Vendemos por local y WhatsApp. Somos 8 personas."
)


def test_m27_a_textile_case_understanding_natural_flow() -> None:
    assert TEXTILE_FIXTURE.exists()

    turn_1 = invoke_first_clinical_interview(
        tenant_id=TENANT_ID,
        channel="test",
        text=TURN_1_TEXT,
        previous_progressive_context=None,
    )

    assert turn_1["status"] == "ok"
    assert turn_1["estado_conversacional"] == "encuadre_taxonomico_inicial"

    turn_2 = invoke_first_clinical_interview(
        tenant_id=TENANT_ID,
        channel="test",
        text=TURN_2_TEXT,
        previous_progressive_context=turn_1["progressive_context"],
    )

    assert turn_2["status"] == "ok"
    assert turn_2["estado_conversacional"] == "esperando_documentacion"
    assert turn_2["progressive_context"]["business_identity"]["taxonomy_phase"] == "FASE_0_IDENTIDAD"
    assert turn_2["laboratorio"]["evidencia_requerida"]

    intake = create_intake_record(
        tenant_id=TENANT_ID,
        raw_text=TURN_1_TEXT,
    )

    assert intake.intake_state == INTAKE_NEEDS_EVIDENCE

    margin_request = next(
        request
        for request in intake.evidence_requests
        if request.evidence_type == "excel_ventas_costos"
    )
    assert margin_request.enables_classification == "excel_diagnostic"

    context = {
        "post_ficha_routing": {
            "intake_id": intake.intake_id,
            "evidence_requests": [
                {
                    **margin_request.to_dict(),
                    "required_fields": ["periodo", "venta_neta", "costo_directo"],
                }
            ],
        }
    }

    out, _ = apply_post_ficha_evidence_turn(
        tenant_id=TENANT_ID,
        message_text=f"EVIDENCE::uploaded_file::excel_ventas_costos::{TEXTILE_FIXTURE}",
        previous_context=None,
        updated_context=context,
    )

    metadata = out["evidence_records"][0]["metadata"]
    readiness = out["post_ficha_readiness"]
    analysis = out["analysis_readiness"]
    request = out["post_ficha_routing"]["evidence_requests"][0]

    assert readiness["readiness_state"] == "NEEDS_EVIDENCE"
    assert readiness["ready_for_analysis"] is False
    assert metadata["owner_questions_required"] is True
    assert metadata["owner_questions"]
    assert "venta_neta" in metadata["ambiguous_fields"]
    assert "field_resolution" in metadata

    resolution = metadata["field_resolution"]
    assert resolution["periodo"]["covered"] is True
    assert resolution["periodo"]["confidence"] == "high"
    assert resolution["venta_neta"]["covered"] is False
    assert resolution["venta_neta"]["confidence"] == "medium"
    assert resolution["costo_directo"]["covered"] is False
    assert "periodo" in metadata["fields"]
    assert "venta_neta" not in metadata["fields"]
    assert "costo_directo" not in metadata["fields"]

    assert request["status"] == "RECEIVED"
    assert analysis["status"] == "NEEDS_EVIDENCE"
    assert analysis["can_execute"] is False
