from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    OwnerColumnConfirmationAnswer,
    OwnerColumnConfirmationOutcome,
    infer_calculation_relevance,
)

SCHEMA_VERSION = "SERVICE_1_COLUMN_CONFIRMATION_CLASSIFIER_V1"
SERVICE_NAME = "SERVICE_1"

TARGET_REF_PREFIX_FILE = "file"
TARGET_REF_PREFIX_SHEET = "sheet"
TARGET_REF_PREFIX_COLUMN = "column"

OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED = "DECLARED_NOT_VALIDATED"

_RECTIFIED_FUNCTION_ALIASES: tuple[tuple[str, str], ...] = (
    ("saldo pendiente", "saldo"),
    ("saldo", "saldo"),
    ("medio de pago", "payment_method"),
    ("forma de pago", "payment_method"),
    ("metodo de pago", "payment_method"),
    ("método de pago", "payment_method"),
    ("total de la venta", "venta_total"),
    ("total vendido", "venta_total"),
    ("importe vendido", "venta_total"),
    ("venta total", "venta_total"),
    ("cantidad vendida", "cantidad"),
    ("cantidad", "cantidad"),
    ("producto", "producto"),
)


@dataclass(frozen=True)
class ColumnConfirmationTargetRefV1:
    file_name: str
    sheet_name: str
    column_name: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnConfirmationClassificationV1:
    schema_version: str
    service_name: str
    target_ref: str
    parsed_target_ref: ColumnConfirmationTargetRefV1
    owner_column_confirmation_answer: OwnerColumnConfirmationAnswer
    runtime_authorized: bool
    owner_confirmation_required: bool
    reexecution_authorized: bool
    recalculation_authorized: bool
    owner_answer_validation_status: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["owner_column_confirmation_answer"] = self.owner_column_confirmation_answer.model_dump()
        return data

    @property
    def human_review_required(self) -> bool:
        return self.owner_confirmation_required


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _optional_text(value: str | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value).strip()
    return value.strip()


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_column_target_ref(target_ref: str) -> ColumnConfirmationTargetRefV1:
    """Parse file:{file}:sheet:{sheet}:column:{column} target refs.

    The parser is intentionally strict about segment labels, but allows ':' inside
    file, sheet, or column values by searching for the required delimiters.
    """

    target_ref = _required_text(target_ref, field_name="target_ref")
    file_prefix = f"{TARGET_REF_PREFIX_FILE}:"
    sheet_marker = f":{TARGET_REF_PREFIX_SHEET}:"
    column_marker = f":{TARGET_REF_PREFIX_COLUMN}:"

    if not target_ref.startswith(file_prefix):
        raise ValueError("target_ref must start with file:")
    if sheet_marker not in target_ref or column_marker not in target_ref:
        raise ValueError("target_ref must contain :sheet: and :column: segments")

    file_start = len(file_prefix)
    sheet_start = target_ref.index(sheet_marker)
    column_start = target_ref.index(column_marker, sheet_start + len(sheet_marker))

    file_name = target_ref[file_start:sheet_start].strip()
    sheet_name = target_ref[sheet_start + len(sheet_marker):column_start].strip()
    column_name = target_ref[column_start + len(column_marker):].strip()

    if not file_name or not sheet_name or not column_name:
        raise ValueError("target_ref file_name, sheet_name, and column_name are required")

    return ColumnConfirmationTargetRefV1(
        file_name=file_name,
        sheet_name=sheet_name,
        column_name=column_name,
    )


def _has_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _extract_rectified_role(raw_owner_answer: str) -> str | None:
    normalized = _normalize_text(raw_owner_answer)
    if not normalized.startswith("tu respuesta"):
        return None

    patterns = (
        r"tu respuesta:\s*(?:esa columna\s+)?(?:es|significa|corresponde a|representa)\s+(.*?)(?:,?\s+no\b|$)",
        r"tu respuesta:\s*(.*?)(?:,?\s+no\b|$)",
    )
    candidate = ""
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            candidate = match.group(1).strip(" .,:;")
            break

    if not candidate:
        return None

    candidate = re.sub(r"^(el|la|los|las|un|una)\s+", "", candidate).strip()

    for alias, role in sorted(_RECTIFIED_FUNCTION_ALIASES, key=lambda item: len(item[0]), reverse=True):
        if alias == candidate or alias in candidate:
            return role
    return None


def _classify_outcome(raw_owner_answer: str, proposed_role: str) -> tuple[OwnerColumnConfirmationOutcome, str | None, str]:
    normalized = _normalize_text(raw_owner_answer)
    rectified_role = _extract_rectified_role(raw_owner_answer)
    if rectified_role:
        relevance = infer_calculation_relevance(rectified_role)
        if relevance.value == "INFORMATIONAL":
            outcome = OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL
        else:
            outcome = OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL
        return (
            outcome,
            rectified_role,
            "Owner supplied a normalizable corrected semantic function.",
        )
    if normalized.startswith("tu respuesta"):
        return (
            OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
            None,
            "Owner provided a correction, but it is not normalizable safely.",
        )

    if normalized == "no":
        return (
            OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
            None,
            "Owner rejected PymIA's proposed column interpretation.",
        )
    if len(normalized) < 3:
        return (
            OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
            None,
            "Owner answer is too short to classify safely.",
        )

    ambiguous_phrases = (
        "creo",
        "quizas",
        "quiza",
        "tal vez",
        "puede ser",
        "podria",
        "mas o menos",
        "no se",
        "no estoy seguro",
        "no estoy segura",
        "duda",
        "dudoso",
        "maybe",
        "not sure",
        "i think",
    )
    if "?" in raw_owner_answer or _has_phrase(normalized, ambiguous_phrases):
        return (
            OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
            None,
            "Owner answer is ambiguous and must remain blocked for human review.",
        )

    not_relevant_phrases = (
        "ignorar",
        "ignora",
        "no relevante",
        "no sirve",
        "no usar",
        "descartar",
        "irrelevante",
        "not relevant",
        "ignore",
        "discard",
    )
    if _has_phrase(normalized, not_relevant_phrases):
        return (
            OwnerColumnConfirmationOutcome.CONFIRMED_NOT_RELEVANT,
            None,
            "Owner explicitly marked the column as not relevant for this analysis.",
        )

    explicit_rejection_phrases = (
        "no",
        "no es",
        "no,",
        "no ",
        "no corresponde",
        "no es eso",
        "esta mal clasificada",
        "esta mal interpretada",
        "esta mal",
        "incorrecto",
        "rechazo",
        "esta equivocado",
        "wrong",
        "incorrect",
        "nope",
    )
    if normalized == "no" or _has_phrase(normalized, explicit_rejection_phrases):
        return (
            OwnerColumnConfirmationOutcome.OWNER_REJECTED_MAPPING,
            None,
            "Owner rejected PymIA's proposed column interpretation.",
        )

    confirmation_phrases = (
        "si",
        "si es",
        "sí",
        "correcto",
        "confirmo",
        "confirmado",
        "exacto",
        "tal cual",
        "es correcto",
        "corresponde",
        "yes",
        "correct",
        "confirmed",
        "right",
    )
    if normalized in confirmation_phrases or _has_phrase(normalized, confirmation_phrases):
        if proposed_role and proposed_role != "unknown":
            relevance = infer_calculation_relevance(proposed_role)
            if relevance.value == "INFORMATIONAL":
                outcome = OwnerColumnConfirmationOutcome.CONFIRMED_INFORMATIONAL
            else:
                outcome = OwnerColumnConfirmationOutcome.CONFIRMED_COMPUTATIONAL
            return (
                outcome,
                proposed_role,
                "Owner explicitly confirmed the proposed column role.",
            )
        return (
            OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
            None,
            "Owner confirmed, but proposed_role is unknown; human review is still required.",
        )

    return (
        OwnerColumnConfirmationOutcome.INSUFFICIENT_ANSWER,
        None,
        "Owner answer does not contain an explicit safe confirmation or rejection.",
    )


def classify_owner_column_confirmation_answer(
    *,
    raw_owner_answer: str,
    question_target_ref: str,
    proposed_role: str | None = None,
    suggested_semantic_role: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Service1ColumnConfirmationClassificationV1:
    """Classify raw owner text into an OwnerColumnConfirmationAnswer.

    This function does not apply the answer to a ColumnConfirmationMatrix, does not
    persist anything, does not authorize runtime execution, and does not validate
    the owner text as evidence.
    """

    raw_owner_answer = _required_text(raw_owner_answer, field_name="raw_owner_answer")
    target = parse_column_target_ref(question_target_ref)
    role = _optional_text(proposed_role) or _optional_text(suggested_semantic_role) or "unknown"

    outcome, confirmed_role, reason = _classify_outcome(raw_owner_answer, role)

    answer = OwnerColumnConfirmationAnswer(
        sheet_name=target.sheet_name,
        column_name=target.column_name,
        owner_answer_text=raw_owner_answer,
        proposed_role=role,
        confirmed_role=confirmed_role,
        outcome=outcome,
        unblocks_variable_names=[],
        reason=reason,
    )

    return Service1ColumnConfirmationClassificationV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        target_ref=question_target_ref,
        parsed_target_ref=target,
        owner_column_confirmation_answer=answer,
        runtime_authorized=False,
        owner_confirmation_required=True,
        reexecution_authorized=False,
        recalculation_authorized=False,
        owner_answer_validation_status=OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED,
        created_at=_now_iso(),
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "OWNER_ANSWER_VALIDATION_STATUS_DECLARED_NOT_VALIDATED",
    "ColumnConfirmationTargetRefV1",
    "Service1ColumnConfirmationClassificationV1",
    "parse_column_target_ref",
    "classify_owner_column_confirmation_answer",
]
