import pytest

from pymia.contracts.scn_output_gateway import (
    SCNVerificationError,
    build_render_contract_from_operational_audit_result,
)

build_gateway_contract = build_render_contract_from_operational_audit_result


def valid_result(**overrides):
    data = {
        "schema_version": "scn.operational_audit_result.v1",
        "result_id": "result-1",
        "tenant_id": "tenant-1",
        "status": "ok",
        "findings": ["internal sovereign finding"],
        "evidence_used": ["ev-1"],
        "missing_evidence": [],
        "allowed_rendering": {
            "summary": "Allowed summary.",
            "next_questions": [],
            "next_steps": ["Review costs."],
            "references": ["ev-1"],
        },
        "forbidden_inferences": ["Do not infer missing costs."],
        "audit_trail_ref": "audit-1",
        "sovereign_mark": "pymia-sovereign-mark",
        "created_at": "2026-05-24T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_output_gateway_verifies_and_builds_render_contract():
    contract = build_gateway_contract(
        valid_result(),
        render_id="render-1",
        created_at="2026-05-24T00:00:00Z",
    )

    assert contract["schema_version"] == "scn.render_contract.v1"
    assert contract["result_ref"] == "result-1"
    assert contract["summary"] == "Allowed summary."
    assert contract["forbidden_inferences"] == ["Do not infer missing costs."]
    assert "findings" not in contract


def test_output_gateway_blocks_invalid_operational_audit_result_before_rendering():
    with pytest.raises(SCNVerificationError, match="missing sovereign_mark"):
        build_gateway_contract(valid_result(sovereign_mark=""))


def test_output_gateway_preserves_fail_closed_pending_data():
    contract = build_gateway_contract(
        valid_result(
            status="pending_data",
            missing_evidence=["cost invoices"],
            allowed_rendering={"summary": "Pending evidence."},
        )
    )

    assert contract["blocked_message"]
    assert contract["next_questions"] == ["cost invoices"]
    assert contract["next_steps"] == []
