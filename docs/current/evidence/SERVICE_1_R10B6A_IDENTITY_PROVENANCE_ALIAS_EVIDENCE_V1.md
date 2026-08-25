# Service 1 R10B6A — Canonical Identity/Provenance Alias Consumer Migration

## Scope

This slice migrates productive consumers of the transitional top-level
`CanonicalIngestionOutput` identity/provenance aliases to the canonical
`workbook_context` and `provenance` mappings.  The envelope aliases remain
emitted; their removal is explicitly deferred.

Migrated identity/provenance fields:

- `case_id`, `source_artifact_ref`, `workbook_ref`, and `ingestion_scope` from
  `workbook_context`;
- `source_file_ref`, `source_kind`, `filename`, `sheet_names`, and `sheet_refs`
  from `provenance`.

No semantic/data aliases were changed: `available_data_fields`, `columns`,
`input_values`, `normalized_values`, and `column_evidence` remain untouched.

## Consumer inventory

- Before: 11 productive runtime modules with 56 direct top-level identity /
  provenance alias reads.
- After: 0 productive runtime direct reads of those top-level aliases.
- Missing canonical identity/provenance locations fail closed in the canonical
  bridge, region evidence adapter, D2 logical-table projection, profiler, and
  derived-evidence path.  Downstream Product Root validation remains the
  canonical envelope boundary.

The static post-change scan covered `pymia/smartpyme/service_1_*.py` and found
no direct `ingestion_output[...]/get(...)` reads for the scoped top-level
identity/provenance fields.  Nested `workbook_context` / `provenance` reads
remain by design.

## Alias emission preservation

`service_1_owner_confirmation_to_canonical_ingestion_output_v1.py` continues
to emit the transitional top-level aliases in the same canonical envelope,
including the scoped identity/provenance fields and the untouched semantic/data
aliases.  No envelope field was removed in R10B6A.

## Focused verification

Command:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_canonical_ingestion_to_region_evidence_adapter_v1.py \
  tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py \
  tests/smartpyme/test_service_1_workbook_profiler_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d1_d2_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py \
  tests/smartpyme/test_service_1_logical_relationship_graph_d4_v1.py \
  tests/smartpyme/test_service_1_table_scoped_semantics_d5_v1.py \
  tests/smartpyme/test_service_1_tenant_schema_family_memory_d6_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_analysis_evidence_preparation_f7_v1.py \
  tests/smartpyme/test_service_1_derived_evidence_v1.py \
  tests/smartpyme/test_service_1_catalog_expansion_f12_v1.py \
  tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

Observed result: **218 passed, 0 failed, 362.42 seconds**.

No full suite, R11 work, commit, push, or deploy was performed.

## Worktree containment

The repository already contained unrelated R0–R10 changes and `_audit/`
artifacts.  They were preserved and not reset, checked out, staged, committed,
pushed, or deployed by this slice.
