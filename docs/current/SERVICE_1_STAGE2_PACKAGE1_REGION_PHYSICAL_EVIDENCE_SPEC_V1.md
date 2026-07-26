# SERVICE_1_STAGE2_PACKAGE1_REGION_PHYSICAL_EVIDENCE_SPEC_V1

**Status:** `CLOSED_PASS`
**Stage:** `STAGE_2_PACKAGE_1`
**Product root changed:** `false`

## Scope

Package 1 establishes bounded Region and physical-evidence contracts without a second XLSX parser and without connecting them to the productive root.

## Implemented authorities

```text
Service1RegionV1
Service1ColumnPhysicalEvidenceV1
Service1RegionRelationalEvidenceV1
```

The temporary adapter consumes `normalized_tables` preserved by the existing canonical ingestion output. It never reads a workbook.

## Region V1

```text
shape = rectangular contiguous columns
rows = contiguous with optional excluded rows
multiple regions per sheet = allowed
cell areas with discontinuous columns = blocked
header rows must precede data rows
```

## Evidence separation

Column evidence contains observed profile only. Relational evidence contains deterministic identities over column sets and records evaluated rows, matching rows, coverage, tolerance and contradictions. Semantic meaning, owner answers, bindings, diagnosis and computed business results are prohibited.

## Acceptance evidence

```text
real canonical provenance preserved
multi-region sheet supported by explicit region specs
column and relational evidence separated
identity coverage and tolerance recorded
unsupported region shapes fail closed
second XLSX parser absent
productive root unchanged
temporary adapter identified
rollback = remove Package 1 modules and canonical normalized_tables projection
```

## Deletion condition

The adapter is deleted when the canonical ingestion producer emits Region and physical-evidence authorities directly and all downstream consumers use them.

## Next gate

```text
CLOSURE_VERDICT = PASS_STAGE2_PACKAGE1_REGION_PHYSICAL_EVIDENCE
NEXT_ACTION = SPECIFY_PACKAGE2_OWNER_CONFIRMATION_EVENT
IMPLEMENTATION_CHANGES_AUTHORIZED = LIMITED_TO_PACKAGE2_SPECIFICATION
```

## Audit hardening

Package 1 preserves exact XLSX `header_row_number` and `source_row_numbers` from the existing canonical parser. Relational evidence separates evaluation coverage from match ratio, validates internal count/ratio consistency, and requires all identity columns to belong to the Region.
