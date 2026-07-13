from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_xlsx_runtime_bridge_v1 import (
    STATUS_BRIDGE_BLOCKED,
    STATUS_BRIDGE_NEXT_OWNER_QUESTION,
    STATUS_BRIDGE_PACKAGE_CANDIDATE_READY,
    build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1,
    build_service_1_xlsx_runtime_bridge_v1,
)


def _payload() -> dict[str, object]:
    return {
        "case_id": "case:s1:runtime:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
        "source_file_ref": "fixtures/rentabilidad.xlsx",
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


def test_bridge_builds_package_candidate_from_normalized_payload() -> None:
    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=_payload(),
    )

    assert result.status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY
    assert result.entrypoint_status == "DELIVERY_PACKAGE_CANDIDATE_READY"
    assert result.pilot_pack_status == "PILOT_PACK_READY"
    assert result.selected_primary_pathology == "REN_001"
    assert result.package_candidate_ref is not None
    assert result.metadata["parser_invoked"] is False


def test_bridge_returns_next_owner_question_when_fields_are_missing() -> None:
    payload = _payload()
    payload["available_data_fields"] = ["precio", "costo"]
    payload["column_meaning_confirmations"] = ["precio=precio de venta", "costo=costo unitario"]
    payload["input_values"] = {"precio": 100, "costo": 60}

    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=payload,
    )

    assert result.status == STATUS_BRIDGE_NEXT_OWNER_QUESTION
    assert result.entrypoint_status == "NEXT_OWNER_QUESTION"
    assert result.next_owner_question is not None
    assert result.package_candidate_ref is None
    assert result.owner_confirmation_required is True


def test_bridge_blocks_empty_owner_narrative() -> None:
    payload = _payload()
    payload["raw_owner_narrative"] = " "

    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=payload,
    )

    assert result.status == STATUS_BRIDGE_BLOCKED
    assert result.entrypoint_status == "BLOCKED"
    assert result.blocked_reason == "EMPTY_OWNER_NARRATIVE"
    assert result.package_candidate_ref is None


def test_bridge_direct_builder_accepts_normalized_values_without_source_file() -> None:
    result = build_service_1_xlsx_runtime_bridge_v1(
        case_id="case:s1:runtime:002",
        tenant_id="tenant:pyme:001",
        intake_id="intake:s1:002",
        run_id="run:s1:002",
        owner_ref="owner:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        source_file_ref=None,
        declared_data_sources=["normalized_payload"],
        business_period_reference="2026-06",
        column_meaning_confirmations=[
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
        available_data_fields=["precio", "costo", "cantidad"],
        input_values={"precio": 100, "costo": 60, "cantidad": 10},
    )

    assert result.status == STATUS_BRIDGE_PACKAGE_CANDIDATE_READY
    assert result.source_file_ref is None
    assert result.metadata["parser_invoked"] is False
    assert result.pilot_pack_status == "PILOT_PACK_NEEDS_OWNER_INPUT"


def test_bridge_never_authorizes_execution_or_delivery_flags() -> None:
    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=_payload(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.entrypoint_result is not None
    assert result.entrypoint_result.delivery_authorized is False
    assert result.pilot_pack_result is not None
    assert result.pilot_pack_result.delivery_authorized is False


def test_bridge_to_dict_contains_nested_contracts() -> None:
    result = build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
        normalized_payload=_payload(),
    )
    data = result.to_dict()

    assert data["entrypoint_result"]["schema_version"] == "SERVICE_1_XLSX_FIRST_PRODUCT_ENTRYPOINT_V1"
    assert data["pilot_pack_result"]["schema_version"] == "SERVICE_1_REAL_CLIENT_XLSX_FIRST_PILOT_PACK_V1"


def test_bridge_rejects_invalid_normalized_payload_type() -> None:
    with pytest.raises(ValueError):
        build_service_1_xlsx_runtime_bridge_from_normalized_payload_v1(
            normalized_payload=object(),  # type: ignore[arg-type]
        )
