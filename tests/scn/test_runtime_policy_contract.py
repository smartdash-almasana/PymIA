from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "docs" / "contracts" / "scn" / "runtime_policy.example.yaml"


def load_policy() -> dict:
    return yaml.safe_load(POLICY.read_text(encoding="utf-8"))


def test_runtime_policy_allows_only_scn_safe_actions():
    policy = load_policy()
    allowed = set(policy["allowed_actions"])

    assert allowed == {
        "collect_evidence",
        "request_missing_data",
        "submit_evidence_candidate",
        "request_kernel_evaluation",
        "render_pymia_output",
    }


def test_runtime_policy_forbids_hermes_authority_and_live_channels():
    policy = load_policy()
    forbidden = set(policy["forbidden_actions"])

    assert "generate_findings" in forbidden
    assert "reinterpret_kernel_output" in forbidden
    assert "perform_financial_diagnosis" in forbidden
    assert "emit_operational_truth" in forbidden
    assert "persist_clinical_memory" in forbidden
    assert "create_kernel_logic_skill" in forbidden
    assert "bypass_boundary_layer" in forbidden
    assert "use_real_telegram_in_sandbox" in forbidden
    assert "execute_mcp3_without_authorization" in forbidden


def test_runtime_policy_fails_closed_on_boundary_breaks():
    policy = load_policy()
    fail_closed_on = set(policy["fail_closed_on"])

    assert "invalid_evidence_candidate" in fail_closed_on
    assert "missing_kernel_result" in fail_closed_on
    assert "invalid_operational_audit_result" in fail_closed_on
    assert "missing_sovereign_mark" in fail_closed_on
    assert "forbidden_inferences_not_propagated" in fail_closed_on
    assert "hermes_attempts_to_generate_finding" in fail_closed_on
    assert "policy_conflict" in fail_closed_on
    assert "kernel_error" in fail_closed_on
