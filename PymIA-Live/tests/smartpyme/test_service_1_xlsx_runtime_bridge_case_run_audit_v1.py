from __future__ import annotations

from pymia.smartpyme.service_1_xlsx_runtime_bridge_v1 import (
    STATUS_BRIDGE_BLOCKED,
    STATUS_BRIDGE_NEXT_OWNER_QUESTION,
    STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1,
)


def _case_payload() -> dict[str, object]:
    return {
        "case_id": "case:s1:audit:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:audit:001",
        "run_id": "run:s1:audit:001",
        "owner_ref": "owner:pyme:001",
        "source_file_ref": "audit/rentabilidad.xlsx",
        "raw_owner_narrative": "No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        "business_period_reference": "2026-06",
        "declared_data_sources": ["rentabilidad.xlsx"],
        "column_meaning_confirmations": [
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
        "available_data_fields": ["precio", "costo", "cantidad"],
        "input_values": {"precio": 100, "costo": 60, "cantidad": 10},
    }


def test_case_run_audit_happy_path_reaches_package_candidate() -> None:
    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=_case_payload(),
        metadata={"audit_id": "SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1"},
    )

    assert result.status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY
    assert result.entrypoint_status == "DELIVERY_PACKAGE_CANDIDATE_READY"
    assert result.pilot_pack_status == "PILOT_PACK_READY"
    assert result.selected_primary_pathology == "REN_001"
    assert result.package_candidate_ref is not None
    assert result.metadata["parser_invoked"] is False
    assert result.delivery_authorized is False


def test_case_run_audit_missing_evidence_returns_owner_question() -> None:
    payload = _case_payload()
    payload["available_data_fields"] = ["precio", "costo"]
    payload["column_meaning_confirmations"] = ["precio=precio de venta", "costo=costo unitario"]
    payload["input_values"] = {"precio": 100, "costo": 60}

    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=payload,
    )

    assert result.status == STATUS_BRIDGE_NEXT_OWNER_QUESTION
    assert result.next_owner_question is not None
    assert result.package_candidate_ref is None
    assert result.owner_confirmation_required is True


def test_case_run_audit_empty_narrative_blocks() -> None:
    payload = _case_payload()
    payload["raw_owner_narrative"] = " "

    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=payload,
    )

    assert result.status == STATUS_BRIDGE_BLOCKED
    assert result.blocked_reason == "EMPTY_OWNER_NARRATIVE"
    assert result.package_candidate_ref is None


def test_case_run_audit_nested_outputs_keep_closed_flags() -> None:
    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=_case_payload(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.entrypoint_result is not None
    assert result.entrypoint_result.delivery_authorized is False
    assert result.pilot_pack_result is not None
    assert result.pilot_pack_result.delivery_authorized is False
