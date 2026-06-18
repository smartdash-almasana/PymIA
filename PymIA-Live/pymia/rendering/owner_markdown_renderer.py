from __future__ import annotations

from pathlib import Path

from pymia.contracts.language_corpus_v1 import load_language_corpus_seed, owner_label_for_variable_id
from pymia.contracts.presentation_labels_v1 import label_for_field
from pymia.contracts.vertical_slice_copy_v1 import vertical_slice_copy_for


def _humanize_field(name: str) -> str:
    return label_for_field(name)


def _owner_label_for_variable(name: str) -> str:
    corpus = load_language_corpus_seed()
    label = owner_label_for_variable_id(name, corpus)
    if label == name:
        return name
    return f"{label} ({name})"


def _owner_sufficiency_summary_lines(structured_summary: dict) -> list[str]:
    lines = ["## Suficiencia de evidencia"]
    sufficiency = structured_summary.get("sufficiency") or []
    unsupported_formula_ids = structured_summary.get("unsupported_formula_ids") or []

    if sufficiency:
        lines.append("- Hay chequeos técnicos con evidencia pendiente o en revisión.")
    if unsupported_formula_ids:
        lines.append("- Hay chequeos técnicos no disponibles en esta vista owner-facing.")
    if not sufficiency and not unsupported_formula_ids:
        lines.append("- Sin alertas técnicas adicionales visibles en esta vista.")
    return lines


def _owner_view_lines(path: Path, message: str, profile: dict, report: dict) -> list[str]:
    owner_simple = report["owner_simple"]
    owner_answer_record = report.get("owner_answer_record")
    evidence_request_record = report.get("evidence_request_record")
    lines = [
        "# Reporte owner-facing local",
        f"Estado: {report['status']}",
        f"Archivo: {path.name}",
        f"Mensaje: {message}",
        f"Hoja: {profile['sheet']}",
        f"Filas: {profile['rows']}",
        f"Columnas: {profile['columns']}",
        f"Resumen: {report['summary']}",
        "",
        "Qué entendimos:",
        owner_simple["que_entendimos"],
        "",
        "Qué pudimos leer:",
        owner_simple["que_pudimos_leer"],
        "",
        "Qué todavía no podemos afirmar:",
        owner_simple["que_todavia_no_podemos_afirmar"],
        "",
        "Próxima pregunta:",
        owner_simple["proxima_pregunta"],
        "",
        "Límites:",
        "",
    ]
    for item in owner_simple["limites"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Anamnesis"])
    taxonomy = report["anamnesis_record"].get("business_taxonomy", {})
    lines.append(f"- Empresa tipo: {taxonomy.get('empresa_tipo', 'desconocido')}")
    lines.append(f"- Industria: {taxonomy.get('industria', 'desconocido')}")
    lines.append(f"- Modelo comercial: {taxonomy.get('modelo_comercial', 'desconocido')}")
    if taxonomy.get("canales_venta"):
        lines.append(f"- Canales de venta: {', '.join(taxonomy['canales_venta'])}")
    if taxonomy.get("areas_criticas"):
        lines.append(f"- Áreas críticas: {', '.join(taxonomy['areas_criticas'])}")
    if owner_answer_record:
        lines.extend([
            "",
            "## Respuesta del dueño",
            f"- Pregunta referida: {owner_answer_record['question_ref']}",
            f"- Tipo: {owner_answer_record['answer_kind']}",
        ])
    if evidence_request_record:
        lines.extend([
            "",
            "## Solicitud de evidencia",
            f"- Estado: {evidence_request_record['status']}",
            f"- Motivo: {evidence_request_record['request_reason']}",
        ])
        request_alignment = report.get("evidence_request_alignment", {"status": "ALIGNED"})
        if request_alignment["status"] == "MISALIGNED":
            lines.append("- Pendiente: reconducir con el dueño antes de solicitar evidencia.")
        else:
            for item in evidence_request_record["requested_evidence"]:
                lines.append(f"- {_humanize_field(item)}")
    lines.extend([
        "",
        "## Evidencia usada",
    ])
    for item in report["evidence_used"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Evidencia faltante")
    if report["missing_evidence"]:
        for item in report["missing_evidence"]:
            lines.append(f"- {item}")
    else:
        lines.append("- Sin faltantes mínimos detectados en este slice.")
    lines.append("")
    lines.append("## Evidencia estructurada")
    structured_summary = report["structured_evidence_summary"]
    lines.append(f"- Estado: {structured_summary['status']}")
    if structured_summary["status"] == "available":
        var_count = structured_summary["computed_variables_count"]
        var_names = structured_summary.get("computed_variable_names", [])
        lines.append(f"- Variables computables: {var_count}")
        for name in var_names:
            lines.append(f"  - {_owner_label_for_variable(name)}")
        table_sheets = structured_summary.get("table_sheets", [])
        lines.append(f"- Tablas estructuradas: {structured_summary['tables_count']}")
        for t in table_sheets:
            lines.append(f"  - {t['name']} ({t['rows']} filas, {t['columns']} columnas)")
        if structured_summary["sufficiency"] or structured_summary["unsupported_formula_ids"]:
            lines.append("")
            lines.extend(_owner_sufficiency_summary_lines(structured_summary))
    else:
        lines.append(f"- Motivo: {structured_summary['reason']}")
    lines.append("")
    lines.append("## Próxima pregunta")
    owner_question = report.get("owner_question", "")
    if owner_question:
        lines.append(f"- {owner_question}")
    else:
        lines.append(f"- {vertical_slice_copy_for('next_question_fallback')}")
    lines.append("")
    lines.append("## Límites")
    for warning in report["limit_warnings"]:
        lines.append(f"- {warning}")
    lines.append(f"- {vertical_slice_copy_for('final_limit_warning')}")
    return lines


def _operator_annex_lines(report: dict, diagnostic_operator_summary: dict | None) -> list[str]:
    owner_answer_record = report.get("owner_answer_record")
    evidence_request_record = report.get("evidence_request_record")
    structured_summary = report["structured_evidence_summary"]
    lines = [
        "## Anexo técnico operador",
        f"Tenant: {report['tenant_id']}",
        f"Intake: {report['intake_id']}",
        f"Anamnesis ID: {report['anamnesis_record']['anamnesis_id']}",
        f"Investigation ID: {report['investigation_record']['investigation_id']}",
        f"Evidence ID: {report['evidence_record']['evidence_id']}",
        f"Evidence SHA-256: {report['evidence_record']['content_hash']}",
        f"Run ID: {report['pipeline_run_record']['run_id']}",
    ]
    if owner_answer_record:
        lines.append(f"Owner Answer ID: {owner_answer_record['answer_id']}")
    if evidence_request_record:
        lines.append(f"Evidence Request ID: {evidence_request_record['request_id']}")
    if structured_summary["status"] == "available":
        lines.append(f"Case ID: {structured_summary['case_id']}")
        if structured_summary["sufficiency"] or structured_summary["unsupported_formula_ids"]:
            lines.extend(["", "## Suficiencia de evidencia operador"])
            for item in structured_summary["sufficiency"]:
                lines.append(f"- {item['formula_id']}: {item['status']}")
                if item["missing_variables"]:
                    lines.append(f"  - Faltan: {', '.join(item['missing_variables'])}")
            for formula_id in structured_summary["unsupported_formula_ids"]:
                lines.append(f"- {formula_id}: UNSUPPORTED_FORMULA")

    tech_reference = report.get("owner_question_technical_reference", "")
    if tech_reference:
        lines.extend([
            "",
            "## Referencia técnica operador",
            f"- {tech_reference}",
        ])

    if diagnostic_operator_summary:
        lines.extend([
            "",
            "## Resumen diagnóstico operador",
            f"- Diagnosis status: {diagnostic_operator_summary['diagnosis_status']}",
            f"- Kernel state: {diagnostic_operator_summary['kernel_state']}",
            f"- Blocking reason: {diagnostic_operator_summary['blocking_reason']}",
            f"- Gate status: {diagnostic_operator_summary['gate_status']}",
        ])
        finding_types = diagnostic_operator_summary.get("finding_types") or []
        formulas_used = diagnostic_operator_summary.get("formulas_used") or []
        evidence_used = diagnostic_operator_summary.get("evidence_used") or []
        blocked_formulas = diagnostic_operator_summary.get("blocked_formulas") or []
        if finding_types:
            lines.append(f"- Finding types: {', '.join(finding_types)}")
        if formulas_used:
            lines.append(f"- Formulas used: {', '.join(formulas_used)}")
        if evidence_used:
            lines.append(f"- Evidence used: {', '.join(evidence_used)}")
        if blocked_formulas:
            lines.append(f"- Blocked formulas: {', '.join(blocked_formulas)}")
    return lines


def render_markdown_from_report(
    path: Path,
    message: str,
    profile: dict,
    report: dict,
    *,
    audience: str = "owner",
    diagnostic_operator_summary: dict | None = None,
) -> str:
    if audience not in {"owner", "operator", "combined"}:
        raise ValueError(f"Unsupported audience: {audience}")

    owner_lines = _owner_view_lines(path, message, profile, report)

    if audience == "owner":
        lines = owner_lines
    elif audience == "operator":
        lines = owner_lines + [""] + _operator_annex_lines(report, diagnostic_operator_summary)
    else:
        lines = owner_lines + ["", "---", ""] + _operator_annex_lines(report, diagnostic_operator_summary)

    return "\n".join(lines) + "\n"
