from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_case_reentry_read_model_v1 import (
    Service1CaseReentryReadModelV1,
    load_service_1_case_reentry_read_model_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1 import (
    PERSISTENCE_STATUS_PERSISTED,
    Service1OwnerAnswerReentryPersistenceV1,
    persist_service_1_owner_answer_reentry_v1,
)
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import (
    REENTRY_STATUS_ACCEPTED,
    Service1OwnerAnswerReentryV1,
    bind_owner_answer_for_service_1_reentry_v1,
)
from pymia.smartpyme.service_1_question_bundle_v1 import (
    SERVICE_NAME,
    Service1QuestionBundleV1,
)
from pymia.smartpyme.service_1_reentry_projection_v1 import (
    PROJECTION_STATUS_BLOCKED,
    Service1ReentryProjectionV1,
    project_service_1_reentry_v1,
)

SCHEMA_VERSION = "SERVICE_1_OWNER_REENTRY_BRIDGE_V1"

BRIDGE_STATUS_ACCEPTED_AND_PROJECTED = "ACCEPTED_AND_PROJECTED"
BRIDGE_STATUS_BLOCKED_REENTRY = "BLOCKED_REENTRY"
BRIDGE_STATUS_BLOCKED_PERSISTENCE = "BLOCKED_PERSISTENCE"
BRIDGE_STATUS_BLOCKED_PROJECTION = "BLOCKED_PROJECTION"


@dataclass(frozen=True)
class Service1OwnerReentryBridgeV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    question_ref: str
    reentry_packet: Service1OwnerAnswerReentryV1
    persistence_result: Service1OwnerAnswerReentryPersistenceV1 | None
    read_model: Service1CaseReentryReadModelV1 | None
    projection: Service1ReentryProjectionV1 | None
    selected_next_pending_question_ref: str | None
    blocked_reason: str | None
    runtime_authorized: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    delivery_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["reentry_packet"] = self.reentry_packet.to_dict()
        data["persistence_result"] = (
            self.persistence_result.to_dict() if self.persistence_result is not None else None
        )
        data["read_model"] = self.read_model.to_dict() if self.read_model is not None else None
        data["projection"] = self.projection.to_dict() if self.projection is not None else None
        return data


def _blocked_bridge(
    *,
    status: str,
    reentry_packet: Service1OwnerAnswerReentryV1,
    persistence_result: Service1OwnerAnswerReentryPersistenceV1 | None = None,
    read_model: Service1CaseReentryReadModelV1 | None = None,
    projection: Service1ReentryProjectionV1 | None = None,
    blocked_reason: str | None,
    metadata: dict[str, Any] | None,
) -> Service1OwnerReentryBridgeV1:
    return Service1OwnerReentryBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=reentry_packet.case_id,
        tenant_id=reentry_packet.tenant_id,
        intake_id=reentry_packet.intake_id,
        question_ref=reentry_packet.question_ref,
        reentry_packet=reentry_packet,
        persistence_result=persistence_result,
        read_model=read_model,
        projection=projection,
        selected_next_pending_question_ref=(
            projection.selected_next_pending_question_ref if projection is not None else None
        ),
        blocked_reason=blocked_reason,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def run_service_1_owner_reentry_bridge_v1(
    *,
    question_bundle: Service1QuestionBundleV1 | dict[str, Any],
    question_ref: str,
    raw_owner_answer: str,
    anamnesis_id: str,
    investigation_id: str,
    storage_dir: str | Path,
    metadata: dict[str, Any] | None = None,
) -> Service1OwnerReentryBridgeV1:
    """Run the safe Servicio 1 owner-answer reentry bridge.

    The bridge reuses the existing question bundle, reentry, persistence, read
    model and projection primitives. It does not execute tools, re-run the
    pipeline, recalculate evidence, mutate question bundles or authorize delivery.
    """

    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    reentry_packet = bind_owner_answer_for_service_1_reentry_v1(
        question_bundle=question_bundle,
        question_ref=question_ref,
        raw_owner_answer=raw_owner_answer,
        anamnesis_id=anamnesis_id,
        investigation_id=investigation_id,
        metadata=metadata,
    )

    if reentry_packet.status != REENTRY_STATUS_ACCEPTED:
        return _blocked_bridge(
            status=BRIDGE_STATUS_BLOCKED_REENTRY,
            reentry_packet=reentry_packet,
            blocked_reason=reentry_packet.blocked_reason,
            metadata=metadata,
        )

    persistence_result = persist_service_1_owner_answer_reentry_v1(
        reentry_packet=reentry_packet,
        storage_dir=storage_dir,
        metadata=metadata,
    )

    if persistence_result.status != PERSISTENCE_STATUS_PERSISTED:
        return _blocked_bridge(
            status=BRIDGE_STATUS_BLOCKED_PERSISTENCE,
            reentry_packet=reentry_packet,
            persistence_result=persistence_result,
            blocked_reason=persistence_result.blocked_reason,
            metadata=metadata,
        )

    read_model = load_service_1_case_reentry_read_model_v1(
        storage_dir=storage_dir,
        tenant_id=reentry_packet.tenant_id,
        intake_id=reentry_packet.intake_id,
        metadata=metadata,
    )

    projection = project_service_1_reentry_v1(
        question_bundle=persistence_result.metadata.get("serialized_question_bundle", question_bundle)
        if isinstance(question_bundle, Service1QuestionBundleV1)
        else _ensure_question_bundle_object(question_bundle),
        read_model=read_model,
        metadata=metadata,
    )

    if projection.status == PROJECTION_STATUS_BLOCKED:
        return _blocked_bridge(
            status=BRIDGE_STATUS_BLOCKED_PROJECTION,
            reentry_packet=reentry_packet,
            persistence_result=persistence_result,
            read_model=read_model,
            projection=projection,
            blocked_reason=projection.blocked_reason,
            metadata=metadata,
        )

    return Service1OwnerReentryBridgeV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=BRIDGE_STATUS_ACCEPTED_AND_PROJECTED,
        case_id=reentry_packet.case_id,
        tenant_id=reentry_packet.tenant_id,
        intake_id=reentry_packet.intake_id,
        question_ref=reentry_packet.question_ref,
        reentry_packet=reentry_packet,
        persistence_result=persistence_result,
        read_model=read_model,
        projection=projection,
        selected_next_pending_question_ref=projection.selected_next_pending_question_ref,
        blocked_reason=None,
        runtime_authorized=False,
        reexecution_authorized=False,
        recalculation_authorized=False,
        delivery_authorized=False,
        metadata=dict(metadata or {}),
    )


def _ensure_question_bundle_object(bundle: Service1QuestionBundleV1 | dict[str, Any]) -> Service1QuestionBundleV1:
    """Convert serialized question bundle to object through the reentry binder path.

    The public reentry binder already validates serialized bundles. This helper is
    intentionally narrow and uses the same field structure to avoid a second model.
    """

    if isinstance(bundle, Service1QuestionBundleV1):
        return bundle
    if not isinstance(bundle, dict):
        raise ValueError("question_bundle must be Service1QuestionBundleV1 or dict")

    # Import locally to keep the top-level dependency set explicit and small.
    from pymia.smartpyme.service_1_question_bundle_v1 import Service1QuestionV1

    questions = tuple(
        Service1QuestionV1(
            question_ref=str(item["question_ref"]),
            source=str(item["source"]),
            text=str(item["text"]),
            target_ref=str(item.get("target_ref") or ""),
            answer_type=str(item["answer_type"]),
            required=bool(item.get("required", True)),
            status=str(item["status"]),
            metadata=dict(item.get("metadata") or {}),
        )
        for item in bundle.get("questions", [])
    )
    return Service1QuestionBundleV1(
        schema_version=str(bundle["schema_version"]),
        service_name=str(bundle["service_name"]),
        case_id=str(bundle["case_id"]),
        tenant_id=str(bundle["tenant_id"]),
        intake_id=str(bundle["intake_id"]),
        run_id=str(bundle["run_id"]),
        questions=questions,
        selected_next_question_ref=bundle.get("selected_next_question_ref"),
        runtime_authorized=bool(bundle.get("runtime_authorized", False)),
        owner_confirmation_required=bool(
            bundle.get("owner_confirmation_required", bundle.get("human_review_required", True))
        ),
        created_at=str(bundle["created_at"]),
        metadata=dict(bundle.get("metadata") or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "BRIDGE_STATUS_ACCEPTED_AND_PROJECTED",
    "BRIDGE_STATUS_BLOCKED_REENTRY",
    "BRIDGE_STATUS_BLOCKED_PERSISTENCE",
    "BRIDGE_STATUS_BLOCKED_PROJECTION",
    "Service1OwnerReentryBridgeV1",
    "run_service_1_owner_reentry_bridge_v1",
]
