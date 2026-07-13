from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_real_owner_pilot_case_run_v1 import (
    build_service_1_real_owner_pilot_case_run_v1,
)
from pymia.smartpyme.service_1_real_owner_pilot_to_delivery_packet_adapter_v1 import (
    STATUS_DELIVERY_PACKET_BLOCKED,
    STATUS_DELIVERY_PACKET_INVALID_INPUT,
    STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT,
    STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD,
    build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1,
)


def _base_kwargs() -> dict[str, object]:
    return {
        "case_id": "case:s1:owner:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
        "raw_owner_narrative": "No veo el margen porque tengo precio, costo y cantidad.",
        "business_period_reference": "2026-06",
        "column_meaning_confirmations": [
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
        "ingestion_output": {
            "source_file_ref": "ingestion/rentabilidad.xlsx",
            "declared_data_sources": ["rentabilidad.xlsx"],
            "available_data_fields": ["precio", "costo", "cantidad"],
            "input_values": {"precio": 100, "costo": 60, "cantidad": 10},
        },
    }


def _pilot(**overrides: object):
    kwargs = _base_kwargs()
    kwargs.update(overrides)
    return build_service_1_real_owner_pilot_case_run_v1(**kwargs)


def test_adapter_builds_delivery_packet_ready_for_policy_guard() -> None:
    pilot = _pilot()
    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=pilot,
        metadata={"operator_ref": "operator:001"},
    )

    assert result.status == STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD
    assert result.delivery_packet["asset"]["asset_id"] == "case:s1:owner:001"
    assert result.delivery_packet["asset"]["source_file_ref"] == "ingestion/rentabilidad.xlsx"
    assert result.delivery_packet["case_record"]["status"] == "REAL_OWNER_PACKAGE_CANDIDATE_READY"
    assert result.delivery_packet["owner_delivery_packet"]["package_candidate_ref"] is not None
    assert result.delivery_policy_guard is not None
    assert result.delivery_policy_guard["guard_type"] == "SERVICE_1_DELIVERY_POLICY_GUARD"
    assert result.product_gate["status"] == "READY_FOR_DELIVERY_POLICY_GUARD"


def test_adapter_preserves_needs_owner_input_state() -> None:
    ingestion_output = _base_kwargs()["ingestion_output"]
    assert isinstance(ingestion_output, dict)
    ingestion_output = dict(ingestion_output)
    ingestion_output["available_data_fields"] = ["precio", "costo"]
    ingestion_output["input_values"] = {"precio": 100, "costo": 60}
    pilot = _pilot(
        ingestion_output=ingestion_output,
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
    )

    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=pilot,
    )

    assert result.status == STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT
    assert result.next_owner_question is not None
    assert result.next_owner_question["owner_confirmation_required"] is True
    assert result.delivery_packet["next_owner_question"] == result.next_owner_question
    assert result.product_gate["status"] == "BLOCKED"


def test_adapter_preserves_blocked_state() -> None:
    pilot = _pilot(raw_owner_narrative=" ")
    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=pilot,
    )

    assert result.status == STATUS_DELIVERY_PACKET_BLOCKED
    assert result.blocked_reason == "missing_owner_narrative"
    assert result.delivery_packet["case_record"]["blocked_reason"] == "missing_owner_narrative"
    assert result.product_gate["status"] == "BLOCKED"


def test_adapter_blocks_invalid_input_without_throwing() -> None:
    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result={"not": "a pilot result"},  # type: ignore[arg-type]
    )

    assert result.status == STATUS_DELIVERY_PACKET_INVALID_INPUT
    assert result.delivery_packet == {}
    assert result.delivery_policy_guard is None
    assert result.blocked_reason == "pilot_result_must_be_Service1RealOwnerPilotCaseRunV1"


def test_adapter_never_authorizes_runtime_or_delivery() -> None:
    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=_pilot(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
    assert result.product_gate["runtime_authorized"] is False
    assert result.product_gate["delivery_authorized"] is False


def test_adapter_packet_contains_required_delivery_folder_keys() -> None:
    result = build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=_pilot(),
    )

    packet = result.delivery_packet
    for key in (
        "asset",
        "owner_message",
        "case_record",
        "owner_delivery_packet",
        "product_gate",
        "delivery_policy_guard",
        "evidence_loop_status",
    ):
        assert key in packet


def test_adapter_module_does_not_import_web_or_parser_modules() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_real_owner_pilot_to_delivery_packet_adapter_v1.py"
    )
    source = module_path.read_text(encoding="utf-8")

    forbidden = (
        "import openpyxl",
        "import pandas",
        "import csv",
        "import pathlib",
        "import os",
        "import glob",
        "import flask",
        "import fastapi",
        "import requests",
    )
    for item in forbidden:
        assert item not in source
