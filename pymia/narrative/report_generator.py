from __future__ import annotations

from .models import EvidenceItem, NarrativeClaim, NarrativeReport, NarrativeSection


def _claim(text: str, evidence_id: str, metric: str | None = None, value: float | None = None) -> NarrativeClaim:
    return NarrativeClaim(
        text=text,
        evidence_ids=[evidence_id],
        expected_metric=metric,
        expected_value=value,
    )


def build_narrative_report(evidence_pool: list[EvidenceItem]) -> NarrativeReport:
    by_id = {item.id: item for item in evidence_pool}

    situacion = NarrativeSection(title="Situacion actual", claims=[])
    for metric in ("ventas_total", "costos_total", "margen_bruto", "margen_bruto_pct"):
        eid = f"computed:{metric}"
        item = by_id.get(eid)
        if item is None:
            continue
        situacion.claims.append(
            _claim(
                text=f"{metric} observado: {item.value}.",
                evidence_id=eid,
                metric=metric,
                value=float(item.value) if isinstance(item.value, (int, float)) else None,
            )
        )

    hojas = NarrativeSection(title="Estado por hoja", claims=[])
    for item in evidence_pool:
        if item.source != "sheet_reports":
            continue
        hojas.claims.append(
            _claim(
                text=f"{item.context}.",
                evidence_id=item.id,
                metric=item.metric,
            )
        )

    senales = NarrativeSection(title="Senales", claims=[])
    for item in evidence_pool:
        if item.source != "signals":
            continue
        text = f"Senal {item.metric} con severidad {item.value}."
        if item.context:
            text = f"{text} {item.context}"
        senales.claims.append(
            _claim(
                text=text,
                evidence_id=item.id,
                metric=item.metric,
            )
        )

    sections = [s for s in (situacion, hojas, senales) if s.claims]
    trace = {
        "section_count": len(sections),
        "claims_count": sum(len(s.claims) for s in sections),
        "evidence_count": len(evidence_pool),
    }
    return NarrativeReport(sections=sections, trace=trace)
