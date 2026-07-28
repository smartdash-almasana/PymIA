from __future__ import annotations

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.markdown_exporter import render_markdown
from pymia.narrative.report_generator_v2 import build_narrative_report_v2


def _sample_evidence_v2() -> StructuredEvidence:
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
                    "signal_id": "S_OK",
                    "signal_type": "ok",
                    "severity": "BAJA",
                    "description": "Sin alertas",
                    "suggested_action": "Mantener monitoreo semanal",
                },
                {
                    "signal_id": "S_CRIT",
                    "signal_type": "margen_bajo",
                    "severity": "CRÍTICA",
                    "description": "Margen muy por debajo del objetivo",
                    "suggested_action": "Revisar costos y subir precio en SKUs no elasticos",
                },
                {
                    "signal_id": "S_HIGH",
                    "signal_type": "caja_tensionada",
                    "severity": "ALTA",
                    "description": "Falta liquidez para compras clave",
                    "suggested_action": "Acelerar cobranzas y pausar compras no criticas",
                },
                {
                    "signal_id": "S_MED",
                    "signal_type": "sobrestock",
                    "severity": "MEDIA",
                    "description": "Capital inmovilizado",
                    "suggested_action": "Liquidar stock lento con promo segmentada",
                },
            ],
        },
    )


def _section(report, title: str):
    return next(s for s in report.sections if s.title == title)


def test_build_report_v2_filters_ok_when_critical_or_high_exist() -> None:
    pool = extract_evidence_pool(_sample_evidence_v2())
    report = build_narrative_report_v2(pool)

    top = _section(report, "Top 3 problemas")
    joined = " ".join(c.text.lower() for c in top.claims)

    assert " ok" not in joined
    assert "s_ok" not in " ".join(",".join(c.evidence_ids).lower() for c in top.claims)


def test_build_report_v2_ranks_top3_by_severity() -> None:
    pool = extract_evidence_pool(_sample_evidence_v2())
    report = build_narrative_report_v2(pool)

    top = _section(report, "Top 3 problemas")
    ids = [claim.evidence_ids[0] for claim in top.claims]

    assert ids[0] == "signal:S_CRIT"
    assert ids[1] == "signal:S_HIGH"
    assert ids[2] == "signal:S_MED"


def test_build_report_v2_generates_actions_7_days() -> None:
    pool = extract_evidence_pool(_sample_evidence_v2())
    report = build_narrative_report_v2(pool)

    actions = _section(report, "Acciones 7 dias")
    assert len(actions.claims) >= 1
    assert all(claim.evidence_ids for claim in actions.claims)


def test_report_v2_validates_grounding_and_renders_with_optional_trace_ids() -> None:
    pool = extract_evidence_pool(_sample_evidence_v2())
    report = build_narrative_report_v2(pool)
    result = validate_grounding(report, pool)

    assert result.ok is True

    plain = render_markdown(report, include_trace_ids=False)
    traced = render_markdown(report, include_trace_ids=True)

    assert "## Resumen ejecutivo" in plain
    assert "signal:S_CRIT" not in plain
    assert "signal:S_CRIT" in traced
