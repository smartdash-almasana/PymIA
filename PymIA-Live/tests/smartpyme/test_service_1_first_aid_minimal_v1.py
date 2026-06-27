from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_first_aid_minimal_v1 import (
    load_confirmed_columns_v1,
    evaluate_first_aid_minimal_eligibility_v1,
    run_first_aid_minimal_v1,
    render_first_aid_owner_summary_v1,
)


def _find_xlsx_fixture() -> Path:
    repo_root = Path(__file__).resolve().parent.parent.parent
    candidates = [
        repo_root / "prueba_excels" / "cafeteria_abc.xlsx",
        repo_root / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx",
    ]
    for c in candidates:
        if c.exists():
            return c
    pytest.skip("No XLSX fixture found")


def _complete_packet(confirmed_columns: dict | None = None) -> dict:
    """Build a complete packet that should pass eligibility."""
    cc = confirmed_columns or {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "confirmed_columns": {
            "Cantidad": {"role": "quantity"},
            "Precio": {"role": "price"},
            "Total": {"role": "amount"},
        },
        "runtime_authorized": False,
        "warnings": [],
    }

    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "asset": {"asset_id": "test_asset_001"},
        "owner_message": "Mensaje de prueba.",
        "runtime_authorized": False,
        "detected_structure": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "workbook": {
                "sheet_count": 1,
                "sheets": [
                    {
                        "name": "Hoja1",
                        "max_row": 10,
                        "max_column": 5,
                        "headers": ["Producto", "Cantidad", "Precio", "Total"],
                        "empty_header_count": 0,
                        "sample_rows_count": 9,
                    }
                ],
            },
            "runtime_authorized": False,
        },
        "column_confirmation_packet": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "packet_type": "COLUMN_CONFIRMATION",
            "status": "NEEDS_OWNER_CONFIRMATION",
            "questions": [{"question_id": "col_confirm_001"}],
            "runtime_authorized": False,
        },
        "confirmed_columns": cc,
        "case_delivery_manifest": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "case_id": "case_test",
            "runtime_authorized": False,
        },
        "qa_delivery_gate": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "gate_type": "QA_DELIVERY_GATE",
            "status": "PASS",
            "runtime_authorized": False,
        },
    }


# ---------------------------------------------------------------------------
# 1. load_confirmed_columns_v1 carga JSON válido
# ---------------------------------------------------------------------------

def test_load_confirmed_columns_loads_valid_json(tmp_path) -> None:
    """load_confirmed_columns_v1 must load a valid JSON and return expected shape."""
    cc_file = tmp_path / "confirmed_columns.json"
    cc_file.write_text(
        json.dumps(
            {
                "confirmed_columns": {
                    "Cantidad": {"role": "quantity"},
                    "Precio": {"role": "price"},
                }
            }
        ),
        encoding="utf-8",
    )

    result = load_confirmed_columns_v1(cc_file)

    assert result["schema_version"] == "1.0"
    assert result["service_name"] == "SERVICE_1"
    assert "Cantidad" in result["confirmed_columns"]
    assert "Precio" in result["confirmed_columns"]


# ---------------------------------------------------------------------------
# 2. confirmed_columns runtime_authorized false
# ---------------------------------------------------------------------------

def test_confirmed_columns_runtime_authorized_false(tmp_path) -> None:
    """load_confirmed_columns_v1 must always return runtime_authorized=False."""
    cc_file = tmp_path / "confirmed_columns.json"
    cc_file.write_text(
        json.dumps({"confirmed_columns": {"Col1": {"role": "text"}}}),
        encoding="utf-8",
    )

    result = load_confirmed_columns_v1(cc_file)
    assert result["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 3. eligibility ELIGIBLE con packet completo + confirmed_columns + qa PASS
# ---------------------------------------------------------------------------

def test_eligibility_eligible_with_complete_packet() -> None:
    """Complete packet + confirmed_columns + qa PASS → ELIGIBLE."""
    packet = _complete_packet()
    gate = evaluate_first_aid_minimal_eligibility_v1(packet)

    assert gate["status"] == "ELIGIBLE"
    assert gate["runtime_authorized"] is False
    assert gate["human_review_required"] is True
    assert gate["gate_type"] == "FIRST_AID_MINIMAL_ELIGIBILITY"
    assert len(gate["blockers"]) == 0


# ---------------------------------------------------------------------------
# 4. eligibility BLOCKED sin confirmed_columns
# ---------------------------------------------------------------------------

def test_eligibility_blocked_without_confirmed_columns() -> None:
    """Missing confirmed_columns → BLOCKED."""
    packet = _complete_packet()
    del packet["confirmed_columns"]

    gate = evaluate_first_aid_minimal_eligibility_v1(packet)
    assert gate["status"] == "BLOCKED"
    assert any("confirmed_columns" in b for b in gate["blockers"])


# ---------------------------------------------------------------------------
# 5. eligibility BLOCKED si qa_delivery_gate != PASS
# ---------------------------------------------------------------------------

def test_eligibility_blocked_if_qa_gate_not_pass() -> None:
    """qa_delivery_gate.status != PASS → BLOCKED."""
    packet = _complete_packet()
    packet["qa_delivery_gate"]["status"] = "BLOCKED"

    gate = evaluate_first_aid_minimal_eligibility_v1(packet)
    assert gate["status"] == "BLOCKED"
    assert any("qa_delivery_gate" in b for b in gate["blockers"])


# ---------------------------------------------------------------------------
# 6. eligibility BLOCKED si runtime_authorized true en cualquier nivel
# ---------------------------------------------------------------------------

def test_eligibility_blocked_if_runtime_authorized_true_anywhere() -> None:
    """runtime_authorized=True anywhere → BLOCKED."""
    packet = _complete_packet()
    packet["detected_structure"]["runtime_authorized"] = True

    gate = evaluate_first_aid_minimal_eligibility_v1(packet)
    assert gate["status"] == "BLOCKED"
    assert any("runtime_authorized" in b for b in gate["blockers"])


# ---------------------------------------------------------------------------
# 7. first_aid_result status DRAFT_REVIEW_REQUIRED
# ---------------------------------------------------------------------------

def test_first_aid_result_status_draft_review_required(tmp_path) -> None:
    """run_first_aid_minimal_v1 must return status DRAFT_REVIEW_REQUIRED."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()

    result = run_first_aid_minimal_v1(packet, xlsx_path)

    assert result["status"] == "DRAFT_REVIEW_REQUIRED"
    assert result["result_type"] == "FIRST_AID_MINIMAL"


# ---------------------------------------------------------------------------
# 8. first_aid_result human_review_required true
# ---------------------------------------------------------------------------

def test_first_aid_result_human_review_required_true(tmp_path) -> None:
    """run_first_aid_minimal_v1 must have human_review_required=True."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()

    result = run_first_aid_minimal_v1(packet, xlsx_path)
    assert result["human_review_required"] is True


# ---------------------------------------------------------------------------
# 9. first_aid_result runtime_authorized false
# ---------------------------------------------------------------------------

def test_first_aid_result_runtime_authorized_false(tmp_path) -> None:
    """run_first_aid_minimal_v1 must have runtime_authorized=False."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()

    result = run_first_aid_minimal_v1(packet, xlsx_path)
    assert result["runtime_authorized"] is False


# ---------------------------------------------------------------------------
# 10. No expone diagnosis/accounting_result/recommendation fuerte
# ---------------------------------------------------------------------------

_FORBIDDEN_KEYS = [
    "diagnosis",
    "accounting_result",
    "recommendation",
    "final_diagnosis",
    "business_diagnosis",
    "strong_recommendation",
    "prescriptive_action",
]


def test_first_aid_result_does_not_expose_forbidden_keys(tmp_path) -> None:
    """Result must not contain diagnosis/accounting_result/strong recommendation keys."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()

    result = run_first_aid_minimal_v1(packet, xlsx_path)

    def _check_forbidden(obj):
        if isinstance(obj, dict):
            for key in obj:
                assert key not in _FORBIDDEN_KEYS, f"Forbidden key found: {key}"
                _check_forbidden(obj[key])
        elif isinstance(obj, list):
            for item in obj:
                _check_forbidden(item)

    _check_forbidden(result)


# ---------------------------------------------------------------------------
# 11. No muta packet original
# ---------------------------------------------------------------------------

def test_first_aid_does_not_mutate_packet(tmp_path) -> None:
    """run_first_aid_minimal_v1 must not modify the input packet."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()
    original = json.dumps(packet, sort_keys=True)

    run_first_aid_minimal_v1(packet, xlsx_path)

    after = json.dumps(packet, sort_keys=True)
    assert after == original


# ---------------------------------------------------------------------------
# 12. No importa módulos prohibidos
# ---------------------------------------------------------------------------

_FORBIDDEN_MODULES = [
    "pymia.smartpyme.vertical_pipeline",
    "pymia.smartpyme.service_1_pipeline_v1",
    "pymia.smartpyme.service_1_fsm_decision_patch_v1",
    "pymia.smartpyme.service_1_owner_answer_reentry_v1",
    "pymia.application.vertical_pipeline",
    "tools.document_ingestion",
    "openai",
    "chatbot",
]


def test_module_does_not_import_forbidden_modules() -> None:
    """AST scan: module source must not import forbidden modules."""
    mod_path = (
        Path(__file__).resolve().parent.parent.parent
        / "pymia"
        / "smartpyme"
        / "service_1_first_aid_minimal_v1.py"
    )
    source = mod_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_names = {m.rsplit(".", 1)[-1] for m in _FORBIDDEN_MODULES}
    forbidden_full = set(_FORBIDDEN_MODULES)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden_full, (
                    f"Forbidden import: {alias.name}"
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert node.module not in forbidden_full, (
                    f"Forbidden from-import: {node.module}"
                )
                for alias in node.names:
                    full = f"{node.module}.{alias.name}"
                    assert full not in forbidden_full


# ---------------------------------------------------------------------------
# Extra: render_first_aid_owner_summary_v1 produces markdown
# ---------------------------------------------------------------------------

def test_render_first_aid_owner_summary_produces_markdown(tmp_path) -> None:
    """render_first_aid_owner_summary_v1 must produce non-empty markdown."""
    xlsx_path = _find_xlsx_fixture()
    packet = _complete_packet()

    result = run_first_aid_minimal_v1(packet, xlsx_path)
    md = render_first_aid_owner_summary_v1(result)

    assert len(md) > 0
    assert "First Aid mínimo" in md
    assert "DRAFT_REVIEW_REQUIRED" in md
    assert "Runtime autorizado" in md


# ---------------------------------------------------------------------------
# Extra: load_confirmed_columns_v1 raises FileNotFoundError
# ---------------------------------------------------------------------------

def test_load_confirmed_columns_raises_file_not_found(tmp_path) -> None:
    """Non-existent file → FileNotFoundError."""
    fake_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_confirmed_columns_v1(fake_path)
