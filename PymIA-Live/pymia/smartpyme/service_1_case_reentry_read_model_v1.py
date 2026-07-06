from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_question_bundle_v1 import SERVICE_NAME

SCHEMA_VERSION = "SERVICE_1_CASE_REENTRY_READ_MODEL_V1"

READ_MODEL_STATUS_READY = "READY"
READ_MODEL_STATUS_EMPTY = "EMPTY"
READ_MODEL_STATUS_STORAGE_MISSING = "STORAGE_MISSING"

SERVICE_1_REENTRY_SCHEMA_METADATA_KEY = "service_1_reentry_schema_version"
OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED = "DECLARED_NOT_VALIDATED"


@dataclass(frozen=True)
class Service1ReentryAnswerViewV1:
    answer_id: str
    tenant_id: str
    intake_id: str
    anamnesis_id: str
    investigation_id: str
    question_ref: str
    raw_owner_answer: str
    answer_kind: str
    created_at: str
    case_id: str | None
    source_run_id: str | None
    question_source: str | None
    question_target_ref: str | None
    question_answer_type: str | None
    question_text: str | None
    owner_answer_validation_status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1CaseReentryReadModelV1:
    schema_version: str
    service_name: str
    status: str
    tenant_id: str
    intake_id: str
    case_id: str | None
    answers_count: int
    answered_question_refs: tuple[str, ...]
    latest_answer: Service1ReentryAnswerViewV1 | None
    answers: tuple[Service1ReentryAnswerViewV1, ...]
    storage_path: str | None
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["answered_question_refs"] = list(self.answered_question_refs)
        data["latest_answer"] = self.latest_answer.to_dict() if self.latest_answer else None
        data["answers"] = [answer.to_dict() for answer in self.answers]
        return data


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _safe_tenant_dir(storage_dir: str | Path, tenant_id: str) -> Path:
    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    if ".." in tenant_id or "/" in tenant_id or "\\" in tenant_id:
        raise ValueError("tenant_id contains invalid path traversal markers")
    base = Path(storage_dir).resolve()
    tenant_root = (base / tenant_id).resolve()
    if base not in tenant_root.parents and tenant_root != base:
        raise ValueError("resolved path escapes storage_dir")
    return tenant_root


def _empty_model(
    *,
    status: str,
    storage_dir: str | Path,
    tenant_id: str,
    intake_id: str,
    storage_path: str | None,
    metadata: dict[str, Any] | None,
) -> Service1CaseReentryReadModelV1:
    return Service1CaseReentryReadModelV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        tenant_id=_required_text(tenant_id, field_name="tenant_id"),
        intake_id=_required_text(intake_id, field_name="intake_id"),
        case_id=None,
        answers_count=0,
        answered_question_refs=(),
        latest_answer=None,
        answers=(),
        storage_path=storage_path,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata={"storage_dir": str(Path(storage_dir))} | dict(metadata or {}),
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_number}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"invalid JSONL payload at {path}:{line_number}: expected object")
            records.append(payload)
    return records


def _is_service_1_reentry_answer(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata") or {}
    if not isinstance(metadata, dict):
        return False
    return bool(metadata.get(SERVICE_1_REENTRY_SCHEMA_METADATA_KEY))


def _answer_view_from_record(record: dict[str, Any]) -> Service1ReentryAnswerViewV1:
    metadata = record.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    validation_status = metadata.get(
        "owner_answer_validation_status",
        OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED,
    )
    return Service1ReentryAnswerViewV1(
        answer_id=_required_text(record.get("answer_id", ""), field_name="answer_id"),
        tenant_id=_required_text(record.get("tenant_id", ""), field_name="tenant_id"),
        intake_id=_required_text(record.get("intake_id", ""), field_name="intake_id"),
        anamnesis_id=_required_text(record.get("anamnesis_id", ""), field_name="anamnesis_id"),
        investigation_id=_required_text(record.get("investigation_id", ""), field_name="investigation_id"),
        question_ref=_required_text(record.get("question_ref", ""), field_name="question_ref"),
        raw_owner_answer=_required_text(record.get("raw_owner_answer", ""), field_name="raw_owner_answer"),
        answer_kind=_required_text(record.get("answer_kind", ""), field_name="answer_kind"),
        created_at=_required_text(record.get("created_at", ""), field_name="created_at"),
        case_id=metadata.get("case_id"),
        source_run_id=metadata.get("source_run_id"),
        question_source=metadata.get("question_source"),
        question_target_ref=metadata.get("question_target_ref"),
        question_answer_type=metadata.get("question_answer_type"),
        question_text=metadata.get("question_text"),
        owner_answer_validation_status=str(validation_status),
        metadata=dict(metadata),
    )


def load_service_1_case_reentry_read_model_v1(
    *,
    storage_dir: str | Path,
    tenant_id: str,
    intake_id: str,
    metadata: dict[str, Any] | None = None,
) -> Service1CaseReentryReadModelV1:
    """Load persisted Servicio 1 owner-answer reentry records for a case.

    This is a pure read model over owner_answers.jsonl. It does not mutate storage,
    re-run the pipeline, recalculate evidence, or mark questions as answered.
    """

    tenant_id = _required_text(tenant_id, field_name="tenant_id")
    intake_id = _required_text(intake_id, field_name="intake_id")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    owner_answers_path = _safe_tenant_dir(storage_dir, tenant_id) / "owner_answers.jsonl"
    if not owner_answers_path.exists():
        return _empty_model(
            status=READ_MODEL_STATUS_STORAGE_MISSING,
            storage_dir=storage_dir,
            tenant_id=tenant_id,
            intake_id=intake_id,
            storage_path=str(owner_answers_path),
            metadata=metadata,
        )

    records = _read_jsonl(owner_answers_path)
    matching_records = [
        record
        for record in records
        if record.get("tenant_id") == tenant_id
        and record.get("intake_id") == intake_id
        and _is_service_1_reentry_answer(record)
    ]

    answers = tuple(_answer_view_from_record(record) for record in matching_records)
    if not answers:
        return _empty_model(
            status=READ_MODEL_STATUS_EMPTY,
            storage_dir=storage_dir,
            tenant_id=tenant_id,
            intake_id=intake_id,
            storage_path=str(owner_answers_path),
            metadata=metadata,
        )

    answered_question_refs = tuple(dict.fromkeys(answer.question_ref for answer in answers))
    latest_answer = answers[-1]
    case_id = latest_answer.case_id
    if case_id is None:
        for answer in answers:
            if answer.case_id:
                case_id = answer.case_id
                break

    return Service1CaseReentryReadModelV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=READ_MODEL_STATUS_READY,
        tenant_id=tenant_id,
        intake_id=intake_id,
        case_id=case_id,
        answers_count=len(answers),
        answered_question_refs=answered_question_refs,
        latest_answer=latest_answer,
        answers=answers,
        storage_path=str(owner_answers_path),
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        metadata={"storage_dir": str(Path(storage_dir))} | dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "READ_MODEL_STATUS_READY",
    "READ_MODEL_STATUS_EMPTY",
    "READ_MODEL_STATUS_STORAGE_MISSING",
    "SERVICE_1_REENTRY_SCHEMA_METADATA_KEY",
    "OWNER_ANSWER_VALIDATION_DECLARED_NOT_VALIDATED",
    "Service1ReentryAnswerViewV1",
    "Service1CaseReentryReadModelV1",
    "load_service_1_case_reentry_read_model_v1",
]
