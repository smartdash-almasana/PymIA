from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ColumnProfile:
    name: str
    index: int
    inferred_type: str
    null_pct: float
    unique_count_sample: int
    sample_values: list[Any] = field(default_factory=list)
    semantic_label: str = "unknown"
    is_ambiguous: bool = False
    ambiguity_reason: str | None = None


@dataclass(slots=True)
class SheetProfile:
    sheet_name: str
    max_row: int
    max_column: int
    merged_ranges: list[str] = field(default_factory=list)
    formula_cells_count: int = 0
    probable_header_row: int | None = None
    columns: list[ColumnProfile] = field(default_factory=list)
    empty_columns: list[str] = field(default_factory=list)
    first_useful_rows: list[dict[str, Any]] = field(default_factory=list)
    tabular_likelihood: float = 0.0
    sheet_kind: str = "auxiliary"


@dataclass(slots=True)
class ExcelProfile:
    file_name: str
    file_path: str
    sheets: list[SheetProfile]
    likely_tabular_sheets: list[str]
    likely_summary_sheets: list[str]
    likely_auxiliary_sheets: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
