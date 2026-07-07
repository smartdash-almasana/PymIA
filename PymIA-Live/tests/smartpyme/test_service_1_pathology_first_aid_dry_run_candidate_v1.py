from __future__ import annotations

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    Service1ControlledComputationPlanV1,
    build_service_1_controlled_computation_plan_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_first_aid_dry_run_candidate_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_MISSING_INPUT_VALUES,
    STATUS_BLOCKED_PLAN_NOT_READY,
    STATUS_BLOCKED_UNSUPPORTED_COMPUTATION,
    STATUS_DRY_RUN_CANDIDATE_BUILT,
    build_service_1_pathology_first_aid_dry_run_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def _entrypoint_kwargs() -> dict[str, str]:
    return {
        "case_id": "case:s1:dryrun:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _ready_plan_ren() -> Service1ControlledComputationPlanV1:
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
    readiness_gate = build_service_1_pathology_evidence_readiness_gate_v1(
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
    return build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
    )


def _ready_plan_liq() -> Service1ControlledComputationPlanV1:
    entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="LIQ_001",
        available_data_fields=["ventas", "cobros", "saldo"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )
    readiness_gate = build_service_1_pathology_evidence_readiness_gate_v1(
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
    return build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
    )


def _ready_plan_stk() -> Service1ControlledComputationPlanV1:
    entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative="Tengo problemas de stock e inventario.",
        business_period_reference="2026-06",
        declared_data_sources=["stock.xlsx"],
        column_meaning_confirmations=["stock=stock actual", "producto=producto"],
        available_data_fields=["producto", "stock", "movimientos"],
    )
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code="STK_001",
        available_data_fields=["producto", "stock", "movimientos"],
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )
    readiness_gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=["producto", "stock", "movimientos"],
        column_meaning_confirmations=[
            "producto=producto",
            "stock=stock actual",
            "movimientos=movimientos de stock",
        ],
        business_period_reference="2026-06",
    )
    return build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
    )


def test_builds_margin_dry_run_candidate() -> None:
    plan = _ready_plan_ren()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"precio": 100, "costo": 60, "cantidad": 3},
    )

    assert result.schema_version == SCHEMA_VERSION
    assert result.service_name == SERVICE_NAME
    assert result.status == STATUS_DRY_RUN_CANDIDATE_BUILT
    assert result.computed_values["unit_margin"] == 40
    assert result.computed_values["total_margin"] == 120
    assert result.computed_values["margin_rate"] == 0.4


def test_builds_liquidity_dry_run_candidate() -> None:
    plan = _ready_plan_liq()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"ventas": 200, "cobros": 150},
    )

    assert result.status == STATUS_DRY_RUN_CANDIDATE_BUILT
    assert result.computed_values["collection_gap"] == 50
    assert result.computed_values["collection_rate"] == 0.75


def test_builds_stock_dry_run_candidate() -> None:
    plan = _ready_plan_stk()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"stock_actual": 8, "stock_minimo": 10},
    )

    assert result.status == STATUS_DRY_RUN_CANDIDATE_BUILT
    assert result.computed_values["stock_gap"] == -2
    assert result.computed_values["below_minimum"] is True


def test_blocks_when_plan_is_not_ready() -> None:
    ready_plan = _ready_plan_ren()
    blocked_plan = Service1ControlledComputationPlanV1(
        schema_version=ready_plan.schema_version,
        service_name=ready_plan.service_name,
        status="BLOCKED_READINESS_NOT_READY",
        case_id=ready_plan.case_id,
        tenant_id=ready_plan.tenant_id,
        intake_id=ready_plan.intake_id,
        run_id=ready_plan.run_id,
        pathology_code=ready_plan.pathology_code,
        allowed_computation_ref=ready_plan.allowed_computation_ref,
        computation_plan_id=None,
        execution_mode=ready_plan.execution_mode,
        required_fields=ready_plan.required_fields,
        available_fields=ready_plan.available_fields,
        field_bindings={},
        blocked_reason="readiness_gate_not_ready_for_computation_plan",
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=blocked_plan,
        input_values={"precio": 100, "costo": 60, "cantidad": 3},
    )

    assert result.status == STATUS_BLOCKED_PLAN_NOT_READY
    assert result.blocked_reason == "computation_plan_not_ready_for_dry_run_candidate"


def test_blocks_when_computation_is_unsupported() -> None:
    ready_plan = _ready_plan_ren()
    unsupported_plan = Service1ControlledComputationPlanV1(
        schema_version=ready_plan.schema_version,
        service_name=ready_plan.service_name,
        status=ready_plan.status,
        case_id=ready_plan.case_id,
        tenant_id=ready_plan.tenant_id,
        intake_id=ready_plan.intake_id,
        run_id=ready_plan.run_id,
        pathology_code=ready_plan.pathology_code,
        allowed_computation_ref="first_aid_no_soportado_v1",
        computation_plan_id=ready_plan.computation_plan_id,
        execution_mode=ready_plan.execution_mode,
        required_fields=ready_plan.required_fields,
        available_fields=ready_plan.available_fields,
        field_bindings=ready_plan.field_bindings,
        blocked_reason=None,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=unsupported_plan,
        input_values={"precio": 100, "costo": 60, "cantidad": 3},
    )

    assert result.status == STATUS_BLOCKED_UNSUPPORTED_COMPUTATION
    assert result.blocked_reason == "unsupported_allowed_computation_ref"


def test_blocks_when_input_values_are_missing() -> None:
    plan = _ready_plan_ren()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"precio": 100, "costo": 60},
    )

    assert result.status == STATUS_BLOCKED_MISSING_INPUT_VALUES
    assert result.blocked_reason == "missing_input_values"
    assert result.metadata["missing_input_fields"] == ("volumen_vendido",)


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    plan = _ready_plan_liq()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"ventas": 200, "cobros": 150},
    )

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False


def test_primary_dict_does_not_expose_human_review_fields() -> None:
    plan = _ready_plan_stk()
    result = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"stock_actual": 8, "stock_minimo": 10},
    )
    data = result.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
