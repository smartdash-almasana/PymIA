from __future__ import annotations

from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_MISMATCHED_PATHOLOGY,
    STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY,
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY_FOR_COMPUTATION_PLAN,
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def _entrypoint_kwargs() -> dict[str, str]:
    return {
        "case_id": "case:s1:readiness:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _ren_entrypoint():
    return build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )


def _liq_entrypoint():
    return build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )


def test_gate_returns_ready_for_computation_plan_when_everything_is_present() -> None:
    entrypoint = _ren_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="REN_001",
        available_data_fields=["precio", "costo", "cantidad"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["precio", "costo", "cantidad"],
        column_meaning_confirmations=[
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=cantidad vendida",
        ],
        business_period_reference="2026-06",
    )

    assert gate.schema_version == SCHEMA_VERSION
    assert gate.service_name == SERVICE_NAME
    assert gate.status == STATUS_READY_FOR_COMPUTATION_PLAN
    assert gate.blocked_reason is None
    assert gate.owner_confirmation_required is False


def test_gate_returns_blocked_unsupported_pathology_when_allowed_candidate_is_blocked() -> None:
    entrypoint = _ren_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="SAL_001",
        available_data_fields=["ventas", "producto"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "producto"],
        column_meaning_confirmations=["ventas=importe vendido"],
        business_period_reference="2026-06",
    )

    assert gate.status == STATUS_BLOCKED_UNSUPPORTED_PATHOLOGY
    assert gate.blocked_reason == "unsupported_pathology_code"


def test_gate_returns_blocked_mismatched_pathology_when_codes_do_not_match() -> None:
    entrypoint = _ren_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "cobros", "saldo"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        business_period_reference="2026-06",
    )

    assert gate.status == STATUS_BLOCKED_MISMATCHED_PATHOLOGY
    assert gate.blocked_reason == "mismatched_pathology_code"


def test_gate_returns_needs_evidence_when_required_fields_are_missing() -> None:
    entrypoint = _liq_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros"],
        missing_evidence_items=["saldo_pendiente"],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "cobros"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        business_period_reference="2026-06",
    )

    assert gate.status == STATUS_NEEDS_EVIDENCE
    assert "saldo_pendiente" in gate.missing_fields
    assert gate.owner_confirmation_required is False
    assert gate.next_owner_questions


def test_gate_returns_needs_owner_confirmation_when_column_meanings_are_missing() -> None:
    entrypoint = _ren_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="REN_001",
        available_data_fields=["precio", "costo", "cantidad"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["precio", "costo", "cantidad"],
        column_meaning_confirmations=["precio=precio de venta"],
        business_period_reference="2026-06",
    )

    assert gate.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert "costo_unitario" in gate.missing_confirmation_items
    assert "volumen_vendido" in gate.missing_confirmation_items
    assert gate.owner_confirmation_required is True


def test_gate_returns_needs_owner_confirmation_when_business_period_is_missing() -> None:
    entrypoint = _liq_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference=None,
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "cobros", "saldo"],
        column_meaning_confirmations=[
            "ventas=importe vendido",
            "cobros=importe cobrado",
            "saldo=saldo pendiente",
        ],
        business_period_reference=None,
    )

    assert gate.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert "business_period_reference" in gate.missing_confirmation_items
    assert gate.owner_confirmation_required is True


def test_gate_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    entrypoint = _ren_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="REN_001",
        available_data_fields=["precio", "costo", "cantidad"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["precio", "costo", "cantidad"],
        column_meaning_confirmations=[
            "precio=precio de venta",
            "costo=costo unitario",
            "cantidad=cantidad vendida",
        ],
        business_period_reference="2026-06",
    )

    assert gate.runtime_authorized is False
    assert gate.reexecution_authorized is False
    assert gate.recalculation_authorized is False
    assert gate.delivery_authorized is False


def test_gate_primary_dict_does_not_expose_human_review_fields() -> None:
    entrypoint = _liq_entrypoint()
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )

    gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "cobros", "saldo"],
        column_meaning_confirmations=[
            "ventas=importe vendido",
            "cobros=importe cobrado",
            "saldo=saldo pendiente",
        ],
        business_period_reference="2026-06",
    )
    data = gate.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
