"""
Audit tests for SERVICE_1_CONTROLLED_EXECUTION_RESULT_TO_DELIVERY_PACKET_V1.

Scope: delivery packet builder only (READY execution result -> deliverables on
disk under an authorized output_dir). These tests do NOT authorize
runtime/product/diagnosis, do NOT execute external tools, and write ONLY under
temporary directories created by pytest. Full-chain tests use real fixtures so
the execution result reaches CONTROLLED_EXECUTION_RESULT_READY.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_intake,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_conn,
)
from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
    STATUS_READY as BRIDGE_READY,
    build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
)
from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
    STATUS_READY as GATE_READY,
    build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
)
from pymia.smartpyme.service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1 import (
    STATUS_OWNER_CONFIRMATION_RECHECK_READY,
    build_service_1_owner_confirmation_loop_from_controlled_execution_gate_v1 as build_loop,
)
from pymia.smartpyme.service_1_controlled_execution_ready_to_plan_packet_v1 import (
    STATUS_PLAN_READY as PLAN_READY,
    build_service_1_controlled_execution_plan_packet_v1 as build_plan,
)
from pymia.smartpyme.service_1_plan_packet_to_owner_authorization_dialogue_v1 import (
    AUTH_ACCEPT,
    STATUS_ACCEPTED as DIALOGUE_STATUS_ACCEPTED,
    build_service_1_owner_authorization_dialogue_from_plan_packet_v1 as build_dialogue,
)
from pymia.smartpyme.service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 import (
    STATUS_READY as CANDIDATE_READY,
    build_service_1_owner_authorized_plan_to_controlled_dry_run_candidate_v1 as build_candidate,
)
from pymia.smartpyme.service_1_dry_run_candidate_to_owner_validation_dialogue_v1 import (
    STATUS_ACCEPTED as VALIDATION_STATUS_ACCEPTED,
    VALIDATION_ACCEPT,
    build_service_1_owner_validation_dialogue_from_dry_run_candidate_v1 as build_validation,
)
from pymia.smartpyme.service_1_owner_validated_dry_run_to_controlled_execution_result_v1 import (
    STATUS_READY as EXEC_STATUS_READY,
    build_service_1_owner_validated_dry_run_to_controlled_execution_result_v1 as build_result,
)
from pymia.smartpyme.service_1_controlled_execution_result_to_delivery_packet_v1 import (
    BLOCK_DELIVERY_NOT_AUTHORIZED,
    BLOCK_INPUT_FLAGS_FORBIDDEN,
    BLOCK_INPUT_NOT_DICT,
    BLOCK_MISSING_OUTPUT_DIR,
    BLOCK_MISSING_RESULTS,
    BLOCK_REQUEST_FLAGS_FORBIDDEN,
    BLOCK_WRONG_STATUS,
    STATUS_READY,
    build_service_1_controlled_execution_result_to_delivery_packet_v1 as build_delivery,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT_ROOT = _REPO_ROOT.parent

_CASE_001_CANDIDATES = [
    _PARENT_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
    _REPO_ROOT / "prueba_excels" / "CASE_001_ventas_junio_2026_margin_leak.xlsx",
]


def _first_existing(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    pytest.skip(f"No fixture found among: {[str(c) for c in candidates]}")


def _assert_delivery_flags(packet: dict) -> None:
    is_ready = packet["status"] == STATUS_READY
    # Delivery flags are only True when the packet was actually created.
    assert packet["delivery_created"] is is_ready
    assert packet["product_ready"] is is_ready
    assert packet["delivery_authorized"] is is_ready
    assert packet["execution_executed"] is is_ready  # carried from exec result only when READY
    assert packet["diagnosis_generated"] is False
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False


@pytest.fixture()
def case_001_execution_result() -> dict:
    fixture = _first_existing(_CASE_001_CANDIDATES)
    packet = build_intake(local_xlsx_path=str(fixture))
    answers = {column: f"significado de {column}" for column in packet["columns"]}
    connector = build_conn(owner_question_packet=packet, owner_answers=answers)
    bridge = build_bridge(ingestion_output=connector["ingestion_output"])
    assert bridge["status"] == BRIDGE_READY
    gate = build_gate(semantic_bridge_packet=bridge)
    assert gate["status"] == GATE_READY
    ready_gate = gate
    plan = build_plan(gate_packet=ready_gate)
    assert plan["status"] == PLAN_READY
    dialogue = build_dialogue(plan_packet=plan, owner_authorization=AUTH_ACCEPT)
    assert dialogue["status"] == DIALOGUE_STATUS_ACCEPTED
    candidate = build_candidate(owner_authorization_dialogue_packet=dialogue)
    assert candidate["status"] == CANDIDATE_READY
    validation = build_validation(dry_run_candidate_packet=candidate, owner_validation=VALIDATION_ACCEPT)
    assert validation["status"] == VALIDATION_STATUS_ACCEPTED
    result = build_result(owner_validation_dialogue_packet=validation)
    assert result["status"] == EXEC_STATUS_READY
    return result


# --- 1. Full chain -> delivery READY (authorized) -------------------------

def test_case_001_delivery_authorized_ready(case_001_execution_result: dict, tmp_path: Path) -> None:
    out = build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=str(tmp_path / "delivery"),
        delivery_authorized=True,
    )
    assert out["status"] == STATUS_READY
    _assert_delivery_flags(out)
    # The 4 deliverables must exist on disk.
    names = {d["name"] for d in out["deliverables"]}
    assert names == {"README.md", "manifest.json", "execution_result.json", "hashes.json"}
    for d in out["deliverables"]:
        assert Path(d["path"]).exists()

    # manifest lists the delivered files.
    manifest = json.loads((Path(out["output_dir"]) / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["files"]) == names
    # hashes.json is deterministic SHA-256 over the 3 data files.
    hashes = json.loads((Path(out["output_dir"]) / "hashes.json").read_text(encoding="utf-8"))
    assert hashes["algorithm"] == "sha256"
    for name in ("manifest.json", "execution_result.json", "README.md"):
        content = (Path(out["output_dir"]) / name).read_text(encoding="utf-8")
        import hashlib

        assert hashes["files"][name] == hashlib.sha256(content.encode("utf-8")).hexdigest()


def test_delivery_is_deterministic(case_001_execution_result: dict, tmp_path: Path) -> None:
    a = build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=str(tmp_path / "a"),
        delivery_authorized=True,
    )
    b = build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=str(tmp_path / "b"),
        delivery_authorized=True,
    )
    ha = json.loads((Path(a["output_dir"]) / "hashes.json").read_text(encoding="utf-8"))
    hb = json.loads((Path(b["output_dir"]) / "hashes.json").read_text(encoding="utf-8"))
    assert ha == hb


# --- 2. No authorization -> BLOCKED, no writes ---------------------------

def test_no_delivery_authorized_blocks(case_001_execution_result: dict, tmp_path: Path) -> None:
    out = build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=str(tmp_path / "blocked"),
        delivery_authorized=False,
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_DELIVERY_NOT_AUTHORIZED
    _assert_delivery_flags(out)
    # Nothing was written to disk.
    assert not (tmp_path / "blocked").exists()


# --- 3. Blocks ------------------------------------------------------------

@pytest.mark.parametrize(
    "flag",
    [
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "diagnosis_generated",
    ],
)
def test_block_request_flags_true(case_001_execution_result: dict, flag: str, tmp_path: Path) -> None:
    out = build_delivery(
        **{
            "controlled_execution_result_packet": case_001_execution_result,
            "output_dir": str(tmp_path / "blk"),
            "delivery_authorized": True,
            flag: True,
        }
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_REQUEST_FLAGS_FORBIDDEN
    _assert_delivery_flags(out)


def test_block_input_not_dict(tmp_path: Path) -> None:
    for bad in (None, {}, ["x"]):
        out = build_delivery(
            controlled_execution_result_packet=bad,
            output_dir=str(tmp_path / "blk"),
            delivery_authorized=True,
        )
        assert out["blocked_reason"] == BLOCK_INPUT_NOT_DICT
        _assert_delivery_flags(out)


def test_block_wrong_status(tmp_path: Path) -> None:
    out = build_delivery(
        controlled_execution_result_packet={"status": "BLOCKED", "results": [{"step": 1}]},
        output_dir=str(tmp_path / "blk"),
        delivery_authorized=True,
    )
    assert out["blocked_reason"] == BLOCK_WRONG_STATUS


def test_block_input_flags_true(case_001_execution_result: dict, tmp_path: Path) -> None:
    tainted = dict(case_001_execution_result)
    tainted["delivery_authorized"] = True
    out = build_delivery(
        controlled_execution_result_packet=tainted,
        output_dir=str(tmp_path / "blk"),
        delivery_authorized=True,
    )
    assert out["blocked_reason"] == BLOCK_INPUT_FLAGS_FORBIDDEN


def test_block_missing_results(case_001_execution_result: dict, tmp_path: Path) -> None:
    bad = dict(case_001_execution_result)
    bad.pop("results", None)
    out = build_delivery(
        controlled_execution_result_packet=bad,
        output_dir=str(tmp_path / "blk"),
        delivery_authorized=True,
    )
    assert out["blocked_reason"] == BLOCK_MISSING_RESULTS


def test_block_missing_output_dir(case_001_execution_result: dict) -> None:
    out = build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=None,
        delivery_authorized=True,
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_MISSING_OUTPUT_DIR


# --- 4. Stability ---------------------------------------------------------

def test_does_not_mutate_execution_result(case_001_execution_result: dict, tmp_path: Path) -> None:
    before_status = case_001_execution_result["status"]
    before_results = list(case_001_execution_result["results"])
    build_delivery(
        controlled_execution_result_packet=case_001_execution_result,
        output_dir=str(tmp_path / "m"),
        delivery_authorized=True,
    )
    assert case_001_execution_result["status"] == before_status
    assert list(case_001_execution_result["results"]) == before_results
