from __future__ import annotations

from pathlib import Path

from pymia.orchestration.state import PymIAState
from pymia.orchestration.state_storage import find_conversations_by_tenant, load_state, save_state


def _context(owner_message: str, report_ref: str, next_step: str) -> dict:
    return {
        "assisted_case": {
            "owner_message": owner_message,
            "evidence_refs": ["ventas_costos_margen.xlsx"],
            "finding_codes": ["LOW_MARGIN", "PRODUCT_WITHOUT_COST"],
            "minimal_report_ref": report_ref,
            "next_step": next_step,
            "case_status": "DELIVERY_READY",
        }
    }


def test_m30_case_continuity_acceptance(tmp_path: Path) -> None:
    tenant_a = "tenant_a_case_continuity"
    tenant_b = "tenant_b_case_continuity"
    chat_a = "chat_case_a"
    chat_b = "chat_case_b"

    state_a1 = PymIAState(
        tenant_id=tenant_a,
        chat_id=chat_a,
        conversation_id="case_a_001",
        phase="DELIVERY_READY",
        last_user_message="Mi margen es dudoso y tengo un Excel con ventas y costos.",
        progressive_context=_context(
            "Mi margen es dudoso y tengo un Excel con ventas y costos.",
            "reports/case_a/minimal_delivery.md",
            "Revisar margen bajo y completar costos faltantes.",
        ),
        evidence_ids=["evidence_a_excel"],
        delivery_summary="Reporte minimo generado.",
        output_refs=["reports/case_a/minimal_delivery.md"],
        findings_count=2,
    )
    state_a1.add_decision("case initialized with evidence findings and report")
    save_state(tenant_a, chat_a, state_a1, tmp_path)

    state_b1 = PymIAState(
        tenant_id=tenant_b,
        chat_id=chat_b,
        conversation_id="case_b_001",
        phase="WAITING_FOR_EVIDENCE",
        last_user_message="Quiero revisar proveedores duplicados.",
        progressive_context=_context(
            "Quiero revisar proveedores duplicados.",
            "reports/case_b/pending.md",
            "Subir Excel de proveedores.",
        ),
        evidence_ids=[],
        output_refs=[],
        findings_count=0,
    )
    state_b1.add_decision("independent tenant case initialized")
    save_state(tenant_b, chat_b, state_b1, tmp_path)

    loaded_a1 = load_state(tenant_a, chat_a, tmp_path)
    loaded_b1 = load_state(tenant_b, chat_b, tmp_path)

    assert loaded_a1 is not None
    assert loaded_b1 is not None
    assert loaded_a1.progressive_context != loaded_b1.progressive_context
    assert loaded_a1.output_refs == ["reports/case_a/minimal_delivery.md"]
    assert loaded_a1.findings_count == 2
    assert loaded_b1.output_refs == []
    assert loaded_b1.findings_count == 0

    previous = dict(loaded_a1.progressive_context["assisted_case"])

    state_a2 = PymIAState(
        tenant_id=tenant_a,
        chat_id=chat_a,
        conversation_id="case_a_001",
        phase="DELIVERED",
        last_user_message="Quiero seguir con el proximo paso.",
        progressive_context={
            "assisted_case": {
                **previous,
                "last_follow_up": "Quiero seguir con el proximo paso.",
                "case_status": "DELIVERED",
            }
        },
        evidence_ids=loaded_a1.evidence_ids,
        delivery_summary=loaded_a1.delivery_summary,
        output_refs=loaded_a1.output_refs,
        findings_count=loaded_a1.findings_count,
    )
    state_a2.add_decision("tenant returned and case context continued")
    save_state(tenant_a, chat_a, state_a2, tmp_path)

    loaded_a2 = load_state(tenant_a, chat_a, tmp_path)
    assert loaded_a2 is not None
    continued = loaded_a2.progressive_context["assisted_case"]

    assert continued["owner_message"] == previous["owner_message"]
    assert continued["evidence_refs"] == previous["evidence_refs"]
    assert continued["finding_codes"] == previous["finding_codes"]
    assert continued["minimal_report_ref"] == previous["minimal_report_ref"]
    assert continued["next_step"] == previous["next_step"]
    assert continued["last_follow_up"] == "Quiero seguir con el proximo paso."
    assert continued["case_status"] == "DELIVERED"

    convs_a = find_conversations_by_tenant(tenant_a, tmp_path)
    convs_b = find_conversations_by_tenant(tenant_b, tmp_path)

    assert len(convs_a) == 1
    assert len(convs_b) == 1
    assert convs_a[0]["chat_id"] == chat_a
    assert convs_b[0]["chat_id"] == chat_b
    assert convs_a[0]["last_phase"] == "DELIVERED"
    assert convs_b[0]["last_phase"] == "WAITING_FOR_EVIDENCE"
