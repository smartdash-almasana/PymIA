from __future__ import annotations

from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    PATHOLOGY_CSH_001,
    PATHOLOGY_LIQ_001,
    PATHOLOGY_REN_001,
    PATHOLOGY_STK_001,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
    STATUS_NEEDS_EVIDENCE,
    STATUS_READY_FOR_COMPUTATION_PLAN,
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def test_maps_ren_001_to_precio_margen_candidate() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_REN_001,
        available_data_fields=["precio", "costo", "cantidad"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.schema_version == SCHEMA_VERSION
    assert candidate.service_name == SERVICE_NAME
    assert candidate.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert candidate.status == STATUS_READY_FOR_COMPUTATION_PLAN


def test_maps_liq_001_to_caja_diaria_triage_candidate() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_LIQ_001,
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.allowed_computation_ref == "first_aid_caja_diaria_triage_v1"
    assert candidate.required_fields == ("ventas_periodo", "cobranzas_periodo", "saldo_pendiente")


def test_maps_stk_001_to_stock_alertas_candidate() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_STK_001,
        available_data_fields=["producto", "stock", "movimientos"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.allowed_computation_ref == "first_aid_stock_alertas_basicas_v1"
    assert candidate.status == STATUS_READY_FOR_COMPUTATION_PLAN


def test_maps_csh_001_to_caja_diaria_triage_candidate() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_CSH_001,
        available_data_fields=["fecha", "monto", "entrada_salida"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.allowed_computation_ref == "first_aid_caja_diaria_triage_v1"
    assert candidate.status == STATUS_READY_FOR_COMPUTATION_PLAN


def test_returns_needs_evidence_when_required_fields_are_missing() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_REN_001,
        available_data_fields=["precio", "costo"],
        missing_evidence_items=["volumen_vendido"],
        business_period_reference="2026-06",
    )

    assert candidate.status == STATUS_NEEDS_EVIDENCE
    assert "volumen_vendido" in candidate.missing_fields
    assert candidate.blocked_reason == "missing_required_fields"


def test_returns_blocked_for_unsupported_pathology() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="SAL_001",
        available_data_fields=["ventas", "producto"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.status == STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY
    assert candidate.allowed_computation_ref is None
    assert candidate.blocked_reason == "unsupported_pathology_code"


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_LIQ_001,
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    assert candidate.runtime_authorized is False
    assert candidate.reexecution_authorized is False
    assert candidate.recalculation_authorized is False
    assert candidate.delivery_authorized is False


def test_primary_dict_does_not_expose_human_review_fields() -> None:
    candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=PATHOLOGY_CSH_001,
        available_data_fields=["fecha", "monto", "entrada_salida"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )
    data = candidate.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
