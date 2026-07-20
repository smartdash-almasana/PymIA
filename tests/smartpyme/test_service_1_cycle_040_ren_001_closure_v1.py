from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs" / "service_1_cycle_040_ren_001_productive_root_closure.v1.json"
CURRENT_DOC = ROOT / "docs" / "current" / "SERVICE_1_CYCLE_040_REN_001_PRODUCTIVE_ROOT_CLOSURE.md"


def _record() -> dict[str, object]:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_cycle_040_closure_record_is_closed_pass() -> None:
    record = _record()
    assert record["cycle"] == "CYCLE_040_CONNECT_REN_001_TO_PRODUCTIVE_ROOT"
    assert record["status"] == "CLOSED_PASS"
    assert record["next_authorized_cycle"] == "CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP"


def test_cycle_040_closure_records_productive_ren_001_surface() -> None:
    capability = _record()["productive_capability"]
    assert capability["pathology_code"] == "REN_001"
    assert capability["capability_ref"] == "net_margin_real"
    assert capability["required_variables"] == ["sale_price", "costs", "taxes"]
    for field in ("product_root", "evaluator", "outcome", "normalized_evidence_adapter"):
        assert (ROOT / capability[field]).is_file()


def test_cycle_040_closure_keeps_safety_invariants_false() -> None:
    invariants = _record()["safety_invariants"]
    assert invariants == {
        "automatic_capability_selection": False,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
        "ren_001_xlsx_delivery": False,
    }


def test_cycle_040_current_doc_preserves_explicit_limits() -> None:
    text = CURRENT_DOC.read_text(encoding="utf-8")
    assert "CLOSED_PASS" in text
    assert "1671 passed" in text
    assert "La entrega XLSX de `REN_001` permanece bloqueada" in text
    assert "CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP" in text
    assert "scrap/OEE" in text
