"""
Audit tests for SERVICE_1_ASSISTED_FLOW_ORCHESTRATOR_V1.

Scope: end-to-end orchestrator only. Composes the 12 audited links and (when
authorized) produces a delivery. These tests do NOT run an LLM, do NOT touch the
legacy CLI, do NOT duplicate XLSX parsing, and write ONLY under tmp_path via the
final delivery module. Full-chain tests use the real CASE_001 fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_assisted_flow_orchestrator_v1 import (
    LINK_AUTH_DIALOGUE,
    LINK_BOUNDARY,
    LINK_DELIVERY,
    LINK_EXECUTION_RESULT,
    LINK_GATE,
    LINK_GATE_RECHECK,
    LINK_PLAN,
    LINK_SEMANTIC_BRIDGE,
    LINK_VALIDATION,
    STATUS_READY,
    build_service_1_assisted_flow_orchestrator_v1 as run_flow,
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


def _full_answers(columns: list[str]) -> dict[str, str]:
    return {column: f"respuesta {column}" for column in columns}


@pytest.fixture()
def case_001_path() -> Path:
    return _first_existing(_CASE_001_CANDIDATES)


@pytest.fixture()
def case_001_columns(case_001_path: Path) -> list[str]:
    from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
        build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
    )

    packet = build_boundary(local_xlsx_path=str(case_001_path))
    return list(packet["columns"])


@pytest.fixture()
def semantic_answers(case_001_path: Path) -> dict[str, str]:
    return _semantic_answers_for_gate(case_001_path)


def _semantic_answers_for_gate(case_001_path: Path) -> dict[str, str]:
    """Answer exactly the columns the gate asks the owner to confirm."""
    from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
        build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
    )
    from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
        build_service_1_canonical_ingestion_output_from_owner_confirmation_v1 as build_connector,
    )
    from pymia.smartpyme.service_1_canonical_ingestion_output_to_semantic_bridge_v1 import (
        build_service_1_semantic_bridge_from_canonical_ingestion_output_v1 as build_bridge,
    )
    from pymia.smartpyme.service_1_semantic_bridge_to_controlled_execution_gate_v1 import (
        build_service_1_controlled_execution_gate_from_semantic_bridge_v1 as build_gate,
    )

    cols = list(build_boundary(local_xlsx_path=str(case_001_path))["columns"])
    connector = build_connector(owner_question_packet=build_boundary(local_xlsx_path=str(case_001_path)), owner_answers={c: f"r {c}" for c in cols})
    gate = build_gate(semantic_bridge_packet=build_bridge(ingestion_output=connector["ingestion_output"]))
    return {q["column_name"]: f"rol {q['column_name']}" for q in gate["owner_questions"]}


# --- 1. Happy path -> delivery READY + 4 files ---------------------------

def test_case_001_happy_path_delivery_ready(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        owner_authorization="accept",
        owner_validation="accept",
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )

    assert out["status"] == STATUS_READY
    # The trace must span the full chain (boundary .. delivery).
    trace = out["trace"]
    assert trace[LINK_BOUNDARY] == "NEEDS_OWNER_CONFIRMATION"
    assert trace[LINK_SEMANTIC_BRIDGE] == "SEMANTIC_CANDIDATES_READY"
    assert trace[LINK_GATE] in ("CONTROLLED_EXECUTION_CANDIDATE_READY", "NEEDS_OWNER_CONFIRMATION")
    assert trace[LINK_AUTH_DIALOGUE] == "OWNER_AUTHORIZATION_ACCEPTED"
    assert trace[LINK_VALIDATION] == "OWNER_VALIDATION_ACCEPTED"
    assert trace[LINK_EXECUTION_RESULT] == "CONTROLLED_EXECUTION_RESULT_READY"
    assert trace[LINK_DELIVERY] == "DELIVERY_PACKET_READY"
    assert len(trace) == 13  # 12 links + delivery

    delivery = out["delivery_packet"]
    names = {d["name"] for d in delivery["deliverables"]}
    assert names == {"README.md", "manifest.json", "execution_result.json", "hashes.json"}
    for d in delivery["deliverables"]:
        assert Path(d["path"]).exists()

    assert out["delivery_created"] is True
    assert out["delivery_authorized"] is True
    assert out["product_ready"] is True
    assert out["runtime_authorized"] is False
    assert out["diagnosis_generated"] is False


# --- 2. Missing owner answers -> BLOCKED before semantic READY -----------

def test_missing_owner_column_answers_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers={},  # missing everything
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    # Connector should have failed (missing answers) before the semantic bridge.
    assert out["blocked_at_link"] == "owner_confirmation_to_ingestion"
    assert out["trace"][LINK_BOUNDARY] == "NEEDS_OWNER_CONFIRMATION"
    assert "semantic_bridge" not in out["trace"] or out["trace"].get("semantic_bridge") != "SEMANTIC_CANDIDATES_READY"
    assert out["delivery_created"] is False


# --- 3. Auth reject / validation reject -> BLOCKED, no delivery ----------

def test_auth_reject_blocks_no_delivery(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        owner_authorization="reject",
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_at_link"] == LINK_AUTH_DIALOGUE
    assert out["delivery_created"] is False
    assert not (tmp_path / "delivery").exists()


def test_validation_reject_blocks_no_delivery(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        owner_validation="reject",
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_at_link"] == LINK_VALIDATION
    assert out["delivery_created"] is False
    assert not (tmp_path / "delivery").exists()


# --- 4. No delivery_authorized -> BLOCKED, no writes ----------------------

def test_no_delivery_authorized_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=False,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_at_link"] == LINK_DELIVERY
    assert out["delivery_created"] is False
    assert not (tmp_path / "delivery").exists()


# --- 5. Determinism / no writes outside output_dir -----------------------

def test_deterministic_trace(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    a = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=str(tmp_path / "a"),
    )
    b = run_flow(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=str(tmp_path / "b"),
    )
    assert a["status"] == b["status"] == STATUS_READY
    assert a["trace"] == b["trace"]
