"""
Audit tests for SERVICE_1_WEB_EXPERIMENT_BACKEND_BOUNDARY_V1.

Scope: web upload transport boundary only. It must delegate 100% to the real
assisted-flow orchestrator and never parse XLSX itself. These tests do NOT run an
LLM, do NOT use the legacy CLI, do NOT use SheetJS, and write ONLY under tmp_path
via the orchestrator's delivery module. Full-chain tests use the real CASE_001
fixture (local path and raw upload bytes).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_assisted_flow_orchestrator_v1 import (
    STATUS_READY as ORCH_READY,
)
from pymia.smartpyme.service_1_web_experiment_backend_boundary_v1 import (
    BLOCK_DUAL_SOURCE,
    BLOCK_INVALID_EXTENSION,
    BLOCK_NO_SOURCE,
    STATUS_READY,
    build_service_1_web_experiment_backend_boundary_v1 as run_backend,
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
    connector = build_connector(
        owner_question_packet=build_boundary(local_xlsx_path=str(case_001_path)),
        owner_answers={c: f"r {c}" for c in cols},
    )
    gate = build_gate(semantic_bridge_packet=build_bridge(ingestion_output=connector["ingestion_output"]))
    return {q["column_name"]: f"rol {q['column_name']}" for q in gate["owner_questions"]}


@pytest.fixture()
def case_001_path() -> Path:
    return _first_existing(_CASE_001_CANDIDATES)


@pytest.fixture()
def case_001_columns(case_001_path: Path) -> list[str]:
    from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
        build_service_1_web_column_confirmation_intake_boundary_v1 as build_boundary,
    )

    return list(build_boundary(local_xlsx_path=str(case_001_path))["columns"])


@pytest.fixture()
def semantic_answers(case_001_path: Path) -> dict[str, str]:
    return _semantic_answers_for_gate(case_001_path)


# --- 1. Local happy path -> DELIVERY_READY ---------------------------------

def test_local_case_001_happy_path(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_backend(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        owner_authorization="accept",
        owner_validation="accept",
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == STATUS_READY
    assert out["orchestrator_status"] == ORCH_READY
    assert out["trace"]  # orchestrator trace propagated
    names = {d["name"] for d in out["delivery_packet"]["deliverables"]}
    assert names == {"README.md", "manifest.json", "execution_result.json", "hashes.json"}


# --- 2. Uploaded bytes happy path -> DELIVERY_READY, temp cleaned ----------

def test_uploaded_bytes_case_001_happy_path(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    raw = case_001_path.read_bytes()
    out = run_backend(
        uploaded_xlsx_bytes=raw,
        uploaded_filename="CASE_001_ventas_junio_2026_margin_leak.xlsx",
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        owner_authorization="accept",
        owner_validation="accept",
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == STATUS_READY
    assert out["orchestrator_status"] == ORCH_READY
    # No temp upload file should linger.
    leftovers = list(tmp_path.glob("s1_upload_*.xlsx"))
    assert leftovers == []


# --- 3. Missing answers -> BLOCKED, no writes -----------------------------

def test_missing_answers_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_backend(
        local_xlsx_path=str(case_001_path),
        owner_column_answers={},
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    assert out["delivery_created"] is False
    assert not (tmp_path / "delivery").exists()


# --- 4. Transport rejections ----------------------------------------------

def test_no_source_blocks(case_001_columns: list[str], semantic_answers: dict[str, str]) -> None:
    out = run_backend(
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=None,
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_NO_SOURCE


def test_dual_source_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str]) -> None:
    raw = case_001_path.read_bytes()
    out = run_backend(
        local_xlsx_path=str(case_001_path),
        uploaded_xlsx_bytes=raw,
        uploaded_filename="CASE_001.xlsx",
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=None,
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_DUAL_SOURCE


def test_invalid_extension_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str]) -> None:
    raw = case_001_path.read_bytes()
    out = run_backend(
        uploaded_xlsx_bytes=raw,
        uploaded_filename="CASE_001.csv",
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
        output_dir=None,
    )
    assert out["status"] == "BLOCKED"
    assert out["blocked_reason"] == BLOCK_INVALID_EXTENSION


# --- 5. No delivery_authorized -> BLOCKED, no writes -----------------------

def test_no_delivery_authorized_blocks(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    out = run_backend(
        local_xlsx_path=str(case_001_path),
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=False,
        output_dir=str(tmp_path / "delivery"),
    )
    assert out["status"] == "BLOCKED"
    assert out["delivery_created"] is False
    assert not (tmp_path / "delivery").exists()


# --- 6. Determinism (local == bytes) --------------------------------------

def test_local_equals_bytes(case_001_path: Path, case_001_columns: list[str], semantic_answers: dict[str, str], tmp_path: Path) -> None:
    common = dict(
        owner_column_answers=_full_answers(case_001_columns),
        semantic_owner_answers=semantic_answers,
        delivery_authorized=True,
    )
    local = run_backend(local_xlsx_path=str(case_001_path), output_dir=str(tmp_path / "a"), **common)
    uploaded = run_backend(
        uploaded_xlsx_bytes=case_001_path.read_bytes(),
        uploaded_filename="CASE_001_ventas_junio_2026_margin_leak.xlsx",
        output_dir=str(tmp_path / "b"),
        **common,
    )
    assert local["status"] == uploaded["status"] == STATUS_READY
    assert local["trace"] == uploaded["trace"]
