from __future__ import annotations

from .models import EvidenceItem, NarrativeClaim, NarrativeReport, NarrativeSection

_SEVERITY_ORDER = {
    "CRITICA": 4,
    "CRÍTICA": 4,
    "ALTA": 3,
    "MEDIA": 2,
    "BAJA": 1,
    "OK": 0,
}


def _claim(text: str, evidence_id: str, metric: str | None = None, value: float | None = None) -> NarrativeClaim:
    return NarrativeClaim(
        text=text,
        evidence_ids=[evidence_id],
        expected_metric=metric,
        expected_value=value,
    )


def _severity_rank(value: object) -> int:
    if value is None:
        return 0
    return _SEVERITY_ORDER.get(str(value).strip().upper(), 0)


def _is_ok_signal(item: EvidenceItem) -> bool:
    return str(item.metric).strip().lower() == "ok" or str(item.value).strip().upper() == "OK"


def build_narrative_report_v2(evidence_pool: list[EvidenceItem]) -> NarrativeReport:
    by_id = {item.id: item for item in evidence_pool}

    situacion = NarrativeSection(title="Resumen ejecutivo", claims=[])
    metrics_for_summary = [
        ("ventas_total", "Ventas totales"),
        ("costos_total", "Costos totales"),
        ("margen_bruto", "Margen bruto"),
        ("margen_bruto_pct", "Margen bruto pct"),
    ]
    for metric_key, label in metrics_for_summary:
        eid = f"computed:{metric_key}"
        item = by_id.get(eid)
        if item is None:
            continue
        situacion.claims.append(
            _claim(
                text=f"{label}: {item.value}.",
                evidence_id=eid,
                metric=metric_key,
                value=float(item.value) if isinstance(item.value, (int, float)) else None,
            )
        )

    signal_items = [item for item in evidence_pool if item.source == "signals"]
    has_high_priority = any(_severity_rank(item.value) >= 3 for item in signal_items)
    if has_high_priority:
        signal_items = [item for item in signal_items if not _is_ok_signal(item)]

    signal_items_sorted = sorted(signal_items, key=lambda item: _severity_rank(item.value), reverse=True)
    top3 = signal_items_sorted[:3]

    top_section = NarrativeSection(title="Top 3 problemas", claims=[])
    for item in top3:
        sev = str(item.value) if item.value is not None else "N/A"
        text = f"{item.metric} (severidad {sev})."
        if item.context:
            text = f"{text} {item.context}"
        top_section.claims.append(
            _claim(
                text=text,
                evidence_id=item.id,
                metric=item.metric,
            )
        )

    actions = NarrativeSection(title="Acciones 7 dias", claims=[])
    for item in top3:
        suggested_action = str(item.details.get("suggested_action") or "").strip()
        if not suggested_action:
            continue
        actions.claims.append(
            _claim(
                text=f"Priorizar {item.metric}: {suggested_action}.",
                evidence_id=item.id,
                metric=item.metric,
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

    sections = [s for s in (situacion, top_section, actions, hojas) if s.claims]
    trace = {
        "version": "v2",
        "section_count": len(sections),
        "claims_count": sum(len(s.claims) for s in sections),
        "evidence_count": len(evidence_pool),
        "top_signals": [item.id for item in top3],
        "ok_signal_filtered": has_high_priority,
    }
    return NarrativeReport(sections=sections, trace=trace)
