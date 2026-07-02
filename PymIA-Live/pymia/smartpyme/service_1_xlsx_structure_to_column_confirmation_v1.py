from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
import re
from typing import Any

from pymia.contracts.column_confirmation_v1 import (
    CalculationRelevance,
    ColumnConfirmationEntry,
    ColumnConfirmationMatrix,
    ConfirmationStatus,
    SemanticRectificationStatus,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    Service1ColumnConfirmationOwnerPromptBatchV1,
    build_service_1_column_confirmation_owner_prompt_batch_v1,
)

STATUS_COLUMN_CONFIRMATION_READY = "COLUMN_CONFIRMATION_READY"
STATUS_NEEDS_HEADER_REVIEW = "NEEDS_HEADER_REVIEW"
STATUS_NO_COLUMNS_DETECTED = "NO_COLUMNS_DETECTED"
UNKNOWN_SEMANTIC_ROLE = "unknown"
UNKNOWN_CONFIDENCE = "unknown"
UNKNOWN_SUGGESTED_DATA_TYPE = "unknown"
MAX_SAMPLE_VALUES_PER_COLUMN = 5
_DATE_TEXT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INTEGER_TEXT_RE = re.compile(r"^-?\d+$")
_FLOAT_TEXT_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


@dataclass(frozen=True)
class Service1XlsxStructureToColumnConfirmationResultV1:
    status: str
    file_name: str
    matrix: ColumnConfirmationMatrix
    owner_prompt_batch: Service1ColumnConfirmationOwnerPromptBatchV1
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "file_name": self.file_name,
            "matrix": self.matrix.model_dump(),
            "owner_prompt_batch": self.owner_prompt_batch.to_dict(),
            "runtime_authorized": self.runtime_authorized,
            "tool_execution_authorized": self.tool_execution_authorized,
            "delivery_authorized": self.delivery_authorized,
            "diagnosis_generated": self.diagnosis_generated,
            "metadata": dict(self.metadata),
        }


def build_service_1_xlsx_structure_to_column_confirmation_v1(
    *,
    xlsx_structure: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> Service1XlsxStructureToColumnConfirmationResultV1:
    if not isinstance(xlsx_structure, dict):
        raise ValueError("xlsx_structure must be a dict")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict or None")

    file_name = _required_text(xlsx_structure.get("file_name"), field_name="file_name")
    sheets = xlsx_structure.get("sheets")
    if not isinstance(sheets, list):
        raise ValueError("xlsx_structure.sheets must be a list")

    entries: list[ColumnConfirmationEntry] = []
    saw_headers_container = False
    saw_legible_header = False

    for index, sheet in enumerate(sheets):
        if not isinstance(sheet, dict):
            raise ValueError(f"sheets[{index}] must be a dict")

        sheet_name = _required_text(sheet.get("sheet_name"), field_name=f"sheets[{index}].sheet_name")
        raw_headers = sheet.get("headers")
        if not isinstance(raw_headers, list):
            raise ValueError(f"sheets[{index}].headers must be a list")
        saw_headers_container = True

        sample_rows = sheet.get("sample_rows", [])
        if not isinstance(sample_rows, list):
            raise ValueError(f"sheets[{index}].sample_rows must be a list")

        normalized_headers = _normalize_headers(raw_headers)
        if normalized_headers:
            saw_legible_header = True

        for column_index, header in normalized_headers:
            entries.append(
                _build_entry(
                    sheet_name=sheet_name,
                    header=header,
                    column_index=column_index,
                    sample_rows=sample_rows,
                )
            )

    status = _resolve_status(
        entries=entries,
        saw_headers_container=saw_headers_container,
        saw_legible_header=saw_legible_header,
    )
    matrix = ColumnConfirmationMatrix(file_name=file_name, entries=entries)
    batch_metadata = dict(metadata or {})
    owner_prompt_batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=matrix,
        metadata=batch_metadata,
    )

    return Service1XlsxStructureToColumnConfirmationResultV1(
        status=status,
        file_name=file_name,
        matrix=matrix,
        owner_prompt_batch=owner_prompt_batch,
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=batch_metadata,
    )


def _required_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _normalize_headers(raw_headers: list[Any]) -> list[tuple[int, str]]:
    normalized: list[tuple[int, str]] = []
    for index, value in enumerate(raw_headers):
        text = _normalize_header_text(value)
        if text is None:
            continue
        normalized.append((index, text))
    return normalized


def _normalize_header_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text


def _build_entry(
    *,
    sheet_name: str,
    header: str,
    column_index: int,
    sample_rows: list[Any],
) -> ColumnConfirmationEntry:
    sample_values = _collect_sample_values(sample_rows=sample_rows, column_index=column_index)
    inferred_type = _infer_column_type(sample_values)
    suggested_data_type = _infer_suggested_data_type(sample_values)

    return ColumnConfirmationEntry(
        original_column_name=header,
        sheet_name=sheet_name,
        sample_values=sample_values,
        inferred_type=inferred_type,
        suggested_semantic_role=UNKNOWN_SEMANTIC_ROLE,
        suggested_data_type=suggested_data_type,
        calculation_relevance=CalculationRelevance.INFORMATIONAL,
        confidence=UNKNOWN_CONFIDENCE,
        owner_question=None,
        owner_confirmed_role=None,
        owner_rectified_function=None,
        semantic_rectification_status=SemanticRectificationStatus.INFERRED_NOT_RECTIFIED,
        confirmation_status=ConfirmationStatus.PENDING_OWNER_CONFIRMATION,
    )


def _collect_sample_values(*, sample_rows: list[Any], column_index: int) -> list[Any]:
    values: list[Any] = []
    for row_index, row in enumerate(sample_rows):
        if not isinstance(row, (list, tuple)):
            raise ValueError(f"sample_rows[{row_index}] must be a list or tuple")
        if column_index >= len(row):
            continue
        value = row[column_index]
        if _is_empty_cell(value):
            continue
        values.append(value)
        if len(values) >= MAX_SAMPLE_VALUES_PER_COLUMN:
            break
    return values


def _is_empty_cell(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _infer_column_type(sample_values: list[Any]) -> str:
    if not sample_values:
        return "empty"

    value_kinds = {_classify_value_kind(value) for value in sample_values}
    if len(value_kinds) == 1:
        return next(iter(value_kinds))
    return "mixed"


def _infer_suggested_data_type(sample_values: list[Any]) -> str:
    if not sample_values:
        return UNKNOWN_SUGGESTED_DATA_TYPE

    value_kinds = [_classify_value_kind(value) for value in sample_values]
    if all(kind == "date" for kind in value_kinds):
        return "date"
    if all(kind == "number" for kind in value_kinds):
        if all(_looks_like_integer(value) for value in sample_values):
            return "int"
        return "float"
    if all(kind == "text" for kind in value_kinds):
        return "text"
    return UNKNOWN_SUGGESTED_DATA_TYPE


def _classify_value_kind(value: Any) -> str:
    if isinstance(value, datetime):
        return "date"
    if isinstance(value, date):
        return "date"
    if isinstance(value, bool):
        return "text"
    if isinstance(value, (int, float, Decimal)):
        return "number"
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return "empty"
        if _DATE_TEXT_RE.match(normalized):
            return "date"
        if _INTEGER_TEXT_RE.match(normalized) or _FLOAT_TEXT_RE.match(normalized):
            return "number"
        return "text"
    return "text"


def _looks_like_integer(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return value.is_integer()
    if isinstance(value, Decimal):
        return value == int(value)
    if isinstance(value, str):
        return bool(_INTEGER_TEXT_RE.match(value.strip()))
    return False


def _resolve_status(
    *,
    entries: list[ColumnConfirmationEntry],
    saw_headers_container: bool,
    saw_legible_header: bool,
) -> str:
    if entries:
        return STATUS_COLUMN_CONFIRMATION_READY
    if saw_headers_container and not saw_legible_header:
        return STATUS_NEEDS_HEADER_REVIEW
    return STATUS_NO_COLUMNS_DETECTED


__all__ = [
    "MAX_SAMPLE_VALUES_PER_COLUMN",
    "STATUS_COLUMN_CONFIRMATION_READY",
    "STATUS_NEEDS_HEADER_REVIEW",
    "STATUS_NO_COLUMNS_DETECTED",
    "Service1XlsxStructureToColumnConfirmationResultV1",
    "build_service_1_xlsx_structure_to_column_confirmation_v1",
]
