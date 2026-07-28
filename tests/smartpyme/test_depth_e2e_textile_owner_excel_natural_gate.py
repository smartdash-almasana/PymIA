from pathlib import Path

from pymia.smartpyme.post_ficha_evidence_gate import apply_post_ficha_evidence_turn


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXTILE_FIXTURE = REPO_ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def _textile_margin_context() -> dict:
    return {
        "post_ficha_routing": {
            "intake_id": "intake_textile_margin_natural_gate",
            "evidence_requests": [
                {
                    "request_id": "req_textile_sales_costs",
                    "evidence_type": "sales_records",
                    "description": "Excel textil real de ventas/costos aportado por el dueño",
                    "reason": "Evaluar si existe evidencia literal suficiente para análisis de margen",
                    "status": "REQUESTED",
                    "hypothesis_id": "hyp_textile_margin",
                    "blocks_analysis": True,
                    "required_fields": ["periodo", "venta_neta", "costo_directo"],
                    "enables_classification": "excel_diagnostic",
                }
            ],
        }
    }


def test_textile_owner_excel_natural_gate_requires_owner_questions_without_manual_metadata() -> None:
    assert TEXTILE_FIXTURE.exists()

    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="tenant_textile_natural_gate",
        message_text=f"EVIDENCE::uploaded_file::sales_records::{TEXTILE_FIXTURE}",
        previous_context=None,
        updated_context=_textile_margin_context(),
    )

    record = out["evidence_records"][0]
    metadata = record["metadata"]
    readiness = out["post_ficha_readiness"]
    request = out["post_ficha_routing"]["evidence_requests"][0]

    assert request["status"] == "RECEIVED"
    assert readiness["readiness_state"] == "NEEDS_EVIDENCE"
    assert readiness["ready_for_analysis"] is False
    assert readiness["received_count"] == 1
    assert readiness["satisfied_count"] == 0
    assert readiness["missing_evidence_types"] == ["sales_records"]

    assert metadata["owner_questions_required"] is True
    assert metadata["owner_questions"]
    assert "venta_neta" in metadata["ambiguous_fields"]

    resolution = metadata["field_resolution"]
    assert resolution["periodo"]["covered"] is True
    assert resolution["periodo"]["confidence"] == "high"
    assert resolution["venta_neta"]["covered"] is False
    assert resolution["venta_neta"]["confidence"] == "medium"
    assert resolution["costo_directo"]["covered"] is False
    assert resolution["costo_directo"]["confidence"] in {"medium", "low"}

    assert "periodo" in metadata["fields"]
    assert "venta_neta" not in metadata["fields"]
    assert "costo_directo" not in metadata["fields"]
