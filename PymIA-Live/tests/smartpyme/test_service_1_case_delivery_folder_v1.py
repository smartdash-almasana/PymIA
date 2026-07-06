from __future__ import annotations

import json
import sys
from pathlib import Path

from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    build_service_1_delivery_policy_guard_v1,
    build_service_1_human_review_gate_v1,
    evaluate_service_1_final_delivery_folder_gate_v1,
    finalize_service_1_case_delivery_folder_v1,
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
    assert "confirmacion del dueno" in content


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
    assert "control de politica de entrega" in content


def test_finalize_writes_canonical_manifest_and_final_qa(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    (case_dir / "operator_packet.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )

    final_manifest = finalize_service_1_case_delivery_folder_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
    )

    assert final_manifest["manifest_type"] == "SERVICE_1_CANONICAL_DELIVERY_MANIFEST"
    assert final_manifest["runtime_authorized"] is False
    assert final_manifest["delivery_status"] == "READY_FOR_DELIVERY_POLICY_GUARD"
    assert (case_dir / "manifest.json").exists()
    assert (case_dir / "final_qa_delivery_gate.json").exists()
    assert (case_dir / "delivery_policy_guard.json").exists()
    assert final_manifest["final_qa_delivery_gate"]["status"] == "PASS"
    assert final_manifest["delivery_policy_guard"]["status"] == "PENDING_DELIVERY_POLICY_GUARD"
    assert final_manifest["delivery_policy_guard"]["delivery_policy_guard_required"] is True
    assert final_manifest["human_review_gate"]["status"] == "PENDING_DELIVERY_POLICY_GUARD"
    assert all("sha256" in file_record for file_record in final_manifest["files"])


def test_finalize_blocks_runtime_authorized_true(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    packet["taskspec_patch"] = {"runtime_authorized": True}
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    (case_dir / "operator_packet.json").write_text(
        json.dumps(packet, indent=2), encoding="utf-8"
    )

    final_manifest = finalize_service_1_case_delivery_folder_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
    )

    assert final_manifest["delivery_status"] == "BLOCKED"
    assert final_manifest["final_qa_delivery_gate"]["status"] == "BLOCKED"



def test_finalize_manifest_does_not_hash_itself(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    (case_dir / "operator_packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    final_manifest = finalize_service_1_case_delivery_folder_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
    )

    filenames = [record["filename"] for record in final_manifest["files"]]
    assert "manifest.json" not in filenames
    assert final_manifest["hash_policy"]["excluded_files"] == ["manifest.json"]



def test_final_qa_blocks_incomplete_manifest_record(tmp_path) -> None:
    base_dir = tmp_path / "cases"
    packet = _packet_with_structure()
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=str(base_dir))
    case_dir = Path(manifest["case_dir"])
    (case_dir / "operator_packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    records = [{"filename": "README.txt"}]
    gate = evaluate_service_1_final_delivery_folder_gate_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
        human_review_gate=packet["delivery_policy_guard"],
        manifest_file_records=records,
    )

    assert gate["status"] == "BLOCKED"


def test_legacy_human_review_gate_builder_is_alias_to_delivery_policy_guard() -> None:
    packet = _minimal_packet()

    assert build_service_1_human_review_gate_v1(packet) == build_service_1_delivery_policy_guard_v1(packet)
