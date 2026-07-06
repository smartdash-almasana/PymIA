from __future__ import annotations

import json
from pathlib import Path

from pymia.smartpyme.service_1_case_delivery_folder_v1 import (
    build_service_1_delivery_policy_guard_v1,
    build_service_1_human_review_gate_v1,
    finalize_service_1_case_delivery_folder_v1,
    write_service_1_case_delivery_folder_v1,
)


def _packet_with_reentry_bridge() -> dict:
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "asset": {"asset_id": "test_asset_reentry"},
        "owner_message": "Mensaje de prueba para el dueno.",
        "runtime_authorized": False,
        "owner_reentry_bridge": {
            "schema_version": "SERVICE_1_OWNER_REENTRY_BRIDGE_V1",
            "service_name": "SERVICE_1",
            "status": "ACCEPTED_AND_PROJECTED",
            "case_id": "case_1",
            "tenant_id": "tenant_1",
            "intake_id": "intake_1",
            "question_ref": "service_1:next_questions:owner_axis_cash",
            "selected_next_pending_question_ref": "service_1:next_questions:missing_period",
            "runtime_authorized": False,
            "reexecution_authorized": False,
            "recalculation_authorized": False,
            "delivery_authorized": False,
        },
    }


def test_writes_owner_reentry_bridge_json_when_present(tmp_path: Path) -> None:
    packet = _packet_with_reentry_bridge()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=tmp_path)
    case_dir = Path(manifest["case_dir"])
    artifact = case_dir / "owner_reentry_bridge.json"

    assert artifact.exists()
    assert "owner_reentry_bridge.json" in manifest["files_written"]
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["status"] == "ACCEPTED_AND_PROJECTED"
    assert data["runtime_authorized"] is False
    assert data["delivery_authorized"] is False


def test_readme_mentions_owner_reentry_bridge(tmp_path: Path) -> None:
    packet = _packet_with_reentry_bridge()
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=tmp_path)
    readme = Path(manifest["case_dir"]) / "README.txt"

    content = readme.read_text(encoding="utf-8")
    assert "owner_reentry_bridge.json" in content
    assert "respuesta del dueno" in content


def test_finalize_manifest_hashes_owner_reentry_bridge(tmp_path: Path) -> None:
    packet = _packet_with_reentry_bridge()
    packet["delivery_policy_guard"] = build_service_1_delivery_policy_guard_v1(packet)
    manifest = write_service_1_case_delivery_folder_v1(packet, base_dir=tmp_path)
    case_dir = Path(manifest["case_dir"])
    (case_dir / "operator_packet.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    final_manifest = finalize_service_1_case_delivery_folder_v1(
        packet=packet,
        case_dir=case_dir,
        files_written=manifest["files_written"],
    )

    file_records = {record["filename"]: record for record in final_manifest["files"]}
    assert "owner_reentry_bridge.json" in file_records
    assert file_records["owner_reentry_bridge.json"]["bytes"] > 0
    assert len(file_records["owner_reentry_bridge.json"]["sha256"]) == 64
    assert final_manifest["runtime_authorized"] is False
    assert final_manifest["delivery_policy_guard"]["status"] == "PENDING_DELIVERY_POLICY_GUARD"


def test_legacy_human_review_gate_alias_matches_delivery_policy_guard() -> None:
    packet = _packet_with_reentry_bridge()

    assert build_service_1_human_review_gate_v1(packet) == build_service_1_delivery_policy_guard_v1(packet)
