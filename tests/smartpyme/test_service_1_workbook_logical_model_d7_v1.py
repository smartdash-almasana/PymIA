from __future__ import annotations

from pymia.smartpyme.service_1_tenant_schema_family_memory_v1 import (
    build_service_1_tenant_schema_family_memory_v1,
)
from pymia.smartpyme.service_1_workbook_logical_model_v1 import (
    STATUS_READY,
    build_service_1_workbook_logical_model_v1,
)


def _ingestion() -> dict:
    table = {
        "status": "OK",
        "source_kind": "xlsx",
        "source_path": "fixture.xlsx",
        "sheet_name": "Datos",
        "headers": ["ID", "Importe"],
        "normalized_headers": ["id", "importe"],
        "rows": [
            {"id": "A-1", "importe": "10"},
            {"id": "A-2", "importe": "20"},
            {"id": "A-3", "importe": "30"},
        ],
        "header_row_number": 1,
        "source_row_numbers": [2, 3, 4],
        "row_count": 3,
        "column_count": 2,
        "warnings": [],
        "blocking_errors": [],
        "physical_rows": [
            {"row_number": 1, "cells": ["ID", "Importe"], "physical_width": 2},
            {"row_number": 2, "cells": ["A-1", "10"], "physical_width": 2},
            {"row_number": 3, "cells": ["A-2", "20"], "physical_width": 2},
            {"row_number": 4, "cells": ["A-3", "30"], "physical_width": 2},
        ],
        "physical_max_column": 2,
        "physical_max_row": 4,
        "runtime_authorized": False,
    }
    return {
        "case_id": "case-d7",
        "source_artifact_ref": "xlsx:sha256:d7-artifact",
        "workbook_ref": "workbook:sha256:d7-workbook",
        "ingestion_scope": "first_non_empty_sheet",
        "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
        "workbook_context": {
            "case_id": "case-d7",
            "source_artifact_ref": "xlsx:sha256:d7-artifact",
            "workbook_ref": "workbook:sha256:d7-workbook",
            "ingestion_scope": "first_non_empty_sheet",
            "canonical_reader_schema_version": "SERVICE_1_XLSX_TO_NORMALIZED_TABLE_V1",
            "source_system_ref": "uploaded_bytes",
            "source_context_ref": None,
        },
        "source_kind": "uploaded_bytes",
        "filename": "fixture.xlsx",
        "source_file_ref": "sha256:d7-fixture",
        "provenance": {
            "source_kind": "uploaded_bytes",
            "source_artifact_ref": "xlsx:sha256:d7-artifact",
            "source_file_ref": "workbook:sha256:d7-workbook",
            "workbook_ref": "workbook:sha256:d7-workbook",
            "filename": "fixture.xlsx",
            "sheet_names": ["Datos"],
            "sheet_refs": [],
        },
        "normalized_tables": [table],
        "column_refs": [
            {
                "field_id": "q-id",
                "question_id": "q-id",
                "sheet_name": "Datos",
                "column_name": "ID",
                "normalized_column_name": "id",
            },
            {
                "field_id": "q-importe",
                "question_id": "q-importe",
                "sheet_name": "Datos",
                "column_name": "Importe",
                "normalized_column_name": "importe",
            },
        ],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def test_d7_composes_d1_d6_without_temporary_region_adapter() -> None:
    result = build_service_1_workbook_logical_model_v1(ingestion_output=_ingestion())

    assert result["status"] == STATUS_READY
    assert result["region_evidence"]["canonical_region_evidence"] is True
    assert "temporary_adapter" not in result["region_evidence"]
    assert result["logical_tables"]["candidate_count"] == 1
    assert result["schema_identity"]["schema_fingerprint"]
    assert result["table_scoped_semantics"]["resolved_count"] == 2
    assert result["schema_revalidation"]["revalidation_state"] == "UNKNOWN_FAMILY"
    assert result["schema_revalidation"]["tenant_context_available"] is False


def test_d7_projection_is_evidence_only_for_existing_authorities() -> None:
    result = build_service_1_workbook_logical_model_v1(ingestion_output=_ingestion())
    projection = result["p7_p8_evidence_projection"]

    assert projection["logical_table_ids"]
    assert len(projection["selected_source_bindings"]) == 2
    assert projection["schema_fingerprint"] == result["schema_identity"]["schema_fingerprint"]
    for flag in (
        "runtime_authorized",
        "tool_execution_authorized",
        "product_ready",
        "delivery_authorized",
        "diagnosis_generated",
        "grain_authorized",
        "join_execution_authorized",
        "computability_authorized",
        "automatic_reuse_authorized",
        "semantic_rebind_authorized",
    ):
        assert projection[flag] is False


def test_d7_projection_separates_owner_evidence_refs_from_historical_hint_objects() -> None:
    initial = build_service_1_workbook_logical_model_v1(ingestion_output=_ingestion())
    memory = build_service_1_tenant_schema_family_memory_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_identity=initial["schema_identity"],
        semantic_mapping_refs=[
            {
                "contract_id": "contract:importe",
                "normalized_column_ref": "importe",
            }
        ],
        relationship_evidence_refs=["relationship:historical:1"],
    )

    result = build_service_1_workbook_logical_model_v1(
        ingestion_output=_ingestion(),
        tenant_id="tenant-a",
        source_system_ref="xlsx",
        source_context_ref="gestion",
        schema_family_memory_records=[memory],
    )
    projection = result["p7_p8_evidence_projection"]

    assert result["status"] == STATUS_READY
    assert projection["owner_evidence_refs"] == ["contract:importe"]
    assert all(isinstance(ref, str) for ref in projection["owner_evidence_refs"])
    assert projection["historical_semantic_hints"][0]["contract_id"] == "contract:importe"
    assert projection["historical_relationship_evidence_refs"] == ["relationship:historical:1"]
    assert projection["historical_evidence_only"] is True


def test_d7_does_not_fallback_to_filename_for_workbook_identity() -> None:
    ingestion = _ingestion()
    ingestion.pop("workbook_context")

    result = build_service_1_workbook_logical_model_v1(ingestion_output=ingestion)

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == "WORKBOOK_CONTEXT_REQUIRED"
