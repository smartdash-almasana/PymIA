from __future__ import annotations

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    EXECUTION_MODE_DRY_RUN_CANDIDATE,
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_READINESS_NOT_READY,
    STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
    STATUS_READY_FOR_DRY_RUN_CANDIDATE,
    build_service_1_controlled_computation_plan_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def _entrypoint_kwargs() -> dict[str, str]:
    return {
        "case_id": "case:s1:plan:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _ready_ren_gate():
    entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="REN_001",
        available_data_fields=["precio", "costo", "cantidad"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )
    return build_service_1_pathology_evidence_readiness_gate_v1(
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


def _not_ready_liq_gate():
    entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros"],
    )
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros"],
        missing_evidence_items=["saldo_pendiente"],
        business_period_reference="2026-06",
    )
    return build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["ventas", "cobros"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        business_period_reference="2026-06",
    )


def test_builds_ready_dry_run_candidate_from_ready_gate() -> None:
    gate = _ready_ren_gate()

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )

    assert plan.schema_version == SCHEMA_VERSION
    assert plan.service_name == SERVICE_NAME
    assert plan.status == STATUS_READY_FOR_DRY_RUN_CANDIDATE
    assert plan.execution_mode == EXECUTION_MODE_DRY_RUN_CANDIDATE
    assert plan.allowed_computation_ref == "first_aid_precio_margen_basico_v1"
    assert plan.computation_plan_id is not None


def test_blocks_when_readiness_gate_is_not_ready() -> None:
    gate = _not_ready_liq_gate()

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )

    assert plan.status == STATUS_BLOCKED_READINESS_NOT_READY
    assert plan.blocked_reason == "readiness_gate_not_ready_for_computation_plan"
    assert plan.computation_plan_id is None


def test_blocks_when_computation_is_not_in_allowlist() -> None:
    gate = _ready_ren_gate()
    gate = type(gate)(
        schema_version=gate.schema_version,
        service_name=gate.service_name,
        status=gate.status,
        case_id=gate.case_id,
        tenant_id=gate.tenant_id,
        intake_id=gate.intake_id,
        run_id=gate.run_id,
        pathology_code=gate.pathology_code,
        allowed_computation_ref="not_allowlisted_v1",
        required_fields=gate.required_fields,
        available_fields=gate.available_fields,
        missing_fields=gate.missing_fields,
        missing_confirmation_items=gate.missing_confirmation_items,
        business_period_reference=gate.business_period_reference,
        next_owner_questions=gate.next_owner_questions,
        blocked_reason=gate.blocked_reason,
        owner_confirmation_required=gate.owner_confirmation_required,
        runtime_authorized=gate.runtime_authorized,
        reexecution_authorized=gate.reexecution_authorized,
        recalculation_authorized=gate.recalculation_authorized,
        delivery_authorized=gate.delivery_authorized,
        metadata=gate.metadata,
    )

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )

    assert plan.status == STATUS_BLOCKED_UNSUPPORTED_COMPUTATION
    assert plan.blocked_reason == "unsupported_allowed_computation_ref"


def test_field_bindings_map_required_fields_to_canonical_names() -> None:
    gate = _ready_ren_gate()

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )

    assert plan.field_bindings == {
        "precio_venta": "precio_venta",
        "costo_unitario": "costo_unitario",
        "volumen_vendido": "volumen_vendido",
    }


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    gate = _ready_ren_gate()

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )

    assert plan.runtime_authorized is False
    assert plan.reexecution_authorized is False
    assert plan.recalculation_authorized is False
    assert plan.delivery_authorized is False


def test_primary_dict_does_not_expose_human_review_fields() -> None:
    gate = _ready_ren_gate()

    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=gate,
    )
    data = plan.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
