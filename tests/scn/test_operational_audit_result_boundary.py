import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCN = ROOT / "docs" / "contracts" / "scn"


def load_schema(name: str) -> dict:
    return json.loads((SCN / name).read_text(encoding="utf-8"))


def test_operational_audit_result_requires_sovereign_mark_and_audit_trail():
    schema = load_schema("operational_audit_result.scn.schema.json")
    required = set(schema.get("required", []))

    assert "sovereign_mark" in required
    assert "audit_trail_ref" in required
    assert "forbidden_inferences" in required


def test_operational_audit_result_distinguishes_evidence_used_and_missing_evidence():
    schema = load_schema("operational_audit_result.scn.schema.json")
    props = schema["properties"]

    assert "evidence_used" in props
    assert "missing_evidence" in props
    assert props["evidence_used"] != props["missing_evidence"] or props["evidence_used"]["description"] != props["missing_evidence"]["description"]


def test_operational_audit_result_status_supports_fail_closed_states():
    schema = load_schema("operational_audit_result.scn.schema.json")
    status = schema["properties"]["status"]
    enum = set(status.get("enum", []))

    assert {"blocked", "pending_data"} <= enum


def test_operational_audit_result_is_not_free_text_report():
    schema = load_schema("operational_audit_result.scn.schema.json")
    props = schema["properties"]

    assert "free_text" not in props
    assert "reply_text" not in props
    assert "narrative_only" not in props
    assert "findings" in props
    assert "allowed_rendering" in props
