from __future__ import annotations

import json
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _decision() -> dict:
    return json.loads(
        (_root() / "docs" / "service_1_next_productive_capability_decision.v1.json").read_text(
            encoding="utf-8"
        )
    )


def test_next_productive_capability_decision_prioritizes_ren_001() -> None:
    decision = _decision()
    assert decision["schema_version"] == "SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION_V1"
    assert decision["status"] == "DECIDED"
    assert decision["priority_order"] == [
        "CONNECT_REN_001_TO_PRODUCTIVE_ROOT",
        "COMPLETE_12_PRODUCTIVE_PATHOLOGIES",
        "DESIGN_INDUSTRIAL_SCRAP_OEE_CAPABILITIES",
    ]
    assert decision["next_authorized_cycle"] == "CYCLE_040_CONNECT_REN_001_TO_PRODUCTIVE_ROOT"


def test_ren_001_is_ready_for_integration_but_not_yet_root_reachable() -> None:
    readiness = _decision()["ren_001_readiness"]
    assert readiness["pathology_catalogued"] is True
    assert readiness["formula_catalogued"] is True
    assert readiness["deterministic_evaluator_exists"] is True
    assert readiness["mathematical_limits_exist"] is True
    assert readiness["governed_plan_validation_exists"] is True
    assert readiness["currently_root_reachable"] is False
    assert readiness["currently_cli_reachable"] is False


def test_twelve_pathology_goal_requires_complete_verticals() -> None:
    criteria = _decision()["productive_pathology_completion_criteria"]
    assert len(criteria) == 12
    assert "official root integration" in criteria
    assert "bounded non-causal finding" in criteria
    assert "current documentation and observed execution evidence" in criteria


def test_scrap_oee_remain_blocked_until_industrial_preconditions_exist() -> None:
    decision = _decision()
    preconditions = "\n".join(decision["industrial_preconditions"])
    forbidden = "\n".join(decision["cycle_040_forbidden_scope"])
    assert "availability performance and quality definitions for OEE" in preconditions
    assert "no causal diagnosis from isolated indicators" in preconditions
    assert "scrap or OEE implementation" in forbidden


def test_current_readme_lists_next_productive_capability_decision() -> None:
    root = _root()
    readme = (root / "docs" / "current" / "README.md").read_text(encoding="utf-8")
    status = (root / "docs" / "current" / "SERVICE_1_STATUS.md").read_text(encoding="utf-8")
    assert "SERVICE_1_NEXT_PRODUCTIVE_CAPABILITY_DECISION.md" in readme
    assert "12/12 PATOLOGÍAS PRODUCTIVAS CONECTADAS" in status
    assert "KERNEL_IS_FORMULA_EXECUTION_AUTHORITY" in status
