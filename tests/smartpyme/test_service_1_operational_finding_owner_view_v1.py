from __future__ import annotations

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    Service1ControlledComputationPlanV1,
    build_service_1_controlled_computation_plan_v1,
)
from pymia.smartpyme.service_1_operational_finding_owner_view_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_DRY_RUN_NOT_BUILT,
    STATUS_BLOCKED_EMPTY_FINDING,
    STATUS_OWNER_VIEW_BUILT,
    build_service_1_operational_finding_owner_view_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_first_aid_dry_run_candidate_v1 import (
    Service1PathologyFirstAidDryRunCandidateV1,
    build_service_1_pathology_first_aid_dry_run_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def _entrypoint_kwargs() -> dict[str, str]:
    return {
        "case_id": "case:s1:owner_view:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _build_plan(pathology_code: str, narrative: str, available_fields: list[str], confirmations: list[str]) -> Service1ControlledComputationPlanV1:
    entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        **_entrypoint_kwargs(),
        raw_owner_narrative=narrative,
        business_period_reference="2026-06",
        declared_data_sources=["input.xlsx"],
        column_meaning_confirmations=confirmations,
        available_data_fields=available_fields,
    )
    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=pathology_code,
        available_data_fields=available_fields,
        missing_evidence_items=[],
        business_period_reference="2026-06",
    )
    readiness_gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=available_fields,
        column_meaning_confirmations=confirmations,
        business_period_reference="2026-06",
    )
    return build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
    )


def _ren_dry_run() -> Service1PathologyFirstAidDryRunCandidateV1:
    plan = _build_plan(
        "REN_001",
        "No veo el margen porque tengo precio, costo y ganancia por cantidad.",
        ["precio", "costo", "cantidad"],
        ["precio=precio de venta", "costo=costo unitario", "cantidad=cantidad vendida"],
    )
    return build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"precio": 100, "costo": 60, "cantidad": 3},
    )


def _liq_dry_run() -> Service1PathologyFirstAidDryRunCandidateV1:
    plan = _build_plan(
        "LIQ_001",
        "Tengo ventas pero los cobros no entran en caja.",
        ["ventas", "cobros", "saldo"],
        ["ventas=importe vendido", "cobros=importe cobrado", "saldo=saldo pendiente"],
    )
    return build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"ventas": 200, "cobros": 150},
    )


def _stk_dry_run() -> Service1PathologyFirstAidDryRunCandidateV1:
    plan = _build_plan(
        "STK_001",
        "Tengo problemas de stock e inventario.",
        ["producto", "stock", "movimientos"],
        ["producto=producto", "stock=stock actual", "movimientos=movimientos de stock"],
    )
    return build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"stock_actual": 8, "stock_minimo": 10},
    )


def test_builds_owner_view_for_ren() -> None:
    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=_ren_dry_run(),
    )

    assert view.schema_version == SCHEMA_VERSION
    assert view.service_name == SERVICE_NAME
    assert view.status == STATUS_OWNER_VIEW_BUILT
    assert "margen" in (view.title or "").lower()
    assert "rentabilidad global" in " ".join(view.limits).lower()


def test_builds_owner_view_for_liq() -> None:
    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=_liq_dry_run(),
    )

    assert view.status == STATUS_OWNER_VIEW_BUILT
    assert "ventas" in (view.finding_summary or "").lower()
    assert "cobros" in (view.finding_summary or "").lower()
    assert "caja definitivo" in " ".join(view.limits).lower()


def test_builds_owner_view_for_stk() -> None:
    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=_stk_dry_run(),
    )

    assert view.status == STATUS_OWNER_VIEW_BUILT
    assert "stock mínimo" in (view.title or "").lower()
    assert "inventario real definitivo" in " ".join(view.limits).lower()


def test_blocks_when_dry_run_is_not_built() -> None:
    built = _ren_dry_run()
    blocked = Service1PathologyFirstAidDryRunCandidateV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status="BLOCKED_PLAN_NOT_READY",
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        computation_plan_id=built.computation_plan_id,
        execution_mode=built.execution_mode,
        input_values=built.input_values,
        computed_values={},
        finding_summary=None,
        blocked_reason="computation_plan_not_ready_for_dry_run_candidate",
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=blocked,
    )

    assert view.status == STATUS_BLOCKED_DRY_RUN_NOT_BUILT
    assert view.blocked_reason == "dry_run_candidate_not_built"


def test_blocks_when_finding_is_empty() -> None:
    built = _ren_dry_run()
    empty = Service1PathologyFirstAidDryRunCandidateV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status=built.status,
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        computation_plan_id=built.computation_plan_id,
        execution_mode=built.execution_mode,
        input_values=built.input_values,
        computed_values={},
        finding_summary="",
        blocked_reason=None,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=empty,
    )

    assert view.status == STATUS_BLOCKED_EMPTY_FINDING
    assert view.blocked_reason == "empty_finding_summary_and_computed_values"


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=_liq_dry_run(),
    )

    assert view.runtime_authorized is False
    assert view.reexecution_authorized is False
    assert view.recalculation_authorized is False
    assert view.delivery_authorized is False


def test_primary_dict_does_not_expose_human_review_fields() -> None:
    view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=_stk_dry_run(),
    )
    data = view.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
