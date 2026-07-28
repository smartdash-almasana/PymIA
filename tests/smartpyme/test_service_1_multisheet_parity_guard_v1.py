from __future__ import annotations

import inspect
from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme import service_1_web_column_confirmation_intake_boundary_v1 as intake
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    BLOCK_MISSING_ANSWERS,
    BLOCK_UNKNOWN_COLUMNS,
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_CONFIRMED_BINDINGS,
    STATUS_OWNER_QUESTIONS,
    run_initial_pass,
    run_owner_reentry,
)
from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import (
    read_xlsx_to_normalized_tables_v1,
)


def _write_multisheet_xlsx(path: Path) -> None:
    workbook = Workbook()
    ventas = workbook.active
    ventas.title = "Ventas"
    ventas.append(["fecha", "importe", "canal"])
    ventas.append(["2026-07-01", 1000, "Mostrador"])
    ventas.append(["2026-07-02", 1500, "Online"])

    cobros = workbook.create_sheet("Cobros")
    cobros.append(["fecha", "importe", "medio_pago"])
    cobros.append(["2026-07-03", 800, "Transferencia"])
    cobros.append(["2026-07-04", 700, "Efectivo"])
    workbook.save(path)
    workbook.close()


def _multisheet_packet(tmp_path: Path) -> dict:
    xlsx = tmp_path / "multisheet.xlsx"
    _write_multisheet_xlsx(xlsx)
    packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx,
        include_all_sheets=True,
    )
    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    return packet


def _answers_by_question_id(packet: dict) -> dict[str, str]:
    return {
        ref["question_id"]: f"significado de {ref['sheet_name']}.{ref['column_name']}"
        for ref in packet["column_refs"]
    }


def test_canonical_intake_exposes_single_and_multiple_sheet_selection() -> None:
    parameters = inspect.signature(
        intake.build_service_1_web_column_confirmation_intake_boundary_v1
    ).parameters

    assert "sheet_name" in parameters
    assert "sheet_names" in parameters
    assert "include_all_sheets" in parameters


def test_canonical_reader_returns_all_non_empty_sheets_and_releases_file(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "multisheet.xlsx"
    _write_multisheet_xlsx(xlsx)

    tables = read_xlsx_to_normalized_tables_v1(xlsx)

    assert [table["sheet_name"] for table in tables] == ["Ventas", "Cobros"]
    assert all(table["status"] == "OK" for table in tables)
    assert tables[0]["headers"] == ["fecha", "importe", "canal"]
    assert tables[1]["headers"] == ["fecha", "importe", "medio_pago"]

    replacement = tmp_path / "renamed.xlsx"
    xlsx.rename(replacement)
    assert replacement.exists()


def test_canonical_owner_questions_are_sheet_qualified_and_collision_safe(
    tmp_path: Path,
) -> None:
    packet = _multisheet_packet(tmp_path)

    assert packet["sheet_names"] == ["Ventas", "Cobros"]
    assert packet["normalized_table"] is None
    assert len(packet["normalized_tables"]) == 2
    assert packet["question_count"] == len(packet["column_refs"]) == 6
    assert len({ref["question_id"] for ref in packet["column_refs"]}) == 6
    assert [ref["column_name"] for ref in packet["column_refs"]].count("fecha") == 2
    assert [ref["column_name"] for ref in packet["column_refs"]].count("importe") == 2
    assert all(question["sheet_name"] in question["question"] for question in packet["owner_questions"])
    assert all(question["field_id"] == question["question_id"] for question in packet["owner_questions"])


def test_multisheet_connector_requires_question_ids_and_preserves_evidence(
    tmp_path: Path,
) -> None:
    packet = _multisheet_packet(tmp_path)

    legacy_answers = {column: f"significado de {column}" for column in packet["columns"]}
    blocked = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers=legacy_answers,
    )
    assert blocked["status"] == "BLOCKED"
    assert blocked["blocked_reason"] in {BLOCK_UNKNOWN_COLUMNS, BLOCK_MISSING_ANSWERS}

    result = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers=_answers_by_question_id(packet),
    )

    assert result["status"] == "INGESTION_OUTPUT_READY"
    ingestion = result["ingestion_output"]
    assert ingestion["sheet_name"] is None
    assert ingestion["sheet_names"] == ["Ventas", "Cobros"]
    assert len(ingestion["column_refs"]) == 6
    assert ingestion["available_data_fields"] == [
        ref["question_id"] for ref in packet["column_refs"]
    ]
    assert all(item["sample_values"] for item in ingestion["column_evidence"].values())
    assert {item["inferred_type"] for item in ingestion["column_evidence"].values()} >= {
        "date",
        "number",
        "text",
    }


def test_semantic_bridge_preserves_sheet_identity_for_duplicate_headers(
    tmp_path: Path,
) -> None:
    packet = _multisheet_packet(tmp_path)
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers=_answers_by_question_id(packet),
    )

    bridge = build_service_1_semantic_bridge_from_canonical_ingestion_output_v1(
        ingestion_output=connector["ingestion_output"]
    )

    assert bridge["status"] == "SEMANTIC_CANDIDATES_READY"
    entries = bridge["confirmation_matrix"].entries
    assert len(entries) == 6
    assert {(entry.sheet_name, entry.original_column_name) for entry in entries} == {
        ("Ventas", "fecha"),
        ("Ventas", "importe"),
        ("Ventas", "canal"),
        ("Cobros", "fecha"),
        ("Cobros", "importe"),
        ("Cobros", "medio_pago"),
    }
    assert all(entry.sample_values for entry in entries)
    assert {candidate.sheet_name for candidate in bridge["column_candidates"]} == {
        "Ventas",
        "Cobros",
    }


def test_explicit_single_sheet_selection_preserves_legacy_answer_keys(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "multisheet.xlsx"
    _write_multisheet_xlsx(xlsx)
    packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx,
        sheet_name="Cobros",
    )

    assert packet["sheet_names"] == ["Cobros"]
    assert packet["columns"] == ["fecha", "importe", "medio_pago"]
    assert all(ref["field_id"] == ref["column_name"] for ref in packet["column_refs"])

    answers = {column: f"significado de {column}" for column in packet["columns"]}
    result = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers=answers,
    )
    assert result["status"] == "INGESTION_OUTPUT_READY"
    assert result["owner_answers"] == answers
    assert result["ingestion_output"]["sheet_name"] == "Cobros"


def test_default_single_sheet_and_explicit_all_sheets_are_distinct_scopes(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "multisheet.xlsx"
    _write_multisheet_xlsx(xlsx)

    default_packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx
    )
    all_packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx,
        include_all_sheets=True,
    )

    assert default_packet["sheet_names"] == ["Ventas"]
    assert default_packet["question_count"] == 3
    assert all_packet["sheet_names"] == ["Ventas", "Cobros"]
    assert all_packet["question_count"] == 6
    assert default_packet["case_id"] != all_packet["case_id"]


def test_duplicate_ambiguous_headers_reenter_semantic_loop_by_question_id(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "ambiguous_multisheet.xlsx"
    workbook = Workbook()
    ventas = workbook.active
    ventas.title = "Ventas"
    ventas.append(["monto"])
    ventas.append([1000])
    cobros = workbook.create_sheet("Cobros")
    cobros.append(["monto"])
    cobros.append([800])
    workbook.save(xlsx)
    workbook.close()

    packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=xlsx,
        include_all_sheets=True,
    )
    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=packet,
        owner_answers={
            ref["question_id"]: f"importe de {ref['sheet_name']}"
            for ref in packet["column_refs"]
        },
    )

    initial = run_initial_pass(ingestion_output=connector["ingestion_output"])

    assert initial["status"] == STATUS_OWNER_QUESTIONS
    questions = initial["owner_questions"]
    assert [question["column_name"] for question in questions] == ["monto", "monto"]
    assert {question["sheet_name"] for question in questions} == {"Ventas", "Cobros"}
    assert len({question["question_id"] for question in questions}) == 2
    assert initial["gate_packet"]["owner_answer_bindings"] == {}
    confirmation_candidates = initial["gate_packet"]["owner_confirmation_candidates"]
    assert len(confirmation_candidates) == 2
    assert {
        candidate.metadata["question_id"] for candidate in confirmation_candidates
    } == {question["question_id"] for question in questions}

    semantic_answers = {
        question["question_id"]: next(
            option_id
            for option_id in question["allowed_option_ids"]
            if option_id not in {"OTHER", "IGNORE"}
        )
        for question in questions
    }
    final = run_owner_reentry(previous_run=initial, owner_answers=semantic_answers)

    assert final["status"] == STATUS_CONFIRMED_BINDINGS
    reinjected = final["reentry_packet"]["column_candidates"]
    assert len(reinjected) == 2
    assert all(candidate.owner_confirmation_required is False for candidate in reinjected)
    assert {candidate.metadata["column_ref_id"] for candidate in reinjected} == set(
        semantic_answers
    )


def test_uploaded_bytes_support_explicit_all_sheets(tmp_path: Path) -> None:
    xlsx = tmp_path / "uploaded_multisheet.xlsx"
    _write_multisheet_xlsx(xlsx)

    packet = intake.build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=xlsx.read_bytes(),
        uploaded_filename="uploaded_multisheet.xlsx",
        include_all_sheets=True,
    )

    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert packet["source_kind"] == "uploaded_bytes"
    assert packet["sheet_names"] == ["Ventas", "Cobros"]
    assert packet["question_count"] == 6
    assert len({ref["question_id"] for ref in packet["column_refs"]}) == 6
