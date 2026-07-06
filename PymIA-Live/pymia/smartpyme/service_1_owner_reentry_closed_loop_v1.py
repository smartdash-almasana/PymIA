from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_case_reentry_read_model_v1 import load_service_1_case_reentry_read_model_v1
from pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1 import persist_service_1_owner_answer_reentry_v1
from pymia.smartpyme.service_1_owner_answer_reentry_v1 import bind_owner_answer_for_service_1_reentry_v1
from pymia.smartpyme.service_1_question_bundle_v1 import ANSWER_TYPE_CONFIRM_COLUMN_ROLE, SERVICE_NAME, SOURCE_COLUMN_CONFIRMATION, Service1QuestionBundleV1, build_service_1_question_bundle_v1, create_service_1_question_v1
from pymia.smartpyme.service_1_reentry_projection_v1 import PROJECTION_STATUS_COMPLETE, PROJECTION_STATUS_NO_ANSWERS, PROJECTION_STATUS_NO_QUESTIONS, PROJECTION_STATUS_PARTIAL, project_service_1_reentry_v1

SCHEMA_VERSION = "SERVICE_1_OWNER_REENTRY_MINIMAL_CLOSED_LOOP_V1"
STATUS_NO_REENTRY_NEEDED = "NO_REENTRY_NEEDED"
STATUS_WAITING_OWNER_ANSWERS = "WAITING_OWNER_ANSWERS"
STATUS_PARTIAL_OWNER_ANSWERS = "PARTIAL_OWNER_ANSWERS"
STATUS_READY_FOR_OPERATOR_RERUN = "READY_FOR_OPERATOR_RERUN"
STATUS_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Service1OwnerReentryClosedLoopV1:
    schema_version: str
    service_name: str
    status: str
    case_id: str
    tenant_id: str
    intake_id: str
    source_run_id: str
    question_count: int
    answered_count: int
    pending_count: int
    persisted_answer_count: int
    question_ref_by_question_id: dict[str, str]
    confirmed_columns_patch: dict[str, Any]
    operator_rerun_required: bool
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _ids(packet: dict[str, Any]) -> tuple[str, str, str, str, str]:
    asset = packet.get("asset") if isinstance(packet.get("asset"), dict) else {}
    file_intake = packet.get("file_intake") if isinstance(packet.get("file_intake"), dict) else {}
    manifest = packet.get("case_delivery_manifest") if isinstance(packet.get("case_delivery_manifest"), dict) else {}
    asset_id = _text(asset.get("asset_id")) or "unknown"
    case_id = _text(manifest.get("case_id")) or f"case_{asset_id}"
    tenant_id = _text(packet.get("tenant_id")) or "local_operator"
    intake_id = _text(file_intake.get("file_intake_id")) or "intake_unknown"
    run_id = f"run_{asset_id}"
    filename = _text(asset.get("filename")) or "unknown.xlsx"
    return case_id, tenant_id, intake_id, run_id, filename


def _answers_by_id(owner_answers: dict[str, Any] | list[Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    raw = owner_answers.get("answers", owner_answers) if isinstance(owner_answers, dict) else owner_answers
    if isinstance(raw, dict):
        for key, value in raw.items():
            if _text(key) and _text(value):
                result[_text(key)] = _text(value)
        return result
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            question_id = _text(item.get("question_id") or item.get("question_ref"))
            answer = _text(item.get("answer") or item.get("raw_owner_answer"))
            if question_id and answer:
                result[question_id] = answer
        return result
    raise ValueError("owner_answers must be a dict or list")


def build_service_1_question_bundle_from_column_confirmation_packet_v1(*, packet: dict[str, Any]) -> tuple[Service1QuestionBundleV1, dict[str, str]]:
    column_packet = packet.get("column_confirmation_packet")
    if not isinstance(column_packet, dict):
        raise ValueError("column_confirmation_packet is required")
    case_id, tenant_id, intake_id, run_id, filename = _ids(packet)
    questions = []
    question_ref_by_question_id: dict[str, str] = {}
    for item in column_packet.get("questions", []) or []:
        if not isinstance(item, dict):
            continue
        question_id = _text(item.get("question_id"))
        sheet_name = _text(item.get("sheet_name"))
        column_name = _text(item.get("column_name"))
        text = _text(item.get("question"))
        if not question_id or not sheet_name or not column_name or not text:
            continue
        question = create_service_1_question_v1(
            source=SOURCE_COLUMN_CONFIRMATION,
            text=text,
            target_ref=f"file:{filename}:sheet:{sheet_name}:column:{column_name}",
            answer_type=ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
            metadata={"question_id": question_id, "sheet_name": sheet_name, "column_name": column_name},
        )
        questions.append(question)
        question_ref_by_question_id[question_id] = question.question_ref
    empty = build_service_1_question_bundle_v1(case_id=case_id, tenant_id=tenant_id, intake_id=intake_id, run_id=run_id)
    owner_confirmation_required = True
    bundle = Service1QuestionBundleV1(
        schema_version=empty.schema_version,
        service_name=empty.service_name,
        case_id=empty.case_id,
        tenant_id=empty.tenant_id,
        intake_id=empty.intake_id,
        run_id=empty.run_id,
        questions=tuple(questions),
        selected_next_question_ref=questions[0].question_ref if questions else None,
        runtime_authorized=False,
        owner_confirmation_required=owner_confirmation_required,
        created_at=empty.created_at,
        metadata={"origin": SCHEMA_VERSION},
    )
    return bundle, question_ref_by_question_id


def _status(status: str) -> str:
    if status == PROJECTION_STATUS_NO_QUESTIONS:
        return STATUS_NO_REENTRY_NEEDED
    if status == PROJECTION_STATUS_NO_ANSWERS:
        return STATUS_WAITING_OWNER_ANSWERS
    if status == PROJECTION_STATUS_PARTIAL:
        return STATUS_PARTIAL_OWNER_ANSWERS
    if status == PROJECTION_STATUS_COMPLETE:
        return STATUS_READY_FOR_OPERATOR_RERUN
    return STATUS_BLOCKED


def _patch_from_projection(projection: Any) -> dict[str, Any]:
    columns = []
    for item in projection.to_dict().get("answered_questions", []):
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        columns.append({
            "question_ref": item.get("question_ref"),
            "question_id": metadata.get("question_id"),
            "sheet_name": metadata.get("sheet_name"),
            "column_name": metadata.get("column_name"),
            "declared_owner_answer": item.get("latest_raw_owner_answer"),
            "validation_status": item.get("owner_answer_validation_status"),
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "patch_type": "OWNER_DECLARED_COLUMN_CONFIRMATION_PATCH",
        "status": "DECLARED_NOT_VALIDATED",
        "runtime_authorized": False,
        "owner_confirmation_required": True,
        "columns": columns,
    }


def run_service_1_owner_reentry_minimal_closed_loop_v1(*, packet: dict[str, Any], owner_answers: dict[str, Any] | list[Any], storage_dir: str | Path) -> Service1OwnerReentryClosedLoopV1:
    if not isinstance(packet, dict):
        raise ValueError("packet must be a dict")
    answers = _answers_by_id(owner_answers)
    bundle, question_ref_by_question_id = build_service_1_question_bundle_from_column_confirmation_packet_v1(packet=packet)
    storage_path = Path(storage_dir)
    persisted = 0
    for question_id, answer in answers.items():
        question_ref = question_ref_by_question_id.get(question_id, question_id)
        reentry = bind_owner_answer_for_service_1_reentry_v1(
            question_bundle=bundle,
            question_ref=question_ref,
            raw_owner_answer=answer,
            anamnesis_id=f"anamnesis_{bundle.intake_id}",
            investigation_id=f"investigation_{bundle.run_id}",
            metadata={"source": SCHEMA_VERSION, "question_id": question_id},
        )
        persistence = persist_service_1_owner_answer_reentry_v1(
            reentry_packet=reentry,
            storage_dir=storage_path,
            metadata={"source": SCHEMA_VERSION},
        )
        if persistence.status == "PERSISTED":
            persisted += 1
    read_model = load_service_1_case_reentry_read_model_v1(storage_dir=storage_path, tenant_id=bundle.tenant_id, intake_id=bundle.intake_id)
    projection = project_service_1_reentry_v1(question_bundle=bundle, read_model=read_model)
    status = _status(projection.status)
    return Service1OwnerReentryClosedLoopV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        case_id=bundle.case_id,
        tenant_id=bundle.tenant_id,
        intake_id=bundle.intake_id,
        source_run_id=bundle.run_id,
        question_count=projection.total_questions,
        answered_count=projection.answered_count,
        pending_count=projection.pending_count,
        persisted_answer_count=persisted,
        question_ref_by_question_id=question_ref_by_question_id,
        confirmed_columns_patch=_patch_from_projection(projection),
        operator_rerun_required=status == STATUS_READY_FOR_OPERATOR_RERUN,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata={"hardening_scope": "S1_FULL_ASSISTED_V1_HARDENING", "does_not_reopen_full_assisted_v1_closure": True},
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_NO_REENTRY_NEEDED",
    "STATUS_WAITING_OWNER_ANSWERS",
    "STATUS_PARTIAL_OWNER_ANSWERS",
    "STATUS_READY_FOR_OPERATOR_RERUN",
    "STATUS_BLOCKED",
    "Service1OwnerReentryClosedLoopV1",
    "build_service_1_question_bundle_from_column_confirmation_packet_v1",
    "run_service_1_owner_reentry_minimal_closed_loop_v1",
]
