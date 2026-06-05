from __future__ import annotations

from pymia.smartpyme.evidence_gate import (
    SUFFICIENCY_READY,
    SUGGESTED_READY_FOR_ANALYSIS,
    evaluate_evidence_sufficiency,
)
from pymia.smartpyme.intake import INTAKE_NEEDS_EVIDENCE, create_intake_record

OWNER_MESSAGE = "Mi margen es dudoso y tengo un Excel con ventas y costos."
EXCEL_FIXTURE_REF = "tests/fixtures/smartpyme/ventas_costos_margen.xlsx"


def _evidence_for_request(*, tenant_id: str, intake_id: str, request) -> dict:
    metadata = {"owner_message": OWNER_MESSAGE, "fixture_ref": EXCEL_FIXTURE_REF}
    if request.required_fields:
        metadata["fields"] = list(request.required_fields)
        
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "evidence_id": f"m27_{request.request_id}",
        "request_id": request.request_id,
        "evidence_type": request.evidence_type,
        "source_kind": "uploaded_file",
        "source_ref": EXCEL_FIXTURE_REF,
        "original_filename": "ventas_costos_margen.xlsx",
        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size_bytes": 1024,
        "content_hash": "m27-fixture-hash",
        "status": "RECEIVED",
        "received_at": "2026-06-04T00:00:00+00:00",
        "notes": [],
        "metadata": metadata,
    }


def test_m27_owner_semantics_plus_margin_excel_reaches_ready_case_state() -> None:
    intake = create_intake_record(tenant_id="tenant_m27", raw_text=OWNER_MESSAGE)

    assert intake.intake_state == INTAKE_NEEDS_EVIDENCE
    assert intake.raw_input == OWNER_MESSAGE

    margin_request = next(
        request
        for request in intake.evidence_requests
        if request.evidence_type == "excel_ventas_costos"
    )
    assert margin_request.blocks_analysis is True
    assert margin_request.enables_classification == "excel_diagnostic"
    assert {"producto", "venta_neta", "costo_directo"}.issubset(
        set(margin_request.required_fields)
    )

    evidence_records = [
        _evidence_for_request(
            tenant_id=intake.tenant_id,
            intake_id=intake.intake_id,
            request=request,
        )
        for request in intake.evidence_requests
        if request.blocks_analysis
    ]
    gate = evaluate_evidence_sufficiency(intake.to_dict(), evidence_records)

    assert gate.status == SUFFICIENCY_READY
    assert gate.suggested_next_state == SUGGESTED_READY_FOR_ANALYSIS
    assert f"m27_{margin_request.request_id}" in gate.matched_evidence_ids

    structured_case = {
        "tenant_id": intake.tenant_id,
        "owner_message": intake.raw_input,
        "excel_fixture": EXCEL_FIXTURE_REF,
        "classification": margin_request.enables_classification,
        "evidence_gate_status": gate.status,
        "case_status": gate.suggested_next_state,
        "not_product_claim": True,
    }

    assert structured_case["classification"] == "excel_diagnostic"
    assert structured_case["case_status"] == SUGGESTED_READY_FOR_ANALYSIS
    assert structured_case["not_product_claim"] is True
