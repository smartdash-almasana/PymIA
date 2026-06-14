from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from openpyxl import load_workbook

from pymia.contracts.language_corpus_v1 import load_language_corpus_seed, owner_label_for_variable_id
from pymia.smartpyme.owner_facing_report import build_owner_facing_report
from pymia.smartpyme.question_alignment_gate import align_next_question


OPERATIONAL_TERMS = ("venta", "precio", "costo", "producto", "sku", "cantidad", "fecha")

# Presentation-layer mappings for owner-friendly language (not core business logic)
_PATHOLOGY_LABELS: dict[str, str] = {
    "LIQ_001": "cobranza de ventas",
    "LIQ_002": "saldo de caja proyectado",
    "INV_001": "reposición de stock",
    "INV_002": "rotación de stock",
    "REN_001": "margen neto",
    "REN_002": "reposición de precios",
    "OPE_001": "centralización de decisiones",
    "PYME_004": "ajuste por inflación",
    "PYME_007": "deriva de reputación",
    "PYME_008": "control de stock",
    "PYME_009": "discrepancias en ARCA",
    "PYME_011": "plazo de cobranza",
    "PYME_012": "retraso en impuestos",
    "PYME_013": "brecha de pagos",
    "PYME_014": "composición del margen",
    "PYME_015": "conciliación bancaria",
    "PYME_017": "desviación de precios",
    "PYME_018": "actualización de datos",
    "PYME_019": "visibilidad de decisiones",
    "PYME_020": "carga operativa",
    "PYME_021": "seguridad de procesos",
    "PYME_022": "dispersión de datos",
    "PYME_023": "costos logísticos",
    "PYME_024": "liquidez corriente",
    "PYME_025": "dependencia de crédito",
    "PYME_026": "flujo operativo",
    "PYME_027": "carga financiera",
    "PYME_028": "fondo de emergencia",
    "PYME_029": "gestión de ventas",
    "PYME_030": "ventana de despacho",
    "PYME_031": "comunicación con clientes",
    "PYME_032": "reclamos de clientes",
    "PYME_033": "concentración de productos",
    "PYME_034": "cancelaciones",
    "PYME_035": "consistencia fiscal",
    "PYME_036": "conexión con sistemas",
    "PYME_037": "clasificación en IVA",
    "PYME_038": "control de versiones",
    "PYME_039": "recategorización",
    "PYME_040": "gestión de tareas",
    "PYME_041": "liquidación de sueldos",
    "PYME_042": "conexión e-commerce",
    "PYME_043": "carga laboral",
    "PYME_044": "margen por cliente",
    "PYME_045": "uso de IVA",
    "PYME_046": "separación de finanzas",
    "PYME_047": "automatización de procesos",
    "PYME_048": "actualización de precios",
    "PYME_049": "rentabilidad real",
    "PYME_050": "organización general",
}

_FIELD_LABELS: dict[str, str] = {
    "historial_ventas_sku": "historial de ventas por producto",
    "lead_time_proveedor": "tiempos de reposición de proveedores",
    "politica_stock_seguridad": "política de stock de seguridad",
    "ventas_del_periodo": "ventas del período",
    "cobranzas_del_periodo": "cobranzas del período",
    "cuentas_corrientes_clientes": "estado de cuentas corrientes",
    "costos_directos": "costos directos",
    "impuestos_y_comisiones": "impuestos y comisiones",
    "indice_origen": "índice de origen",
    "indice_cierre": "índice de cierre",
    "fecha_origen": "fecha de origen",
    "fecha_cierre": "fecha de cierre",
    "saldo_inicial_caja_banco": "saldo inicial de caja y banco",
    "cobranzas_esperadas": "cobranzas esperadas",
    "pagos_esperados": "pagos esperados",
    "cmv_periodo": "costo de mercadería vendida",
    "inventario_inicial": "inventario inicial",
    "inventario_final": "inventario final",
    "registro_decisiones": "registro de decisiones",
    "workflow_aprobaciones": "flujo de aprobaciones",
    "entrevista_dueño": "entrevista con el dueño",
    "cuentas_por_cobrar": "cuentas por cobrar",
    "ventas_periodo": "ventas del período",
    "periodo_dias": "días del período",
    "dso_calculado": "días de cobranza calculados",
    "dpo_calculado": "días de pago calculados",
    "lista_precios_propia": "lista de precios propia",
    "benchmark_precios_mercado": "precios de referencia del mercado",
    "balance_general": "balance general",
    "saldos_activo_corriente": "saldos de activo corriente",
    "saldos_pasivo_corriente": "saldos de pasivo corriente",
    "estado_resultados": "estado de resultados",
    "balance_dos_periodos": "balance de dos períodos",
    "detalle_intereses": "detalle de intereses",
    "calculo_ebitda": "cálculo de EBITDA",
    "ventas_por_sku": "ventas por producto",
    "ventas_totales": "ventas totales",
    "ventas_por_cliente": "ventas por cliente",
    "costos_por_cliente": "costos por cliente",
    "horas_atencion_cliente": "horas de atención al cliente",
    "medicion_tiempos_proceso": "medición de tiempos de proceso",
    "flujo_actual": "flujo de trabajo actual",
    "flujo_automatizado_estimado": "flujo automatizado estimado",
    "horas_manual_actuales": "horas manuales actuales",
    "costo_hora": "costo por hora",
    "cotizacion_automatizacion": "cotización de automatización",
    "costo_operacion_anual": "costo de operación anual",
    "valor_origen": "valor de origen",
    "cuentas_por_pagar": "cuentas por pagar",
}


def _humanize_field(name: str) -> str:
    if name in _FIELD_LABELS:
        return _FIELD_LABELS[name]
    return name.replace("_", " ").lower()


def _owner_label_for_variable(name: str) -> str:
    corpus = load_language_corpus_seed()
    label = owner_label_for_variable_id(name, corpus)
    if label == name:
        return name
    return f"{label} ({name})"


def _build_owner_question(entry: dict) -> tuple[str | None, str | None]:
    """Build (owner_question, technical_reference) from a catalog reconciliation entry."""
    qs = entry.get("next_audit_questions", [])
    if not qs:
        return None, None
    pathology_code = entry.get("pathology_code", "")
    formula_id = entry.get("formula_id", "")
    missing = entry.get("missing_evidence", [])
    pathology_label = _PATHOLOGY_LABELS.get(pathology_code)
    if not pathology_label:
        pathology_label = pathology_code.replace("_", " ").lower()
    humanized_fields = [_humanize_field(f) for f in missing]
    if humanized_fields:
        if len(humanized_fields) == 1:
            field_text = humanized_fields[0]
        elif len(humanized_fields) == 2:
            field_text = f"{humanized_fields[0]} y {humanized_fields[1]}"
        else:
            field_text = ", ".join(humanized_fields[:-1]) + f" y {humanized_fields[-1]}"
        owner_q = f"Falta información sobre {pathology_label}. ¿Podés compartir {field_text}?"
    else:
        owner_q = f"Falta información sobre {pathology_label} para continuar el análisis."
    tech_parts = [f"Referencia técnica: {formula_id}"]
    if missing:
        tech_parts.append(f"inputs faltantes: {', '.join(missing)}")
    tech_ref = "; ".join(tech_parts)
    return owner_q, tech_ref


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


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_jsonl_line(target: Path, payload: dict) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    import json

    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
    return target


def register_anamnesis_record(
    message: str,
    tenant_id: str,
    intake_id: str,
    storage_dir: Path,
    *,
    business_taxonomy: dict | None = None,
) -> dict:
    from pymia.smartpyme.anamnesis import create_anamnesis_record
    from pymia.smartpyme.storage import save_anamnesis_record

    record = create_anamnesis_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        raw_owner_message=message,
        business_taxonomy=business_taxonomy,
        metadata={"registered_by": "vertical_slice_cli"},
    )
    save_anamnesis_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_evidence_record(path: Path, tenant_id: str, intake_id: str, storage_dir: Path) -> dict:
    from pymia.smartpyme.evidence import (
        EVIDENCE_STATUS_REGISTERED,
        SOURCE_KIND_UPLOADED_FILE,
        create_evidence_record,
    )
    from pymia.smartpyme.storage import save_evidence_record

    record = create_evidence_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        evidence_type="xlsx_upload",
        source_kind=SOURCE_KIND_UPLOADED_FILE,
        source_ref=str(path),
        original_filename=path.name,
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        size_bytes=path.stat().st_size,
        content_hash=calculate_sha256(path),
        status=EVIDENCE_STATUS_REGISTERED,
        metadata={"registered_by": "vertical_slice_cli"},
    )
    save_evidence_record(tenant_id, record, base_dir=storage_dir)
    return record.to_dict()


def register_pipeline_run_record(
    *,
    tenant_id: str,
    intake_id: str,
    message: str,
    anamnesis_record: dict,
    evidence_record: dict,
    structured_summary: dict,
    blocked: bool,
    storage_dir: Path,
) -> dict:
    from pymia.contracts.pipeline_run_v1 import build_pipeline_run_record

    output_payload = {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "anamnesis_id": anamnesis_record["anamnesis_id"],
        "evidence_id": evidence_record["evidence_id"],
        "structured_evidence_status": structured_summary["status"],
        "blocked": blocked,
    }
    record = build_pipeline_run_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        message=message,
        evidence_ids=[evidence_record["evidence_id"]],
        status="BLOCKED" if blocked else "COMPLETED",
        output_payload=output_payload,
        steps_executed=[
            "evidence_record_registered",
            "structured_evidence_built",
            "evidence_sufficiency_checked",
            "owner_facing_report_built",
        ],
    )
    payload = record.model_dump(mode="json")
    payload["metadata"]["anamnesis_id"] = anamnesis_record["anamnesis_id"]
    _write_jsonl_line(storage_dir / tenant_id / "pipeline_runs.jsonl", payload)
    return payload


def build_structured_summary(
    path: Path,
    tenant_id: str,
    *,
    intake_id: str = "intake_cli_local",
    formula_ids: list[str] | None = None,
) -> dict:
    try:
        from pymia.smartpyme.structured_evidence_builder import build_structured_evidence_context
        from pymia.contracts.evidence_v1 import StructuredEvidence
        from pymia.audit_result.evidence_requirement_matcher import match_evidence_requirements

        original_formula_ids = formula_ids
        formula_ids = formula_ids or []
        payload = build_structured_evidence_context(
            excel_path=path,
            tenant_id=tenant_id,
            intake_record={"evidence_requests": [{"formula_ids": formula_ids}]},
        )
        evidence = payload["structured_evidence"]
        computed = evidence.get("computed_variables") or {}
        tables = evidence.get("tables") or []
        summary = {
            "status": "available",
            "computed_variables_count": len(computed),
            "computed_variable_names": sorted(computed.keys()),
            "tables_count": len(tables),
            "table_sheets": [
                {"name": t.get("sheet_name", "?"), "columns": len(t.get("columns", [])), "rows": len(t.get("rows", []))}
                for t in tables
            ],
            "case_id": intake_id,
            "sufficiency": [],
            "unsupported_formula_ids": [],
            "catalog_reconciliation": [],
        }

        # Run catalog reconciliation
        structured_ev = StructuredEvidence.model_validate(evidence)
        matches = match_evidence_requirements(structured_ev)
        reconciliation_list = []
        for m in matches:
            reconciliation_list.append({
                "formula_id": m.formula_id,
                "pathology_code": m.pathology_code,
                "status": m.status,
                "available_evidence": m.available_evidence,
                "missing_evidence": m.missing_evidence,
                "matched_sources": m.matched_sources,
                "required_evidence": m.required_evidence,
                "required_variables": m.required_variables,
                "next_audit_questions": m.next_audit_questions,
            })

        if original_formula_ids:
            reconciliation_list = [
                d for d in reconciliation_list if d["formula_id"] in original_formula_ids
            ]
        summary["catalog_reconciliation"] = reconciliation_list

        if formula_ids:
            from pymia.contracts.formula_contract import SUPPORTED_FORMULAS
            from pymia.diagnostic_core.evidence_sufficiency import build_evidence_sufficiency_report_from_structured_evidence

            supported_formula_ids = [formula_id for formula_id in formula_ids if formula_id in SUPPORTED_FORMULAS]
            unsupported_formula_ids = [formula_id for formula_id in formula_ids if formula_id not in SUPPORTED_FORMULAS]
            summary["unsupported_formula_ids"] = unsupported_formula_ids
            if supported_formula_ids:
                sufficiency = build_evidence_sufficiency_report_from_structured_evidence(
                    structured_ev,
                    case_id=intake_id,
                    tenant_id=tenant_id,
                    formula_ids=supported_formula_ids,
                )
                summary["sufficiency"] = [item.model_dump(mode="json") for item in sufficiency]
        return summary
    except Exception as exc:
        raise exc


def build_report(
    path: Path,
    message: str,
    profile: dict,
    *,
    tenant_id: str = "tenant_cli_local",
    intake_id: str = "intake_cli_local",
    formula_ids: list[str] | None = None,
    storage_dir: Path | None = None,
    business_taxonomy: dict | None = None,
) -> dict:
    has_rows = profile["rows"] > 1 and profile["columns"] > 0
    has_columns = has_operational_columns(profile["headers"])
    actual_storage_dir = storage_dir or Path(".tmp/vertical_slice_storage")
    anamnesis_record = register_anamnesis_record(
        message,
        tenant_id,
        intake_id,
        actual_storage_dir,
        business_taxonomy=business_taxonomy,
    )
    evidence_record = register_evidence_record(
        path,
        tenant_id,
        intake_id,
        actual_storage_dir,
    )
    structured_summary = build_structured_summary(
        path,
        tenant_id,
        intake_id=intake_id,
        formula_ids=formula_ids,
    )
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
    pipeline_run_record = register_pipeline_run_record(
        tenant_id=tenant_id,
        intake_id=intake_id,
        message=message,
        anamnesis_record=anamnesis_record,
        evidence_record=evidence_record,
        structured_summary=structured_summary,
        blocked=blocked,
        storage_dir=actual_storage_dir,
    )
    report["anamnesis_record"] = anamnesis_record
    report["evidence_record"] = evidence_record
    report["pipeline_run_record"] = pipeline_run_record
    report["structured_evidence_summary"] = structured_summary
    return report


def build_markdown(
    path: Path,
    message: str,
    profile: dict,
    *,
    tenant_id: str = "tenant_cli_local",
    intake_id: str = "intake_cli_local",
    formula_ids: list[str] | None = None,
    storage_dir: Path | None = None,
    business_taxonomy: dict | None = None,
) -> str:
    report = build_report(
        path,
        message,
        profile,
        tenant_id=tenant_id,
        intake_id=intake_id,
        formula_ids=formula_ids,
        storage_dir=storage_dir,
        business_taxonomy=business_taxonomy,
    )
    return render_markdown_from_report(path, message, profile, report)


def render_markdown_from_report(path: Path, message: str, profile: dict, report: dict) -> str:
    lines = [
        "# Reporte owner-facing local",
        f"Estado: {report['status']}",
        f"Archivo: {path.name}",
        f"Mensaje: {message}",
        f"Tenant: {report['tenant_id']}",
        f"Intake: {report['intake_id']}",
        f"Anamnesis ID: {report['anamnesis_record']['anamnesis_id']}",
        f"Evidence ID: {report['evidence_record']['evidence_id']}",
        f"Evidence SHA-256: {report['evidence_record']['content_hash']}",
        f"Run ID: {report['pipeline_run_record']['run_id']}",
        f"Hoja: {profile['sheet']}",
        f"Filas: {profile['rows']}",
        f"Columnas: {profile['columns']}",
        f"Resumen: {report['summary']}",
        "",
        "## Anamnesis",
    ]
    taxonomy = report["anamnesis_record"].get("business_taxonomy", {})
    lines.append(f"- Empresa tipo: {taxonomy.get('empresa_tipo', 'desconocido')}")
    lines.append(f"- Industria: {taxonomy.get('industria', 'desconocido')}")
    lines.append(f"- Modelo comercial: {taxonomy.get('modelo_comercial', 'desconocido')}")
    if taxonomy.get("canales_venta"):
        lines.append(f"- Canales de venta: {', '.join(taxonomy['canales_venta'])}")
    if taxonomy.get("areas_criticas"):
        lines.append(f"- Áreas críticas: {', '.join(taxonomy['areas_criticas'])}")
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
        lines.append(f"- Case ID: {structured_summary['case_id']}")
        if structured_summary["sufficiency"] or structured_summary["unsupported_formula_ids"]:
            lines.append("")
            lines.append("## Suficiencia de evidencia")
            for item in structured_summary["sufficiency"]:
                lines.append(f"- {item['formula_id']}: {item['status']}")
                if item["missing_variables"]:
                    lines.append(f"  - Faltan: {', '.join(item['missing_variables'])}")
            for formula_id in structured_summary["unsupported_formula_ids"]:
                lines.append(f"- {formula_id}: UNSUPPORTED_FORMULA")
    else:
        lines.append(f"- Motivo: {structured_summary['reason']}")
    lines.append("")
    lines.append("## Próxima pregunta")
    reconciliation = structured_summary.get("catalog_reconciliation") if structured_summary.get("status") == "available" else None
    owner_question = None
    tech_reference = None
    if reconciliation:
        question_candidates = [e for e in reconciliation if e.get("next_audit_questions")]
        alignment = align_next_question(message, question_candidates)
        if alignment["status"] == "MISALIGNED":
            owner_question = "Entiendo que tu preocupación principal parece ser caja/liquidez. Antes de avanzar con una pregunta técnica sobre stock, ¿querés que enfoquemos el análisis en caja, banco, cobros o pagos?"
            tech_reference = f"Referencia técnica: reconducción_axis_{alignment['declared_axis']}"
        else:
            for entry in question_candidates:
                owner_q, tech_ref = _build_owner_question(entry)
                if owner_q:
                    owner_question = owner_q
                    tech_reference = tech_ref
                    break
    if owner_question:
        lines.append(f"- {owner_question}")
        if tech_reference:
            lines.append(f"  - {tech_reference}")
    elif report["next_questions"]:
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


def build_pipeline(
    path: Path,
    message: str,
    *,
    tenant_id: str = "tenant_cli_local",
    intake_id: str = "intake_cli_local",
    formula_ids: list[str] | None = None,
    storage_dir: Path | None = None,
    business_taxonomy: dict | None = None,
) -> dict:
    profile = inspect_excel(path)
    report = build_report(
        path,
        message,
        profile,
        tenant_id=tenant_id,
        intake_id=intake_id,
        formula_ids=formula_ids,
        storage_dir=storage_dir,
        business_taxonomy=business_taxonomy,
    )
    markdown = render_markdown_from_report(path, message, profile, report)
    evidence_record = report["evidence_record"]
    pipeline_run_record = report["pipeline_run_record"]
    structured_summary = report.get("structured_evidence_summary") or {}
    catalog_reconciliation = structured_summary.get("catalog_reconciliation") or []
    return {
        "status": report["status"],
        "profile": profile,
        "report": report,
        "markdown": markdown,
        "evidence_id": evidence_record["evidence_id"],
        "evidence_hash": evidence_record["content_hash"],
        "run_id": pipeline_run_record["run_id"],
        "output_hash": pipeline_run_record["output_hash"],
        "missing_evidence": report["missing_evidence"],
        "next_questions": report["next_questions"],
        "structured_summary": report["structured_evidence_summary"],
        "catalog_reconciliation": catalog_reconciliation,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--output")
    parser.add_argument("--tenant-id", default="tenant_cli_local")
    parser.add_argument("--intake-id", default="intake_cli_local")
    parser.add_argument("--formula-id", action="append", default=[])
    parser.add_argument("--storage-dir", default=".tmp/vertical_slice_storage")
    parser.add_argument("--empresa-tipo", default=None)
    parser.add_argument("--industria", default=None)
    parser.add_argument("--modelo-comercial", default=None)
    parser.add_argument("--canal-venta", action="append", default=[])
    parser.add_argument("--area-critica", action="append", default=[])
    args = parser.parse_args(argv)
    path = Path(args.excel)
    if not path.exists():
        raise FileNotFoundError(path)
    business_taxonomy = {
        key: value
        for key, value in {
            "empresa_tipo": args.empresa_tipo,
            "industria": args.industria,
            "modelo_comercial": args.modelo_comercial,
            "canales_venta": args.canal_venta,
            "areas_criticas": args.area_critica,
        }.items()
        if value not in (None, [])
    }
    pipeline = build_pipeline(
        path,
        args.message,
        tenant_id=args.tenant_id,
        intake_id=args.intake_id,
        formula_ids=args.formula_id,
        storage_dir=Path(args.storage_dir),
        business_taxonomy=business_taxonomy or None,
    )
    markdown = pipeline["markdown"]
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
