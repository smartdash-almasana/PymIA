from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_canonical_ingestion_to_region_evidence_adapter_v1 import (
    STATUS_BLOCKED as REGION_EVIDENCE_BLOCKED,
    STATUS_READY as REGION_EVIDENCE_READY,
    STATUS_UNRESOLVED as REGION_EVIDENCE_UNRESOLVED,
    build_service_1_region_evidence_from_canonical_ingestion_v1,
)
from pymia.smartpyme.service_1_logical_table_candidate_v1 import (
    GRAIN_RESOLVED,
    GRAIN_UNRESOLVED,
    STATUS_READY as LOGICAL_TABLES_READY,
    build_service_1_logical_table_candidates_v1,
)
from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import (
    read_xlsx_to_normalized_tables_v1,
)


def _save_workbook(path: Path, rows: list[list[object | None]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Datos"
    for row in rows:
        worksheet.append(row)
    workbook.save(path)
    workbook.close()


def _canonical_packet(table: dict, file_ref: str) -> dict:
    output = {
        "case_id": "d1-d2-case",
        "filename": file_ref,
        "source_file_ref": file_ref,
        "workbook_context": {
            "case_id": "d1-d2-case",
            "source_artifact_ref": "artifact:d1-d2",
            "workbook_ref": f"workbook:{file_ref}",
            "ingestion_scope": "first_non_empty_sheet",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        },
        "provenance": {
            "source_kind": "xlsx",
            "source_artifact_ref": "artifact:d1-d2",
            "source_file_ref": f"workbook:{file_ref}",
            "workbook_ref": f"workbook:{file_ref}",
            "filename": file_ref,
            "sheet_names": [str(table.get("sheet_name") or "")],
            "sheet_refs": [],
        },
        "normalized_tables": [table],
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }
    return {
        "schema_version": "D1_D2_TEST_PACKET",
        "status": "INGESTION_OUTPUT_READY",
        "case_id": "d1-d2-case",
        "filename": file_ref,
        "ingestion_output": output,
        "runtime_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
    }


def test_canonical_parser_preserves_raw_width_and_coordinates_for_later_regions(tmp_path: Path) -> None:
    path = tmp_path / "two-regions.xlsx"
    _save_workbook(
        path,
        [
            ["Code", "Amount"],
            ["A", 10],
            ["B", 10],
            [None, None],
            ["Name", "Qty", "Unit"],
            ["X", 2, 3],
            ["Y", 2, 3],
        ],
    )

    table = read_xlsx_to_normalized_tables_v1(path)[0]

    assert table["status"] == "OK"
    assert table["physical_max_column"] == 3
    raw_second_header = next(item for item in table["physical_rows"] if item["row_number"] == 5)
    assert raw_second_header["cells"] == ["Name", "Qty", "Unit"]
    assert raw_second_header["physical_width"] == 3
    assert table["rows"][2] == {"code": "Name", "amount": "Qty"}


def test_adapter_detects_two_rectangular_regions_in_one_sheet_without_second_reader(tmp_path: Path) -> None:
    path = tmp_path / "two-regions.xlsx"
    _save_workbook(
        path,
        [
            ["Code", "Amount"],
            ["A", 10],
            ["B", 10],
            [None, None],
            ["Name", "Qty", "Unit"],
            ["X", 2, 3],
            ["Y", 2, 3],
        ],
    )
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=_canonical_packet(table, "renamed.xlsx"),
    )

    assert result["status"] == REGION_EVIDENCE_READY
    assert [item["region_ref"] for item in result["regions"]] == [
        "Datos:region:1",
        "Datos:region:2",
    ]
    assert result["regions"][0]["column_refs"] == ("code", "amount")
    assert result["regions"][1]["column_refs"] == ("name", "qty", "unit")
    assert result["regions"][0]["provenance"]["data_row_numbers"] == [2, 3]
    assert result["regions"][1]["provenance"]["data_row_numbers"] == [6, 7]


def test_region_evidence_fails_closed_when_canonical_table_has_no_sheet_identity(tmp_path: Path) -> None:
    path = tmp_path / "missing-sheet.xlsx"
    _save_workbook(path, [["Code", "Amount"], ["A", 10]])
    table = dict(read_xlsx_to_normalized_tables_v1(path)[0])
    table["sheet_name"] = ""

    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=_canonical_packet(table, "missing-sheet.xlsx"),
    )

    assert result["status"] == REGION_EVIDENCE_BLOCKED
    assert result["blocked_reason"] == "NORMALIZED_TABLE_SHEET_REF_REQUIRED"
    assert result["regions"] == []


def test_region_evidence_fails_closed_on_duplicate_sheet_identity(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-sheet.xlsx"
    _save_workbook(path, [["Code", "Amount"], ["A", 10]])
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    packet = _canonical_packet(table, "duplicate-sheet.xlsx")
    packet["ingestion_output"]["normalized_tables"] = [table, dict(table)]

    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet,
    )

    assert result["status"] == REGION_EVIDENCE_BLOCKED
    assert result["blocked_reason"] == "NORMALIZED_TABLE_SHEET_REF_AMBIGUOUS"
    assert result["regions"] == []


def test_d2_projects_candidates_with_filename_independent_structural_identity(tmp_path: Path) -> None:
    path = tmp_path / "two-regions.xlsx"
    _save_workbook(
        path,
        [
            ["Code", "Amount"],
            ["A", 10],
            ["B", 10],
            [None, None],
            ["Name", "Qty", "Unit"],
            ["X", 2, 3],
            ["Y", 2, 3],
        ],
    )
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    signatures: list[str] = []
    ids: list[str] = []

    for file_ref in ("enero.xlsx", "archivo_renombrado.xlsx"):
        packet = _canonical_packet(table, file_ref)
        regions = build_service_1_region_evidence_from_canonical_ingestion_v1(
            canonical_packet=packet,
        )
        candidates = build_service_1_logical_table_candidates_v1(
            canonical_packet=packet,
            region_evidence=regions,
        )
        assert candidates["status"] == LOGICAL_TABLES_READY
        assert candidates["candidate_count"] == 2
        signatures.extend(item["structural_signature"] for item in candidates["candidates"])
        ids.extend(item["logical_table_id"] for item in candidates["candidates"])
        assert all(item["grain_state"] == GRAIN_RESOLVED for item in candidates["candidates"])
        assert all(file_ref not in item["structural_signature"] for item in candidates["candidates"])

    assert signatures[:2] == signatures[2:]
    assert ids[:2] == ids[2:]


def test_ambiguous_physical_width_fails_closed_instead_of_inventing_boundary(tmp_path: Path) -> None:
    path = tmp_path / "ambiguous.xlsx"
    _save_workbook(
        path,
        [
            ["Code", "Amount"],
            ["A", 10],
            ["B", 20],
            [5, 6, 7],
        ],
    )
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=_canonical_packet(table, "ambiguous.xlsx"),
    )

    assert result["status"] == REGION_EVIDENCE_UNRESOLVED
    assert result["regions"] == []


def test_region_detection_excludes_repeated_headers_and_totals_with_row_lineage(tmp_path: Path) -> None:
    path = tmp_path / "repeated-header.xlsx"
    _save_workbook(
        path,
        [
            ["ID", "Value"],
            ["A", 1],
            ["ID", "Value"],
            ["B", 2],
            ["Total", 3],
        ],
    )
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    result = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=_canonical_packet(table, "repeated-header.xlsx"),
    )

    assert result["status"] == REGION_EVIDENCE_READY
    assert len(result["regions"]) == 1
    evidence = result["regions"][0]["provenance"]["detection_evidence"]
    assert evidence["repeated_header_rows"] == [3]
    assert evidence["total_or_subtotal_rows"] == [5]
    assert evidence["data_row_numbers"] == [2, 4]


def test_d2_marks_source_grain_unresolved_without_unique_key_evidence(tmp_path: Path) -> None:
    path = tmp_path / "no-key.xlsx"
    _save_workbook(
        path,
        [
            ["Group", "Value"],
            ["A", "same"],
            ["A", "same"],
        ],
    )
    table = read_xlsx_to_normalized_tables_v1(path)[0]
    packet = _canonical_packet(table, "no-key.xlsx")
    regions = build_service_1_region_evidence_from_canonical_ingestion_v1(
        canonical_packet=packet,
    )
    candidates = build_service_1_logical_table_candidates_v1(
        canonical_packet=packet,
        region_evidence=regions,
    )

    assert candidates["status"] == LOGICAL_TABLES_READY
    assert candidates["candidates"][0]["grain_state"] == GRAIN_UNRESOLVED
    assert candidates["candidates"][0]["grain_candidate"] is None


def test_required_heterogeneous_corpus_stays_rubro_agnostic() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture_names = (
        "cafeteria_abc.xlsx",
        "constructora_nueva_era_srl.xlsx",
        "distribuidora_mayorista_compleja.xlsx",
        "PYMIA_CONSORCIO_CABILDO_2026_07.xlsx",
    )
    fixtures = [
        next(
            candidate
            for candidate in (repo_root / "prueba_excels" / name, repo_root.parent / "prueba_excels" / name)
            if candidate.exists()
        )
        for name in fixture_names
    ]

    for fixture in fixtures:
        tables = read_xlsx_to_normalized_tables_v1(fixture)
        assert tables
        packet = _canonical_packet(
            tables[0],
            fixture.name,
        )
        packet["ingestion_output"]["normalized_tables"] = tables
        regions = build_service_1_region_evidence_from_canonical_ingestion_v1(
            canonical_packet=packet,
        )
        assert regions["status"] == REGION_EVIDENCE_READY
        candidates = build_service_1_logical_table_candidates_v1(
            canonical_packet=packet,
            region_evidence=regions,
        )
        assert candidates["status"] == LOGICAL_TABLES_READY
        assert candidates["candidate_count"] >= len(tables)
