from __future__ import annotations

from pathlib import Path

import pytest

from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import build_service_1_workbook_profile_v1
from pymia.contracts.formula_contract import FormulaInput

from .performance_support import record_benchmark


pytestmark = pytest.mark.performance
XLSX_INPUT = Path(__file__).resolve().parents[2] / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"


def _owner_answers(packet: dict) -> dict[str, str]:
    return {
        str(question["field_id"]): f"La columna {question['column_name']} representa {question['column_name']}"
        for question in packet["owner_questions"]
    }


def _canonical_ingestion_from_xlsx() -> dict:
    xlsx_bytes = XLSX_INPUT.read_bytes()
    packet = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=xlsx_bytes,
        uploaded_filename=XLSX_INPUT.name,
        include_all_sheets=True,
    )
    return build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers=_owner_answers(packet),
    )


@pytest.fixture(scope="module")
def canonical_ingestion_output() -> dict:
    output = _canonical_ingestion_from_xlsx()
    assert output["status"] == "INGESTION_OUTPUT_READY"
    assert output["ingestion_output"]["runtime_authorized"] is False
    return output["ingestion_output"]


def test_xlsx_canonical_ingestion(benchmark) -> None:
    result = benchmark(_canonical_ingestion_from_xlsx)
    assert result["status"] == "INGESTION_OUTPUT_READY"
    assert result["ingestion_output"]["normalized_tables"]
    record_benchmark(
        name="xlsx_canonical_ingestion",
        target="XLSX bytes -> canonical ingestion output",
        boundary="build_service_1_web_column_confirmation_intake_boundary_v1 + build_service_1_canonical_ingestion_output_from_owner_confirmation_v1",
        fixture_input="bytes(prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx), all sheets",
        stats=benchmark.stats,
    )


def test_workbook_profiling(benchmark, canonical_ingestion_output: dict) -> None:
    result = benchmark(
        build_service_1_workbook_profile_v1,
        ingestion_output=canonical_ingestion_output,
    )
    assert result["status"] == "WORKBOOK_PROFILE_READY"
    assert result["columns"]
    record_benchmark(
        name="workbook_profiling",
        target="canonical ingestion output -> workbook profile",
        boundary="build_service_1_workbook_profile_v1",
        fixture_input="canonical output from la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        stats=benchmark.stats,
    )


def test_formula_engine_ganancia_bruta(benchmark) -> None:
    service = FormulaEngineService()
    inputs = [
        FormulaInput(name="ventas", value=125000.0, source_refs=["bench:ventas"]),
        FormulaInput(name="costos", value=83000.0, source_refs=["bench:costos"]),
    ]
    result = benchmark(service.calculate, "ganancia_bruta", inputs)
    assert result.status.value == "OK"
    assert result.value == 42000.0
    record_benchmark(
        name="formula_engine_ganancia_bruta",
        target="FormulaEngineService.calculate",
        boundary="FormulaEngineService.calculate('ganancia_bruta', valid inputs)",
        fixture_input="ventas=125000.0, costos=83000.0",
        stats=benchmark.stats,
    )
