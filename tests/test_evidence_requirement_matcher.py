from __future__ import annotations

from pymia.audit_result.builder import build_operational_audit_result
from pymia.audit_result.evidence_requirement_matcher import match_evidence_requirements
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.report_generator_v2 import build_narrative_report_v2


def _mk_evidence(*, computed: dict[str, float], sheets: dict[str, str], signals: list[dict] | None = None) -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant-test",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="test.xlsx",
        computed_variables=computed,
        metadata={
            "sheet_reports": sheets,
            "signals": signals or [],
        },
    )


def _status(matches, pathology_code: str):
    for m in matches:
        if m.pathology_code == pathology_code:
            return m.status
    raise AssertionError(f"Pathology not found: {pathology_code}")


def test_liq001_pending_when_sales_without_collections() -> None:
    evidence = _mk_evidence(
        computed={"ventas_total": 1000.0},
        sheets={"ventas": "OK"},
    )
    matches = match_evidence_requirements(evidence)
    assert _status(matches, "LIQ_001") == "pending_data"


def test_ren001_pending_when_sales_and_costs_without_taxes() -> None:
    evidence = _mk_evidence(
        computed={"ventas_total": 1000.0, "costos_total": 500.0},
        sheets={"ventas": "OK", "compras": "OK"},
    )
    matches = match_evidence_requirements(evidence)
    assert _status(matches, "REN_001") in {"pending_data", "candidate"}


def test_inv002_pending_with_stock_and_sales() -> None:
    evidence = _mk_evidence(
        computed={"ventas_total": 1000.0},
        sheets={"ventas": "OK", "stock": "OK"},
    )
    matches = match_evidence_requirements(evidence)
    assert _status(matches, "INV_002") in {"pending_data", "candidate"}


def test_open_threads_created_from_catalog_without_explicit_signals() -> None:
    evidence = _mk_evidence(
        computed={"ventas_total": 1000.0, "costos_total": 600.0},
        sheets={"ventas": "OK", "compras": "OK", "stock": "OK"},
        signals=[],
    )
    pool = extract_evidence_pool(evidence)
    report = build_narrative_report_v2(pool)
    grounding = validate_grounding(report, pool)

    result = build_operational_audit_result(
        evidence=evidence,
        report=report,
        grounding=grounding,
        audit_id="audit-no-signals",
    )

    assert result.open_audit_threads
    assert all(t.thread_id.startswith("audit_thread:") for t in result.open_audit_threads)
    assert all(t.opened_by for t in result.open_audit_threads)


def test_pyme033_pending_without_sku_sales() -> None:
    evidence = _mk_evidence(
        computed={"ventas_total": 1000.0},
        sheets={"ventas": "OK"},
    )
    matches = match_evidence_requirements(evidence)
    pyme033_match = None
    for m in matches:
        if m.pathology_code == "PYME_033":
            pyme033_match = m
            break
    assert pyme033_match is not None
    assert pyme033_match.status == "pending_data"
    assert "ventas_por_sku" in pyme033_match.missing_evidence

