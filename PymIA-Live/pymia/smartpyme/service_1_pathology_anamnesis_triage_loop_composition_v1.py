from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from pymia.smartpyme.service_1_owner_answer_reentry_v1 import Service1OwnerAnswerReentryV1
from pymia.smartpyme.service_1_pathology_anamnesis_triage_intake_bridge_v1 import (
    BRIDGE_STATUS_BUILT,
    Service1PathologyAnamnesisTriageIntakeBridgeV1,
    build_service_1_pathology_anamnesis_triage_intake_bridge_v1,
)
from pymia.smartpyme.service_1_pathology_anamnesis_triage_question_bundle_output_v1 import (
    OUTPUT_STATUS_BLOCKED,
    Service1PathologyAnamnesisTriageQuestionBundleOutputV1,
    build_service_1_pathology_anamnesis_triage_question_bundle_output_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import Service1QuestionBundleV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_LOOP_COMPOSITION_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

COMPOSITION_STATUS_BUILT = "BUILT"
COMPOSITION_STATUS_BLOCKED = "BLOCKED"
COMPOSITION_STATUS_NO_OWNER_QUESTIONS_REQUIRED = "NO_OWNER_QUESTIONS_REQUIRED"

COMPOSITION_BLOCK_BRIDGE_BLOCKED = "BRIDGE_BLOCKED"
COMPOSITION_BLOCK_QUESTION_OUTPUT_BLOCKED = "QUESTION_OUTPUT_BLOCKED"


@dataclass(frozen=True)
class Service1PathologyAnamnesisTriageLoopCompositionV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    bridge_result: Service1PathologyAnamnesisTriageIntakeBridgeV1
    question_bundle_output: Service1PathologyAnamnesisTriageQuestionBundleOutputV1
    blocked_reason: str | None
    selected_primary_pathology: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bridge_result"] = self.bridge_result.to_dict()
        data["question_bundle_output"] = self.question_bundle_output.to_dict()
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _composition_status(
    *,
    bridge_result: Service1PathologyAnamnesisTriageIntakeBridgeV1,
    question_bundle_output: Service1PathologyAnamnesisTriageQuestionBundleOutputV1,
) -> tuple[str, str | None]:
    if bridge_result.status != BRIDGE_STATUS_BUILT:
        return COMPOSITION_STATUS_BLOCKED, COMPOSITION_BLOCK_BRIDGE_BLOCKED
    if question_bundle_output.status == OUTPUT_STATUS_BLOCKED:
        return COMPOSITION_STATUS_BLOCKED, COMPOSITION_BLOCK_QUESTION_OUTPUT_BLOCKED
    if not question_bundle_output.owner_confirmation_required:
        return COMPOSITION_STATUS_NO_OWNER_QUESTIONS_REQUIRED, None
    return COMPOSITION_STATUS_BUILT, None


def build_service_1_pathology_anamnesis_triage_loop_composition_v1(
    *,
    question_bundle: Service1QuestionBundleV1,
    owner_ref: str,
    raw_owner_narrative: str | None = None,
    owner_answer_reentry: Service1OwnerAnswerReentryV1 | None = None,
    business_period_reference: str | None = None,
    declared_data_sources: list[str] | tuple[str, ...] | None = None,
    column_meaning_confirmations: list[str] | tuple[str, ...] | None = None,
    owner_constraints: list[str] | tuple[str, ...] | None = None,
    delivery_policy_constraints: list[str] | tuple[str, ...] | None = None,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyAnamnesisTriageLoopCompositionV1:
    """Compose Servicio 1 pathology/anamnesis triage loop as a pure chain.

    Chain:
    question_bundle / owner answer reentry / owner narrative
    -> intake bridge
    -> triage decision
    -> question bundle output.

    This composition does not execute IO, tools, LLM calls, runtime,
    recalculation, delivery, accounting, SaaS, or Servicio 2 behavior.
    """

    bridge_result = build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
        question_bundle=question_bundle,
        owner_ref=owner_ref,
        raw_owner_narrative=raw_owner_narrative,
        owner_answer_reentry=owner_answer_reentry,
        business_period_reference=business_period_reference,
        declared_data_sources=declared_data_sources,
        column_meaning_confirmations=column_meaning_confirmations,
        owner_constraints=owner_constraints,
        delivery_policy_constraints=delivery_policy_constraints,
        available_data_fields=available_data_fields,
        metadata={
            "source_schema_version": SCHEMA_VERSION,
            **dict(metadata or {}),
        },
    )
    question_bundle_output = build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
        bridge=bridge_result,
        metadata={
            "source_schema_version": SCHEMA_VERSION,
            **dict(metadata or {}),
        },
    )
    status, blocked_reason = _composition_status(
        bridge_result=bridge_result,
        question_bundle_output=question_bundle_output,
    )
    selected_primary_pathology = None
    if bridge_result.triage_decision is not None:
        selected_primary_pathology = bridge_result.triage_decision.selected_primary_pathology

    return Service1PathologyAnamnesisTriageLoopCompositionV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=bridge_result.case_id,
        tenant_id=bridge_result.tenant_id,
        intake_id=bridge_result.intake_id,
        run_id=bridge_result.run_id,
        bridge_result=bridge_result,
        question_bundle_output=question_bundle_output,
        blocked_reason=blocked_reason,
        selected_primary_pathology=selected_primary_pathology,
        owner_confirmation_required=question_bundle_output.owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "COMPOSITION_STATUS_BUILT",
    "COMPOSITION_STATUS_BLOCKED",
    "COMPOSITION_STATUS_NO_OWNER_QUESTIONS_REQUIRED",
    "COMPOSITION_BLOCK_BRIDGE_BLOCKED",
    "COMPOSITION_BLOCK_QUESTION_OUTPUT_BLOCKED",
    "Service1PathologyAnamnesisTriageLoopCompositionV1",
    "build_service_1_pathology_anamnesis_triage_loop_composition_v1",
]
