from __future__ import annotations

import ast
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _runner_text() -> str:
    return (_root() / "scripts" / "run_service_1_pilot_008_textil_completa.py").read_text(encoding="utf-8")


def test_pilot_008_runner_targets_authorized_fixture_and_sheet() -> None:
    text = _runner_text()
    assert "la_textil_cosida_srl_mar_abr_may_2026.xlsx" in text
    assert 'SHEET_NAME = "ventas"' in text
    assert "CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA" in text


def test_pilot_008_runner_uses_official_product_entrypoint() -> None:
    tree = ast.parse(_runner_text())
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "pymia.cli.service_1_product"
        for alias in node.names
    }
    assert imported == {"run_service_1_product_entrypoint_v1"}


def test_pilot_008_runner_keeps_tool_request_explicit() -> None:
    text = _runner_text()
    assert '"tool_ref": "precio_margen_basico"' in text
    assert "automatic tool selection" in text
    assert "No new formula" in text


def test_pilot_008_runner_does_not_certify_before_observation_review() -> None:
    text = _runner_text()
    assert "OBSERVED_NOT_YET_CERTIFIED" in text
    assert '"status": "PASS"' not in text
    assert "docs/service_1_pilot_008" not in text


def test_pilot_008_runner_reentry_uses_allowed_option_ids_only() -> None:
    text = _runner_text()
    assert 'question["allowed_option_ids"]' in text
    assert '{"OTHER", "IGNORE", "IGNORED_NOT_RELEVANT"}' in text
    assert "No canonical semantic option available" in text
