from __future__ import annotations

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.markdown_exporter import render_markdown
from pymia.narrative.models import NarrativeClaim, NarrativeReport, NarrativeSection
from pymia.narrative.report_generator import build_narrative_report


def _sample_evidence() -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant-test",
        document_type="xlsx_evidence",
        source="xlsx_upload",
        file_name="sample.xlsx",
        computed_variables={
            "ventas_total": 1000.0,
            "costos_total": 700.0,
            "margen_bruto": 300.0,
            "margen_bruto_pct": 0.3,
        },
        metadata={
            "sheet_reports": {"ventas": "OK", "stock": "PARTIAL"},
            "signals": [
                {
                    "signal_id": "S1",
                    "signal_type": "margen_bajo",
                    "severity": "ALTA",
                    "description": "Margen bajo en abril",
                }
            ],
        },
    )


def test_extract_evidence_pool_contains_computed_sheet_and_signals() -> None:
    evidence = _sample_evidence()

    pool = extract_evidence_pool(evidence)
    ids = {item.id for item in pool}

    assert "computed:ventas_total" in ids
    assert "sheet:ventas:status" in ids
    assert "signal:S1" in ids


def test_build_report_and_validate_grounding_ok() -> None:
    evidence = _sample_evidence()
    pool = extract_evidence_pool(evidence)

    report = build_narrative_report(pool)
    result = validate_grounding(report, pool)

    assert len(report.sections) >= 1
    assert result.ok is True
    assert result.errors == []


def test_validate_grounding_fails_on_missing_evidence_id() -> None:
    evidence = _sample_evidence()
    pool = extract_evidence_pool(evidence)

    report = NarrativeReport(
        sections=[
            NarrativeSection(
                title="Test",
                claims=[
                    NarrativeClaim(
                        text="Claim without real evidence.",
                        evidence_ids=["missing:id"],
                    )
                ],
            )
        ]
    )

    result = validate_grounding(report, pool)

    assert result.ok is False
    assert any("missing evidence id" in err for err in result.errors)


def test_validate_grounding_fails_on_metric_or_value_mismatch() -> None:
    evidence = _sample_evidence()
    pool = extract_evidence_pool(evidence)

    report = NarrativeReport(
        sections=[
            NarrativeSection(
                title="Test",
                claims=[
                    NarrativeClaim(
                        text="Mismatch metric and value.",
                        evidence_ids=["computed:ventas_total"],
                        expected_metric="costos_total",
                        expected_value=999.0,
                    )
                ],
            )
        ]
    )

    result = validate_grounding(report, pool)

    assert result.ok is False
    assert any("metric mismatch" in err for err in result.errors)
    assert any("value mismatch" in err for err in result.errors)


def test_render_markdown_with_and_without_trace_ids() -> None:
    evidence = _sample_evidence()
    pool = extract_evidence_pool(evidence)
    report = build_narrative_report(pool)

    plain = render_markdown(report, include_trace_ids=False)
    traced = render_markdown(report, include_trace_ids=True)

    assert "## " in plain
    assert "computed:ventas_total" not in plain
    assert "computed:ventas_total" in traced
