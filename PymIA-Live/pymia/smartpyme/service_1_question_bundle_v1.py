from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "SERVICE_1_QUESTION_BUNDLE_V1"
SERVICE_NAME = "SERVICE_1"

QUESTION_STATUS_PENDING = "PENDING"
QUESTION_STATUS_ANSWERED = "ANSWERED"
QUESTION_STATUS_SUPERSEDED = "SUPERSEDED"

ALLOWED_QUESTION_STATUSES = (
    QUESTION_STATUS_PENDING,
    QUESTION_STATUS_ANSWERED,
    QUESTION_STATUS_SUPERSEDED,
)

SOURCE_OWNER_QUESTION = "owner_question"
SOURCE_NEXT_QUESTIONS = "next_questions"
SOURCE_CATALOG_RECONCILIATION = "catalog_reconciliation"
SOURCE_COLUMN_CONFIRMATION = "column_confirmation_matrix"

ANSWER_TYPE_FREE_TEXT = "free_text"
ANSWER_TYPE_CONFIRM_COLUMN_ROLE = "confirm_column_role"
ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE = "provide_missing_evidence"

ALLOWED_ANSWER_TYPES = (
    ANSWER_TYPE_FREE_TEXT,
    ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
    ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE,
)


@dataclass(frozen=True)
class Service1QuestionV1:
    question_ref: str
    source: str
    text: str
    target_ref: str
    answer_type: str
    required: bool = True
    status: str = QUESTION_STATUS_PENDING
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1QuestionBundleV1:
    schema_version: str
    service_name: str
    case_id: str
    tenant_id: str
    intake_id: str
    run_id: str
    questions: tuple[Service1QuestionV1, ...]
    selected_next_question_ref: str | None
    runtime_authorized: bool
    human_review_required: bool
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["questions"] = [question.to_dict() for question in self.questions]
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _slug(value: Any) -> str:
    text = _as_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def build_stable_question_ref(*, source: str, target_ref: str, text: str) -> str:
    """Build a deterministic question reference for answer binding."""

    clean_source = _slug(source)
    clean_target = _slug(target_ref)
    if clean_target != "unknown":
        return f"service_1:{clean_source}:{clean_target}"
    return f"service_1:{clean_source}:text_{_short_hash(_as_text(text))}"


def create_service_1_question_v1(
    *,
    source: str,
    text: str,
    target_ref: str = "",
    answer_type: str = ANSWER_TYPE_FREE_TEXT,
    required: bool = True,
    status: str = QUESTION_STATUS_PENDING,
    metadata: dict[str, Any] | None = None,
) -> Service1QuestionV1:
    source = _required_text(source, field_name="source")
    text = _required_text(text, field_name="text")
    target_ref = _as_text(target_ref)
    if answer_type not in ALLOWED_ANSWER_TYPES:
        raise ValueError(f"answer_type {answer_type!r} not in allowed: {ALLOWED_ANSWER_TYPES}")
    if status not in ALLOWED_QUESTION_STATUSES:
        raise ValueError(f"status {status!r} not in allowed: {ALLOWED_QUESTION_STATUSES}")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    return Service1QuestionV1(
        question_ref=build_stable_question_ref(source=source, target_ref=target_ref, text=text),
        source=source,
        text=text,
        target_ref=target_ref,
        answer_type=answer_type,
        required=bool(required),
        status=status,
        metadata=dict(metadata or {}),
    )


def _iter_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _extract_report_owner_question(report: dict[str, Any]) -> list[Service1QuestionV1]:
    question_text = _as_text(report.get("owner_question"))
    if not question_text:
        return []
    target_ref = _as_text(report.get("owner_question_technical_reference"))
    return [
        create_service_1_question_v1(
            source=SOURCE_OWNER_QUESTION,
            text=question_text,
            target_ref=target_ref,
            answer_type=ANSWER_TYPE_FREE_TEXT,
            metadata={"origin": "report.owner_question"},
        )
    ]


def _extract_next_questions(report: dict[str, Any]) -> list[Service1QuestionV1]:
    questions: list[Service1QuestionV1] = []
    for index, item in enumerate(_iter_list(report.get("next_questions"))):
        if isinstance(item, dict):
            text = _as_text(item.get("question") or item.get("text") or item.get("owner_question"))
            target_ref = _as_text(item.get("question_ref") or item.get("target_ref") or item.get("technical_reference"))
            metadata = {"origin": "report.next_questions", "index": index, "raw": dict(item)}
        else:
            text = _as_text(item)
            target_ref = f"next_question:{index}"
            metadata = {"origin": "report.next_questions", "index": index}
        if text:
            questions.append(
                create_service_1_question_v1(
                    source=SOURCE_NEXT_QUESTIONS,
                    text=text,
                    target_ref=target_ref,
                    answer_type=ANSWER_TYPE_FREE_TEXT,
                    metadata=metadata,
                )
            )
    return questions


def _extract_catalog_reconciliation_questions(structured_summary: dict[str, Any]) -> list[Service1QuestionV1]:
    questions: list[Service1QuestionV1] = []
    reconciliation = structured_summary.get("catalog_reconciliation")
    if isinstance(reconciliation, dict):
        entries = _iter_list(reconciliation.get("items") or reconciliation.get("entries") or reconciliation.get("formulas"))
    else:
        entries = _iter_list(reconciliation)

    for entry_index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        formula_id = _as_text(entry.get("formula_id") or entry.get("formula") or entry.get("id"))
        pathology_code = _as_text(entry.get("pathology_code") or entry.get("pathology") or entry.get("code"))
        base_target = ":".join(part for part in ("catalog", formula_id, pathology_code) if part)
        for question_index, raw_question in enumerate(_iter_list(entry.get("next_audit_questions") or entry.get("next_questions"))):
            text = _as_text(raw_question.get("question") if isinstance(raw_question, dict) else raw_question)
            if not text:
                continue
            target_ref = f"{base_target}:question:{question_index}" if base_target else f"catalog:entry:{entry_index}:question:{question_index}"
            questions.append(
                create_service_1_question_v1(
                    source=SOURCE_CATALOG_RECONCILIATION,
                    text=text,
                    target_ref=target_ref,
                    answer_type=ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE,
                    metadata={"origin": "structured_summary.catalog_reconciliation", "entry_index": entry_index, "question_index": question_index},
                )
            )
    return questions


def _extract_column_confirmation_questions(column_confirmation_matrix: Any) -> list[Service1QuestionV1]:
    if not column_confirmation_matrix:
        return []
    if hasattr(column_confirmation_matrix, "to_dict"):
        matrix = column_confirmation_matrix.to_dict()
    elif isinstance(column_confirmation_matrix, dict):
        matrix = column_confirmation_matrix
    else:
        return []

    questions: list[Service1QuestionV1] = []
    file_name = _as_text(matrix.get("file_name"))
    for index, entry in enumerate(_iter_list(matrix.get("entries"))):
        if hasattr(entry, "to_dict"):
            item = entry.to_dict()
        elif isinstance(entry, dict):
            item = entry
        else:
            continue
        text = _as_text(item.get("owner_question"))
        if not text:
            continue
        sheet_name = _as_text(item.get("sheet_name"))
        column_name = _as_text(item.get("original_column_name") or item.get("column_name"))
        target_ref = ":".join(part for part in ("file", file_name, "sheet", sheet_name, "column", column_name) if part)
        if not target_ref:
            target_ref = f"column_confirmation:entry:{index}"
        questions.append(
            create_service_1_question_v1(
                source=SOURCE_COLUMN_CONFIRMATION,
                text=text,
                target_ref=target_ref,
                answer_type=ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
                metadata={"origin": "column_confirmation_matrix.entries", "entry_index": index},
            )
        )
    return questions


def build_service_1_question_bundle_v1(
    *,
    case_id: str,
    tenant_id: str,
    intake_id: str,
    run_id: str,
    report: dict[str, Any] | None = None,
    structured_summary: dict[str, Any] | None = None,
    column_confirmation_matrix: Any | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1QuestionBundleV1:
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    report = dict(report or {})
    structured_summary = dict(structured_summary or {})
    matrix = column_confirmation_matrix
    if matrix is None:
        matrix = report.get("column_confirmation_matrix") or structured_summary.get("column_confirmation_matrix")

    candidates: list[Service1QuestionV1] = []
    candidates.extend(_extract_column_confirmation_questions(matrix))
    candidates.extend(_extract_report_owner_question(report))
    candidates.extend(_extract_next_questions(report))
    candidates.extend(_extract_catalog_reconciliation_questions(structured_summary))

    deduped: list[Service1QuestionV1] = []
    seen: set[str] = set()
    for question in candidates:
        if question.question_ref in seen:
            continue
        seen.add(question.question_ref)
        deduped.append(question)

    selected_next_question_ref = None
    for question in deduped:
        if question.status == QUESTION_STATUS_PENDING and question.required:
            selected_next_question_ref = question.question_ref
            break

    return Service1QuestionBundleV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        case_id=_required_text(case_id, field_name="case_id"),
        tenant_id=_required_text(tenant_id, field_name="tenant_id"),
        intake_id=_required_text(intake_id, field_name="intake_id"),
        run_id=_required_text(run_id, field_name="run_id"),
        questions=tuple(deduped),
        selected_next_question_ref=selected_next_question_ref,
        runtime_authorized=False,
        human_review_required=True,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "QUESTION_STATUS_PENDING",
    "QUESTION_STATUS_ANSWERED",
    "QUESTION_STATUS_SUPERSEDED",
    "ALLOWED_QUESTION_STATUSES",
    "SOURCE_OWNER_QUESTION",
    "SOURCE_NEXT_QUESTIONS",
    "SOURCE_CATALOG_RECONCILIATION",
    "SOURCE_COLUMN_CONFIRMATION",
    "ANSWER_TYPE_FREE_TEXT",
    "ANSWER_TYPE_CONFIRM_COLUMN_ROLE",
    "ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE",
    "ALLOWED_ANSWER_TYPES",
    "Service1QuestionV1",
    "Service1QuestionBundleV1",
    "build_stable_question_ref",
    "create_service_1_question_v1",
    "build_service_1_question_bundle_v1",
]
