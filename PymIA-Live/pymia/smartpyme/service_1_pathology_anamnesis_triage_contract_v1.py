from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final, Literal

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_CONTRACT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"
CONFIDENCE_MODE_RULE_BASED_CANDIDATE_ONLY: Final[str] = "RULE_BASED_CANDIDATE_ONLY"

STATUS_OWNER_NARRATIVE_CAPTURED: Final[str] = "OWNER_NARRATIVE_CAPTURED"
STATUS_ANAMNESIS_PARTIAL: Final[str] = "ANAMNESIS_PARTIAL"
STATUS_PATHOLOGY_CANDIDATES_IDENTIFIED: Final[str] = "PATHOLOGY_CANDIDATES_IDENTIFIED"
STATUS_EVIDENCE_REQUIRED: Final[str] = "EVIDENCE_REQUIRED"
STATUS_OWNER_CONFIRMATION_REQUIRED: Final[str] = "OWNER_CONFIRMATION_REQUIRED"
STATUS_READY_FOR_DETERMINISTIC_COMPUTATION: Final[str] = "READY_FOR_DETERMINISTIC_COMPUTATION"
STATUS_EVIDENCE_INSUFFICIENT: Final[str] = "EVIDENCE_INSUFFICIENT"
STATUS_ASSISTED_FINDING_AVAILABLE: Final[str] = "ASSISTED_FINDING_AVAILABLE"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_OWNER_NARRATIVE_CAPTURED,
    STATUS_ANAMNESIS_PARTIAL,
    STATUS_PATHOLOGY_CANDIDATES_IDENTIFIED,
    STATUS_EVIDENCE_REQUIRED,
    STATUS_OWNER_CONFIRMATION_REQUIRED,
    STATUS_READY_FOR_DETERMINISTIC_COMPUTATION,
    STATUS_EVIDENCE_INSUFFICIENT,
    STATUS_ASSISTED_FINDING_AVAILABLE,
)

PATHOLOGY_LIQ_001: Final[str] = "LIQ_001"
PATHOLOGY_REN_001: Final[str] = "REN_001"
PATHOLOGY_STK_001: Final[str] = "STK_001"
PATHOLOGY_CST_001: Final[str] = "CST_001"
PATHOLOGY_SAL_001: Final[str] = "SAL_001"
PATHOLOGY_CSH_001: Final[str] = "CSH_001"

ALLOWED_PATHOLOGY_CODES: Final[tuple[str, ...]] = (
    PATHOLOGY_LIQ_001,
    PATHOLOGY_REN_001,
    PATHOLOGY_STK_001,
    PATHOLOGY_CST_001,
    PATHOLOGY_SAL_001,
    PATHOLOGY_CSH_001,
)

AnamnesisStatusV1 = Literal[
    "OWNER_NARRATIVE_CAPTURED",
    "ANAMNESIS_PARTIAL",
    "PATHOLOGY_CANDIDATES_IDENTIFIED",
    "EVIDENCE_REQUIRED",
    "OWNER_CONFIRMATION_REQUIRED",
    "READY_FOR_DETERMINISTIC_COMPUTATION",
    "EVIDENCE_INSUFFICIENT",
    "ASSISTED_FINDING_AVAILABLE",
]

_PATHOLOGY_DEFINITIONS: Final[dict[str, dict[str, Any]]] = {
    PATHOLOGY_LIQ_001: {
        "label": "Descalce ventas-cobranzas",
        "trigger_groups": (
            ("venta", "ventas", "vendi", "vendiendo"),
            ("cobro", "cobros", "cobranza", "cobranzas", "caja", "plata", "cobrado"),
        ),
        "minimum_trigger_groups": 2,
        "required_evidence": ("ventas_periodo", "cobranzas_periodo", "saldo_pendiente"),
        "owner_questions": (
            "¿De qué período querés revisar ventas y cobranzas?",
            "¿Qué columnas representan ventas, cobros o saldo pendiente?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
    PATHOLOGY_REN_001: {
        "label": "Margen invisible",
        "trigger_groups": (
            ("margen", "rentabilidad", "ganancia", "gano", "ganar"),
            ("costo", "costos", "precio", "precios"),
        ),
        "minimum_trigger_groups": 2,
        "required_evidence": ("precio_venta", "costo_unitario", "volumen_vendido"),
        "owner_questions": (
            "¿De qué período querés entender margen o rentabilidad?",
            "¿Qué columnas representan precio de venta y costo unitario?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
    PATHOLOGY_STK_001: {
        "label": "Stock incierto",
        "trigger_groups": (("stock", "inventario", "existencias"),),
        "minimum_trigger_groups": 1,
        "required_evidence": ("producto", "stock_actual", "movimientos_stock"),
        "owner_questions": (
            "¿Qué archivo usás para seguir stock o inventario?",
            "¿Qué columnas representan producto, entradas y salidas?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
    PATHOLOGY_CST_001: {
        "label": "Costeo incompleto",
        "trigger_groups": (("costo", "costos", "costeo"),),
        "minimum_trigger_groups": 1,
        "required_evidence": ("costo_base", "gastos_asociados"),
        "owner_questions": (
            "¿Qué costos ya tenés en el archivo y cuáles quedan afuera?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
    PATHOLOGY_SAL_001: {
        "label": "Mezcla de ventas sin segmentación",
        "trigger_groups": (
            ("ventas", "vendo", "vendemos"),
            ("producto", "canal", "categoria", "categoría", "segmento"),
        ),
        "minimum_trigger_groups": 1,
        "required_evidence": ("fecha", "producto_servicio", "importe"),
        "owner_questions": (
            "¿Qué columnas separan producto, canal o categoría?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
    PATHOLOGY_CSH_001: {
        "label": "Caja desordenada por período",
        "trigger_groups": (
            ("caja", "efectivo", "plata"),
            ("fecha", "periodo", "período", "dia", "día"),
        ),
        "minimum_trigger_groups": 1,
        "required_evidence": ("fecha", "monto", "entrada_salida"),
        "owner_questions": (
            "¿Qué período querés revisar en caja?",
            "¿Qué columnas distinguen entrada y salida?",
        ),
        "allowed_microservices": ("normalized_table_v1",),
    },
}

_FIELD_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "ventas_periodo": ("ventas_periodo", "ventas", "venta_total", "total_ventas", "importe_venta"),
    "cobranzas_periodo": ("cobranzas_periodo", "cobranzas", "cobros", "total_cobrado", "importe_cobrado"),
    "saldo_pendiente": ("saldo_pendiente", "cuentas_por_cobrar", "saldo", "saldo_cobrar"),
    "precio_venta": ("precio_venta", "precio", "precio_unitario", "precio_de_venta"),
    "costo_unitario": ("costo_unitario", "costo", "costo_base", "precio_compra"),
    "volumen_vendido": ("volumen_vendido", "cantidad", "cantidad_vendida", "unidades_vendidas"),
    "producto": ("producto", "sku", "articulo", "item"),
    "stock_actual": ("stock_actual", "stock", "inventario_actual"),
    "movimientos_stock": ("movimientos_stock", "entradas_salidas", "movimientos"),
    "costo_base": ("costo_base", "costo", "precio_compra"),
    "gastos_asociados": ("gastos_asociados", "gastos_variables", "comisiones", "logistica"),
    "fecha": ("fecha", "periodo", "periodo_ref", "fecha_movimiento"),
    "producto_servicio": ("producto_servicio", "producto", "servicio", "categoria_producto"),
    "importe": ("importe", "monto", "total", "importe_total"),
    "monto": ("monto", "importe", "valor"),
    "entrada_salida": ("entrada_salida", "tipo_movimiento", "debe_haber", "ingreso_egreso"),
}


@dataclass(frozen=True)
class Service1AnamnesisRecordV1:
    schema_version: str
    service_name: str
    case_id: str
    owner_ref: str
    tenant_ref: str
    raw_owner_narrative: str
    declared_primary_pain: str | None
    business_period_reference: str | None
    declared_data_sources: tuple[str, ...]
    column_meaning_confirmations: tuple[str, ...]
    owner_constraints: tuple[str, ...]
    signals_detected: tuple[str, ...]
    candidate_pathology_codes: tuple[str, ...]
    owner_confirmation_required: bool
    missing_evidence_items: tuple[str, ...]
    delivery_policy_constraints: tuple[str, ...]
    status: AnamnesisStatusV1
    runtime_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1PathologyCandidateV1:
    pathology_code: str
    pathology_label: str
    confidence_mode: str
    trigger_signals: tuple[str, ...]
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    allowed_microservices: tuple[str, ...]
    diagnostic_scope_limit: str
    owner_confirmation_required: bool
    delivery_policy_constraints: tuple[str, ...]
    status: AnamnesisStatusV1
    runtime_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1AnamnesisTriageDecisionV1:
    case_id: str
    selected_primary_pathology: str | None
    alternative_pathologies: tuple[str, ...]
    why_selected: str | None
    why_not_ready: str | None
    next_owner_questions: tuple[str, ...]
    next_allowed_computation: tuple[str, ...]
    delivery_policy_constraints: tuple[str, ...]
    status: AnamnesisStatusV1
    owner_confirmation_required: bool
    runtime_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
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


def _detect_signals(raw_owner_narrative: str) -> tuple[str, ...]:
    normalized = _normalize_text(raw_owner_narrative)
    signals: list[str] = []
    for token in (
        "ventas",
        "venta",
        "cobros",
        "cobro",
        "caja",
        "plata",
        "margen",
        "rentabilidad",
        "ganancia",
        "costo",
        "precio",
        "stock",
        "inventario",
        "canal",
        "categoria",
        "fecha",
        "periodo",
    ):
        if token in normalized:
            signals.append(token)
    return tuple(dict.fromkeys(signals))


def _candidate_score(normalized_narrative: str, pathology_code: str) -> int:
    definition = _PATHOLOGY_DEFINITIONS[pathology_code]
    score = 0
    for trigger_group in definition["trigger_groups"]:
        if any(term in normalized_narrative for term in trigger_group):
            score += 1
    return score


def _is_pathology_candidate(normalized_narrative: str, pathology_code: str) -> bool:
    definition = _PATHOLOGY_DEFINITIONS[pathology_code]
    score = _candidate_score(normalized_narrative, pathology_code)
    minimum_trigger_groups = int(definition.get("minimum_trigger_groups", 1))
    return score >= minimum_trigger_groups


def _detect_pathology_codes(raw_owner_narrative: str) -> tuple[str, ...]:
    normalized = _normalize_text(raw_owner_narrative)
    candidates = [
        code
        for code in ALLOWED_PATHOLOGY_CODES
        if _is_pathology_candidate(normalized, code)
    ]
    return tuple(candidates)


def _normalize_fields(available_data_fields: Any) -> set[str]:
    fields = {_normalize_text(item) for item in _clean_list(available_data_fields)}
    return {field for field in fields if field}


def _resolve_missing_evidence(pathology_code: str, available_data_fields: Any) -> tuple[str, ...]:
    available = _normalize_fields(available_data_fields)
    missing: list[str] = []
    for field_name in _PATHOLOGY_DEFINITIONS[pathology_code]["required_evidence"]:
        aliases = _FIELD_ALIASES.get(field_name, (field_name,))
        if not any(_normalize_text(alias) in available for alias in aliases):
            missing.append(field_name)
    return tuple(missing)


def _owner_confirmation_missing(
    *,
    business_period_reference: str | None,
    declared_data_sources: tuple[str, ...],
    column_meaning_confirmations: tuple[str, ...],
) -> bool:
    if business_period_reference is None:
        return True
    if not declared_data_sources:
        return True
    if not column_meaning_confirmations:
        return True
    return False


def create_service_1_anamnesis_record_v1(
    *,
    case_id: str,
    owner_ref: str,
    tenant_ref: str,
    raw_owner_narrative: str,
    declared_primary_pain: str | None = None,
    business_period_reference: str | None = None,
    declared_data_sources: list[str] | tuple[str, ...] | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    owner_constraints: list[str] | tuple[str, ...] | None = None,
    delivery_policy_constraints: list[str] | tuple[str, ...] | None = None,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1AnamnesisRecordV1:
    case_id = _required_text(case_id, field_name="case_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    tenant_ref = _required_text(tenant_ref, field_name="tenant_ref")
    raw_owner_narrative = _required_text(raw_owner_narrative, field_name="raw_owner_narrative")

    declared_data_sources_tuple = _clean_list(declared_data_sources)
    column_meaning_confirmations_tuple = _clean_list(column_meaning_confirmations)
    owner_constraints_tuple = _clean_list(owner_constraints)
    delivery_policy_constraints_tuple = _clean_list(delivery_policy_constraints)
    candidate_pathology_codes = _detect_pathology_codes(raw_owner_narrative)
    signals_detected = _detect_signals(raw_owner_narrative)

    if candidate_pathology_codes:
        primary_candidate = candidate_pathology_codes[0]
        missing_evidence_items = _resolve_missing_evidence(primary_candidate, available_data_fields)
    else:
        missing_evidence_items = ()

    owner_confirmation_required = _owner_confirmation_missing(
        business_period_reference=_clean_optional_text(business_period_reference),
        declared_data_sources=declared_data_sources_tuple,
        column_meaning_confirmations=column_meaning_confirmations_tuple,
    )

    if owner_confirmation_required:
        status = STATUS_OWNER_CONFIRMATION_REQUIRED
    elif candidate_pathology_codes and missing_evidence_items:
        status = STATUS_EVIDENCE_REQUIRED
    elif candidate_pathology_codes:
        status = STATUS_PATHOLOGY_CANDIDATES_IDENTIFIED
    else:
        status = STATUS_OWNER_NARRATIVE_CAPTURED

    return Service1AnamnesisRecordV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=case_id,
        owner_ref=owner_ref,
        tenant_ref=tenant_ref,
        raw_owner_narrative=raw_owner_narrative,
        declared_primary_pain=_clean_optional_text(declared_primary_pain),
        business_period_reference=_clean_optional_text(business_period_reference),
        declared_data_sources=declared_data_sources_tuple,
        column_meaning_confirmations=column_meaning_confirmations_tuple,
        owner_constraints=owner_constraints_tuple,
        signals_detected=signals_detected,
        candidate_pathology_codes=candidate_pathology_codes,
        owner_confirmation_required=owner_confirmation_required,
        missing_evidence_items=missing_evidence_items,
        delivery_policy_constraints=delivery_policy_constraints_tuple,
        status=status,
        runtime_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def detect_service_1_pathology_candidates_v1(
    anamnesis_record: Service1AnamnesisRecordV1,
    *,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
) -> tuple[Service1PathologyCandidateV1, ...]:
    if not isinstance(anamnesis_record, Service1AnamnesisRecordV1):
        raise ValueError("anamnesis_record must be a Service1AnamnesisRecordV1")

    candidates: list[Service1PathologyCandidateV1] = []
    for pathology_code in anamnesis_record.candidate_pathology_codes:
        definition = _PATHOLOGY_DEFINITIONS[pathology_code]
        missing_evidence = _resolve_missing_evidence(pathology_code, available_data_fields)
        if anamnesis_record.owner_confirmation_required:
            status = STATUS_OWNER_CONFIRMATION_REQUIRED
        elif missing_evidence:
            status = STATUS_EVIDENCE_REQUIRED
        else:
            status = STATUS_READY_FOR_DETERMINISTIC_COMPUTATION
        candidates.append(
            Service1PathologyCandidateV1(
                pathology_code=pathology_code,
                pathology_label=definition["label"],
                confidence_mode=CONFIDENCE_MODE_RULE_BASED_CANDIDATE_ONLY,
                trigger_signals=anamnesis_record.signals_detected,
                required_evidence=tuple(definition["required_evidence"]),
                missing_evidence=missing_evidence,
                allowed_microservices=tuple(definition["allowed_microservices"]),
                diagnostic_scope_limit="No diagnosis is authorized by this contract; only triage readiness is expressed.",
                owner_confirmation_required=anamnesis_record.owner_confirmation_required,
                delivery_policy_constraints=anamnesis_record.delivery_policy_constraints,
                status=status,
                runtime_authorized=False,
                metadata={"case_id": anamnesis_record.case_id},
            )
        )
    return tuple(candidates)


def build_service_1_anamnesis_triage_decision_v1(
    anamnesis_record: Service1AnamnesisRecordV1,
    *,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
) -> Service1AnamnesisTriageDecisionV1:
    if not isinstance(anamnesis_record, Service1AnamnesisRecordV1):
        raise ValueError("anamnesis_record must be a Service1AnamnesisRecordV1")

    candidates = detect_service_1_pathology_candidates_v1(
        anamnesis_record,
        available_data_fields=available_data_fields,
    )
    if not candidates:
        return Service1AnamnesisTriageDecisionV1(
            case_id=anamnesis_record.case_id,
            selected_primary_pathology=None,
            alternative_pathologies=(),
            why_selected=None,
            why_not_ready="No pathology candidate can be proposed safely from the owner narrative alone.",
            next_owner_questions=("¿Qué problema operativo querés entender primero?",),
            next_allowed_computation=(),
            delivery_policy_constraints=anamnesis_record.delivery_policy_constraints,
            status=STATUS_ANAMNESIS_PARTIAL,
            owner_confirmation_required=True,
            runtime_authorized=False,
            created_at=_now_iso(),
            metadata={"candidate_count": 0},
        )

    primary_candidate = candidates[0]
    alternative_pathologies = tuple(candidate.pathology_code for candidate in candidates[1:])

    if primary_candidate.status == STATUS_OWNER_CONFIRMATION_REQUIRED:
        status = STATUS_OWNER_CONFIRMATION_REQUIRED
        why_not_ready = "Owner confirmation is still required for period, column meaning, or business context."
        next_allowed_computation: tuple[str, ...] = ()
    elif primary_candidate.status == STATUS_EVIDENCE_REQUIRED:
        status = STATUS_EVIDENCE_REQUIRED
        why_not_ready = "Minimum evidence is still missing for the selected pathology candidate."
        next_allowed_computation = ()
    else:
        status = STATUS_READY_FOR_DETERMINISTIC_COMPUTATION
        why_not_ready = None
        next_allowed_computation = primary_candidate.allowed_microservices

    next_owner_questions = ()
    if status != STATUS_READY_FOR_DETERMINISTIC_COMPUTATION:
        next_owner_questions = _PATHOLOGY_DEFINITIONS[primary_candidate.pathology_code]["owner_questions"]

    return Service1AnamnesisTriageDecisionV1(
        case_id=anamnesis_record.case_id,
        selected_primary_pathology=primary_candidate.pathology_code,
        alternative_pathologies=alternative_pathologies,
        why_selected=f"Selected by rule-based signal match for {primary_candidate.pathology_label}.",
        why_not_ready=why_not_ready,
        next_owner_questions=tuple(next_owner_questions),
        next_allowed_computation=next_allowed_computation,
        delivery_policy_constraints=anamnesis_record.delivery_policy_constraints,
        status=status,
        owner_confirmation_required=(status == STATUS_OWNER_CONFIRMATION_REQUIRED),
        runtime_authorized=False,
        created_at=_now_iso(),
        metadata={"candidate_count": len(candidates)},
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "CONFIDENCE_MODE_RULE_BASED_CANDIDATE_ONLY",
    "STATUS_OWNER_NARRATIVE_CAPTURED",
    "STATUS_ANAMNESIS_PARTIAL",
    "STATUS_PATHOLOGY_CANDIDATES_IDENTIFIED",
    "STATUS_EVIDENCE_REQUIRED",
    "STATUS_OWNER_CONFIRMATION_REQUIRED",
    "STATUS_READY_FOR_DETERMINISTIC_COMPUTATION",
    "STATUS_EVIDENCE_INSUFFICIENT",
    "STATUS_ASSISTED_FINDING_AVAILABLE",
    "ALLOWED_STATUSES",
    "PATHOLOGY_LIQ_001",
    "PATHOLOGY_REN_001",
    "PATHOLOGY_STK_001",
    "PATHOLOGY_CST_001",
    "PATHOLOGY_SAL_001",
    "PATHOLOGY_CSH_001",
    "ALLOWED_PATHOLOGY_CODES",
    "Service1AnamnesisRecordV1",
    "Service1PathologyCandidateV1",
    "Service1AnamnesisTriageDecisionV1",
    "create_service_1_anamnesis_record_v1",
    "detect_service_1_pathology_candidates_v1",
    "build_service_1_anamnesis_triage_decision_v1",
]
