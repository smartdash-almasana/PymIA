from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "docs" / "contracts" / "scn" / "runtime_policy.example.yaml"


def load_policy() -> dict:
    return yaml.safe_load(POLICY.read_text(encoding="utf-8"))


def test_policy_forbids_hermes_from_producing_truth():
    policy = load_policy()
    forbidden = set(policy["forbidden_actions"])

    assert {"generate_findings", "emit_operational_truth", "perform_financial_diagnosis"} <= forbidden


def test_policy_forbids_live_channels_and_boundary_bypass():
    policy = load_policy()
    forbidden = set(policy["forbidden_actions"])

    assert {"use_real_telegram_in_sandbox", "execute_mcp3_without_authorization", "bypass_boundary_layer"} <= forbidden


def test_policy_fails_closed_on_missing_sovereign_controls():
    policy = load_policy()
    fail_closed_on = set(policy["fail_closed_on"])

    assert {"missing_sovereign_mark", "forbidden_inferences_not_propagated", "policy_conflict"} <= fail_closed_on


def test_policy_fails_closed_when_hermes_attempts_findings():
    policy = load_policy()
    fail_closed_on = set(policy["fail_closed_on"])

    assert "hermes_attempts_to_generate_finding" in fail_closed_on
