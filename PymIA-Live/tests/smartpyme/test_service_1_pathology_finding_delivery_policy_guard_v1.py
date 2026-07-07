from __future__ import annotations

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    build_service_1_controlled_computation_plan_v1,
)
from pymia.smartpyme.service_1_operational_finding_owner_view_v1 import (
    Service1OperationalFindingOwnerViewV1,
    build_service_1_operational_finding_owner_view_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_first_aid_dry_run_candidate_v1 import (
    build_service_1_pathology_first_aid_dry_run_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_finding_delivery_policy_guard_v1 import (
    SCHEMA_VERSION,
    SERVICE_NAME,
    STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_POLICY_BLOCKED,
    STATUS_POLICY_PASS,
    build_service_1_pathology_finding_delivery_policy_guard_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)


def _entrypoint_kwargs() -> dict[str, str]:
    return {
        "case_id": "case:s1:policy:001",
        "tenant_id": "tenant:pyme:001",
        "intake_id": "intake:s1:001",
        "run_id": "run:s1:001",
        "owner_ref": "owner:pyme:001",
    }


def _owner_view_liq() -> Service1OperationalFindingOwnerViewV1:
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
    plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
    )
    dry_run = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=plan,
        input_values={"ventas": 200, "cobros": 150},
    )
    return build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=dry_run,
    )


def test_policy_pass_when_owner_view_is_bounded() -> None:
    owner_view = _owner_view_liq()
    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=owner_view,
    )

    assert guard.schema_version == SCHEMA_VERSION
    assert guard.service_name == SERVICE_NAME
    assert guard.status == STATUS_POLICY_PASS
    assert guard.delivery_allowed_candidate is True
    assert guard.blocked_reason is None


def test_blocked_when_owner_view_is_not_built() -> None:
    built = _owner_view_liq()
    blocked = Service1OperationalFindingOwnerViewV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status="BLOCKED_DRY_RUN_NOT_BUILT",
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        title=None,
        finding_summary=None,
        evidence_used=built.evidence_used,
        computed_values={},
        limits=(),
        next_recommended_action=None,
        blocked_reason="dry_run_candidate_not_built",
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=blocked,
    )

    assert guard.status == STATUS_BLOCKED_OWNER_VIEW_NOT_BUILT
    assert guard.blocked_reason == "owner_view_not_built"
    assert guard.delivery_allowed_candidate is False


def test_policy_blocked_when_limits_are_missing() -> None:
    built = _owner_view_liq()
    no_limits = Service1OperationalFindingOwnerViewV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status=built.status,
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        title=built.title,
        finding_summary=built.finding_summary,
        evidence_used=built.evidence_used,
        computed_values=built.computed_values,
        limits=(),
        next_recommended_action=built.next_recommended_action,
        blocked_reason=None,
        owner_confirmation_required=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=no_limits,
    )

    assert guard.status == STATUS_POLICY_BLOCKED
    assert "missing_explicit_limits" in guard.policy_violations
    assert guard.delivery_allowed_candidate is False


def test_policy_blocked_when_prohibited_claim_is_present() -> None:
    built = _owner_view_liq()
    overclaim = Service1OperationalFindingOwnerViewV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status=built.status,
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        title=built.title,
        finding_summary="Este resultado es un diagnóstico definitivo con certeza absoluta.",
        evidence_used=built.evidence_used,
        computed_values=built.computed_values,
        limits=built.limits,
        next_recommended_action=built.next_recommended_action,
        blocked_reason=None,
        owner_confirmation_required=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=overclaim,
    )

    assert guard.status == STATUS_POLICY_BLOCKED
    assert guard.blocked_reason == "prohibited_claims_detected"
    assert guard.policy_violations


def test_needs_owner_confirmation_when_owner_view_requires_it() -> None:
    built = _owner_view_liq()
    needs_confirmation = Service1OperationalFindingOwnerViewV1(
        schema_version=built.schema_version,
        service_name=built.service_name,
        status=built.status,
        case_id=built.case_id,
        tenant_id=built.tenant_id,
        intake_id=built.intake_id,
        run_id=built.run_id,
        pathology_code=built.pathology_code,
        allowed_computation_ref=built.allowed_computation_ref,
        title=built.title,
        finding_summary=built.finding_summary,
        evidence_used=built.evidence_used,
        computed_values=built.computed_values,
        limits=built.limits,
        next_recommended_action=built.next_recommended_action,
        blocked_reason=None,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata={},
    )

    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=needs_confirmation,
    )

    assert guard.status == STATUS_NEEDS_OWNER_CONFIRMATION
    assert guard.required_owner_confirmations == ("owner_confirmation_required",)
    assert guard.delivery_allowed_candidate is False


def test_never_authorizes_runtime_reexecution_recalculation_or_delivery() -> None:
    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=_owner_view_liq(),
    )

    assert guard.runtime_authorized is False
    assert guard.reexecution_authorized is False
    assert guard.recalculation_authorized is False
    assert guard.delivery_authorized is False


def test_primary_dict_does_not_expose_human_review_fields() -> None:
    guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=_owner_view_liq(),
    )
    data = guard.to_dict()

    assert "human_review_required" not in data
    assert "human_review_gate" not in data
