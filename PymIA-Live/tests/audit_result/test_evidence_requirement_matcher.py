from __future__ import annotations

from pathlib import Path
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.audit_result.evidence_requirement_matcher import (
    match_evidence_requirements,
    _load_evidence_requirement_aliases,
)


def test_evidence_requirement_matcher_loads_catalog():
    aliases = _load_evidence_requirement_aliases()
    assert isinstance(aliases, dict)
    assert aliases.get("schema_version") == "1.0"
    assert "signal_to_pathology" in aliases
    assert "sheet_evidence_aliases" in aliases
    assert "computed_variable_aliases" in aliases


def test_evidence_requirement_matcher_match_logic():
    # Construct a dummy StructuredEvidence with computed variables and sheet reports
    evidence = StructuredEvidence(
        tenant_id="test-tenant",
        intake_id="test-intake",
        document_type="xlsx",
        file_name="test.xlsx",
        sheet_reports={"ventas": "OK"},
        computed_variables={"ventas_total": 1000.0, "costos_total": 400.0},
        metadata={"signals": [{"signal_id": "sig1", "signal_type": "margen_bajo"}]},
    )

    matches = match_evidence_requirements(evidence)
    assert isinstance(matches, list)
    assert len(matches) > 0

    # Find the match for REN_001
    ren_match = next((m for m in matches if m.pathology_code == "REN_001"), None)
    assert ren_match is not None
    # "ventas_total" in computed triggers the alias resolving for sales/ventas keys
    assert "ventas_del_periodo" in ren_match.available_evidence
    assert "sales" in ren_match.available_evidence
    assert "ventas_totales" in ren_match.available_evidence

    # "margen_bajo" signal is classified as candidate for REN_001
    # Check that it matched or has candidate status if variables were missing
    # In this case we provided sales & costs, let's verify match status
    assert ren_match.status in ("calculable", "pending_data", "candidate")
