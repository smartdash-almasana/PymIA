from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_synthetic_real_owner_evidence_case_v1 import (
    run_service_1_synthetic_real_owner_evidence_case_v1,
)


def test_synthetic_real_owner_evidence_case_runs_current_service_1_flow(tmp_path: Path) -> None:
    result = run_service_1_synthetic_real_owner_evidence_case_v1(tmp_path)

    assert result["exit_code"] == 0
    assert result["synthetic_data"] is True
    assert result["real_client_data"] is False
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False
    assert result["case_dir"] is not None
    assert Path(result["case_dir"]).exists()
    assert result["product_gate_status"] in {
        "READY_FOR_OWNER_DELIVERY",
        "NEEDS_OWNER_EVIDENCE",
        "NEEDS_FILE_EVIDENCE",
        "NEEDS_SCOPE_REDUCTION",
        "BLOCKED",
    }


def test_synthetic_real_owner_evidence_case_persists_expected_artifacts(tmp_path: Path) -> None:
    result = run_service_1_synthetic_real_owner_evidence_case_v1(tmp_path)

    assert result["manifest_status"] is not None
    assert result["product_gate_status"] is not None

    artifacts_present = result["artifacts_present"]
    for name in (
        "question_bundle.json",
        "owner_reentry_bridge.json",
        "pipeline_result.json",
        "evidence_loop_status.json",
        "case_record.json",
        "owner_delivery_packet.json",
        "product_gate.json",
        "manifest.json",
        "operator_packet.json",
    ):
        assert artifacts_present[name] is True

    operator_packet_status = result["operator_packet_status"]
    assert operator_packet_status["has_question_bundle"] is True
    assert operator_packet_status["has_owner_reentry_bridge"] is True
    assert operator_packet_status["has_pipeline_result"] is True
    assert operator_packet_status["has_product_gate"] is True
