from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from pymia.smartpyme.service_1_owner_answer_reentry_v1 import Service1OwnerAnswerReentryV1
from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    Service1AnamnesisRecordV1,
    Service1AnamnesisTriageDecisionV1,
    Service1PathologyCandidateV1,
    build_service_1_anamnesis_triage_decision_v1,
    create_service_1_anamnesis_record_v1,
    detect_service_1_pathology_candidates_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import Service1QuestionBundleV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_INTAKE_BRIDGE_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

BRIDGE_STATUS_BUILT = "BUILT"
BRIDGE_STATUS_BLOCKED = "BLOCKED"

BRIDGE_BLOCK_INVALID_QUESTION_BUNDLE = "INVALID_QUESTION_BUNDLE"
BRIDGE_BLOCK_INVALID_REENTRY = "INVALID_REENTRY"
BRIDGE_BLOCK_CASE_MISMATCH = "CASE_MISMATCH"
BRIDGE_BLOCK_EMPTY_OWNER_NARRATIVE = "EMPTY_OWNER_NARRATIVE"


@dataclass(frozen=True)
class Service1PathologyAnamnesisTriageIntakeBridgeV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    source_question_ref: str | None
    raw_owner_narrative: str | None
    anamnesis_record: Service1AnamnesisRecordV1 | None
    pathology_candidates: tuple[Service1PathologyCandidateV1, ...]
    triage_decision: Service1AnamnesisTriageDecisionV1 | None
    blocked_reason: str | None
    owner_confirmation_required: bool
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["anamnesis_record"] = (
            self.anamnesis_record.to_dict() if self.anamnesis_record is not None else None
        )
        data["pathology_candidates"] = [candidate.to_dict() for candidate in self.pathology_candidates]
        data["triage_decision"] = (
            self.triage_decision.to_dict() if self.triage_decision is not None else None
        )
        return data


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


def _question_bundle_to_object(question_bundle: Service1QuestionBundleV1) -> Service1QuestionBundleV1:
    if not isinstance(question_bundle, Service1QuestionBundleV1):
        raise ValueError(BRIDGE_BLOCK_INVALID_QUESTION_BUNDLE)
    return question_bundle


def _extract_owner_answer_text(owner_answer_reentry: Service1OwnerAnswerReentryV1 | None) -> str | None:
    if owner_answer_reentry is None:
        return None
    if not isinstance(owner_answer_reentry, Service1OwnerAnswerReentryV1):
        raise ValueError(BRIDGE_BLOCK_INVALID_REENTRY)
    if owner_answer_reentry.owner_answer_record is None:
        return None
    return _clean_optional_text(owner_answer_reentry.owner_answer_record.raw_owner_answer)


def _blocked_bridge(
    *,
    question_bundle: Service1QuestionBundleV1,
    blocked_reason: str,
    source_question_ref: str | None = None,
    raw_owner_narrative: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyAnamnesisTriageIntakeBridgeV1:
    return Service1PathologyAnamnesisTriageIntakeBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=BRIDGE_STATUS_BLOCKED,
        case_id=question_bundle.case_id,
        tenant_id=question_bundle.tenant_id,
        intake_id=question_bundle.intake_id,
        run_id=question_bundle.run_id,
        source_question_ref=source_question_ref,
        raw_owner_narrative=raw_owner_narrative,
        anamnesis_record=None,
        pathology_candidates=(),
        triage_decision=None,
        blocked_reason=blocked_reason,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def build_service_1_pathology_anamnesis_triage_intake_bridge_v1(
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
) -> Service1PathologyAnamnesisTriageIntakeBridgeV1:
    """Bridge Servicio 1 intake/reentry/question bundle into pathology/anamnesis triage.

    This function is deliberately pure. It does not execute IO, tools, LLM calls,
    runtime, recalculation, delivery, or accounting actions. It only converts an
    owner narrative/answer into the first pathology/anamnesis triage contract.
    """

    bundle = _question_bundle_to_object(question_bundle)
    owner_ref = _required_text(owner_ref, field_name="owner_ref")

    if owner_answer_reentry is not None:
        if not isinstance(owner_answer_reentry, Service1OwnerAnswerReentryV1):
            raise ValueError(BRIDGE_BLOCK_INVALID_REENTRY)
        if owner_answer_reentry.case_id != bundle.case_id:
            return _blocked_bridge(
                question_bundle=bundle,
                blocked_reason=BRIDGE_BLOCK_CASE_MISMATCH,
                source_question_ref=owner_answer_reentry.question_ref,
                metadata=metadata,
            )

    narrative_from_reentry = _extract_owner_answer_text(owner_answer_reentry)
    narrative = _clean_optional_text(raw_owner_narrative) or narrative_from_reentry
    source_question_ref = owner_answer_reentry.question_ref if owner_answer_reentry is not None else None

    if not narrative:
        return _blocked_bridge(
            question_bundle=bundle,
            blocked_reason=BRIDGE_BLOCK_EMPTY_OWNER_NARRATIVE,
            source_question_ref=source_question_ref,
            metadata=metadata,
        )

    anamnesis_record = create_service_1_anamnesis_record_v1(
        case_id=bundle.case_id,
        owner_ref=owner_ref,
        tenant_ref=bundle.tenant_id,
        raw_owner_narrative=narrative,
        declared_primary_pain=None,
        business_period_reference=business_period_reference,
        declared_data_sources=declared_data_sources,
        column_meaning_confirmations=column_meaning_confirmations,
        owner_constraints=owner_constraints,
        delivery_policy_constraints=delivery_policy_constraints,
        available_data_fields=available_data_fields,
        metadata={
            "source_schema_version": SCHEMA_VERSION,
            "source_question_bundle_schema_version": bundle.schema_version,
            "source_question_ref": source_question_ref,
            "intake_id": bundle.intake_id,
            "run_id": bundle.run_id,
            **dict(metadata or {}),
        },
    )
    pathology_candidates = detect_service_1_pathology_candidates_v1(
        anamnesis_record,
        available_data_fields=available_data_fields,
    )
    triage_decision = build_service_1_anamnesis_triage_decision_v1(
        anamnesis_record,
        available_data_fields=available_data_fields,
    )

    return Service1PathologyAnamnesisTriageIntakeBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=BRIDGE_STATUS_BUILT,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        run_id=bundle.run_id,
        source_question_ref=source_question_ref,
        raw_owner_narrative=narrative,
        anamnesis_record=anamnesis_record,
        pathology_candidates=pathology_candidates,
        triage_decision=triage_decision,
        blocked_reason=None,
        owner_confirmation_required=anamnesis_record.owner_confirmation_required,
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
    "BRIDGE_STATUS_BUILT",
    "BRIDGE_STATUS_BLOCKED",
    "BRIDGE_BLOCK_INVALID_QUESTION_BUNDLE",
    "BRIDGE_BLOCK_INVALID_REENTRY",
    "BRIDGE_BLOCK_CASE_MISMATCH",
    "BRIDGE_BLOCK_EMPTY_OWNER_NARRATIVE",
    "Service1PathologyAnamnesisTriageIntakeBridgeV1",
    "build_service_1_pathology_anamnesis_triage_intake_bridge_v1",
]
