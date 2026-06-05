from __future__ import annotations

from pathlib import Path
from typing import Any

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.models import NarrativeReport


JsonObject = dict[str, Any]


def render_minimum_assisted_report(
    *,
    evidence: StructuredEvidence,
    narrative_report: NarrativeReport,
    curation_report: JsonObject,
    tenant_id: str,
    source_file: str | Path,
) -> str:
    """Render the smallest useful SmartPyme assisted report.

    This is intentionally not a product PDF, not an autonomous diagnosis, and not
    a commercial promise. It is a local Markdown deliverable grounded in the
    evidence extracted from a single XLSX file.
    """

    source = Path(source_file)
    computed = evidence.computed_variables or {}
    metadata = evidence.metadata or {}
    sheet_reports = metadata.get("sheet_reports", {})
    missing_or_limits = _build_limitations(evidence=evidence, curation_report=curation_report)

    lines: list[str] = []
    lines.append(f"# SmartPyme — Diagnóstico operativo asistido")
    lines.append("")
    lines.append("## 1. Contexto del procesamiento")
    lines.append("")
    lines.append(f"- Tenant: `{tenant_id}`")
    lines.append(f"- Archivo: `{source.name}`")
    lines.append(f"- Tipo de documento: `{evidence.document_type}`")
    lines.append(f"- Estado de curación: `{metadata.get('curation_status', 'unknown')}`")
    lines.append(f"- Tablas detectadas: `{metadata.get('tables_count', 0)}`")
    lines.append(f"- Filas detectadas: `{metadata.get('rows_count', 0)}`")
    lines.append("")

    lines.append("## 2. Qué se pudo observar")
    lines.append("")
    if computed:
        for key, value in sorted(computed.items()):
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- No se calcularon variables operativas suficientes con la evidencia disponible.")
    lines.append("")

    lines.append("## 3. Hallazgos narrativos generados")
    lines.append("")
    if narrative_report.sections:
        for section in narrative_report.sections:
            lines.append(f"### {section.title}")
            lines.append("")
            for claim in section.claims:
                evidence_ids = ", ".join(claim.evidence_ids) if claim.evidence_ids else "sin evidencia asociada"
                lines.append(f"- {claim.text} _(evidencia: {evidence_ids})_")
            lines.append("")
    else:
        lines.append("- No se generaron hallazgos narrativos con la evidencia disponible.")
        lines.append("")

    lines.append("## 4. Estado por hoja")
    lines.append("")
    if isinstance(sheet_reports, dict) and sheet_reports:
        for sheet, status in sheet_reports.items():
            lines.append(f"- `{sheet}`: `{status}`")
    else:
        lines.append("- No hay estado por hoja disponible.")
    lines.append("")

    lines.append("## 5. Límites y evidencia faltante")
    lines.append("")
    for item in missing_or_limits:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## 6. Próximo paso recomendado")
    lines.append("")
    if computed:
        lines.append("- Revisar estas métricas con el dueño PyME y pedir aclaración sobre cualquier campo ambiguo o faltante antes de tomar decisiones.")
    else:
        lines.append("- Pedir más evidencia operativa o explicación de columnas antes de intentar diagnosticar.")
    lines.append("")

    lines.append("## 7. No-promesas")
    lines.append("")
    lines.append("Este entregable no es auditoría contable/legal, no garantiza resultado económico, no reemplaza ERP/contador y no debe leerse como diagnóstico total sin evidencia adicional.")
    lines.append("")

    return "\n".join(lines)


def _build_limitations(*, evidence: StructuredEvidence, curation_report: JsonObject) -> list[str]:
    metadata = evidence.metadata or {}
    limitations: list[str] = []

    if metadata.get("owner_questions_required"):
        limitations.append("Hay campos desconocidos o ambiguos; se requiere sentido operativo del dueño PyME.")

    unknown = metadata.get("fields_unknown") or []
    if unknown:
        limitations.append(f"Campos desconocidos: {', '.join(map(str, unknown))}.")

    ambiguous = metadata.get("fields_ambiguous") or []
    if ambiguous:
        limitations.append(f"Campos ambiguos: {', '.join(map(str, ambiguous))}.")

    validation_count = metadata.get("validation_issues_count", 0)
    if validation_count:
        limitations.append(f"Validaciones con observaciones: {validation_count}.")

    report = curation_report.get("report", {}) if isinstance(curation_report, dict) else {}
    if report.get("status") == "BLOCKED":
        limitations.append("La curación quedó bloqueada; no corresponde emitir diagnóstico operativo.")
    elif report.get("status") == "PARTIAL":
        limitations.append("La curación fue parcial; las conclusiones deben tratarse como lectura limitada.")

    if not limitations:
        limitations.append("No se detectaron límites estructurales graves, pero toda lectura debe validarse con el dueño PyME.")

    return limitations
