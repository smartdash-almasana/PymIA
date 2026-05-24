import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "pymia" / "contracts" / "scn_render_contract.py"
SPEC = importlib.util.spec_from_file_location("scn_render_contract", MODULE_PATH)
scn_render_contract = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(scn_render_contract)

SCNBoundaryError = scn_render_contract.SCNBoundaryError
build_render_contract = scn_render_contract.build_render_contract


def valid_result(**overrides):
    data = {
        "schema_version": "scn.operational_audit_result.v1",
        "result_id": "result-1",
        "tenant_id": "tenant-1",
        "status": "ok",
        "findings": ["internal finding should not be rendered"],
        "evidence_used": ["ev-1"],
        "missing_evidence": [],
        "allowed_rendering": {
            "summary": "Allowed operational summary.",
            "next_questions": [],
            "next_steps": ["Review costs."],
            "references": ["ev-1"],
        },
        "forbidden_inferences": ["Do not infer margin without costs."],
        "audit_trail_ref": "audit-1",
        "sovereign_mark": "pymia-sovereign-mark",
        "created_at": "2026-05-24T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_build_render_contract_excludes_findings_and_preserves_forbidden_inferences():
    contract = build_render_contract(valid_result(), render_id="render-1", created_at="2026-05-24T00:00:00Z")

    assert contract["schema_version"] == "scn.render_contract.v1"
    assert contract["render_id"] == "render-1"
    assert contract["result_ref"] == "result-1"
    assert contract["tenant_id"] == "tenant-1"
    assert contract["summary"] == "Allowed operational summary."
    assert contract["next_steps"] == ["Review costs."]
    assert contract["forbidden_inferences"] == ["Do not infer margin without costs."]
    assert "findings" not in contract


def test_build_render_contract_blocks_without_sovereign_mark():
    with pytest.raises(SCNBoundaryError, match="missing sovereign_mark"):
        build_render_contract(valid_result(sovereign_mark=""))


def test_build_render_contract_pending_data_uses_missing_evidence_as_questions_and_no_steps():
    contract = build_render_contract(
        valid_result(
            status="pending_data",
            missing_evidence=["cost invoices", "sales period"],
            allowed_rendering={"summary": "Pending evidence."},
        )
    )

    assert contract["blocked_message"]
    assert contract["next_questions"] == ["cost invoices", "sales period"]
    assert contract["next_steps"] == []


def test_build_render_contract_requires_allowed_rendering_mapping():
    with pytest.raises(SCNBoundaryError, match="allowed_rendering must be a mapping"):
        build_render_contract(valid_result(allowed_rendering="not-a-mapping"))
