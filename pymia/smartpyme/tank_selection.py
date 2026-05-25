"""
SmartPyme Tank Selection Slice.

Selección determinística mínima de KnowledgeTanks a partir de InterrogationResult.
NO ejecuta análisis. NO procesa archivos. NO diagnostica.
Produce TankSelectionResult serializable con:
- selected_tanks
- candidate_tanks
- suspended_tanks
- rejected_tanks
- evidence_requests
- warnings
- suggested_next_state

Tanques soportados:
- SMARTPYME_OPERATIONAL_PATHOLOGY_TANK
- SMARTPYME_EVIDENCE_AND_FORMULA_TANK

Ver: docs/smartpyme/SMARTPYME_TANK_SELECTION_SLICE.md
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from pymia.smartpyme.interrogation import (
    InterrogationResult,
    StructuredSelectors,
    SYMPTOM_DESCONOCIDO,
    SYMPTOM_DATOS_DUPLICADOS,
    SYMPTOM_MAESTRO_DESORDENADO,
    SYMPTOM_MARGEN_DUDOSO,
    SYMPTOM_COSTO_INCIERTO,
    SYMPTOM_DESCUADRE_DINERO,
    SYMPTOM_STOCK_INCONSISTENTE,
    SYMPTOM_SOBRECARGA_MANUAL,
    STATUS_BLOCKED_INSUFFICIENT_CONTEXT,
    STATUS_NEEDS_DISAMBIGUATION,
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_ORGANISM_CONTEXT,
    CLASSIFICATION_EXCEL_DIAGNOSTIC,
    CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
)


# ---------------------------------------------------------------------------
# Estados del ciclo de vida de un KnowledgeTank
# ---------------------------------------------------------------------------
TANK_AVAILABLE = "AVAILABLE"
TANK_CANDIDATE = "CANDIDATE"
TANK_ACTIVE = "ACTIVE"
TANK_SUSPENDED = "SUSPENDED"
TANK_DEACTIVATED = "DEACTIVATED"
TANK_REJECTED = "REJECTED"

ALLOWED_TANK_STATES = (
    TANK_AVAILABLE,
    TANK_CANDIDATE,
    TANK_ACTIVE,
    TANK_SUSPENDED,
    TANK_DEACTIVATED,
    TANK_REJECTED,
)


# ---------------------------------------------------------------------------
# Tanques conocidos
# ---------------------------------------------------------------------------
TANK_OPERATIONAL_PATHOLOGY = "SMARTPYME_OPERATIONAL_PATHOLOGY_TANK"
TANK_EVIDENCE_AND_FORMULA = "SMARTPYME_EVIDENCE_AND_FORMULA_TANK"

KNOWN_TANKS = (TANK_OPERATIONAL_PATHOLOGY, TANK_EVIDENCE_AND_FORMULA)


# ---------------------------------------------------------------------------
# Siguiente estado sugerido del interrogatorio
# ---------------------------------------------------------------------------
NEXT_ASK_CLARIFICATION = "ASK_CLARIFICATION"
NEXT_REQUEST_EVIDENCE = "REQUEST_EVIDENCE"
NEXT_CONFIRM_REFORMULATION = "CONFIRM_REFORMULATION"
NEXT_BLOCKED = "BLOCKED"
NEXT_READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"


# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------
@dataclass
class TankEvaluation:
    """Resultado de evaluación de un KnowledgeTank individual."""
    tank_id: str
    version: str
    lifecycle_state: str
    activation_score: int  # 0-100
    activation_reasons: List[str]
    deactivation_reasons: List[str]
    missing_context: List[str]
    missing_evidence: List[str]
    supported_outputs: List[str]
    unsupported_outputs: List[str]
    safety_warnings: List[str]
    next_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceRequest:
    """Pedido de evidencia generado por los tanques activos."""
    evidence_type: str
    description: str
    required_fields: List[str]
    reason: str
    blocks_analysis: bool
    enables_classification: Optional[str]
    source_tank: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TankSelectionResult:
    """Resultado completo de la selección de tanques."""
    input_summary: str
    selected_tanks: List[TankEvaluation]
    candidate_tanks: List[TankEvaluation]
    suspended_tanks: List[TankEvaluation]
    rejected_tanks: List[TankEvaluation]
    evidence_requests: List[EvidenceRequest]
    warnings: List[str]
    suggested_next_state: str
    suggested_classifications: List[str]
    runtime_compatibility: Dict[str, bool]
    audit_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_summary": self.input_summary,
            "selected_tanks": [t.to_dict() for t in self.selected_tanks],
            "candidate_tanks": [t.to_dict() for t in self.candidate_tanks],
            "suspended_tanks": [t.to_dict() for t in self.suspended_tanks],
            "rejected_tanks": [t.to_dict() for t in self.rejected_tanks],
            "evidence_requests": [e.to_dict() for e in self.evidence_requests],
            "warnings": self.warnings,
            "suggested_next_state": self.suggested_next_state,
            "suggested_classifications": self.suggested_classifications,
            "runtime_compatibility": self.runtime_compatibility,
            "audit_notes": self.audit_notes,
        }


# ---------------------------------------------------------------------------
# Reglas de activación por tanque
# ---------------------------------------------------------------------------

# Síntomas que activan el Operational Pathology Tank
_PATHOLOGY_SYMPTOMS = {
    SYMPTOM_DESCUADRE_DINERO,
    SYMPTOM_MARGEN_DUDOSO,
    SYMPTOM_DATOS_DUPLICADOS,
    SYMPTOM_STOCK_INCONSISTENTE,
    SYMPTOM_SOBRECARGA_MANUAL,
    SYMPTOM_COSTO_INCIERTO,
}

# Síntomas que activan el Evidence and Formula Tank
_EVIDENCE_SYMPTOMS = {
    SYMPTOM_MARGEN_DUDOSO,
    SYMPTOM_COSTO_INCIERTO,
    SYMPTOM_DATOS_DUPLICADOS,
    SYMPTOM_MAESTRO_DESORDENADO,
    SYMPTOM_DESCUADRE_DINERO,
    SYMPTOM_STOCK_INCONSISTENTE,
    SYMPTOM_SOBRECARGA_MANUAL,
}


def _has_real_symptoms(ir: InterrogationResult) -> bool:
    """¿El InterrogationResult tiene síntomas reales (no DESCONOCIDO)?"""
    return bool(
        ir.candidate_symptoms
        and ir.candidate_symptoms != [SYMPTOM_DESCONOCIDO]
    )


def _has_only_selectors(ir: InterrogationResult) -> bool:
    """¿Solo hay selectores estructurales sin relato con señal?"""
    return bool(ir.business_context) and not ir.semantic_signals


def _has_tabular_evidence(ir: InterrogationResult) -> bool:
    """¿Hay evidencia tabular disponible (Excel/export/sistema)?"""
    ev = ir.business_context.get("evidence_available", "")
    if ev:
        ev_lower = ev.lower()
        if any(k in ev_lower for k in ("excel", "export", "sistema")):
            return True
    # También revisar en el raw_input
    raw_lower = ir.raw_input.lower() if ir.raw_input else ""
    return any(k in raw_lower for k in ("excel", "planilla", "archivo", "export"))


def _evaluate_operational_pathology(ir: InterrogationResult) -> TankEvaluation:
    """Evalúa el Operational Pathology Tank para el caso dado."""
    activation_reasons: List[str] = []
    deactivation_reasons: List[str] = []
    missing_context: List[str] = []
    safety_warnings: List[str] = []
    score = 0

    has_symptoms = _has_real_symptoms(ir)
    only_selectors = _has_only_selectors(ir)
    blocked = ir.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT

    # Activadores
    if has_symptoms:
        matching = [s for s in ir.candidate_symptoms if s in _PATHOLOGY_SYMPTOMS]
        if matching:
            activation_reasons.append(
                f"Síntomas compatibles detectados: {', '.join(matching)}"
            )
            score += 40 + (len(matching) * 10)
        if ir.semantic_signals:
            activation_reasons.append(
                f"Señales semánticas presentes: {len(ir.semantic_signals)}"
            )
            score += 15
    elif only_selectors:
        # Safety gate: NO_SELECTOR_ONLY_ACTIVATION
        safety_warnings.append(
            "NO_SELECTOR_ONLY_ACTIVATION: selectores sin relato no activan tanque"
        )
        score = 10

    # Desactivadores
    if blocked:
        deactivation_reasons.append("Interrogatorio bloqueado por contexto insuficiente")
        score = 0
    if ir.candidate_symptoms == [SYMPTOM_DESCONOCIDO] and not only_selectors:
        deactivation_reasons.append("Sin síntomas identificables en el relato")

    # Missing context
    if ir.status == STATUS_NEEDS_DISAMBIGUATION:
        missing_context.append("Desambiguación pendiente del usuario")
    if not ir.reformulation or "no tengo suficiente" in ir.reformulation.lower():
        missing_context.append("Reformulación insuficiente")

    # Determinar estado
    if blocked or ir.candidate_symptoms == [SYMPTOM_DESCONOCIDO]:
        state = TANK_DEACTIVATED
    elif only_selectors:
        state = TANK_AVAILABLE  # No candidato sin relato
    elif has_symptoms and score >= 40:
        state = TANK_ACTIVE
    elif has_symptoms:
        state = TANK_CANDIDATE
    else:
        state = TANK_AVAILABLE

    # Cap score
    score = min(score, 100)

    # Next action
    if state == TANK_ACTIVE:
        if ir.status == STATUS_NEEDS_DISAMBIGUATION:
            next_action = NEXT_ASK_CLARIFICATION
        else:
            next_action = NEXT_REQUEST_EVIDENCE
    elif state == TANK_CANDIDATE:
        next_action = NEXT_CONFIRM_REFORMULATION
    else:
        next_action = NEXT_BLOCKED

    return TankEvaluation(
        tank_id=TANK_OPERATIONAL_PATHOLOGY,
        version="0.1.0-doc",
        lifecycle_state=state,
        activation_score=score,
        activation_reasons=activation_reasons,
        deactivation_reasons=deactivation_reasons,
        missing_context=missing_context,
        missing_evidence=[],
        supported_outputs=[
            "symptoms_candidates",
            "pathology_candidates",
            "clarification_questions",
            "hypothesis_candidates",
            "evidence_suggestions",
            "safety_warnings",
        ],
        unsupported_outputs=[
            "confirmed_diagnosis",
            "causal_assertion",
            "final_report",
        ],
        safety_warnings=safety_warnings,
        next_action=next_action,
    )


def _evaluate_evidence_and_formula(ir: InterrogationResult) -> TankEvaluation:
    """Evalúa el Evidence and Formula Tank para el caso dado."""
    activation_reasons: List[str] = []
    deactivation_reasons: List[str] = []
    missing_evidence: List[str] = []
    safety_warnings: List[str] = []
    score = 0

    has_symptoms = _has_real_symptoms(ir)
    has_evidence_needs = bool(ir.evidence_needs)
    has_suggested_class = ir.suggested_classification is not None
    has_tabular = _has_tabular_evidence(ir)
    blocked = ir.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT

    # Activadores
    if has_symptoms:
        matching = [s for s in ir.candidate_symptoms if s in _EVIDENCE_SYMPTOMS]
        if matching:
            activation_reasons.append(
                f"Síntomas con fórmulas asociadas: {', '.join(matching)}"
            )
            score += 30
    if has_evidence_needs:
        activation_reasons.append(
            f"EvidenceNeeds declarados: {len(ir.evidence_needs)}"
        )
        score += 25
    if has_suggested_class:
        activation_reasons.append(
            f"Clasificación sugerida compatible: {ir.suggested_classification}"
        )
        score += 20
    if has_tabular:
        activation_reasons.append("Evidencia tabular disponible")
        score += 15

    # Desactivadores
    if blocked:
        deactivation_reasons.append("Interrogatorio bloqueado por contexto insuficiente")
        score = 0
    if not has_evidence_needs and not has_suggested_class:
        deactivation_reasons.append("Sin evidence_needs ni clasificación sugerida")

    # Missing evidence
    if not has_tabular and has_symptoms:
        missing_evidence.append("Evidencia tabular (Excel/export) no confirmada")
    for en in ir.evidence_needs:
        missing_evidence.append(f"Falta: {en.evidence_type} ({en.description})")

    # Safety
    if has_suggested_class and not has_tabular:
        safety_warnings.append(
            "Clasificación sugerida sin evidencia tabular confirmada"
        )

    # Determinar estado
    if blocked:
        state = TANK_DEACTIVATED
    elif not has_symptoms and not has_evidence_needs:
        state = TANK_AVAILABLE
    elif has_evidence_needs and (has_tabular or has_suggested_class):
        state = TANK_ACTIVE
    elif has_evidence_needs or has_symptoms:
        state = TANK_CANDIDATE
    else:
        state = TANK_AVAILABLE

    score = min(score, 100)

    # Next action
    if state == TANK_ACTIVE:
        next_action = NEXT_REQUEST_EVIDENCE
    elif state == TANK_CANDIDATE:
        next_action = NEXT_CONFIRM_REFORMULATION
    else:
        next_action = NEXT_BLOCKED

    return TankEvaluation(
        tank_id=TANK_EVIDENCE_AND_FORMULA,
        version="0.1.0-doc",
        lifecycle_state=state,
        activation_score=score,
        activation_reasons=activation_reasons,
        deactivation_reasons=deactivation_reasons,
        missing_context=[],
        missing_evidence=missing_evidence,
        supported_outputs=[
            "document_type_suggestions",
            "expected_fields",
            "formula_candidates",
            "hypothesis_tests",
            "sufficiency_criteria",
            "evidence_requests",
        ],
        unsupported_outputs=[
            "formula_execution",
            "file_processing",
            "numeric_results",
            "final_diagnosis",
        ],
        safety_warnings=safety_warnings,
        next_action=next_action,
    )


def _build_evidence_requests(
    ir: InterrogationResult,
    pathology_eval: TankEvaluation,
    evidence_eval: TankEvaluation,
) -> List[EvidenceRequest]:
    """Construye EvidenceRequests a partir de los tanques activos."""
    requests: List[EvidenceRequest] = []
    seen_types: set = set()

    # Solo generar si al menos un tanque está ACTIVE o CANDIDATE
    active_or_candidate = (
        pathology_eval.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)
        or evidence_eval.lifecycle_state in (TANK_ACTIVE, TANK_CANDIDATE)
    )
    if not active_or_candidate:
        return requests

    for en in ir.evidence_needs:
        if en.evidence_type in seen_types:
            continue
        seen_types.add(en.evidence_type)

        # Determinar clasificación habilitada
        enables_class: Optional[str] = None
        if en.evidence_type == "excel_proveedores":
            enables_class = CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK
        elif en.evidence_type in ("excel_ventas_costos", "excel_caja_banco",
                                   "excel_stock"):
            enables_class = CLASSIFICATION_EXCEL_DIAGNOSTIC

        requests.append(EvidenceRequest(
            evidence_type=en.evidence_type,
            description=en.description,
            required_fields=en.required_fields,
            reason=en.reason,
            blocks_analysis=True,
            enables_classification=enables_class,
            source_tank=TANK_EVIDENCE_AND_FORMULA,
        ))

    return requests


def _resolve_suggested_next_state(
    pathology_eval: TankEvaluation,
    evidence_eval: TankEvaluation,
    ir: InterrogationResult,
) -> str:
    """Determina el próximo estado sugerido del interrogatorio."""
    if ir.status == STATUS_BLOCKED_INSUFFICIENT_CONTEXT:
        return NEXT_BLOCKED
    if ir.status == STATUS_NEEDS_DISAMBIGUATION:
        return NEXT_ASK_CLARIFICATION
    if pathology_eval.lifecycle_state == TANK_ACTIVE:
        return NEXT_REQUEST_EVIDENCE
    if evidence_eval.lifecycle_state == TANK_ACTIVE:
        return NEXT_REQUEST_EVIDENCE
    if (pathology_eval.lifecycle_state == TANK_CANDIDATE
            or evidence_eval.lifecycle_state == TANK_CANDIDATE):
        return NEXT_CONFIRM_REFORMULATION
    return NEXT_BLOCKED


def _collect_warnings(
    pathology_eval: TankEvaluation,
    evidence_eval: TankEvaluation,
    ir: InterrogationResult,
) -> List[str]:
    """Recopila warnings de ambos tanques + reglas globales."""
    warnings: List[str] = []
    warnings.extend(pathology_eval.safety_warnings)
    warnings.extend(evidence_eval.safety_warnings)

    # Regla global: selector-only
    if _has_only_selectors(ir):
        warnings.append(
            "Solo selectores estructurales sin relato. "
            "No se activa diagnóstico. Pedir contexto verbal."
        )

    # Regla global: sin runtime para clasificación sugerida
    if ir.suggested_classification and ir.suggested_classification not in (
        CLASSIFICATION_EXCEL_DIAGNOSTIC,
        CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
    ):
        warnings.append(
            f"RUNTIME_COMPATIBILITY: clasificación '{ir.suggested_classification}' "
            "no está implementada en runtime real"
        )

    return warnings


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def select_tanks(ir: InterrogationResult) -> TankSelectionResult:
    """
    Selección determinística de KnowledgeTanks a partir de InterrogationResult.

    No ejecuta análisis. No procesa archivos. No diagnostica.
    Produce TankSelectionResult serializable.

    Safety gates aplicados:
    - NO_DIAGNOSIS_WITHOUT_EVIDENCE
    - NO_SELECTOR_ONLY_ACTIVATION
    - NO_UNSUPPORTED_OUTPUT_PROMISE
    - RUNTIME_COMPATIBILITY_REQUIRED
    """
    if not isinstance(ir, InterrogationResult):
        raise TypeError("Se requiere InterrogationResult")

    # Evaluar ambos tanques
    pathology_eval = _evaluate_operational_pathology(ir)
    evidence_eval = _evaluate_evidence_and_formula(ir)

    # Clasificar en buckets según lifecycle_state
    selected: List[TankEvaluation] = []
    candidates: List[TankEvaluation] = []
    suspended: List[TankEvaluation] = []
    rejected: List[TankEvaluation] = []

    for ev in (pathology_eval, evidence_eval):
        if ev.lifecycle_state == TANK_ACTIVE:
            selected.append(ev)
        elif ev.lifecycle_state == TANK_CANDIDATE:
            candidates.append(ev)
        elif ev.lifecycle_state == TANK_SUSPENDED:
            suspended.append(ev)
        elif ev.lifecycle_state in (TANK_DEACTIVATED, TANK_REJECTED, TANK_AVAILABLE):
            rejected.append(ev)

    # Evidence requests
    evidence_requests = _build_evidence_requests(ir, pathology_eval, evidence_eval)

    # Warnings
    warnings = _collect_warnings(pathology_eval, evidence_eval, ir)

    # Suggested next state
    next_state = _resolve_suggested_next_state(pathology_eval, evidence_eval, ir)

    # Suggested classifications (solo las runtime-compatible)
    suggested_class: List[str] = []
    if ir.suggested_classification in (
        CLASSIFICATION_EXCEL_DIAGNOSTIC,
        CLASSIFICATION_SUPPLIER_DUPLICATE_CHECK,
    ):
        suggested_class.append(ir.suggested_classification)

    # Runtime compatibility
    runtime_compat = {
        "excel_diagnostic": True,
        "supplier_duplicate_check": True,
        "classification_auto": False,
        "html_output": False,
        "cash_reconciliation": False,
        "margin_analysis": False,
    }

    # Audit notes
    audit: List[str] = []
    audit.append(f"InterrogationResult.status={ir.status}")
    audit.append(f"candidate_symptoms={ir.candidate_symptoms}")
    audit.append(f"OperationalPathology: {pathology_eval.lifecycle_state} "
                 f"(score={pathology_eval.activation_score})")
    audit.append(f"EvidenceAndFormula: {evidence_eval.lifecycle_state} "
                 f"(score={evidence_eval.activation_score})")

    input_summary = (ir.raw_input[:80] + "...") if len(ir.raw_input) > 80 else ir.raw_input

    return TankSelectionResult(
        input_summary=input_summary,
        selected_tanks=selected,
        candidate_tanks=candidates,
        suspended_tanks=suspended,
        rejected_tanks=rejected,
        evidence_requests=evidence_requests,
        warnings=warnings,
        suggested_next_state=next_state,
        suggested_classifications=suggested_class,
        runtime_compatibility=runtime_compat,
        audit_notes=audit,
    )


__all__ = [
    "TankEvaluation",
    "EvidenceRequest",
    "TankSelectionResult",
    "select_tanks",
    "ALLOWED_TANK_STATES",
    "KNOWN_TANKS",
    "TANK_AVAILABLE",
    "TANK_CANDIDATE",
    "TANK_ACTIVE",
    "TANK_SUSPENDED",
    "TANK_DEACTIVATED",
    "TANK_REJECTED",
    "TANK_OPERATIONAL_PATHOLOGY",
    "TANK_EVIDENCE_AND_FORMULA",
    "NEXT_ASK_CLARIFICATION",
    "NEXT_REQUEST_EVIDENCE",
    "NEXT_CONFIRM_REFORMULATION",
    "NEXT_BLOCKED",
    "NEXT_READY_FOR_ANALYSIS",
]
