from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    finalize_service_1_case_delivery_folder_v1,
    write_service_1_case_delivery_folder_v1,
)
from pymia.smartpyme.service_1_real_owner_pilot_case_run_v1 import (
    build_service_1_real_owner_pilot_case_run_v1,
)
from pymia.smartpyme.service_1_real_owner_pilot_to_delivery_packet_adapter_v1 import (
    STATUS_DELIVERY_PACKET_BLOCKED,
    STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT,
    STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD,
    build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1,
)

# Smoke controlado: usa SOLO service_1_case_delivery_folder_v1.py.
# No crea delivery paralelo, no abre web/API/SaaS, no copia XLSX original.


def _base_kwargs() -> dict[str, object]:
    return {
        "case_id": "case_s1_smoke_001",
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
    kwargs: dict[str, object] = _base_kwargs()
    kwargs.update(overrides)
    return build_service_1_real_owner_pilot_case_run_v1(**kwargs)


def _adapter_for(**overrides: object):
    pilot = _pilot(**overrides)
    return build_service_1_real_owner_pilot_to_delivery_packet_adapter_v1(
        pilot_result=pilot,
        metadata={"smoke": "service_1_delivery_packet_folder_smoke_v1"},
    )


def _has_delivery_authorized_true(obj: Any) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "delivery_authorized" and value is True:
                return True
            if _has_delivery_authorized_true(value):
                return True
    if isinstance(obj, list):
        return any(_has_delivery_authorized_true(item) for item in obj)
    return False


def _write_and_finalize(*, tmp_path: Path, packet: dict[str, Any]) -> dict[str, Any]:
    base_dir = tmp_path / "cases"
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    # operator_packet.json es parte del contrato canonico de carpeta existente.
    (case_dir / "operator_packet.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return finalize_service_1_case_delivery_folder_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
    )


# ---------------------------------------------------------------------------
# Test 1: Happy path -> package ready -> folder + finalize
# ---------------------------------------------------------------------------
def test_smoke_001_happy_path_writes_canonical_folder(tmp_path: Path) -> None:
    result = _adapter_for()
    assert result.status == STATUS_DELIVERY_PACKET_READY_FOR_POLICY_GUARD

    packet = result.delivery_packet
    final_manifest = _write_and_finalize(tmp_path=tmp_path, packet=packet)
    case_dir = Path(final_manifest["case_dir"])

    # Carpeta de caso creada dentro de tmp_path (no delivery real al cliente).
    assert case_dir.exists()
    assert case_dir.is_dir()
    assert tmp_path in case_dir.parents or str(case_dir).startswith(str(tmp_path))

    # Archivos esperados del contrato canonico.
    for filename in (
        "README.txt",
        "owner_message.md",
        "case_record.json",
        "owner_delivery_packet.json",
        "product_gate.json",
        "delivery_policy_guard.json",
        "manifest.json",
    ):
        assert (case_dir / filename).exists(), f"missing {filename}"

    # runtime_authorized sigue False en todo el camino.
    assert final_manifest["runtime_authorized"] is False
    assert packet["product_gate"]["runtime_authorized"] is False
    assert final_manifest["delivery_policy_guard"]["runtime_authorized"] is False

    # Ningun artefacto autoriza delivery.
    assert _has_delivery_authorized_true(packet) is False
    assert _has_delivery_authorized_true(final_manifest) is False

    # No se copio el XLSX original (solo queda como referencia de string).
    xlsx_files = list(case_dir.glob("*.xlsx")) + list(case_dir.glob("*.xlsm"))
    assert xlsx_files == []
    case_record_raw = case_dir.joinpath("case_record.json").read_text(encoding="utf-8")
    assert "rentabilidad.xlsx" in case_record_raw  # referencia, no archivo copiado


# ---------------------------------------------------------------------------
# Test 2: Needs owner input -> product gate bloqueado, sin delivery
# ---------------------------------------------------------------------------
def test_smoke_002_needs_owner_input_blocks_delivery(tmp_path: Path) -> None:
    ingestion_output = dict(_base_kwargs()["ingestion_output"])  # type: ignore[arg-type]
    ingestion_output["available_data_fields"] = ["precio", "costo"]
    ingestion_output["input_values"] = {"precio": 100, "costo": 60}

    result = _adapter_for(
        ingestion_output=ingestion_output,
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
    )
    assert result.status == STATUS_DELIVERY_PACKET_NEEDS_OWNER_INPUT
    assert result.next_owner_question is not None

    packet = result.delivery_packet
    manifest = write_service_1_case_delivery_folder_v1(
        packet, base_dir=str(tmp_path / "cases")
    )
    case_dir = Path(manifest["case_dir"])

    # Pregunta legible al dueno presente en la carpeta.
    assert (case_dir / "next_owner_question.md").exists()
    # Product gate bloqueado: no listo para delivery policy guard.
    assert packet["product_gate"]["status"] == "BLOCKED"

    # Sin delivery autorizado en ningun artefacto.
    assert _has_delivery_authorized_true(packet) is False
    assert packet["product_gate"]["delivery_authorized"] is False

    # No se copio XLSX original.
    assert list(case_dir.glob("*.xlsx")) == []


# ---------------------------------------------------------------------------
# Test 3: Blocked -> expediente bloqueado, sin delivery
# ---------------------------------------------------------------------------
def test_smoke_003_blocked_writes_blocked_folder_without_delivery(tmp_path: Path) -> None:
    result = _adapter_for(raw_owner_narrative=" ")
    assert result.status == STATUS_DELIVERY_PACKET_BLOCKED
    assert result.blocked_reason == "missing_owner_narrative"

    packet = result.delivery_packet
    manifest = write_service_1_case_delivery_folder_v1(
        packet, base_dir=str(tmp_path / "cases")
    )
    case_dir = Path(manifest["case_dir"])

    # La infraestructura escribe el expediente bloqueado sin fallar.
    assert case_dir.exists()
    assert (case_dir / "README.txt").exists()
    assert (case_dir / "owner_message.md").exists()
    assert packet["product_gate"]["status"] == "BLOCKED"

    # Sin delivery autorizado en ningun artefacto.
    assert _has_delivery_authorized_true(packet) is False
    assert packet["product_gate"]["delivery_authorized"] is False

    # No se copio XLSX original.
    assert list(case_dir.glob("*.xlsx")) == []


# ---------------------------------------------------------------------------
# Test 4: Guard anti delivery paralelo / web / parser
# ---------------------------------------------------------------------------
def test_smoke_004_no_parallel_delivery_web_or_parser_imports() -> None:
    module_paths = [
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_real_owner_pilot_case_run_v1.py",
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_real_owner_pilot_to_delivery_packet_adapter_v1.py",
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_case_delivery_folder_v1.py",
    ]

    forbidden = (
        "import openpyxl",
        "import pandas",
        "import csv",
        "import flask",
        "import fastapi",
        "import requests",
    )

    for module_path in module_paths:
        source = module_path.read_text(encoding="utf-8")
        for item in forbidden:
            assert item not in source, f"Forbidden import {item} in {module_path.name}"
