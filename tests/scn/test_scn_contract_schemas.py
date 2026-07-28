import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCN = ROOT / "docs" / "contracts" / "scn"


def load_schema(name: str) -> dict:
    return json.loads((SCN / name).read_text(encoding="utf-8"))


def test_evidence_candidate_schema_declares_required_boundary_fields():
    schema = load_schema("evidence_candidate.schema.json")
    props = schema["properties"]
    required = set(schema.get("required", []))

    expected = {
        "schema_version",
        "evidence_id",
        "tenant_id",
        "conversation_id",
        "source_type",
        "source_origin",
        "collected_by",
        "collected_at",
        "raw_content_hash",
        "payload",
        "provenance",
        "confidence",
        "hermes_notes",
    }

    assert expected <= set(props)
    assert expected <= required
    assert "EvidenceCandidate is not a Finding" in schema["description"]

    hermes_notes = props["hermes_notes"]["properties"]
    assert "role" in hermes_notes
    assert "diagnostic_authority" in hermes_notes
    assert hermes_notes["diagnostic_authority"].get("const") is False


def test_kernel_request_schema_declares_boundary_layer_requirement():
    schema = load_schema("kernel_request.schema.json")
    props = schema["properties"]
    required = set(schema.get("required", []))

    expected = {
        "schema_version",
        "request_id",
        "tenant_id",
        "operation",
        "evidence_refs",
        "requested_by",
        "conversation_context_ref",
        "policy_profile",
        "created_at",
    }

    assert expected <= set(props)
    assert expected <= required
    assert "Hermes must not call kernel directly outside Boundary Layer" in schema["description"]


def test_operational_audit_result_scn_schema_declares_sovereign_output_fields():
    schema = load_schema("operational_audit_result.scn.schema.json")
    props = schema["properties"]
    required = set(schema.get("required", []))

    expected = {
        "schema_version",
        "result_id",
        "tenant_id",
        "status",
        "findings",
        "evidence_used",
        "missing_evidence",
        "allowed_rendering",
        "forbidden_inferences",
        "audit_trail_ref",
        "sovereign_mark",
        "created_at",
    }

    assert expected <= set(props)
    assert expected <= required
    assert "Finding without PymIA sovereign mark is not valid" in schema["description"]


def test_render_contract_schema_limits_hermes_to_rendering():
    schema = load_schema("render_contract.schema.json")
    props = schema["properties"]
    required = set(schema.get("required", []))

    expected = {
        "schema_version",
        "render_id",
        "result_ref",
        "tenant_id",
        "summary",
        "next_questions",
        "next_steps",
        "blocked_message",
        "forbidden_inferences",
        "references",
        "allowed_tone",
        "created_at",
    }

    assert expected <= set(props)
    assert expected <= required
    assert "Hermes renders. Hermes does not reinterpret" in schema["description"]
    assert "findings" not in props
