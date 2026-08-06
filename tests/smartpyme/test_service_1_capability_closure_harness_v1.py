from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _harness() -> dict:
    return json.loads(
        (_root() / "docs" / "service_1_capability_closure_harness.v1.json").read_text(
            encoding="utf-8"
        )
    )


def test_ren_001_is_closed_proved_and_frozen() -> None:
    harness = _harness()
    ren = next(
        item for item in harness["ordered_capabilities"] if item["pathology_code"] == "REN_001"
    )

    assert harness["baseline"]["head"] == "372fe6e"
    assert harness["current_state"] == {
        "active_capability": None,
        "active_phase": None,
        "next_capability_selected": False,
        "last_closed_capability": "REN_001",
        "last_closed_commit": "372fe6e",
    }
    assert ren["state"] == "CLOSED_AND_FROZEN"
    assert ren["close"] == "PASS"
    assert ren["prove"] == "PASS"
    assert ren["freeze"] == "PASS"
    assert ren["closure_evidence"]["delivery_function"] == "deliver_ren_001_outcome_xlsx_v1"
    assert ren["closure_evidence"]["canonical_root"] == "run_service_1_product_pipeline_v1"
    assert ren["closure_evidence"]["sheet_count"] == 7
    assert ren["closure_evidence"]["invalid_outcome_fail_closed"] is True
    assert ren["closure_evidence"]["liq_001_regression_pass"] is True
    assert ren["closure_evidence"]["runtime_authorized"] is False
    assert ren["closure_evidence"]["causal_diagnosis_generated"] is False
    assert ren["closure_evidence"]["delivery_authorized"] is False


def test_no_next_capability_is_implicitly_activated() -> None:
    harness = _harness()
    pyme_013 = next(
        item for item in harness["ordered_capabilities"] if item["pathology_code"] == "PYME_013"
    )
    pyme_026 = next(
        item for item in harness["ordered_capabilities"] if item["pathology_code"] == "PYME_026"
    )

    assert harness["execution_policy"]["automatic_next_capability"] is False
    assert harness["current_state"]["next_capability_selected"] is False
    assert pyme_013["state"] == "LOCKED_PENDING_EXPLICIT_SELECTION"
    assert pyme_013["close"] == "NOT_STARTED_PENDING_EXPLICIT_SELECTION"
    assert pyme_026["state"] == "LOCKED"
