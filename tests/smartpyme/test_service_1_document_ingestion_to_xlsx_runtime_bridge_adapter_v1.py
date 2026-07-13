from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1 import (
    STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT,
    STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT,
    STATUS_ADAPTER_BRIDGE_BLOCKED,
    STATUS_ADAPTER_BRIDGE_READY,
    STATUS_ADAPTER_NEXT_OWNER_QUESTION,
    build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1,
)


def _kwargs() -> dict[str, object]:
    return {
        "case_id": "case:s1:adapter:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
        "raw_owner_narrative": "No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        "business_period_reference": "2026-06",
        "column_meaning_confirmations": [
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
    }


def _ingestion_output() -> dict[str, object]:
    return {
        "source_file_ref": "ingestion/rentabilidad.xlsx",
        "declared_data_sources": ["rentabilidad.xlsx"],
        "available_data_fields": ["precio", "costo", "cantidad"],
        "input_values": {"precio": 100, "costo": 60, "cantidad": 10},
    }


def test_adapter_happy_path_reaches_bridge_ready() -> None:
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **_kwargs(),
        ingestion_output=_ingestion_output(),
    )

    assert result.status == STATUS_ADAPTER_BRIDGE_READY
    assert result.bridge_result is not None
    assert result.bridge_result.status == "BRIDGE_PACKAGE_CANDIDATE_READY"
    assert result.available_data_fields == ("precio", "costo", "cantidad")
    assert result.input_values == {"precio": 100, "costo": 60, "cantidad": 10}
    assert result.normalized_payload["source_file_ref"] == "ingestion/rentabilidad.xlsx"


def test_adapter_blocks_missing_ingestion_output() -> None:
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **_kwargs(),
        ingestion_output={},
    )

    assert result.status == STATUS_ADAPTER_BLOCKED_MISSING_INGESTION_OUTPUT
    assert result.bridge_result is None
    assert result.missing_adapter_items == ("ingestion_output",)


def test_adapter_blocks_invalid_ingestion_output_without_fields() -> None:
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **_kwargs(),
        ingestion_output={"input_values": {"precio": 100}},
    )

    assert result.status == STATUS_ADAPTER_BLOCKED_INVALID_INGESTION_OUTPUT
    assert result.bridge_result is None
    assert "available_data_fields" in result.missing_adapter_items


def test_adapter_incomplete_fields_returns_next_owner_question() -> None:
    ingestion_output = _ingestion_output()
    ingestion_output["available_data_fields"] = ["precio", "costo"]
    ingestion_output["input_values"] = {"precio": 100, "costo": 60}
    kwargs = _kwargs()
    kwargs["column_meaning_confirmations"] = ["precio=precio de venta", "costo=costo unitario"]
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **kwargs,
        ingestion_output=ingestion_output,
    )

    assert result.status == STATUS_ADAPTER_NEXT_OWNER_QUESTION
    assert result.bridge_result is not None
    assert result.bridge_result.status == "BRIDGE_NEXT_OWNER_QUESTION"
    assert result.owner_confirmation_required is True


def test_adapter_empty_owner_narrative_maps_bridge_blocked() -> None:
    kwargs = _kwargs()
    kwargs["raw_owner_narrative"] = " "
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **kwargs,
        ingestion_output=_ingestion_output(),
    )

    assert result.status == STATUS_ADAPTER_BRIDGE_BLOCKED
    assert result.bridge_result is not None
    assert result.bridge_result.status == "BRIDGE_BLOCKED"
    assert result.blocked_reason == "EMPTY_OWNER_NARRATIVE"


def test_adapter_never_authorizes_execution_or_delivery() -> None:
    result = build_service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1(
        **_kwargs(),
        ingestion_output=_ingestion_output(),
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_adapter_does_not_import_parser_or_file_runtime_modules() -> None:
    source = Path(
        "pymia/smartpyme/service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py"
    ).read_text(encoding="utf-8")

    forbidden = ("import openpyxl", "import pandas", "import csv", "import os", "import glob")
    for item in forbidden:
        assert item not in source
