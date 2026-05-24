import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

VERIFIER_MODULE_PATH = ROOT / "pymia" / "contracts" / "scn_operational_audit_verifier.py"
VERIFIER_SPEC = importlib.util.spec_from_file_location("scn_operational_audit_verifier", VERIFIER_MODULE_PATH)
scn_operational_audit_verifier = importlib.util.module_from_spec(VERIFIER_SPEC)
assert VERIFIER_SPEC and VERIFIER_SPEC.loader
VERIFIER_SPEC.loader.exec_module(scn_operational_audit_verifier)

RENDER_MODULE_PATH = ROOT / "pymia" / "contracts" / "scn_render_contract.py"
RENDER_SPEC = importlib.util.spec_from_file_location("scn_render_contract", RENDER_MODULE_PATH)
scn_render_contract = importlib.util.module_from_spec(RENDER_SPEC)
assert RENDER_SPEC and RENDER_SPEC.loader
RENDER_SPEC.loader.exec_module(scn_render_contract)

SCNVerificationError = scn_operational_audit_verifier.SCNVerificationError
verify_operational_audit_result = scn_operational_audit_verifier.verify_operational_audit_result
build_render_contract = scn_render_contract.build_render_contract


def valid_result(**overrides):
    data = {
        "schema_version": "scn.operational_audit_result.v1",
        "result_id": "result-1",
        "tenant_id": "tenant-1",
        "status": "ok",
        "findings": [],
        "evidence_used": ["ev-1"],
        "missing_evidence": [],
        "allowed_rendering": {
            "summary": "Allowed summary",
            "next_questions": [],
            "next_steps": ["Continue"],
            "references": ["ev-1"],
        },
        "forbidden_inferences": ["Do not infer missing values."],
        "audit_trail_ref": "audit-1",
        "sovereign_mark": "pymia-mark",
        "created_at": "2026-05-24T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_valid_result_passes_and_returns_same_mapping():
    result = valid_result()
    verified = verify_operational_audit_result(result)
    assert verified is result


def test_non_mapping_blocked():
    with pytest.raises(SCNVerificationError, match="must be a mapping"):
        verify_operational_audit_result(["not-a-mapping"])


def test_missing_sovereign_mark_blocked():
    result = valid_result()
    result.pop("sovereign_mark")
    with pytest.raises(SCNVerificationError, match="missing sovereign_mark"):
        verify_operational_audit_result(result)


def test_missing_audit_trail_ref_blocked():
    result = valid_result()
    result.pop("audit_trail_ref")
    with pytest.raises(SCNVerificationError, match="missing audit_trail_ref"):
        verify_operational_audit_result(result)


def test_missing_forbidden_inferences_blocked():
    result = valid_result()
    result.pop("forbidden_inferences")
    with pytest.raises(SCNVerificationError, match="missing forbidden_inferences"):
        verify_operational_audit_result(result)


def test_invalid_status_blocked():
    with pytest.raises(SCNVerificationError, match="invalid status"):
        verify_operational_audit_result(valid_result(status="error"))


def test_forbidden_inferences_not_list_blocked():
    with pytest.raises(SCNVerificationError, match="forbidden_inferences must be a list"):
        verify_operational_audit_result(valid_result(forbidden_inferences="not-a-list"))


def test_allowed_rendering_not_mapping_blocked():
    with pytest.raises(SCNVerificationError, match="allowed_rendering must be a mapping"):
        verify_operational_audit_result(valid_result(allowed_rendering="not-a-mapping"))


def test_verifier_result_can_be_passed_to_build_render_contract():
    verified = verify_operational_audit_result(valid_result())
    contract = build_render_contract(verified, render_id="render-1", created_at="2026-05-24T00:00:00Z")
    assert contract["result_ref"] == "result-1"
