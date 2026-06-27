from __future__ import annotations

import json
import sys
from pathlib import Path

from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    write_service_1_case_delivery_folder_v1,
)


def _minimal_packet() -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "asset": {"asset_id": "test_asset_001"},
        "owner_message": "Mensaje de prueba para el dueno.",
        "runtime_authorized": False,
    }


def _packet_with_structure() -> dict:
    packet = _minimal_packet()
    packet["detected_structure"] = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "workbook": {
            "sheet_count": 1,
            "sheets": [{"name": "Hoja1", "headers": ["A", "B"]}],
        },
        "runtime_authorized": False,
    }
    packet["column_confirmation_packet"] = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "packet_type": "COLUMN_CONFIRMATION",
        "status": "NEEDS_OWNER_CONFIRMATION",
        "questions": [{"question_id": "col_confirm_001"}],
        "runtime_authorized": False,
    }
    return packet


def _packet_with_first_aid() -> dict:
    packet = _packet_with_structure()
    packet["confirmed_columns"] = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "confirmed_columns": {"Cantidad": {"role": "quantity"}},
        "runtime_authorized": False,
        "warnings": [],
    }
    packet["first_aid_eligibility_gate"] = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "gate_type": "FIRST_AID_MINIMAL_ELIGIBILITY",
        "status": "ELIGIBLE",
        "runtime_authorized": False,
        "human_review_required": True,
    }
    packet["first_aid_result"] = {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "result_type": "FIRST_AID_MINIMAL",
        "status": "DRAFT_REVIEW_REQUIRED",
        "runtime_authorized": False,
        "human_review_required": True,
        "summary": {"sheet_count": 1, "sheets_profiled": 1, "total_findings": 1},
        "findings": [
            {
                "finding_type": "sheet_profile",
                "sheet_name": "Hoja1",
                "row_count": 5,
                "col_count": 2,
                "headers": ["A", "B"],
            }
        ],
        "warnings": [],
    }
    packet["first_aid_owner_summary"] = "# First Aid\n\nBorrador para revisión."
    return packet


# ---------------------------------------------------------------------------
# 1. Crea carpeta de caso
# ---------------------------------------------------------------------------
def test_creates_case_folder(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    assert case_dir.exists()
    assert case_dir.is_dir()


# ---------------------------------------------------------------------------
# 2. Escribe owner_message.md
# ---------------------------------------------------------------------------
def test_writes_owner_message_md(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    owner_md = Path(manifest["case_dir"]) / "owner_message.md"
    assert owner_md.exists()
    content = owner_md.read_text(encoding="utf-8")
    assert "Mensaje de prueba para el dueno" in content


# ---------------------------------------------------------------------------
# 3. Manifest lists operator_packet.json
# ---------------------------------------------------------------------------
def test_manifest_lists_operator_packet_json(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    assert "operator_packet.json" in manifest["files_written"]


# ---------------------------------------------------------------------------
# 4. Escribe detected_structure.json si existe
# ---------------------------------------------------------------------------
def test_writes_detected_structure_json_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    ds_file = Path(manifest["case_dir"]) / "detected_structure.json"
    assert ds_file.exists()
    assert "detected_structure.json" in manifest["files_written"]


# ---------------------------------------------------------------------------
# 5. Escribe column_confirmation_packet.json si existe
# ---------------------------------------------------------------------------
def test_writes_column_confirmation_packet_json_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    cc_file = Path(manifest["case_dir"]) / "column_confirmation_packet.json"
    assert cc_file.exists()


# ---------------------------------------------------------------------------
# 6. No escribe XLSX original
# ---------------------------------------------------------------------------
def test_does_not_write_original_xlsx(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    xlsx_files = list(case_dir.glob("*.xlsx")) + list(case_dir.glob("*.xlsm"))
    assert len(xlsx_files) == 0


# ---------------------------------------------------------------------------
# 7. runtime_authorized false en manifest
# ---------------------------------------------------------------------------
def test_manifest_runtime_authorized_is_false(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    assert manifest["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 8. No muta packet original
# ---------------------------------------------------------------------------
def test_does_not_mutate_original_packet(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    original = json.dumps(packet, sort_keys=True)
    write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    after = json.dumps(packet, sort_keys=True)
    assert after == original


# ---------------------------------------------------------------------------
# 9. README.txt contiene límites
# ---------------------------------------------------------------------------
def test_readme_contains_required_limits(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    readme = Path(manifest["case_dir"]) / "README.txt"
    content = readme.read_text(encoding="utf-8").lower()
    assert "no contiene diagnostico" in content
    assert "no contiene calculos" in content
    assert "confirmacion humana" in content


# ---------------------------------------------------------------------------
# 10. No importa módulos prohibidos
# ---------------------------------------------------------------------------
def test_module_does_not_import_forbidden_modules() -> None:
    forbidden_modules = [
        "pymia.smartpyme.vertical_pipeline",
        "pymia.smartpyme.service_1_pipeline_v1",
        "pymia.smartpyme.service_1_fsm_decision_patch_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_v1",
        "pymia.application.vertical_pipeline",
        "tools.document_ingestion",
        "openai",
        "chatbot",
    ]
    for mod in forbidden_modules:
        sys.modules.pop(mod, None)
    import importlib
    import pymia.smartpyme.service_1_case_delivery_folder_v1 as cd_mod
    importlib.reload(cd_mod)
    for mod in forbidden_modules:
        assert mod not in sys.modules, f"Module must not import {mod}"


# ---------------------------------------------------------------------------
# 11. Escribe confirmed_columns.json si existe
# ---------------------------------------------------------------------------
def test_writes_confirmed_columns_json_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_first_aid()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    cc_file = Path(manifest["case_dir"]) / "confirmed_columns.json"
    assert cc_file.exists()
    assert "confirmed_columns.json" in manifest["files_written"]


# ---------------------------------------------------------------------------
# 12. Escribe first_aid_eligibility_gate.json si existe
# ---------------------------------------------------------------------------
def test_writes_first_aid_eligibility_gate_json_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_first_aid()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    gate_file = Path(manifest["case_dir"]) / "first_aid_eligibility_gate.json"
    assert gate_file.exists()
    assert "first_aid_eligibility_gate.json" in manifest["files_written"]


# ---------------------------------------------------------------------------
# 13. Escribe first_aid_result.json si existe
# ---------------------------------------------------------------------------
def test_writes_first_aid_result_json_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_first_aid()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    fa_file = Path(manifest["case_dir"]) / "first_aid_result.json"
    assert fa_file.exists()
    assert "first_aid_result.json" in manifest["files_written"]

    data = json.loads(fa_file.read_text(encoding="utf-8"))
    assert data["status"] == "DRAFT_REVIEW_REQUIRED"
    assert data["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 14. Escribe first_aid_owner_summary.md si existe
# ---------------------------------------------------------------------------
def test_writes_first_aid_owner_summary_md_when_present(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_first_aid()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    md_file = Path(manifest["case_dir"]) / "first_aid_owner_summary.md"
    assert md_file.exists()
    assert "first_aid_owner_summary.md" in manifest["files_written"]

    content = md_file.read_text(encoding="utf-8")
    assert "First Aid" in content


# ---------------------------------------------------------------------------
# 15. README menciona First Aid
# ---------------------------------------------------------------------------
def test_readme_mentions_first_aid(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    readme = Path(manifest["case_dir"]) / "README.txt"
    content = readme.read_text(encoding="utf-8").lower()
    assert "first aid" in content
    assert "revision humana" in content
