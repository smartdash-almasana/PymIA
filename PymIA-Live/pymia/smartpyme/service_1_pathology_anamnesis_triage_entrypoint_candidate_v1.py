from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from pymia.smartpyme.service_1_pathology_anamnesis_triage_loop_composition_v1 import (
    COMPOSITION_STATUS_BLOCKED,
    Service1PathologyAnamnesisTriageLoopCompositionV1,
    build_service_1_pathology_anamnesis_triage_loop_composition_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    SERVICE_NAME,
    Service1QuestionBundleV1,
    build_service_1_question_bundle_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_ENTRYPOINT_CANDIDATE_V1"

ENTRYPOINT_STATUS_BUILT = "BUILT"
ENTRYPOINT_STATUS_BLOCKED = "BLOCKED"
ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED = "NO_OWNER_QUESTIONS_REQUIRED"

ENTRYPOINT_BLOCK_EMPTY_OWNER_NARRATIVE = "EMPTY_OWNER_NARRATIVE"
ENTRYPOINT_BLOCK_LOOP_COMPOSITION_BLOCKED = "LOOP_COMPOSITION_BLOCKED"

DEFAULT_INITIAL_OWNER_QUESTION = "¿Qué problema operativo querés entender primero?"


@dataclass(frozen=True)
class Service1PathologyAnamnesisTriageEntrypointCandidateV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    owner_ref: str
    raw_owner_narrative: str | None
    initial_question_bundle: Service1QuestionBundleV1 | None
    loop_composition: Service1PathologyAnamnesisTriageLoopCompositionV1 | None
    selected_primary_pathology: str | None
    next_question_text: str | None
    missing_evidence_items: tuple[str, ...]
    owner_confirmation_required: bool
    blocked_reason: str | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["initial_question_bundle"] = (
            self.initial_question_bundle.to_dict() if self.initial_question_bundle is not None else None
        )
        data["loop_composition"] = (
            self.loop_composition.to_dict() if self.loop_composition is not None else None
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


def _blocked_entrypoint(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    owner_ref: str,
    raw_owner_narrative: str | None,
    initial_question_bundle: Service1QuestionBundleV1 | None,
    loop_composition: Service1PathologyAnamnesisTriageLoopCompositionV1 | None,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1PathologyAnamnesisTriageEntrypointCandidateV1:
    return Service1PathologyAnamnesisTriageEntrypointCandidateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=ENTRYPOINT_STATUS_BLOCKED,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        raw_owner_narrative=raw_owner_narrative,
        initial_question_bundle=initial_question_bundle,
        loop_composition=loop_composition,
        selected_primary_pathology=(
            loop_composition.selected_primary_pathology if loop_composition is not None else None
        ),
        next_question_text=None,
        missing_evidence_items=(),
        owner_confirmation_required=True,
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def _build_initial_question_bundle(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    metadata: dict[str, Any] | None,
) -> Service1QuestionBundleV1:
    return build_service_1_question_bundle_v1(
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        report={
            "next_questions": [
                {
                    "question": DEFAULT_INITIAL_OWNER_QUESTION,
                    "target_ref": "owner:primary_pain",
                }
            ]
        },
        metadata={
            "origin": SCHEMA_VERSION,
            **dict(metadata or {}),
        },
    )


def _first_next_question_text(
    loop_composition: Service1PathologyAnamnesisTriageLoopCompositionV1,
) -> str | None:
    output_bundle = loop_composition.question_bundle_output.question_bundle
    if output_bundle is None or not output_bundle.questions:
        return None
    return output_bundle.questions[0].text


def _missing_evidence_items(
    loop_composition: Service1PathologyAnamnesisTriageLoopCompositionV1,
) -> tuple[str, ...]:
    bridge = loop_composition.bridge_result
    if bridge.anamnesis_record is None:
        return ()
    return bridge.anamnesis_record.missing_evidence_items


def build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1(
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
    owner_constraints: list[str] | tuple[str, ...] | None = None,
    delivery_policy_constraints: list[str] | tuple[str, ...] | None = None,
    available_data_fields: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyAnamnesisTriageEntrypointCandidateV1:
    """Controlled candidate entrypoint for Servicio 1 pathology/anamnesis triage.

    This is a product-facing pure boundary candidate. It builds the initial S1
    question bundle, runs the pathology/anamnesis loop composition, and returns a
    compact result for the caller. It does not execute IO, tools, LLM calls,
    runtime, recalculation, delivery, accounting, SaaS, or Servicio 2 behavior.
    """

    case_id = _required_text(case_id, field_name="case_id")
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    run_id = _required_text(run_id, field_name="run_id")
    owner_ref = _required_text(owner_ref, field_name="owner_ref")
    narrative = _clean_optional_text(raw_owner_narrative)

    initial_question_bundle = _build_initial_question_bundle(
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        metadata=metadata,
    )

    if not narrative:
        return _blocked_entrypoint(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            raw_owner_narrative=narrative,
            initial_question_bundle=initial_question_bundle,
            loop_composition=None,
            blocked_reason=ENTRYPOINT_BLOCK_EMPTY_OWNER_NARRATIVE,
            metadata=metadata,
        )

    loop_composition = build_service_1_pathology_anamnesis_triage_loop_composition_v1(
        question_bundle=initial_question_bundle,
        owner_ref=owner_ref,
        raw_owner_narrative=narrative,
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

    if loop_composition.status == COMPOSITION_STATUS_BLOCKED:
        return _blocked_entrypoint(
            case_id=case_id,
            tenant_id=tenant_id,
            intake_id=intake_id,
            run_id=run_id,
            owner_ref=owner_ref,
            raw_owner_narrative=narrative,
            initial_question_bundle=initial_question_bundle,
            loop_composition=loop_composition,
            blocked_reason=ENTRYPOINT_BLOCK_LOOP_COMPOSITION_BLOCKED,
            metadata=metadata,
        )

    owner_confirmation_required = loop_composition.owner_confirmation_required
    status = (
        ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED
        if not owner_confirmation_required
        else ENTRYPOINT_STATUS_BUILT
    )

    return Service1PathologyAnamnesisTriageEntrypointCandidateV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=case_id,
        tenant_id=tenant_id,
        intake_id=intake_id,
        run_id=run_id,
        owner_ref=owner_ref,
        raw_owner_narrative=narrative,
        initial_question_bundle=initial_question_bundle,
        loop_composition=loop_composition,
        selected_primary_pathology=loop_composition.selected_primary_pathology,
        next_question_text=_first_next_question_text(loop_composition),
        missing_evidence_items=_missing_evidence_items(loop_composition),
        owner_confirmation_required=owner_confirmation_required,
        blocked_reason=None,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata={
            "declared_data_sources": _clean_tuple(declared_data_sources),
            "available_data_fields": _clean_tuple(available_data_fields),
            **dict(metadata or {}),
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "ENTRYPOINT_STATUS_BUILT",
    "ENTRYPOINT_STATUS_BLOCKED",
    "ENTRYPOINT_STATUS_NO_OWNER_QUESTIONS_REQUIRED",
    "ENTRYPOINT_BLOCK_EMPTY_OWNER_NARRATIVE",
    "ENTRYPOINT_BLOCK_LOOP_COMPOSITION_BLOCKED",
    "DEFAULT_INITIAL_OWNER_QUESTION",
    "Service1PathologyAnamnesisTriageEntrypointCandidateV1",
    "build_service_1_pathology_anamnesis_triage_entrypoint_candidate_v1",
]
