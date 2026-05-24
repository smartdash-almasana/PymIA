import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCN = ROOT / "docs" / "contracts" / "scn"


def load_schema(name: str) -> dict:
    return json.loads((SCN / name).read_text(encoding="utf-8"))


def test_render_contract_excludes_findings_from_allowed_surface():
    schema = load_schema("render_contract.schema.json")
    props = schema["properties"]

    assert "findings" not in props
    assert "diagnosis" not in props
    assert "operational_truth" not in props
    assert "summary" in props
    assert "forbidden_inferences" in props


def test_render_contract_requires_blocked_and_next_step_fields():
    schema = load_schema("render_contract.schema.json")
    required = set(schema.get("required", []))

    assert "blocked_message" in required
    assert "next_questions" in required
    assert "next_steps" in required
    assert "forbidden_inferences" in required


def test_render_contract_description_preserves_hermes_subordination():
    schema = load_schema("render_contract.schema.json")
    description = schema["description"]

    assert "Hermes renders" in description
    assert "Hermes does not reinterpret" in description
