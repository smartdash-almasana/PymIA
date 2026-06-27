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


# ---------------------------------------------------------------------------
# 1. Crea carpeta de caso
# ---------------------------------------------------------------------------

def test_creates_case_folder(tmp_path) -> None:
    """Module must create the case directory under base_dir."""
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
    """owner_message.md must contain the packet's owner_message."""
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()

    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))

    owner_md = Path(manifest["case_dir"]) / "owner_message.md"
    assert owner_md.exists()
    content = owner_md.read_text(encoding="utf-8")
    assert "Mensaje de prueba para el dueno" in content


# ---------------------------------------------------------------------------
# 3. Escribe operator_packet.json como parte del manifest (lo escribe el CLI,
#    pero el manifest lo lista en files_written)
# ---------------------------------------------------------------------------

def test_manifest_lists_operator_packet_json(tmp_path) -> None:
    """The manifest must include operator_packet.json in files_written."""
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()

    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))

    assert "operator_packet.json" in manifest["files_written"]


# ---------------------------------------------------------------------------
# 4. Escribe detected_structure.json si existe
# ---------------------------------------------------------------------------

def test_writes_detected_structure_json_when_present(tmp_path) -> None:
    """detected_structure.json must be written when packet has detected_structure."""
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()

    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))

    ds_file = Path(manifest["case_dir"]) / "detected_structure.json"
    assert ds_file.exists()
    assert "detected_structure.json" in manifest["files_written"]

    data = json.loads(ds_file.read_text(encoding="utf-8"))
    assert data["service_name"] == "SERVICE_1"
    assert data["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 5. Escribe column_confirmation_packet.json si existe
# ---------------------------------------------------------------------------

def test_writes_column_confirmation_packet_json_when_present(tmp_path) -> None:
    """column_confirmation_packet.json must be written when packet has it."""
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()

    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))

    cc_file = Path(manifest["case_dir"]) / "column_confirmation_packet.json"
    assert cc_file.exists()
    assert "column_confirmation_packet.json" in manifest["files_written"]

    data = json.loads(cc_file.read_text(encoding="utf-8"))
    assert data["packet_type"] == "COLUMN_CONFIRMATION"


# ---------------------------------------------------------------------------
# 6. No escribe XLSX original
# ---------------------------------------------------------------------------

def test_does_not_write_original_xlsx(tmp_path) -> None:
    """Case folder must NOT contain the original Excel file."""
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
    """Manifest must have runtime_authorized = False."""
    base_dir = tmp_path / "cases"
    packet = _minimal_packet()

    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))

    assert manifest["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 8. No muta packet original
# ---------------------------------------------------------------------------

def test_does_not_mutate_original_packet(tmp_path) -> None:
    """The input packet dict must not be modified by the function."""
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
    """README.txt must state: no diagnosis, no calculation, human confirmation needed."""
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
    """Loading this module must not import pipeline, FSM, reentry, LLM modules."""
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
