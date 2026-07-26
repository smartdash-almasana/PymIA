"""Stage 2 Package 1 contracts for Region and physical evidence.

No I/O. No XLSX parsing. No semantic interpretation. No runtime, tool,
diagnosis or delivery authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Final, Literal

SCHEMA_VERSION: Final[str] = "SERVICE_1_REGION_PHYSICAL_EVIDENCE_CONTRACTS_V1"
REGION_SHAPE_RECTANGULAR: Final[str] = "RECTANGULAR_CONTIGUOUS_COLUMNS"
ALLOWED_OBSERVED_DATA_TYPES: Final[tuple[str, ...]] = ("number", "date", "text", "empty", "mixed")
ALLOWED_RELATIONAL_RESULTS: Final[tuple[str, ...]] = ("SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE")
RelationalEvidenceResultV1 = Literal["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _texts(value: Any, name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be a list or tuple")
    result = tuple(_text(item, name) for item in value)
    if len(set(result)) != len(result):
        raise ValueError(f"{name} must not contain duplicates")
    return result


def _rows(value: Any, name: str) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be a list or tuple")
    result = tuple(int(item) for item in value)
    if any(item < 1 for item in result) or len(set(result)) != len(result):
        raise ValueError(f"{name} must contain unique positive row numbers")
    return result


def _ratio(value: Any, name: str) -> float:
    number = float(value)
    if number < 0 or number > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return number


def _closed(value: bool, name: str) -> bool:
    if value is not False:
        raise ValueError(f"{name} must remain False")
    return False


@dataclass(frozen=True)
class Service1RegionV1:
    case_id: str
    file_ref: str
    workbook_ref: str
    sheet_ref: str
    region_ref: str
    header_rows: tuple[int, ...]
    first_data_row: int
    last_data_row: int
    column_refs: tuple[str, ...]
    excluded_rows: tuple[int, ...] = ()
    region_shape: str = REGION_SHAPE_RECTANGULAR
    provenance: dict[str, Any] = field(default_factory=dict)
    grain: dict[str, str] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        for name in ("case_id", "file_ref", "workbook_ref", "sheet_ref", "region_ref"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "header_rows", _rows(self.header_rows, "header_rows"))
        object.__setattr__(self, "column_refs", _texts(self.column_refs, "column_refs"))
        object.__setattr__(self, "excluded_rows", _rows(self.excluded_rows, "excluded_rows"))
        if not self.header_rows or not self.column_refs:
            raise ValueError("header_rows and column_refs must be non-empty")
        if self.region_shape != REGION_SHAPE_RECTANGULAR:
            raise ValueError("unsupported region_shape")
        if self.first_data_row < 1 or self.last_data_row < self.first_data_row:
            raise ValueError("invalid data row range")
        if max(self.header_rows) >= self.first_data_row:
            raise ValueError("header_rows must precede data rows")
        if any(row < self.first_data_row or row > self.last_data_row for row in self.excluded_rows):
            raise ValueError("excluded_rows must be inside the data range")
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        object.__setattr__(self, "grain", dict(self.grain or {}))
        for name in ("runtime_authorized", "tool_execution_authorized", "delivery_authorized", "diagnosis_generated"):
            object.__setattr__(self, name, _closed(getattr(self, name), name))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1ColumnPhysicalEvidenceV1:
    region_ref: str
    column_ref: str
    normalized_header: str
    observed_data_type: str
    sample_values: tuple[Any, ...]
    null_ratio: float
    cardinality: int
    numeric_min: float | None
    numeric_max: float | None
    negative_count: int
    zero_count: int
    positive_count: int
    date_parseable_count: int
    neighbor_column_refs: tuple[str, ...]
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        for name in ("region_ref", "column_ref", "normalized_header"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        if self.observed_data_type not in ALLOWED_OBSERVED_DATA_TYPES:
            raise ValueError("unsupported observed_data_type")
        object.__setattr__(self, "sample_values", tuple(self.sample_values or ()))
        object.__setattr__(self, "null_ratio", _ratio(self.null_ratio, "null_ratio"))
        for name in ("cardinality", "negative_count", "zero_count", "positive_count", "date_parseable_count"):
            if int(getattr(self, name)) < 0:
                raise ValueError(f"{name} must be non-negative")
            object.__setattr__(self, name, int(getattr(self, name)))
        if (self.numeric_min is None) != (self.numeric_max is None):
            raise ValueError("numeric_min and numeric_max must both be present or absent")
        if self.numeric_min is not None and float(self.numeric_min) > float(self.numeric_max):
            raise ValueError("numeric_min must not exceed numeric_max")
        object.__setattr__(self, "neighbor_column_refs", _texts(self.neighbor_column_refs, "neighbor_column_refs"))
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in ("runtime_authorized", "tool_execution_authorized", "delivery_authorized", "diagnosis_generated"):
            object.__setattr__(self, name, _closed(getattr(self, name), name))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1RegionRelationalEvidenceV1:
    region_ref: str
    evidence_ref: str
    evidence_kind: str
    participating_column_refs: tuple[str, ...]
    rows_eligible: int
    rows_evaluated: int
    rows_matching: int
    evaluation_coverage_ratio: float
    match_ratio: float
    tolerance: float
    result: RelationalEvidenceResultV1
    contradicting_rows: tuple[int, ...]
    provenance: dict[str, Any] = field(default_factory=dict)
    runtime_authorized: bool = False
    tool_execution_authorized: bool = False
    delivery_authorized: bool = False
    diagnosis_generated: bool = False

    def __post_init__(self) -> None:
        for name in ("region_ref", "evidence_ref", "evidence_kind"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "participating_column_refs", _texts(self.participating_column_refs, "participating_column_refs"))
        if len(self.participating_column_refs) < 2:
            raise ValueError("relational evidence requires at least two columns")
        eligible = int(self.rows_eligible)
        evaluated = int(self.rows_evaluated)
        matching = int(self.rows_matching)
        if eligible < 0 or evaluated < 0 or matching < 0 or evaluated > eligible or matching > evaluated:
            raise ValueError("invalid relational row counts")
        object.__setattr__(self, "rows_eligible", eligible)
        object.__setattr__(self, "rows_evaluated", evaluated)
        object.__setattr__(self, "rows_matching", matching)
        evaluation_coverage = _ratio(self.evaluation_coverage_ratio, "evaluation_coverage_ratio")
        match_ratio = _ratio(self.match_ratio, "match_ratio")
        expected_coverage = evaluated / eligible if eligible else 0.0
        expected_match = matching / evaluated if evaluated else 0.0
        if abs(evaluation_coverage - expected_coverage) > 1e-12:
            raise ValueError("evaluation_coverage_ratio inconsistent with row counts")
        if abs(match_ratio - expected_match) > 1e-12:
            raise ValueError("match_ratio inconsistent with row counts")
        object.__setattr__(self, "evaluation_coverage_ratio", evaluation_coverage)
        object.__setattr__(self, "match_ratio", match_ratio)
        if float(self.tolerance) < 0:
            raise ValueError("tolerance must be non-negative")
        object.__setattr__(self, "tolerance", float(self.tolerance))
        if self.result not in ALLOWED_RELATIONAL_RESULTS:
            raise ValueError("unsupported relational result")
        contradicting_rows = _rows(self.contradicting_rows, "contradicting_rows")
        if len(contradicting_rows) != evaluated - matching:
            raise ValueError("contradicting_rows inconsistent with row counts")
        object.__setattr__(self, "contradicting_rows", contradicting_rows)
        object.__setattr__(self, "provenance", dict(self.provenance or {}))
        for name in ("runtime_authorized", "tool_execution_authorized", "delivery_authorized", "diagnosis_generated"):
            object.__setattr__(self, name, _closed(getattr(self, name), name))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    "SCHEMA_VERSION", "REGION_SHAPE_RECTANGULAR", "Service1RegionV1",
    "Service1ColumnPhysicalEvidenceV1", "Service1RegionRelationalEvidenceV1",
]
