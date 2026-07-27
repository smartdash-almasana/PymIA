from __future__ import annotations

from datetime import date

from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.models import NarrativeReport, ValidationResult

from .evidence_requirement_matcher import match_evidence_requirements
from .models import (
    AllowedMessage,
    AuditTrail,
    BusinessContext,
    ComputedMetric,
    DocumentRef,
    ExpectedBenefit,
    ImprovementOpportunity,
    Impact,
    NarrativePayload,
    NextAuditQuestion,
    OpenAuditThread,
    OperationalAuditResult,
    OperationalSignal,
    OperationalTaxonomy,
    PathologyFindingResult,
    PathologyRoutingSummary,
    PeriodAnalyzed,
    PriorityProblem,
    Risk,
    SuggestedAction,
    SymptomTaxonomyPathologyLink,
    TaxonomyDimension,
)


_SIGNAL_TO_PATHOLOGY = {
    "margen_bajo": "REN_001",
    "margen_negativo": "REN_001",
    "precio_desactualizado": "REN_001",
    "caja_tensionada": "LIQ_001",
    "sobrestock": "INV_002",
    "stock_bajo": "INV_001",
}


def _severity_to_priority(raw: object) -> str:
    text = str(raw or "").strip().upper()
    mapping = {
        "CRITICA": "critical",
        "CRÍTICA": "critical",
        "ALTA": "high",
        "MEDIA": "medium",
        "BAJA": "low",
        "LOW": "low",
        "MEDIUM": "medium",
        "HIGH": "high",
        "CRITICAL": "critical",
    }
    return mapping.get(text, "medium")


def _severity_rank(priority: str) -> int:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return order.get(priority, 0)


def _infer_business_type(evidence: StructuredEvidence) -> str:
    normalized = evidence.file_name.lower() if evidence.file_name else ""
    if "textil" in normalized:
        return "pyme_textil"
    return "pyme_general"


def _infer_period(evidence: StructuredEvidence) -> PeriodAnalyzed:
    md = evidence.metadata or {}
    period = md.get("period") if isinstance(md, dict) else None
    if isinstance(period, dict) and period.get("from") and period.get("to"):
        return PeriodAnalyzed.model_validate(period)
    year = date.today().year
    return PeriodAnalyzed.model_validate({"from": f"{year}-01-01", "to": f"{year}-12-31", "granularity": "monthly"})


def _deterministic_action(pathology_code: str) -> str:
    defaults = {
        "LIQ_001": "Separar ingresos inmediatos vs diferidos y priorizar cobranzas de mayor monto.",
        "REN_001": "Pausar descuentos acumulados y revisar precio-costo por SKU/canal.",
        "INV_002": "Liquidar stock lento y frenar compras de baja rotacion.",
        "INV_001": "Priorizar reposicion de SKU de alta rotacion por margen.",
    }
    return defaults.get(pathology_code, "Completar evidencia faltante y definir accion operativa en 7 dias.")


def _triage_level(signals: list[dict[str, object]]) -> str:
    if any(_severity_to_priority(s.get("severity")) == "critical" for s in signals):
        return "sangria"
    if any(_severity_to_priority(s.get("severity")) == "high" for s in signals):
        return "inestabilidad"
    return "optimizacion"


def _build_taxonomy(
    evidence: StructuredEvidence,
    *,
    signals_raw: list[dict[str, object]],
    findings: list[PathologyFindingResult],
) -> OperationalTaxonomy:
    md = evidence.metadata if isinstance(evidence.metadata, dict) else {}
    initial = md.get("taxonomia_inicial") if isinstance(md, dict) else None

    dims: list[TaxonomyDimension] = []
    if isinstance(initial, dict):
        for key in ("rubro", "tipo_pyme", "produce_o_revende", "maneja_stock"):
            val = initial.get(key)
            if val:
                dims.append(TaxonomyDimension(key=key, value=str(val), source="anamnesis"))

    inferred_dims = {
        "empresa_tipo": _infer_business_type(evidence),
        "modelo_comercial": "comercio" if "ventas_total" in (evidence.computed_variables or {}) else "mixto",
        "areas_criticas": "margen,caja,stock" if findings else "sin_senales",
    }
    for key, value in inferred_dims.items():
        if not any(d.key == key for d in dims):
            dims.append(TaxonomyDimension(key=key, value=value, source="inference"))

    links: list[SymptomTaxonomyPathologyLink] = []
    by_code = {f.pathology_code: f for f in findings}

    for sig in signals_raw:
        sid = str(sig.get("signal_id") or "unknown")
        sig_type = str(sig.get("signal_type") or "unknown").lower()
        pathology_code = _SIGNAL_TO_PATHOLOGY.get(sig_type)
        if not pathology_code or pathology_code not in by_code:
            continue
        links.append(
            SymptomTaxonomyPathologyLink(
                symptom_text=str(sig.get("description") or sig_type),
                operational_type=sig_type,
                candidate_pathology=pathology_code,
                evidence_required=by_code[pathology_code].required_evidence,
                evidence_ids=[f"signal:{sid}"],
            )
        )

    if not links:
        for finding in findings:
            links.append(
                SymptomTaxonomyPathologyLink(
                    symptom_text=f"Cobertura documental parcial para {finding.pathology_name}.",
                    operational_type=finding.pathology_name,
                    candidate_pathology=finding.pathology_code,
                    evidence_required=finding.required_evidence,
                    evidence_ids=finding.evidence_ids,
                )
            )

    return OperationalTaxonomy(
        taxonomy_version="v1",
        dimensions=dims,
        triage_level=_triage_level(signals_raw),
        symptom_links=links,
    )


def build_operational_audit_result(
    *,
    evidence: StructuredEvidence,
    report: NarrativeReport,
    grounding: ValidationResult,
    audit_id: str,
) -> OperationalAuditResult:
    sheet_reports = evidence.metadata.get("sheet_reports", {}) if isinstance(evidence.metadata, dict) else {}
    signals_raw = evidence.metadata.get("signals", []) if isinstance(evidence.metadata, dict) else []
    signals_raw = [s for s in signals_raw if isinstance(s, dict)]

    docs = [
        DocumentRef(
            name=evidence.file_name or "unknown_file",
            type="xlsx" if (evidence.file_name or "").lower().endswith(".xlsx") else "unknown",
            sheets=list(sheet_reports.keys()) if isinstance(sheet_reports, dict) else [],
        )
    ]

    business_context = BusinessContext(
        business_type=_infer_business_type(evidence),
        period_analyzed=_infer_period(evidence),
        documents_used=docs,
    )

    computed_metrics: list[ComputedMetric] = []
    for key, value in evidence.computed_variables.items():
        computed_metrics.append(
            ComputedMetric(
                metric_id=f"metric:{key}",
                name=key,
                value=float(value),
                unit="ARS",
                period="consolidated",
                formula_id=key,
                evidence_ids=[f"computed:{key}"],
                confidence="high",
            )
        )

    operational_signals: list[OperationalSignal] = []
    for sig in signals_raw:
        sid = str(sig.get("signal_id") or "unknown")
        stype = str(sig.get("signal_type") or "unknown").lower()
        severity = _severity_to_priority(sig.get("severity"))
        pcode = _SIGNAL_TO_PATHOLOGY.get(stype)
        operational_signals.append(
            OperationalSignal(
                signal_id=sid,
                signal_type=stype,
                severity=severity,
                description=str(sig.get("description") or "Signal without description"),
                suggested_action=str(sig.get("suggested_action") or "").strip() or None,
                evidence_ids=[f"signal:{sid}"],
                linked_pathologies=[pcode] if pcode else [],
                opens_audit_threads=[f"audit_thread:{pcode}" if pcode else f"audit_thread:signal:{sid}"],
            )
        )

    matches = match_evidence_requirements(evidence)

    signal_severity_by_code: dict[str, str] = {}
    for sig in operational_signals:
        for code in sig.linked_pathologies:
            current = signal_severity_by_code.get(code, "low")
            if _severity_rank(sig.severity) > _severity_rank(current):
                signal_severity_by_code[code] = sig.severity

    pathology_findings: list[PathologyFindingResult] = []
    for m in matches:
        severity = signal_severity_by_code.get(m.pathology_code)
        if severity is None:
            severity = "high" if m.status in {"blocked", "pending_data"} else "medium"
            if m.status == "not_applicable":
                severity = "low"

        q_items: list[NextAuditQuestion] = []
        for i, q in enumerate(m.next_audit_questions, start=1):
            q_items.append(
                NextAuditQuestion(
                    question_id=f"question:{m.pathology_code}:{i}",
                    question=str(q.get("question") or f"Que falta para evaluar {m.pathology_code}?"),
                    reason=f"Completar evidencia para {m.pathology_code}.",
                    requires_data=[str(x) for x in q.get("requires_data", []) if isinstance(x, str)],
                    priority="high" if m.status in {"blocked", "pending_data"} else "medium",
                )
            )

        pathology_findings.append(
            PathologyFindingResult(
                finding_id=f"finding:{m.pathology_code}:{m.formula_id}",
                pathology_code=m.pathology_code,
                pathology_name=m.pathology_name,
                formula_id=m.formula_id,
                status=m.status,
                severity=severity,
                summary=f"Cobertura de evidencia para {m.pathology_name}: {m.status}.",
                available_evidence=m.available_evidence,
                missing_evidence=m.missing_evidence,
                matched_sources=m.matched_sources,
                required_evidence=m.required_evidence,
                required_variables=m.required_variables,
                impact=Impact(type="operational", description=f"Impacto operativo asociado a {m.pathology_name}.", estimated_amount=None, unit="ARS"),
                risk=Risk(description=f"Riesgo vigente si {m.pathology_name} no se confirma/refuta con evidencia completa.", time_horizon="short_term"),
                evidence_ids=m.matched_sources or [f"formula:{m.formula_id}"],
                related_metrics=[f"metric:{k}" for k in (evidence.computed_variables or {}).keys()][:3],
                suggested_actions=[
                    SuggestedAction(
                        action_id=f"action:{m.pathology_code}:{m.formula_id}:1",
                        description=_deterministic_action(m.pathology_code),
                        timeframe="7_days",
                        source="catalog_rule",
                        evidence_ids=m.matched_sources or [f"formula:{m.formula_id}"],
                    )
                ],
                next_audit_questions=q_items,
            )
        )

    taxonomy = _build_taxonomy(evidence, signals_raw=signals_raw, findings=pathology_findings)

    relevant_findings = [f for f in pathology_findings if f.status in {"calculable", "candidate", "pending_data", "blocked"}]
    ranked_findings = sorted(relevant_findings, key=lambda f: _severity_rank(f.severity), reverse=True)

    priority_problems: list[PriorityProblem] = []
    for i, finding in enumerate(ranked_findings[:3], start=1):
        priority_problems.append(
            PriorityProblem(
                priority=i,
                title=finding.pathology_name,
                severity=finding.severity,
                why_it_matters=finding.summary,
                linked_findings=[finding.finding_id],
                linked_pathologies=[finding.pathology_code],
                recommended_focus=finding.pathology_code.lower(),
            )
        )

    open_threads: list[OpenAuditThread] = []
    for finding in ranked_findings:
        thread_id = f"audit_thread:{finding.pathology_code}"
        open_threads.append(
            OpenAuditThread(
                thread_id=thread_id,
                title=f"Auditoria de {finding.pathology_name}",
                status="open",
                opened_by=[finding.finding_id],
                business_question=f"Que evidencia falta para cerrar {finding.pathology_code} y decidir accion?",
                next_steps=[
                    "Completar evidencia faltante del catalogo.",
                    "Reevaluar formula y estado de auditabilidad.",
                    "Confirmar accion de 7 dias con responsable.",
                ],
                required_data=finding.missing_evidence or finding.required_evidence,
                expected_benefit=ExpectedBenefit(type="operational_improvement", description="Reducir incertidumbre y decidir con evidencia verificable."),
                priority=finding.severity,
            )
        )

    improvement_opportunities: list[ImprovementOpportunity] = []
    for thread in open_threads:
        improvement_opportunities.append(
            ImprovementOpportunity(
                opportunity_id=f"opp:{thread.thread_id}",
                type="process_improvement",
                description=f"Cerrar brechas de evidencia para {thread.title.lower()}.",
                linked_threads=[thread.thread_id],
                estimated_benefit="Mayor trazabilidad y menor incertidumbre operacional.",
                priority="high" if thread.priority in {"critical", "high"} else "medium",
            )
        )

    status_order = {"blocked": 0, "pending_data": 1, "candidate": 2, "calculable": 3, "not_applicable": 4}
    category_by_code = {f.pathology_code: f.impact.type for f in pathology_findings}
    thread_by_code = {t.thread_id.split("audit_thread:")[-1]: t.thread_id for t in open_threads if t.thread_id.startswith("audit_thread:")}
    routing_candidates = sorted(
        ranked_findings,
        key=lambda f: (status_order.get(f.status, 9), -_severity_rank(f.severity), f.pathology_code),
    )
    pathology_routing_summary: list[PathologyRoutingSummary] = []
    for finding in routing_candidates:
        thread_id = f"audit_thread:{finding.pathology_code}"
        next_question = (
            finding.next_audit_questions[0].question
            if finding.next_audit_questions
            else f"Necesito evidencia faltante para auditar {finding.pathology_code}."
        )
        pathology_routing_summary.append(
            PathologyRoutingSummary(
                pathology_code=finding.pathology_code,
                status=finding.status,
                category=category_by_code.get(finding.pathology_code, "operational"),
                thread_id=thread_by_code.get(finding.pathology_code, thread_id),
                missing_evidence=finding.missing_evidence,
                next_question=next_question,
            )
        )

    allowed_messages: list[AllowedMessage] = []
    for claim_idx, section in enumerate(report.sections):
        for claim in section.claims[:2]:
            if not claim.evidence_ids:
                continue
            allowed_messages.append(AllowedMessage(message_id=f"msg:{claim_idx}:{len(allowed_messages)+1}", text=claim.text, evidence_ids=claim.evidence_ids))

    narrative_payload = NarrativePayload(
        allowed_messages=allowed_messages,
        forbidden_inferences=[
            "No afirmar quiebra.",
            "No afirmar fraude.",
            "No afirmar rentabilidad neta si no fue calculada.",
            "No recomendar deuda sin evidencia de capacidad de repago.",
        ],
        tone="dueño_pyme_directo",
    )

    audit_trail = AuditTrail(
        sheet_reports=sheet_reports if isinstance(sheet_reports, dict) else {},
        validation_issues_count=len(grounding.errors),
        source_evidence_count=len(evidence.computed_variables) + len(operational_signals) + len((sheet_reports or {})),
        grounding_status="valid" if grounding.ok else "invalid",
    )

    blocked_sheets = [status for status in (sheet_reports or {}).values() if str(status).upper() == "BLOCKED"]
    audit_status = "blocked" if blocked_sheets else ("complete" if grounding.ok else "partial")
    confidence = "high" if grounding.ok and not blocked_sheets else ("medium" if grounding.ok else "low")

    return OperationalAuditResult(
        audit_id=audit_id,
        tenant_id=evidence.tenant_id,
        source_file=evidence.file_name or "unknown_file",
        audit_status=audit_status,
        confidence=confidence,
        business_context=business_context,
        taxonomy=taxonomy,
        computed_metrics=computed_metrics,
        pathology_findings=pathology_findings,
        operational_signals=operational_signals,
        priority_problems=priority_problems,
        pathology_routing_summary=pathology_routing_summary,
        open_audit_threads=open_threads,
        improvement_opportunities=improvement_opportunities,
        narrative_payload=narrative_payload,
        audit_trail=audit_trail,
    )
