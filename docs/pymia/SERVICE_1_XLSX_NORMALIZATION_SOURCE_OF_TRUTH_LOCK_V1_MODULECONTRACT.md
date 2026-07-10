# SERVICE_1_XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCK_V1 — ModuleContract

## VERDICT

```text
MODULE_CONTRACT_AUTHORIZED_AS_READ_ONLY_GUARD
```

## MODULE_NAME

```text
Service1XlsxNormalizationSourceOfTruthLock
```

Runtime file:

```text
PymIA-Live/pymia/smartpyme/service_1_xlsx_normalization_source_of_truth_lock_v1.py
```

Public function:

```text
build_service_1_xlsx_normalization_source_of_truth_lock_v1()
```

This document is a module contract only. It authorizes a read-only governance guard, not a runtime capability.

## RESPONSIBILITY

Verify that XLSX ingestion in `pymia.smartpyme` has a single source of truth:

- only the canonical runtime table reader (`service_1_xlsx_to_normalized_table_v1.py`)
  and the canonical structural reader (`service_1_xlsx_structure_v1.py`) may open workbooks
  via `openpyxl.load_workbook`;
- `service_1_first_aid_minimal_v1.py` must use the normalized reader, not `openpyxl`;
- the runtime bridge contract must use the normalized table reader;
- the curation pipeline must delegate through `excel_lab_ingestion_v1.py`.

The module protects against a second/parallel XLSX parser appearing in `smartpyme`.

## INPUTS_ALLOWED

| Input | Source | Required |
|---|---|---|
| `package_root` | caller or `__file__` parent | no |
| `metadata` | local passthrough only | no |

## OUTPUTS_REQUIRED

A frozen result:

```text
Service1XlsxNormalizationSourceOfTruthLockResultV1
```

Required fields include:

```text
lock_status
package_root
canonical_runtime_table_reader
canonical_structural_reader
canonical_curation_pipeline
canonical_document_ingestion_shim
allowed_load_workbook_files
detected_load_workbook_files
parallel_reader_files
runtime_bridge_reader_locked
curation_pipeline_locked
first_aid_uses_normalized_reader
runtime_authorized
delivery_authorized
product_ready
blocking_layer
blocking_reasons
```

Expected `lock_status` values:

```text
XLSX_NORMALIZATION_SOURCE_OF_TRUTH_LOCKED
XLSX_NORMALIZATION_BLOCKED_BY_PARALLEL_READER
XLSX_NORMALIZATION_BLOCKED_BY_MISSING_CANONICAL
```

## INTERNAL_FUNCTIONS_ALLOWED

```text
build_service_1_xlsx_normalization_source_of_truth_lock_v1()
_files_containing()
_read()
```

## FORBIDDEN_DEPENDENCIES

The module must not import:

```text
openpyxl
vertical_pipeline.py
storage.py
pipeline_registration.py
diagnostic_core modules
service_1_column_confirmation_applier_v1.py
service_1_column_confirmation_case_patch_v1.py
web/auth/postgres/fasthtml surfaces
external HTTP clients
external LLM SDKs
```

It must never call `load_workbook` itself; it only scans source text for the pattern.

## SAFETY_LINE_REQUIRED

Every output must preserve:

```text
runtime_authorized=False
delivery_authorized=False
product_ready=False
```

## NON_GOALS

This module must not:

```text
parse XLSX
build XLSX structures
curate workbooks
run computation
execute tools
generate diagnosis
deliver artifacts
mutate package state
```

## STOP CONDITIONS

Stop if the guard needs to:

- open or parse an XLSX;
- call runtime, delivery, or diagnostic paths;
- become a runtime capability rather than a static source-of-truth check.
