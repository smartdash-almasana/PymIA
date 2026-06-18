from __future__ import annotations

from typing import Any, Literal, TypedDict

ServiceDepthLevel = Literal["FIRST_AID", "DETERMINISTIC_DIAGNOSIS", "ORGANIZATIONAL_LAB"]
EvidenceDepth = Literal["single_source", "cross_source", "longitudinal"]
CaseFileDepth = Literal["minimal", "partial", "full"]
NextAllowedAction = Literal[
    "request_minimal_evidence",
    "run_first_aid_microservice",
    "request_cross_source_evidence",
    "run_deterministic_diagnosis",
    "request_lab_onboarding_evidence",
    "open_organizational_lab_continuity",
    "block_until_required_evidence",
]


class ServiceDepthVerdict(TypedDict):
    level: ServiceDepthLevel
    reason: str
    required_evidence_depth: EvidenceDepth
    required_case_file_depth: CaseFileDepth
    next_allowed_action: NextAllowedAction


# Reason codes (stable, testable identifiers)
REASON_SINGLE_SOURCE_TASK_REQUEST = "single_source_task_request"
REASON_INSUFFICIENT_SIGNAL = "insufficient_signal_for_deeper_diagnosis"
REASON_ECONOMIC_PAIN_WITH_CROSS_SOURCE = "declared_economic_pain_with_cross_source_evidence"
REASON_ECONOMIC_PAIN_REQUIRES_CROSS_SOURCE = "declared_economic_pain_requires_cross_source_evidence"
REASON_LAB_INTENT_REQUIRES_ONBOARDING = "declared_lab_intent_requires_onboarding"
REASON_LAB_INTENT_WITH_CONTINUITY = "declared_lab_intent_with_case_continuity"
REASON_MULTI_AREA_CRITICAL = "multi_area_critical_case_requires_lab"


# Routing vocabulary (V1). These terms classify service depth only.
# They are not sector knowledge, formulas, pathologies, or diagnosis.
ROUTING_VOCABULARY = {
    "first_aid_terms": (
        "mirame",
        "mirar",
        "revisame",
        "revisar",
        "ordename",
        "ordenar",
        "limpiame",
        "limpiar",
        "sacame algo en limpio",
        "sacar algo en limpio",
        "calculame",
        "calcular",
        "este excel",
        "esta planilla",
        "este archivo",
    ),
    "economic_or_operational_pain_terms": (
        "margen",
        "caja",
        "stock",
        "rentabilidad",
        "costos",
        "costo",
        "ventas",
        "vendo pero no me queda plata",
        "no me queda plata",
        "no me cierra",
        "no se si gano",
        "no sé si gano",
        "mercado libre",
        "proveedores",
        "conciliacion",
        "conciliación",
        "produccion",
        "producción",
    ),
    "lab_intent_terms": (
        "profesionalizar",
        "ordenar mi empresa",
        "ordenar el negocio",
        "ordenar la empresa",
        "que la empresa no dependa de mi",
        "que la empresa no dependa de mí",
        "preparar la empresa para crecer",
        "laboratorio completo",
        "trabajar con pymia como laboratorio",
        "gobernar la empresa",
        "sistema operativo",
    ),
    "generic_pain_terms": (
        "problema",
        "ayuda",
        "no entiendo",
        "quiero ver",
        "necesito revisar",
    ),
}


def derive_service_depth(
    *,
    taxonomic_intake: dict[str, Any] | None = None,
    raw_owner_message: str | None = None,
    evidence_records: list[dict[str, Any]] | None = None,
    owner_answer_records: list[dict[str, Any]] | None = None,
    evidence_request_records: list[dict[str, Any]] | None = None,
    pipeline_run_records: list[dict[str, Any]] | None = None,
) -> ServiceDepthVerdict:
    """Derive the proportional service depth for a case.

    This function is pure and deterministic. It does not diagnose, calculate formulas,
    persist records, call LLMs, or import diagnostic_core.
    """
    taxonomy = taxonomic_intake or {}
    evidences = evidence_records or []
    owner_answers = owner_answer_records or []
    evidence_requests = evidence_request_records or []
    pipeline_runs = pipeline_run_records or []

    text_parts = [raw_owner_message or ""]
    text_parts.extend(_string_values(taxonomy.get("dolores_declarados")))
    text_parts.extend(_string_values(taxonomy.get("frases_textuales")))
    text_parts.extend(_string_values(taxonomy.get("hipotesis_duenio")))
    for answer in owner_answers:
        text_parts.append(str(answer.get("raw_owner_answer") or ""))
    normalized_text = _normalize_text(" ".join(text_parts))

    areas_criticas_count = len(_as_list(taxonomy.get("areas_criticas")))
    has_declared_pain = bool(_as_list(taxonomy.get("dolores_declarados"))) or _contains_any(
        normalized_text,
        ROUTING_VOCABULARY["economic_or_operational_pain_terms"]
        + ROUTING_VOCABULARY["generic_pain_terms"],
    )
    evidence_count = len([record for record in evidences if record.get("status") != "REJECTED"])
    evidence_sources_distinct = len(
        {
            str(record.get("evidence_type") or record.get("source_kind") or "unknown")
            for record in evidences
            if record.get("status") != "REJECTED"
        }
    )
    has_evidence_request = bool(evidence_requests)
    has_pipeline_continuity = bool(pipeline_runs)

    if _contains_any(normalized_text, ROUTING_VOCABULARY["lab_intent_terms"]):
        if evidence_count == 0 and not has_evidence_request and not has_pipeline_continuity:
            return _verdict(
                level="ORGANIZATIONAL_LAB",
                reason=REASON_LAB_INTENT_REQUIRES_ONBOARDING,
                evidence_depth="longitudinal",
                case_file_depth="full",
                next_action="request_lab_onboarding_evidence",
            )
        return _verdict(
            level="ORGANIZATIONAL_LAB",
            reason=REASON_LAB_INTENT_WITH_CONTINUITY,
            evidence_depth="longitudinal",
            case_file_depth="full",
            next_action="open_organizational_lab_continuity",
        )

    if areas_criticas_count >= 3 and has_declared_pain:
        return _verdict(
            level="ORGANIZATIONAL_LAB",
            reason=REASON_MULTI_AREA_CRITICAL,
            evidence_depth="longitudinal",
            case_file_depth="full",
            next_action="request_lab_onboarding_evidence" if evidence_count == 0 else "open_organizational_lab_continuity",
        )

    if _contains_any(normalized_text, ROUTING_VOCABULARY["economic_or_operational_pain_terms"]):
        if evidence_sources_distinct >= 2:
            return _verdict(
                level="DETERMINISTIC_DIAGNOSIS",
                reason=REASON_ECONOMIC_PAIN_WITH_CROSS_SOURCE,
                evidence_depth="cross_source",
                case_file_depth="partial",
                next_action="run_deterministic_diagnosis",
            )
        return _verdict(
            level="DETERMINISTIC_DIAGNOSIS",
            reason=REASON_ECONOMIC_PAIN_REQUIRES_CROSS_SOURCE,
            evidence_depth="cross_source",
            case_file_depth="partial",
            next_action="request_cross_source_evidence",
        )

    if evidence_count <= 1 and _contains_any(normalized_text, ROUTING_VOCABULARY["first_aid_terms"]):
        next_action: NextAllowedAction = "run_first_aid_microservice" if evidence_count == 1 else "request_minimal_evidence"
        return _verdict(
            level="FIRST_AID",
            reason=REASON_SINGLE_SOURCE_TASK_REQUEST,
            evidence_depth="single_source",
            case_file_depth="minimal",
            next_action=next_action,
        )

    return _verdict(
        level="FIRST_AID",
        reason=REASON_INSUFFICIENT_SIGNAL,
        evidence_depth="single_source",
        case_file_depth="minimal",
        next_action="request_minimal_evidence" if evidence_count == 0 else "run_first_aid_microservice",
    )


def _verdict(
    *,
    level: ServiceDepthLevel,
    reason: str,
    evidence_depth: EvidenceDepth,
    case_file_depth: CaseFileDepth,
    next_action: NextAllowedAction,
) -> ServiceDepthVerdict:
    return {
        "level": level,
        "reason": reason,
        "required_evidence_depth": evidence_depth,
        "required_case_file_depth": case_file_depth,
        "next_allowed_action": next_action,
    }


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_values(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if item is not None]
