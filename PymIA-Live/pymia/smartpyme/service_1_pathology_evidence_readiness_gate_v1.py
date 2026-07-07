from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    Service1PathologyAnamnesisTriageEntrypointCandidateV1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY as ALLOWED_CANDIDATE_BLOCKED_UNSUPPORTED_PATHOLOGY,
    Service1AllowedComputationCandidateV1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_EVIDENCE_READINESS_GATE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_READY_FOR_COMPUTATION_PLAN: Final[str] = "READY_FOR_COMPUTATION_PLAN"
STATUS_NEEDS_OWNER_CONFIRMATION: Final[str] = "NEEDS_OWNER_CONFIRMATION"
STATUS_NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY: Final[str] = "BLOCKED_UNSUPPORTED_PATHOLOGY"
STATUS_BLOCKED_MISMATCHED_PATHOLOGY: Final[str] = "BLOCKED_MISMATCHED_PATHOLOGY"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_READY_FOR_COMPUTATION_PLAN,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_NEEDS_EVIDENCE,
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
    STATUS_BLOCKED_MISMATCHED_PATHOLOGY,
)

EvidenceReadinessGateStatusV1 = Literal[
    "READY_FOR_COMPUTATION_PLAN",
    "NEEDS_OWNER_CONFIRMATION",
    "NEEDS_EVIDENCE",
    "BLOCKED_UNSUPPORTED_PATHOLOGY",
    "BLOCKED_MISMATCHED_PATHOLOGY",
]

_FIELD_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "precio_venta": ("precio_venta", "precio", "precio_unitario", "precio_de_venta"),
    "costo_unitario": ("costo_unitario", "costo", "costo_base", "precio_compra"),
    "volumen_vendido": ("volumen_vendido", "cantidad", "cantidad_vendida", "unidades_vendidas"),
    "ventas_periodo": ("ventas_periodo", "ventas", "venta_total", "total_ventas", "importe_venta"),
    "cobranzas_periodo": ("cobranzas_periodo", "cobranzas", "cobros", "total_cobrado", "importe_cobrado"),
    "saldo_pendiente": ("saldo_pendiente", "saldo", "saldo_cobrar", "cuentas_por_cobrar"),
    "producto": ("producto", "sku", "articulo", "item"),
    "stock_actual": ("stock_actual", "stock", "inventario_actual"),
    "movimientos_stock": ("movimientos_stock", "movimientos", "entradas_salidas"),
    "fecha": ("fecha", "periodo", "periodo_ref", "fecha_movimiento"),
    "monto": ("monto", "importe", "valor", "total"),
    "entrada_salida": ("entrada_salida", "tipo_movimiento", "debe_haber", "ingreso_egreso"),
}


@dataclass(frozen=True)
class Service1PathologyEvidenceReadinessGateV1:
    schema_version: str
    service_name: str
    status: EvidenceReadinessGateStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    pathology_code: str | None
    allowed_computation_ref: str | None
    required_fields: tuple[str, ...]
    available_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]
    missing_confirmation_items: tuple[str, ...]
    business_period_reference: str | None
    next_owner_questions: tuple[str, ...]
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_entrypoint(
    entrypoint_candidate_result: Service1PathologyAnamnesisTriageEntrypointCandidateV1,
) -> Service1PathologyAnamnesisTriageEntrypointCandidateV1:
    if not isinstance(entrypoint_candidate_result, Service1PathologyAnamnesisTriageEntrypointCandidateV1):
        raise ValueError("entrypoint_candidate_result must be a Service1PathologyAnamnesisTriageEntrypointCandidateV1")
    return entrypoint_candidate_result


def _required_allowed_candidate(
    allowed_computation_candidate: Service1AllowedComputationCandidateV1,
) -> Service1AllowedComputationCandidateV1:
    if not isinstance(allowed_computation_candidate, Service1AllowedComputationCandidateV1):
        raise ValueError("allowed_computation_candidate must be a Service1AllowedComputationCandidateV1")
    return allowed_computation_candidate


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (tuple, list, set)):
        items = value
    else:
        items = (value,)
    cleaned: list[str] = []
    for item in items:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return tuple(cleaned)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _normalized_available_fields(
    allowed_candidate: Service1AllowedComputationCandidateV1,
    available_data_fields: tuple[str, ...],
) -> tuple[str, ...]:
    if available_data_fields:
        raw_available = available_data_fields
    else:
        raw_available = allowed_candidate.available_fields

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_available:
        normalized_item = _normalize_text(item)
        if normalized_item and normalized_item not in seen:
            normalized.append(normalized_item)
            seen.add(normalized_item)
    return tuple(normalized)


def _resolve_missing_fields(
    *,
    required_fields: tuple[str, ...],
    available_fields: tuple[str, ...],
    allowed_candidate_missing_fields: tuple[str, ...],
) -> tuple[str, ...]:
    available_set = set(available_fields)
    missing: list[str] = []
    for required_field in required_fields:
        aliases = _FIELD_ALIASES.get(required_field, (required_field,))
        if not any(_normalize_text(alias) in available_set for alias in aliases):
            missing.append(required_field)
    for field in allowed_candidate_missing_fields:
        if field not in missing:
            missing.append(field)
    return tuple(missing)


def _resolve_missing_confirmation_items(
    *,
    required_fields: tuple[str, ...],
    column_meaning_confirmations: tuple[str, ...],
    business_period_reference: str | None,
) -> tuple[str, ...]:
    missing: list[str] = []
    normalized_confirmations = tuple(_normalize_text(item) for item in column_meaning_confirmations)

    for required_field in required_fields:
        aliases = _FIELD_ALIASES.get(required_field, (required_field,))
        has_confirmation = any(
            any(_normalize_text(alias) in confirmation for alias in aliases)
            for confirmation in normalized_confirmations
        )
        if not has_confirmation:
            missing.append(required_field)

    if business_period_reference is None:
        missing.append("business_period_reference")

    return tuple(missing)


def _next_owner_questions(
    *,
    missing_fields: tuple[str, ...],
    missing_confirmation_items: tuple[str, ...],
    pathology_code: str | None,
) -> tuple[str, ...]:
    questions: list[str] = []

    if "business_period_reference" in missing_confirmation_items:
        questions.append("¿De qué período querés hacer este análisis?")

    confirmation_only = [item for item in missing_confirmation_items if item != "business_period_reference"]
    if confirmation_only:
        fields_text = ", ".join(confirmation_only)
        questions.append(f"¿Qué significan exactamente estas columnas para vos: {fields_text}?")

    if missing_fields:
        fields_text = ", ".join(missing_fields)
        questions.append(f"¿Podés completar o identificar estos datos mínimos para {pathology_code or 'la patología candidata'}: {fields_text}?")

    return tuple(questions)


def _build_result(
    *,
    entrypoint: Service1PathologyAnamnesisTriageEntrypointCandidateV1,
    allowed_candidate: Service1AllowedComputationCandidateV1,
    status: EvidenceReadinessGateStatusV1,
    available_fields: tuple[str, ...],
    missing_fields: tuple[str, ...],
    missing_confirmation_items: tuple[str, ...],
    business_period_reference: str | None,
    blocked_reason: str | None,
    owner_confirmation_required: bool,
    next_owner_questions: tuple[str, ...],
    metadata: dict[str, Any] | None,
) -> Service1PathologyEvidenceReadinessGateV1:
    return Service1PathologyEvidenceReadinessGateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=entrypoint.case_id,
        tenant_id=entrypoint.tenant_id,
        intake_id=entrypoint.intake_id,
        run_id=entrypoint.run_id,
        pathology_code=entrypoint.selected_primary_pathology,
        allowed_computation_ref=allowed_candidate.allowed_computation_ref,
        required_fields=allowed_candidate.required_fields,
        available_fields=available_fields,
        missing_fields=missing_fields,
        missing_confirmation_items=missing_confirmation_items,
        business_period_reference=business_period_reference,
        next_owner_questions=next_owner_questions,
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_pathology_evidence_readiness_gate_v1(
    *,
    entrypoint_candidate_result: Service1PathologyAnamnesisTriageEntrypointCandidateV1,
    allowed_computation_candidate: Service1AllowedComputationCandidateV1,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    business_period_reference: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyEvidenceReadinessGateV1:
    entrypoint = _required_entrypoint(entrypoint_candidate_result)
    allowed_candidate = _required_allowed_candidate(allowed_computation_candidate)

    effective_business_period_reference = (
        _clean_optional_text(business_period_reference)
        or _clean_optional_text(allowed_candidate.metadata.get("business_period_reference"))
    )
    available_fields = _normalized_available_fields(allowed_candidate, _clean_tuple(available_data_fields))
    required_fields = allowed_candidate.required_fields
    missing_fields = _resolve_missing_fields(
        required_fields=required_fields,
        available_fields=available_fields,
        allowed_candidate_missing_fields=allowed_candidate.missing_fields,
    )
    missing_confirmation_items = _resolve_missing_confirmation_items(
        required_fields=required_fields,
        column_meaning_confirmations=_clean_tuple(column_meaning_confirmations),
        business_period_reference=effective_business_period_reference,
    )

    if allowed_candidate.status == ALLOWED_CANDIDATE_BLOCKED_UNSUPPORTED_PATHOLOGY:
        return _build_result(
            entrypoint=entrypoint,
            allowed_candidate=allowed_candidate,
            status=STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
            available_fields=available_fields,
            missing_fields=missing_fields,
            missing_confirmation_items=missing_confirmation_items,
            business_period_reference=effective_business_period_reference,
            blocked_reason="unsupported_pathology_code",
            owner_confirmation_required=True,
            next_owner_questions=(),
            metadata=metadata,
        )

    if entrypoint.selected_primary_pathology != allowed_candidate.pathology_code:
        return _build_result(
            entrypoint=entrypoint,
            allowed_candidate=allowed_candidate,
            status=STATUS_BLOCKED_MISMATCHED_PATHOLOGY,
            available_fields=available_fields,
            missing_fields=missing_fields,
            missing_confirmation_items=missing_confirmation_items,
            business_period_reference=effective_business_period_reference,
            blocked_reason="mismatched_pathology_code",
            owner_confirmation_required=True,
            next_owner_questions=(),
            metadata=metadata,
        )

    if missing_fields:
        return _build_result(
            entrypoint=entrypoint,
            allowed_candidate=allowed_candidate,
            status=STATUS_NEEDS_EVIDENCE,
            available_fields=available_fields,
            missing_fields=missing_fields,
            missing_confirmation_items=missing_confirmation_items,
            business_period_reference=effective_business_period_reference,
            blocked_reason="missing_required_fields",
            owner_confirmation_required=False,
            next_owner_questions=_next_owner_questions(
                missing_fields=missing_fields,
                missing_confirmation_items=(),
                pathology_code=entrypoint.selected_primary_pathology,
            ),
            metadata=metadata,
        )

    if missing_confirmation_items:
        return _build_result(
            entrypoint=entrypoint,
            allowed_candidate=allowed_candidate,
            status=STATUS_NEEDS_OWNER_CONFIRMATION,
            available_fields=available_fields,
            missing_fields=missing_fields,
            missing_confirmation_items=missing_confirmation_items,
            business_period_reference=effective_business_period_reference,
            blocked_reason="missing_owner_confirmations",
            owner_confirmation_required=True,
            next_owner_questions=_next_owner_questions(
                missing_fields=(),
                missing_confirmation_items=missing_confirmation_items,
                pathology_code=entrypoint.selected_primary_pathology,
            ),
            metadata=metadata,
        )

    return _build_result(
        entrypoint=entrypoint,
        allowed_candidate=allowed_candidate,
        status=STATUS_READY_FOR_COMPUTATION_PLAN,
        available_fields=available_fields,
        missing_fields=missing_fields,
        missing_confirmation_items=missing_confirmation_items,
        business_period_reference=effective_business_period_reference,
        blocked_reason=None,
        owner_confirmation_required=False,
        next_owner_questions=(),
        metadata=metadata,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_READY_FOR_COMPUTATION_PLAN",
    "STATUS_NEEDS_OWNER_CONFIRMATION",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY",
    "STATUS_BLOCKED_MISMATCHED_PATHOLOGY",
    "ALLOWED_STATUSES",
    "Service1PathologyEvidenceReadinessGateV1",
    "build_service_1_pathology_evidence_readiness_gate_v1",
]
