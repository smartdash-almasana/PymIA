from __future__ import annotations

from pymia.smartpyme.finding_projection import ActionableFinding
from pymia.narrative.actionable_findings_adapter import build_narrative_report_from_actionable_findings
from pymia.narrative.markdown_exporter import render_markdown


def render_minimal_delivery_report(
    *,
    tenant_id: str,
    case_id: str,
    owner_message: str,
    evidence_refs: list[str],
    findings: list[ActionableFinding],
    include_trace_ids: bool = False,
) -> str:
    if not tenant_id or not tenant_id.strip():
        raise ValueError("tenant_id must not be empty")
    if not case_id or not case_id.strip():
        raise ValueError("case_id must not be empty")
    if not owner_message or not owner_message.strip():
        raise ValueError("owner_message must not be empty")
    if not evidence_refs:
        raise ValueError("evidence_refs must not be empty")

    if not findings:
        return "El caso fue evaluado pero no arrojó hallazgos operativos."

    report = build_narrative_report_from_actionable_findings(findings)
    rendered_findings = render_markdown(report, include_trace_ids=include_trace_ids)

    evidence_list = "\n".join(f"- {ref.strip()}" for ref in evidence_refs if ref.strip())

    return f"""# Reporte operativo mínimo

## Problema declarado
{owner_message.strip()}

## Evidencia usada
{evidence_list}

{rendered_findings}

## Límites del análisis
Este reporte es un corte determinístico basado en reglas.
No reemplaza el criterio contable ni constituye una auditoría final."""
