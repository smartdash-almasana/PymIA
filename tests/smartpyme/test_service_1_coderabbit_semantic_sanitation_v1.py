from __future__ import annotations

from types import SimpleNamespace

import pymia.smartpyme.service_1_commercial_analytics_v1 as commercial_module
import pymia.smartpyme.service_1_computability_v1 as computability_module
import pymia.smartpyme.service_1_workbook_logical_model_v1 as logical_model_module
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    _bridge_packet_with_v2_correction,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import _p6_decisions
from pymia.smartpyme.service_1_physical_region_detection_v1 import (
    STATUS_READY as PHYSICAL_REGIONS_READY,
    detect_service_1_physical_regions_v1,
)
from pymia.smartpyme.service_1_semantic_evidence_binding_contracts_v1 import (
    Service1ColumnSemanticCandidateV1,
)


def test_v2_correction_preserves_runtime_projection_fields() -> None:
    candidate = Service1ColumnSemanticCandidateV1(
        source_column_name="Cantidad",
        normalized_column_name="cantidad",
        sheet_name="Ventas",
        observed_data_type="number",
        sample_values=(1, 2),
        candidate_semantic_roles=("quantity",),
        candidate_variable_names=("volume_sold",),
        confidence=0.99,
        ambiguity_reason=None,
        owner_confirmation_required=True,
        metadata={"column_ref_id": "col-1"},
        compositional_semantic={
            "field_ref": "Ventas.Cantidad",
            "measure": "quantity",
            "runtime_semantic_role": "quantity",
            "runtime_variable_name": "volume_sold",
        },
    )

    revised = _bridge_packet_with_v2_correction(
        bridge_packet={"column_candidates": (candidate,)},
        column_ref="col-1",
        compositional_semantic={
            "field_ref": "Ventas.Cantidad",
            "measure": "count",
        },
    )

    corrected = revised["column_candidates"][0]
    assert corrected.compositional_semantic["measure"] == "count"
    assert corrected.compositional_semantic["runtime_semantic_role"] == "quantity"
    assert corrected.compositional_semantic["runtime_variable_name"] == "volume_sold"


def test_p6_rehydration_preserves_compositional_semantic_without_approved_role() -> None:
    semantic = {"field_ref": "Ventas.Cantidad", "measure": "quantity"}
    decisions = _p6_decisions(
        {
            "reentry_packet": {
                "p6_decisions": [
                    {
                        "case_id": "case-1",
                        "sheet_ref": "Ventas",
                        "column_ref": "Cantidad",
                        "status": "APPROVED",
                        "approved_role": None,
                        "approved_variable": None,
                        "reason": "OWNER_CONFIRMED_COMPOSITIONAL",
                        "confidence": 0.95,
                        "compositional_semantic": semantic,
                        "provenance": {},
                    }
                ]
            }
        },
        case_id="case-1",
    )

    assert len(decisions) == 1
    assert decisions[0].approved_role is None
    assert dict(decisions[0].compositional_semantic or {}) == semantic


def test_sparse_text_data_row_is_not_reclassified_as_header_without_separator() -> None:
    packet = detect_service_1_physical_regions_v1(
        normalized_table={
            "status": "OK",
            "sheet_name": "Ventas",
            "normalized_headers": ["producto", "categoria", "precio"],
            "physical_rows": [
                {"row_number": 1, "cells": ["Producto", "Categoria", "Precio"], "physical_width": 3},
                {"row_number": 2, "cells": ["Cafe", "Bebida", None], "physical_width": 3},
                {"row_number": 3, "cells": ["Te", "Bebida", 100], "physical_width": 3},
            ],
        }
    )

    assert packet["status"] == PHYSICAL_REGIONS_READY
    assert len(packet["region_specs"]) == 1
    region = packet["region_specs"][0]
    assert region["header_rows"] == [1]
    assert region["data_row_numbers"] == [2, 3]
    assert region["column_refs"] == ["producto", "categoria", "precio"]


def test_workbook_logical_model_accepts_partial_table_scope(monkeypatch) -> None:
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_workbook_profile_v1",
        lambda **_kwargs: {"status": logical_model_module.WORKBOOK_PROFILE_READY},
    )
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_region_evidence_from_canonical_ingestion_v1",
        lambda **_kwargs: {"status": logical_model_module.REGION_EVIDENCE_READY},
    )
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_logical_table_candidates_v1",
        lambda **_kwargs: {
            "status": logical_model_module.LOGICAL_TABLES_READY,
            "candidates": [],
        },
    )
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_workbook_schema_identity_v1",
        lambda **_kwargs: {
            "status": logical_model_module.SCHEMA_IDENTITY_READY,
            "schema_fingerprint": "fp-1",
        },
    )
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_logical_relationship_graph_v1",
        lambda **_kwargs: {
            "graph_ref": "graph-1",
            "relationships": [],
            "fanout_certificate": {},
        },
    )
    monkeypatch.setattr(
        logical_model_module,
        "build_service_1_table_scoped_semantic_context_v1",
        lambda **_kwargs: {
            "status": logical_model_module.TABLE_SCOPE_PARTIAL,
            "column_scopes": [
                {
                    "column_ref": "col-1",
                    "logical_table_ref": None,
                    "region_refs": [],
                    "grain_ref": None,
                }
            ],
        },
    )

    result = logical_model_module.build_service_1_workbook_logical_model_v1(
        ingestion_output={
            "workbook_context": {
                "case_id": "case-1",
                "source_artifact_ref": "book.xlsx",
                "workbook_ref": "book.xlsx",
                "ingestion_scope": "ALL_SHEETS",
            },
            "normalized_tables": [{"sheet_name": "Ventas"}],
            "column_refs": [{"field_id": "col-1"}],
        }
    )

    assert result["status"] == logical_model_module.STATUS_READY
    assert result["table_scoped_semantics"]["status"] == logical_model_module.TABLE_SCOPE_PARTIAL
    assert result["p7_p8_evidence_projection"]["selected_source_bindings"] == [
        {
            "column_ref": "col-1",
            "logical_table_ref": None,
            "region_refs": [],
            "grain_ref": None,
        }
    ]


def test_discount_question_reads_case_id_from_workbook_context() -> None:
    question = commercial_module._discount_question(
        {"workbook_context": {"case_id": "case-42"}},
        {
            "discount_candidate": [
                commercial_module.RoleRefV1(
                    "discount_candidate",
                    "Ventas",
                    "Descuento",
                    "descuento",
                    0.99,
                )
            ]
        },
    )

    assert question["case_id"] == "case-42"
    assert question["question_ref"] == "discount-unit:case-42:Ventas:Descuento"


def test_commercial_context_reuses_product_and_branch_lookup_caches(monkeypatch) -> None:
    product_calls = 0
    branch_calls = 0
    original_product_lookup = commercial_module._Context.product_lookup
    original_branch_lookup = commercial_module._Context.branch_lookup

    def _counted_product_lookup(self):
        nonlocal product_calls
        product_calls += 1
        return original_product_lookup(self)

    def _counted_branch_lookup(self):
        nonlocal branch_calls
        branch_calls += 1
        return original_branch_lookup(self)

    monkeypatch.setattr(commercial_module._Context, "product_lookup", _counted_product_lookup)
    monkeypatch.setattr(commercial_module._Context, "branch_lookup", _counted_branch_lookup)

    ingestion = {
        "normalized_tables": [
            {"sheet_name": "Ventas", "rows": [{"product_id": "p1", "branch_id": "b1", "sales_amount": 10}]},
            {"sheet_name": "Productos", "rows": [{"product_id": "p1", "product_name": "Café"}]},
            {"sheet_name": "Sucursales", "rows": [{"branch_id": "b1", "branch_name": "Centro"}]},
        ]
    }
    inventory = {
        "sales_amount": [commercial_module.RoleRefV1("sales_amount", "Ventas", "sales_amount", "sales_amount", 1.0)],
        "product_identifier": [
            commercial_module.RoleRefV1("product_identifier", "Ventas", "product_id", "product_id", 1.0),
            commercial_module.RoleRefV1("product_identifier", "Productos", "product_id", "product_id", 1.0),
        ],
        "product_name": [commercial_module.RoleRefV1("product_name", "Productos", "product_name", "product_name", 1.0)],
        "branch_identifier": [
            commercial_module.RoleRefV1("branch_identifier", "Ventas", "branch_id", "branch_id", 1.0),
            commercial_module.RoleRefV1("branch_identifier", "Sucursales", "branch_id", "branch_id", 1.0),
        ],
        "branch_name": [commercial_module.RoleRefV1("branch_name", "Sucursales", "branch_name", "branch_name", 1.0)],
    }

    ctx = commercial_module._Context(ingestion, inventory, None)
    sale = ctx.sales_rows[0]

    assert ctx.product_label(sale) == "Café"
    assert ctx.product_label(sale) == "Café"
    assert ctx.branch_label(sale) == "Centro"
    assert ctx.branch_label(sale) == "Centro"
    assert product_calls == 1
    assert branch_calls == 1


def test_commercial_execution_returns_governed_not_computable_on_row_value_error(monkeypatch) -> None:
    monkeypatch.setattr(
        commercial_module,
        "build_tabular_p8_decision_v1",
        lambda **_kwargs: {
            "status": commercial_module.P8_COMPUTABLE,
            "capability_ref": "sales_summary",
            "reason": None,
            "owner_questions": [],
        },
    )
    monkeypatch.setattr(commercial_module, "build_role_inventory_v1", lambda _ingestion: {})

    def _raise(_ctx):
        raise ValueError("sales evidence is not computable")

    monkeypatch.setattr(commercial_module, "_sales_summary", _raise)

    result = commercial_module.execute_commercial_analysis_v1(
        ingestion_output={"normalized_tables": []},
        capability_ref="sales_summary",
    )

    assert result["status"] == commercial_module.P8_NOT_COMPUTABLE
    assert result["p8_decision"]["reason"] == "ROW_LEVEL_EVIDENCE_NOT_COMPUTABLE"
    assert result["limitations"] == ["sales evidence is not computable"]
    assert result["runtime_authorized"] is False


def test_catalog_formula_drift_ignores_unspecified_pathology() -> None:
    formula = SimpleNamespace(
        formula_id="formula-1",
        pathology_code="PATH-1",
        expression="a-b",
        required_variables=("a", "b"),
        metadata={"output_unit": "currency"},
    )
    rule = {
        "formula_id": "formula-1",
        "pathology_code": None,
        "expression": "a-b",
        "required_inputs": ["a", "b"],
        "output_unit": "currency",
    }

    assert computability_module._catalog_formula_drift(rule, formula) is None


def test_catalog_formula_drift_still_checks_explicit_pathology() -> None:
    formula = SimpleNamespace(
        formula_id="formula-1",
        pathology_code="PATH-A",
        expression="a-b",
        required_variables=("a", "b"),
        metadata={"output_unit": "currency"},
    )
    rule = {
        "formula_id": "formula-1",
        "pathology_code": "PATH-B",
        "expression": "a-b",
        "required_inputs": ["a", "b"],
        "output_unit": "currency",
    }

    assert computability_module._catalog_formula_drift(rule, formula) == (
        "FORMULA_RULES_CATALOG_DRIFT:formula-1:pathology_code"
    )
