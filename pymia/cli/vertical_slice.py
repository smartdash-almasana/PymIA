from __future__ import annotations

import argparse
from pathlib import Path

from openpyxl import load_workbook

from pymia.smartpyme.owner_facing_report import build_owner_facing_report


OPERATIONAL_TERMS = ("venta", "precio", "costo", "producto", "sku", "cantidad", "fecha")


def inspect_excel(path: Path) -> dict:
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook.worksheets[0]
        headers = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
        normalized_headers = [str(value).strip().lower() for value in headers if value]
        return {
            "sheet": worksheet.title,
            "rows": int(worksheet.max_row or 0),
            "columns": int(worksheet.max_column or 0),
            "headers": normalized_headers,
        }
    finally:
        workbook.close()


def has_operational_columns(headers: list[str]) -> bool:
    joined = " ".join(headers)
    return any(term in joined for term in OPERATIONAL_TERMS)


def build_structured_summary(path: Path, tenant_id: str) -> dict:
    try:
        from pymia.smartpyme.structured_evidence_builder import build_structured_evidence_context

        payload = build_structured_evidence_context(
            excel_path=path,
            tenant_id=tenant_id,
            intake_record={"evidence_requests": []},
        )
        evidence = payload["structured_evidence"]
        computed = evidence.get("computed_variables") or {}
        tables = evidence.get("tables") or []
        return {
            "status": "available",
            "computed_variables_count": len(computed),
            "tables_count": len(tables),
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "reason": exc.__class__.__name__,
        }


def build_report(
    path: Path,
    message: str,
    profile: dict,
    *,
    tenant_id: str = "tenant_cli_local",
    intake_id: str = "intake_cli_local",
) -> dict:
    has_rows = profile["rows"] > 1 and profile["columns"] > 0
    has_columns = has_operational_columns(profile["headers"])
    structured_summary = build_structured_summary(path, tenant_id)
    missing = []
    questions = []
    if not has_rows:
        missing.append("filas_de_datos")
        questions.append("Necesito al menos una fila de datos además de los encabezados.")
    if not has_columns:
        missing.append("columnas_operativas")
        questions.append("Necesito columnas como fecha, producto, ventas, precio, costo, cantidad o sku.")
    blocked = bool(missing)
    summary = "Falta evidencia mínima para avanzar." if blocked else "Planilla legible con señales operativas mínimas; resultado candidato, no diagnóstico final."
    report = build_owner_facing_report(
        operational_audit_result={"tenant_id": tenant_id, "status": "blocked" if blocked else "candidate", "evidence_used": ["excel_file_readable"], "missing_evidence": missing},
        render_contract={"tenant_id": tenant_id, "summary": summary, "blocked_message": summary if blocked else "", "next_questions": questions, "next_steps": ["Revisar con el dueño antes de diagnosticar."], "references": [str(path)], "forbidden_inferences": ["No inferir diagnóstico desde nombres de columnas."]},
        delivery_package={"tenant_id": tenant_id, "intake_id": intake_id, "status": "BLOCKED" if blocked else "DELIVERED", "summary": summary, "output_refs": ["stdout"], "warnings": ["Slice local; no es canal productivo."]},
    ).to_dict()
    report["structured_evidence_summary"] = structured_summary
    return report


def build_markdown(
    path: Path,
    message: str,
    profile: dict,
    *,
    tenant_id: str = "tenant_cli_local",
    intake_id: str = "intake_cli_local",
) -> str:
    report = build_report(path, message, profile, tenant_id=tenant_id, intake_id=intake_id)
    lines = [
        "# Reporte owner-facing local",
        f"Estado: {report['status']}",
        f"Archivo: {path.name}",
        f"Mensaje: {message}",
        f"Tenant: {report['tenant_id']}",
        f"Intake: {report['intake_id']}",
        f"Hoja: {profile['sheet']}",
        f"Filas: {profile['rows']}",
        f"Columnas: {profile['columns']}",
        f"Resumen: {report['summary']}",
        "",
        "## Evidencia usada",
    ]
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
        lines.append(f"- Variables computables: {structured_summary['computed_variables_count']}")
        lines.append(f"- Tablas estructuradas: {structured_summary['tables_count']}")
    else:
        lines.append(f"- Motivo: {structured_summary['reason']}")
    lines.append("")
    lines.append("## Próxima pregunta")
    if report["next_questions"]:
        for question in report["next_questions"]:
            lines.append(f"- {question}")
    else:
        lines.append("- Confirmar con el dueño si las columnas representan el proceso real.")
    lines.append("")
    lines.append("## Límites")
    for warning in report["limit_warnings"]:
        lines.append(f"- {warning}")
    lines.append("- No diagnostica sin evidencia suficiente ni confirmación del dueño.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--output")
    parser.add_argument("--tenant-id", default="tenant_cli_local")
    parser.add_argument("--intake-id", default="intake_cli_local")
    args = parser.parse_args(argv)
    path = Path(args.excel)
    if not path.exists():
        raise FileNotFoundError(path)
    markdown = build_markdown(
        path,
        args.message,
        inspect_excel(path),
        tenant_id=args.tenant_id,
        intake_id=args.intake_id,
    )
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
