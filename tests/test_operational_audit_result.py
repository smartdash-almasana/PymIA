from __future__ import annotations

from pymia.audit_result.builder import build_operational_audit_result
from pymia.audit_result.validators import validate_operational_audit_result
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.report_generator_v2 import build_narrative_report_v2


def _sample_evidence() -> StructuredEvidence:
    return StructuredEvidence(
        tenant_id="tenant-audit",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="la_textil_cosida_srl_mar_abr_may_2026.xlsx",
        computed_variables={
            "ventas_total": 33554851.0,
            "costos_total": 7931545.0,
            "margen_bruto": 25623306.0,
            "margen_bruto_pct": 0.7636,
        },
        metadata={
            "taxonomia_inicial": {
                "rubro": "textil",
                "tipo_pyme": "comercio",
                "produce_o_revende": "mixto",
                "maneja_stock": "si",
            },
            "sheet_reports": {
                "productos": "OK",
                "ventas": "OK",
                "compras": "OK",
                "stock": "OK",
                "costos_fijos": "OK",
                "caja_banco": "OK",
                "resumen_mensual": "OK",
                "señales_operativas": "OK",
            },
            "signals": [
                {
                    "signal_id": "SIG-001",
                    "signal_type": "margen_bajo",
                    "severity": "CRÍTICA",
                    "description": "Margen bruto por debajo del objetivo operativo.",
                    "suggested_action": "Reducir descuentos acumulados por canal mayorista.",
                },
                {
                    "signal_id": "SIG-006",
                    "signal_type": "caja_tensionada",
                    "severity": "ALTA",
                    "description": "Liquidez limitada para reponer insumos.",
                    "suggested_action": "Acelerar cobranzas y priorizar caja inmediata.",
                },
                {
                    "signal_id": "SIG-002",
                    "signal_type": "sobrestock",
                    "severity": "MEDIA",
                    "description": "Capital inmovilizado en SKU de baja rotacion.",
                    "suggested_action": "Liquidar stock lento en 2 semanas.",
                },
            ],
        },
    )


def _build_result():
    evidence = _sample_evidence()
    pool = extract_evidence_pool(evidence)
    report = build_narrative_report_v2(pool)
    grounding = validate_grounding(report, pool)
    return build_operational_audit_result(
        evidence=evidence,
        report=report,
        grounding=grounding,
        audit_id="audit_la_textil_2026_05_19",
    )


def test_operational_audit_result_build_and_validate() -> None:
    result = _build_result()
    validated = validate_operational_audit_result(result)

    assert validated.audit_id == "audit_la_textil_2026_05_19"
    assert validated.tenant_id == "tenant-audit"
    assert validated.source_file.endswith(".xlsx")
    assert validated.narrative_payload.allowed_messages
    assert validated.audit_trail.grounding_status == "valid"


def test_all_claims_and_actions_have_evidence_ids() -> None:
    result = _build_result()

    for metric in result.computed_metrics:
        assert metric.evidence_ids
    for finding in result.pathology_findings:
        assert finding.evidence_ids
        for action in finding.suggested_actions:
            assert action.evidence_ids
    for msg in result.narrative_payload.allowed_messages:
        assert msg.evidence_ids


def test_open_threads_reference_existing_findings_or_signals() -> None:
    result = _build_result()

    finding_ids = {f.finding_id for f in result.pathology_findings}
    signal_ids = {s.signal_id for s in result.operational_signals}
    for thread in result.open_audit_threads:
        for ref in thread.opened_by:
            assert ref in finding_ids or ref in signal_ids


def test_taxonomy_is_populated_and_traced_to_pathologies() -> None:
    result = _build_result()

    assert result.taxonomy.dimensions
    assert result.taxonomy.triage_level in {"sangria", "inestabilidad", "optimizacion"}
    assert result.taxonomy.symptom_links

    known_pathologies = {f.pathology_code for f in result.pathology_findings}
    for link in result.taxonomy.symptom_links:
        assert link.evidence_ids
        assert link.candidate_pathology in known_pathologies


def test_operational_audit_result_does_not_include_raw_tables_or_kernel_dump() -> None:
    result = _build_result()

    payload = result.model_dump(mode="json")
    assert "tables" not in payload
    assert "raw_tables" not in payload
    assert "kernel_output" not in payload


def test_pathology_routing_summary_is_present_and_hermes_ready() -> None:
    result = _build_result()

    assert result.pathology_routing_summary
    thread_ids = {t.thread_id for t in result.open_audit_threads}
    for route in result.pathology_routing_summary:
        assert route.pathology_code
        assert route.status in {"calculable", "candidate", "pending_data", "blocked", "not_applicable"}
        assert route.thread_id in thread_ids
        assert route.next_question


def test_pathology_routing_summary_sorted_by_status_then_severity() -> None:
    result = _build_result()

    order = {"blocked": 0, "pending_data": 1, "candidate": 2, "calculable": 3, "not_applicable": 4}
    values = [order[item.status] for item in result.pathology_routing_summary]
    assert values == sorted(values)
