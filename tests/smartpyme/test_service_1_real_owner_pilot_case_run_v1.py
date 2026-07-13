from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_real_owner_pilot_case_run_v1 import (
    STATUS_REAL_OWNER_BLOCKED,
    STATUS_REAL_OWNER_NEEDS_OWNER_INPUT,
    STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY,
    Service1RealOwnerPilotCaseRunV1,
    build_service_1_real_owner_pilot_case_run_v1,
)


def _full_ingestion_output() -> dict[str, object]:
    return {
        "source_file_ref": "ingestion/rentabilidad.xlsx",
        "declared_data_sources": ["rentabilidad.xlsx"],
        "available_data_fields": ["precio", "costo", "cantidad"],
        "input_values": {"precio": 100, "costo": 60, "cantidad": 10},
    }


def _kwargs() -> dict[str, object]:
    return {
        "case_id": "case:s1:pilot:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
        "raw_owner_narrative": "No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        "ingestion_output": _full_ingestion_output(),
        "business_period_reference": "2026-06",
        "column_meaning_confirmations": [
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=volumen vendido",
        ],
    }


def _build(**overrides: object) -> Service1RealOwnerPilotCaseRunV1:
    kwargs = _kwargs()
    for key, value in overrides.items():
        kwargs[key] = value
    return build_service_1_real_owner_pilot_case_run_v1(**kwargs)


def test_ren_001_happy_path_package_candidate_ready() -> None:
    result = _build()

    assert result.status == STATUS_REAL_OWNER_PACKAGE_CANDIDATE_READY
    assert result.package_candidate_ref is not None
    assert result.selected_primary_pathology is not None
    assert result.allowed_computation_ref is not None
    assert result.adapter_result is not None
    assert result.adapter_result.status == "ADAPTER_BRIDGE_READY"
    assert result.bridge_status == "BRIDGE_PACKAGE_CANDIDATE_READY"
    assert result.pilot_pack_status == "PILOT_PACK_READY"
    assert result.owner_confirmation_required is False


def test_ren_002_missing_ingestion_output_blocks() -> None:
    result = _build(ingestion_output={})

    assert result.status == STATUS_REAL_OWNER_BLOCKED
    assert result.adapter_result is not None
    assert result.adapter_result.bridge_result is None
    assert result.blocked_reason is not None
    assert result.package_candidate_ref is None
    assert result.next_owner_question is None


def test_ren_003_incomplete_fields_needs_owner_input() -> None:
    ingestion = _full_ingestion_output()
    ingestion["available_data_fields"] = ["precio", "costo"]
    ingestion["input_values"] = {"precio": 100, "costo": 60}
    result = _build(
        ingestion_output=ingestion,
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
    )

    assert result.status == STATUS_REAL_OWNER_NEEDS_OWNER_INPUT
    assert result.next_owner_question is not None
    assert result.owner_confirmation_required is True


def test_ren_004_empty_narrative_blocks() -> None:
    result = _build(raw_owner_narrative=" ")

    assert result.status == STATUS_REAL_OWNER_BLOCKED
    assert result.blocked_reason == "missing_owner_narrative"
    assert result.owner_narrative is None
    assert result.adapter_result is None
    assert result.bridge_status is None
    assert result.package_candidate_ref is None


def test_ren_005_decision_checklist_and_stop_rules_present() -> None:
    result = _build()

    checklist = result.decision_checklist
    assert isinstance(checklist, dict)
    assert len(checklist) == 7
    assert "owner_narrative_present" in checklist
    assert "business_period_present" in checklist
    assert "column_confirmations_present" in checklist
    assert "ingestion_output_present" in checklist
    assert "adapter_status_checked" in checklist
    assert "bridge_status_checked" in checklist
    assert "package_or_question_present" in checklist
    assert checklist["package_or_question_present"] is True

    stop_rules = result.stop_rules
    assert isinstance(stop_rules, tuple)
    assert len(stop_rules) == 7
    assert "detener si falta narrativa del dueno" in stop_rules
    assert "no prometer diagnostico definitivo" in stop_rules
    assert "no producir delivery autonomo" in stop_rules


def test_ren_006_blocked_narrative_has_checklist_with_false_flags() -> None:
    result = _build(raw_owner_narrative=" ")

    checklist = result.decision_checklist
    assert checklist["owner_narrative_present"] is False
    assert checklist["adapter_status_checked"] is False
    assert checklist["bridge_status_checked"] is False
    assert checklist["package_or_question_present"] is False


def test_ren_007_all_execution_delivery_flags_remain_false() -> None:
    result = _build()

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_ren_008_blocked_ingestion_output_has_consistent_metadata() -> None:
    result = _build(ingestion_output={})

    assert result.schema_version == "SERVICE_1_REAL_OWNER_PILOT_CASE_RUN_V1"
    assert result.service_name == "SERVICE_1"
    assert result.case_id == "case:s1:pilot:001"
    assert result.tenant_id == "tenant:pyme:001"
    assert result.intake_id == "intake:s1:001"
    assert result.run_id == "run:s1:001"
    assert result.owner_ref == "owner:pyme:001"


def test_ren_009_guard_anti_web_and_parser_imports() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "pymia"
        / "smartpyme"
        / "service_1_real_owner_pilot_case_run_v1.py"
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
        assert item not in source, f"Forbidden import found: {item}"
