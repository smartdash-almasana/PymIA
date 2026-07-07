from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

from pymia.smartpyme.service_1_controlled_computation_plan_v1 import (
    STATUS_READY_FOR_DRY_RUN_CANDIDATE,
    build_service_1_controlled_computation_plan_v1,
)
from pymia.smartpyme.service_1_operational_finding_owner_view_v1 import (
    STATUS_OWNER_VIEW_BUILT,
    build_service_1_operational_finding_owner_view_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_entrypoint_candidate_v1 import (
    ENTRYPOINT_STATUS_BLOCKED,
    ENTRYPOINT_STATUS_BUILT,
    ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED,
    Service1PathologyAnamnesisTriageEntrypointCandidateV1,
    build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_evidence_readiness_gate_v1 import (
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY_FOR_COMPUTATION_PLAN,
    build_service_1_pathology_evidence_readiness_gate_v1,
)
from pymia.smartpyme.service_1_pathology_finding_delivery_package_v1 import (
    STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT,
    Service1PathologyFindingDeliveryPackageV1,
    build_service_1_pathology_finding_delivery_package_v1,
)
from pymia.smartpyme.service_1_pathology_finding_delivery_policy_guard_v1 import (
    STATUS_POLICY_PASS,
    build_service_1_pathology_finding_delivery_policy_guard_v1,
)
from pymia.smartpyme.service_1_pathology_first_aid_dry_run_candidate_v1 import (
    STATUS_DRY_RUN_CANDIDATE_BUILT,
    build_service_1_pathology_first_aid_dry_run_candidate_v1,
)
from pymia.smartpyme.service_1_pathology_to_allowed_computation_candidate_v1 import (
    STATUS_READY_FOR_COMPUTATION_PLAN as ALLOWED_STATUS_READY_FOR_COMPUTATION_PLAN,
    build_service_1_pathology_to_allowed_computation_candidate_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_XLSX_FIRST_PRODUCT_ENTRYPOINT_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_NEXT_OWNER_QUESTION = "NEXT_OWNER_QUESTION"
STATUS_DELIVERY_PACKAGE_CANDIDATE_READY = "DELIVERY_PACKAGE_CANDIDATE_READY"
STATUS_BLOCKED = "BLOCKED"

BLOCK_EMPTY_OWNER_NARRATIVE = "EMPTY_OWNER_NARRATIVE"
BLOCK_TRIAGE_ENTRYPOINT_BLOCKED = "TRIAGE_ENTRYPOINT_BLOCKED"
BLOCK_UNSUPPORTED_OR_INCOMPLETE_COMPUTATION = "UNSUPPORTED_OR_INCOMPLETE_COMPUTATION"
BLOCK_EVIDENCE_NOT_READY = "EVIDENCE_NOT_READY"
BLOCK_COMPUTATION_PLAN_NOT_READY = "COMPUTATION_PLAN_NOT_READY"
BLOCK_DRY_RUN_NOT_BUILT = "DRY_RUN_NOT_BUILT"
BLOCK_OWNER_VIEW_NOT_BUILT = "OWNER_VIEW_NOT_BUILT"
BLOCK_POLICY_NOT_PASS = "POLICY_NOT_PASS"
BLOCK_PACKAGE_NOT_BUILT = "PACKAGE_NOT_BUILT"

ProductEntrypointStatusV1 = Literal[
    "NEXT_OWNER_QUESTION",
    "DELIVERY_PACKAGE_CANDIDATE_READY",
    "BLOCKED",
]


@dataclass(frozen=True)
class Service1XlsxFirstProductEntrypointV1:
    schema_version: str
    service_name: str
    status: ProductEntrypointStatusV1
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    selected_primary_pathology: str | None
    allowed_computation_ref: str | None
    next_owner_question: str | None
    delivery_package_candidate: Service1PathologyFindingDeliveryPackageV1 | None
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    trace: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["delivery_package_candidate"] = (
            self.delivery_package_candidate.to_dict()
            if self.delivery_package_candidate is not None
            else None
        )
        return data


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, (list, tuple, set)) else (value,)
    return tuple(text for item in values if (text := _text(item)))


def _trace_status(value: Any) -> str | None:
    return getattr(value, "status", None)


def _blocked(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    selected_primary_pathology: str | None,
    allowed_computation_ref: str | None,
    next_owner_question: str | None,
    blocked_reason: str,
    owner_confirmation_required: bool,
    trace: dict[str, Any],
    metadata: dict[str, Any] | None,
) -> Service1XlsxFirstProductEntrypointV1:
    return Service1XlsxFirstProductEntrypointV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=STATUS_BLOCKED,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        selected_primary_pathology=selected_primary_pathology,
        allowed_computation_ref=allowed_computation_ref,
        next_owner_question=next_owner_question,
        delivery_package_candidate=None,
        blocked_reason=blocked_reason,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        trace=dict(trace),
        metadata=dict(metadata or {}),
    )


def _next_question_result(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    triage_entrypoint: Service1PathologyAnamnesisTriageEntrypointCandidateV1,
    next_owner_question: str | None,
    trace: dict[str, Any],
    metadata: dict[str, Any] | None,
) -> Service1XlsxFirstProductEntrypointV1:
    return Service1XlsxFirstProductEntrypointV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=STATUS_NEXT_OWNER_QUESTION,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
        allowed_computation_ref=None,
        next_owner_question=next_owner_question,
        delivery_package_candidate=None,
        blocked_reason=None,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        trace=dict(trace),
        metadata=dict(metadata or {}),
    )


def _package_material(owner_view: Any) -> dict[str, Any]:
    return {
        "owner_title": owner_view.title,
        "owner_summary": owner_view.finding_summary,
        "evidence_used": owner_view.evidence_used,
        "computed_values": owner_view.computed_values,
        "limits": owner_view.limits,
        "next_recommended_action": owner_view.next_recommended_action,
    }


def build_service_1_xlsx_first_product_entrypoint_v1(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    raw_owner_narrative: str | None,
    business_period_reference: str | None = None,
    declared_data_sources: list[str] | tuple[str, ...] | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    input_values: dict[str, object] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxFirstProductEntrypointV1:
    """Official pure entrypoint for Servicio 1 operativo XLSX-first.

    This composes the closed chain and returns either a next owner question,
    a delivery package candidate, or a blocked result. It does not perform IO,
    external tool calls, pipeline calls, SaaS behavior, publication, or real delivery.
    """

    case_id = _required_text(case_id, field_name="case_id")
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    run_id = _required_text(run_id, field_name="run_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    available_fields = _tuple(available_data_fields)
    confirmations = _tuple(column_meaning_confirmations)
    input_values = dict(input_values or {})
    trace: dict[str, Any] = {}

    triage_entrypoint = build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        raw_owner_narrative=raw_owner_narrative,
        business_period_reference=business_period_reference,
        declared_data_sources=declared_data_sources,
        column_meaning_confirmations=confirmations,
        available_data_fields=available_fields,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["triage_entrypoint_status"] = triage_entrypoint.status

    if triage_entrypoint.status == ENTRYPOINT_STATUS_BLOCKED:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=None,
            next_owner_question=triage_entrypoint.next_question_text,
            blocked_reason=triage_entrypoint.blocked_reason or BLOCK_TRIAGE_ENTRYPOINT_BLOCKED,
            owner_confirmation_required=triage_entrypoint.owner_confirmation_required,
            trace=trace,
            metadata=metadata,
        )

    if triage_entrypoint.status == ENTRYPOINT_STATUS_BUILT and triage_entrypoint.owner_confirmation_required:
        return _next_question_result(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            triage_entrypoint=triage_entrypoint,
            next_owner_question=triage_entrypoint.next_question_text,
            trace=trace,
            metadata=metadata,
        )

    if triage_entrypoint.status != ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=None,
            next_owner_question=triage_entrypoint.next_question_text,
            blocked_reason=BLOCK_TRIAGE_ENTRYPOINT_BLOCKED,
            owner_confirmation_required=True,
            trace=trace,
            metadata=metadata,
        )

    allowed_candidate = build_service_1_pathology_to_allowed_computation_candidate_v1(
        pathology_code=triage_entrypoint.selected_primary_pathology or "UNKNOWN_PATHOLOGY",
        available_data_fields=available_fields,
        missing_evidence_items=triage_entrypoint.missing_evidence_items,
        business_period_reference=business_period_reference,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["allowed_computation_candidate_status"] = allowed_candidate.status

    if allowed_candidate.status != ALLOWED_STATUS_READY_FOR_COMPUTATION_PLAN:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_UNSUPPORTED_OR_INCOMPLETE_COMPUTATION,
            owner_confirmation_required=False,
            trace=trace,
            metadata=metadata,
        )

    readiness_gate = build_service_1_pathology_evidence_readiness_gate_v1(
        entrypoint_candidate_result=triage_entrypoint,
        allowed_computation_candidate=allowed_candidate,
        available_data_fields=available_fields,
        column_meaning_confirmations=confirmations,
        business_period_reference=business_period_reference,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["evidence_readiness_gate_status"] = readiness_gate.status

    if readiness_gate.status in (STATUS_NEEDS_OWNER_CONFIRMATION, STATUS_NEEDS_EVIDENCE):
        first_question = readiness_gate.next_owner_questions[0] if readiness_gate.next_owner_questions else None
        return _next_question_result(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            triage_entrypoint=triage_entrypoint,
            next_owner_question=first_question,
            trace=trace,
            metadata=metadata,
        )

    if readiness_gate.status != STATUS_READY_FOR_COMPUTATION_PLAN:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_EVIDENCE_NOT_READY,
            owner_confirmation_required=True,
            trace=trace,
            metadata=metadata,
        )

    computation_plan = build_service_1_controlled_computation_plan_v1(
        evidence_readiness_gate_result=readiness_gate,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["computation_plan_status"] = computation_plan.status

    if computation_plan.status != STATUS_READY_FOR_DRY_RUN_CANDIDATE:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_COMPUTATION_PLAN_NOT_READY,
            owner_confirmation_required=False,
            trace=trace,
            metadata=metadata,
        )

    dry_run = build_service_1_pathology_first_aid_dry_run_candidate_v1(
        computation_plan_result=computation_plan,
        input_values=input_values,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["dry_run_status"] = dry_run.status

    if dry_run.status != STATUS_DRY_RUN_CANDIDATE_BUILT:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_DRY_RUN_NOT_BUILT,
            owner_confirmation_required=False,
            trace=trace,
            metadata=metadata,
        )

    owner_view = build_service_1_operational_finding_owner_view_v1(
        dry_run_candidate_result=dry_run,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["owner_view_status"] = owner_view.status

    if owner_view.status != STATUS_OWNER_VIEW_BUILT:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_OWNER_VIEW_NOT_BUILT,
            owner_confirmation_required=owner_view.owner_confirmation_required,
            trace=trace,
            metadata=metadata,
        )

    policy_guard = build_service_1_pathology_finding_delivery_policy_guard_v1(
        operational_finding_owner_view_result=owner_view,
        metadata={"source_schema_version": SCHEMA_VERSION, **dict(metadata or {})},
    )
    trace["policy_guard_status"] = policy_guard.status

    if policy_guard.status != STATUS_POLICY_PASS:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_POLICY_NOT_PASS,
            owner_confirmation_required=policy_guard.owner_confirmation_required,
            trace=trace,
            metadata=metadata,
        )

    package_candidate = build_service_1_pathology_finding_delivery_package_v1(
        delivery_policy_guard_result=policy_guard,
        metadata={
            "source_schema_version": SCHEMA_VERSION,
            "package_material": _package_material(owner_view),
            **dict(metadata or {}),
        },
    )
    trace["package_candidate_status"] = package_candidate.status

    if package_candidate.status != STATUS_DELIVERY_PACKAGE_CANDIDATE_BUILT:
        return _blocked(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
            allowed_computation_ref=allowed_candidate.allowed_computation_ref,
            next_owner_question=None,
            blocked_reason=BLOCK_PACKAGE_NOT_BUILT,
            owner_confirmation_required=package_candidate.owner_confirmation_required,
            trace=trace,
            metadata=metadata,
        )

    return Service1XlsxFirstProductEntrypointV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=STATUS_DELIVERY_PACKAGE_CANDIDATE_READY,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        selected_primary_pathology=triage_entrypoint.selected_primary_pathology,
        allowed_computation_ref=allowed_candidate.allowed_computation_ref,
        next_owner_question=None,
        delivery_package_candidate=package_candidate,
        blocked_reason=None,
        owner_confirmation_required=False,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        trace=trace,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_NEXT_OWNER_QUESTION",
    "STATUS_DELIVERY_PACKAGE_CANDIDATE_READY",
    "STATUS_BLOCKED",
    "Service1XlsxFirstProductEntrypointV1",
    "build_service_1_xlsx_first_product_entrypoint_v1",
]
