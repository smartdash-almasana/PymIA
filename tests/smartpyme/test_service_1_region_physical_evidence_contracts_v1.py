from __future__ import annotations

import pytest

from pymia.smartpyme.service_1_region_physical_evidence_contracts_v1 import (
    Service1ColumnPhysicalEvidenceV1,
    Service1RegionRelationalEvidenceV1,
    Service1RegionV1,
)


def test_region_accepts_bounded_rectangular_scope_and_remains_closed():
    value = Service1RegionV1(
        case_id="C1", file_ref="book.xlsx", workbook_ref="book.xlsx", sheet_ref="Ventas",
        region_ref="R1", header_rows=(1,), first_data_row=2, last_data_row=5,
        column_refs=("cantidad", "precio", "total"), excluded_rows=(5,),
        provenance={"source": "test"}, grain={"structural_scope": "REGION"},
    )
    assert value.region_shape == "RECTANGULAR_CONTIGUOUS_COLUMNS"
    assert value.runtime_authorized is False
    assert value.to_dict()["column_refs"] == ("cantidad", "precio", "total")


def test_region_rejects_discontinuous_shape_and_invalid_rows():
    with pytest.raises(ValueError):
        Service1RegionV1(case_id="C", file_ref="f", workbook_ref="f", sheet_ref="S", region_ref="R", header_rows=(1,), first_data_row=2, last_data_row=3, column_refs=("a",), region_shape="DISCONTIGUOUS")
    with pytest.raises(ValueError):
        Service1RegionV1(case_id="C", file_ref="f", workbook_ref="f", sheet_ref="S", region_ref="R", header_rows=(2,), first_data_row=2, last_data_row=3, column_refs=("a",))


def test_column_and_relational_evidence_are_distinct_and_closed():
    column = Service1ColumnPhysicalEvidenceV1(
        region_ref="R", column_ref="cantidad", normalized_header="cantidad", observed_data_type="number",
        sample_values=(1, 2), null_ratio=0, cardinality=2, numeric_min=1, numeric_max=2,
        negative_count=0, zero_count=0, positive_count=2, date_parseable_count=0,
        neighbor_column_refs=("precio",), provenance={"rows": [2, 3]},
    )
    relation = Service1RegionRelationalEvidenceV1(
        region_ref="R", evidence_ref="E", evidence_kind="MULTIPLICATION_EQUALS",
        participating_column_refs=("cantidad", "precio", "total"), rows_eligible=2, rows_evaluated=2,
        rows_matching=2, evaluation_coverage_ratio=1, match_ratio=1, tolerance=0.01, result="SUPPORTED",
        contradicting_rows=(), provenance={"source": "test"},
    )
    assert "candidate_semantic_roles" not in column.to_dict()
    assert relation.participating_column_refs == ("cantidad", "precio", "total")
    assert relation.delivery_authorized is False


def test_relational_contract_rejects_inconsistent_ratios():
    with pytest.raises(ValueError):
        Service1RegionRelationalEvidenceV1(
            region_ref="R", evidence_ref="E2", evidence_kind="MULTIPLICATION_EQUALS",
            participating_column_refs=("a", "b", "c"), rows_eligible=100, rows_evaluated=2,
            rows_matching=2, evaluation_coverage_ratio=1.0, match_ratio=1.0, tolerance=0.01,
            result="SUPPORTED", contradicting_rows=(), provenance={},
        )


def test_relational_contract_rejects_inconsistent_contradicting_rows():
    with pytest.raises(ValueError):
        Service1RegionRelationalEvidenceV1(
            region_ref="R", evidence_ref="E3", evidence_kind="MULTIPLICATION_EQUALS",
            participating_column_refs=("a", "b", "c"), rows_eligible=2, rows_evaluated=2,
            rows_matching=1, evaluation_coverage_ratio=1.0, match_ratio=0.5, tolerance=0.01,
            result="CONTRADICTED", contradicting_rows=(), provenance={},
        )
