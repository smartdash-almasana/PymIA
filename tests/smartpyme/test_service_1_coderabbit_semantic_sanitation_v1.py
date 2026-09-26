from __future__ import annotations

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
