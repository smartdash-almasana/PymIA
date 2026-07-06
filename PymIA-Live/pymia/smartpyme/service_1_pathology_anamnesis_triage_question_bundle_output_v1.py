from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from pymia.smartpyme.service_1_pathology_anamnesis_triage_intake_bridge_v1 import (
    BRIDGE_STATUS_BUILT,
    Service1PathologyAnamnesisTriageIntakeBridgeV1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE,
    QUESTION_STATUS_PENDING,
    SCHEMA_VERSION as QUESTION_BUNDLE_SCHEMA_VERSION,
    SERVICE_NAME,
    Service1QuestionBundleV1,
    Service1QuestionV1,
    create_service_1_question_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_PATHOLOGY_ANAMNESIS_TRIAGE_QUESTION_BUNDLE_OUTPUT_V1"

SOURCE_PATHOLOGY_ANAMNESIS_TRIAGE = "pathology_anamnesis_triage"

OUTPUT_STATUS_BUILT = "BUILT"
OUTPUT_STATUS_BLOCKED = "BLOCKED"
OUTPUT_STATUS_NO_OWNER_QUESTIONS_REQUIRED = "NO_OWNER_QUESTIONS_REQUIRED"

OUTPUT_BLOCK_INVALID_BRIDGE = "INVALID_BRIDGE"
OUTPUT_BLOCK_BRIDGE_NOT_BUILT = "BRIDGE_NOT_BUILT"
OUTPUT_BLOCK_TRIAGE_DECISION_MISSING = "TRIAGE_DECISION_MISSING"


@dataclass(frozen=True)
class Service1PathologyAnamnesisTriageQuestionBundleOutputV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    source_bridge_schema_version: str
    selected_primary_pathology: str | None
    source_triage_status: str | None
    question_bundle: Service1QuestionBundleV1 | None
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
        data["question_bundle"] = (
            self.question_bundle.to_dict() if self.question_bundle is not None else None
        )
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_output(
    *,
    bridge: Service1PathologyAnamnesisTriageIntakeBridgeV1,
    blocked_reason: str,
    metadata: dict[str, Any] | None,
) -> Service1PathologyAnamnesisTriageQuestionBundleOutputV1:
    triage_decision = bridge.triage_decision
    return Service1PathologyAnamnesisTriageQuestionBundleOutputV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=OUTPUT_STATUS_BLOCKED,
        case_id=bridge.case_id,
        tenant_id=bridge.tenant_id,
        intake_id=bridge.intake_id,
        run_id=bridge.run_id,
        source_bridge_schema_version=bridge.schema_version,
        selected_primary_pathology=(
            triage_decision.selected_primary_pathology if triage_decision is not None else None
        ),
        source_triage_status=(triage_decision.status if triage_decision is not None else None),
        question_bundle=None,
        blocked_reason=blocked_reason,
        owner_confirmation_required=True,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


def _build_questions(
    *,
    bridge: Service1PathologyAnamnesisTriageIntakeBridgeV1,
) -> tuple[Service1QuestionV1, ...]:
    if bridge.triage_decision is None:
        return ()

    questions: list[Service1QuestionV1] = []
    selected_pathology = bridge.triage_decision.selected_primary_pathology or "none"
    for index, text in enumerate(bridge.triage_decision.next_owner_questions):
        target_ref = f"pathology:{selected_pathology}:owner_question:{index}"
        questions.append(
            create_service_1_question_v1(
                source=SOURCE_PATHOLOGY_ANAMNESIS_TRIAGE,
                text=text,
                target_ref=target_ref,
                answer_type=ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE,
                required=True,
                status=QUESTION_STATUS_PENDING,
                metadata={
                    "origin": SCHEMA_VERSION,
                    "source_triage_status": bridge.triage_decision.status,
                    "selected_primary_pathology": bridge.triage_decision.selected_primary_pathology,
                    "question_index": index,
                    "runtime_authorized": False,
                    "delivery_authorized": False,
                },
            )
        )
    return tuple(questions)


def build_service_1_pathology_anamnesis_triage_question_bundle_output_v1(
    *,
    bridge: Service1PathologyAnamnesisTriageIntakeBridgeV1,
    metadata: dict[str, Any] | None = None,
) -> Service1PathologyAnamnesisTriageQuestionBundleOutputV1:
    """Convert pathology/anamnesis triage next questions into Service1QuestionBundleV1.

    This adapter is pure. It does not execute IO, runtime, LLM calls, tools,
    recalculation, delivery, or accounting actions. It only emits owner-facing
    questions already produced by the triage decision.
    """

    if not isinstance(bridge, Service1PathologyAnamnesisTriageIntakeBridgeV1):
        raise ValueError(OUTPUT_BLOCK_INVALID_BRIDGE)
    if bridge.status != BRIDGE_STATUS_BUILT:
        return _blocked_output(
            bridge=bridge,
            blocked_reason=OUTPUT_BLOCK_BRIDGE_NOT_BUILT,
            metadata=metadata,
        )
    if bridge.triage_decision is None:
        return _blocked_output(
            bridge=bridge,
            blocked_reason=OUTPUT_BLOCK_TRIAGE_DECISION_MISSING,
            metadata=metadata,
        )

    questions = _build_questions(bridge=bridge)
    owner_confirmation_required = bool(questions)
    selected_next_question_ref = questions[0].question_ref if questions else None
    question_bundle = Service1QuestionBundleV1(
        schema_version=QUESTION_BUNDLE_SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=bridge.case_id,
        tenant_id=bridge.tenant_id,
        intake_id=bridge.intake_id,
        run_id=f"{bridge.run_id}:pathology_anamnesis_triage_questions",
        questions=questions,
        selected_next_question_ref=selected_next_question_ref,
        runtime_authorized=False,
        owner_confirmation_required=owner_confirmation_required,
        created_at=_now_iso(),
        metadata={
            "origin": SCHEMA_VERSION,
            "source_bridge_schema_version": bridge.schema_version,
            "source_triage_status": bridge.triage_decision.status,
            "selected_primary_pathology": bridge.triage_decision.selected_primary_pathology,
            "source_run_id": bridge.run_id,
            **dict(metadata or {}),
        },
    )

    return Service1PathologyAnamnesisTriageQuestionBundleOutputV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=(
            OUTPUT_STATUS_BUILT
            if owner_confirmation_required
            else OUTPUT_STATUS_NO_OWNER_QUESTIONS_REQUIRED
        ),
        case_id=bridge.case_id,
        tenant_id=bridge.tenant_id,
        intake_id=bridge.intake_id,
        run_id=bridge.run_id,
        source_bridge_schema_version=bridge.schema_version,
        selected_primary_pathology=bridge.triage_decision.selected_primary_pathology,
        source_triage_status=bridge.triage_decision.status,
        question_bundle=question_bundle,
        blocked_reason=None,
        owner_confirmation_required=owner_confirmation_required,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SOURCE_PATHOLOGY_ANAMNESIS_TRIAGE",
    "OUTPUT_STATUS_BUILT",
    "OUTPUT_STATUS_BLOCKED",
    "OUTPUT_STATUS_NO_OWNER_QUESTIONS_REQUIRED",
    "OUTPUT_BLOCK_INVALID_BRIDGE",
    "OUTPUT_BLOCK_BRIDGE_NOT_BUILT",
    "OUTPUT_BLOCK_TRIAGE_DECISION_MISSING",
    "Service1PathologyAnamnesisTriageQuestionBundleOutputV1",
    "build_service_1_pathology_anamnesis_triage_question_bundle_output_v1",
]
