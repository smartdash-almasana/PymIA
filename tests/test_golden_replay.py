from __future__ import annotations

from pathlib import Path

from pymia.audit_result.builder import build_operational_audit_result
from pymia.audit_result.validators import validate_operational_audit_result
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.report_generator_v2 import build_narrative_report_v2
from tests.golden_replay_utils import (
    assert_json_equivalence,
    canonical_normalize,
    load_json,
)
from tools.excel_evidence import build_excel_structured_evidence


ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "prueba_excels" / "la_textil_cosida_srl_mar_abr_may_2026.xlsx"
EXPECTED = ROOT / "tests" / "golden_findings" / "la_textil_expected.json"


def _run_pipeline() -> dict:
    evidence = build_excel_structured_evidence(
        excel_path=XLSX,
        tenant_id="tenant-la-textil-golden-replay",
    )
    pool = extract_evidence_pool(evidence)
    report = build_narrative_report_v2(pool)
    grounding = validate_grounding(report, pool)
    result = build_operational_audit_result(
        evidence=evidence,
        report=report,
        grounding=grounding,
        audit_id="audit_tenant_la_textil_golden_replay",
    )
    validated = validate_operational_audit_result(result)
    return validated.model_dump(mode="json")


def test_golden_replay_la_textil_operational_audit_result() -> None:
    current = canonical_normalize(_run_pipeline())
    expected = load_json(EXPECTED)

    # Explicit deterministic/semantic checks requested by policy.
    assert current["tenant_id"] == expected["tenant_id"]
    assert current["pathology_findings"] == expected["pathology_findings"]
    assert current["computed_metrics"] == expected["computed_metrics"]
    assert current["audit_trail"] == expected["audit_trail"]

    assert_json_equivalence(current, expected)

