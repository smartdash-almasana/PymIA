# SERVICE 1 — BATCH 016 MULTISHEET PARITY REAUDIT V1

> Historical pre-implementation audit. Its gaps triggered the canonical multisheet implementation documented in `SERVICE_1_CANONICAL_MULTISHEET_INGESTION_IMPLEMENTATION_V1.md`. The preservation verdict remains in force until regression and a fresh deletion audit pass.

## Verdict

**HOLD_PRESERVE_BOTH**

The following modules must remain present:

1. `service_1_xlsx_structure_extraction_to_adapter_chain_v1.py`
2. `service_1_xlsx_structure_to_column_confirmation_v1.py`

Deletion is not technically authorized because canonical multisheet parity is not demonstrated.

## Baseline

- Repository branch: `main`
- Baseline commit: `bec4457`
- Working tree before audit: clean
- Prior full regression: `2108 passed, 1 skipped`

## Sources audited

- `pymia/smartpyme/service_1_xlsx_structure_extraction_to_adapter_chain_v1.py`
- `pymia/smartpyme/service_1_xlsx_structure_to_column_confirmation_v1.py`
- `pymia/smartpyme/service_1_xlsx_structure_v1.py`
- `pymia/smartpyme/service_1_xlsx_to_normalized_table_v1.py`
- `pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py`
- `pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`
- `pymia/smartpyme/service_1_canonical_ingestion_output_to_semantic_bridge_v1.py`
- `pymia/smartpyme/service_1_column_understanding_engine_v1.py`
- Existing focal tests for both preserved modules
- `docs/service_1_module_disposition.v1.json`

## Proven behavior of the preserved path

The preserved structure path accepts every entry in `workbook.sheets` and creates a single `ColumnConfirmationMatrix` containing entries identified by both:

- `sheet_name`
- `original_column_name`

Therefore, two sheets may both contain a column named `fecha` without losing their identity. The matrix-level understanding engine also derives co-column context separately for each sheet.

A controlled two-sheet comparison produced six entries:

- `Ventas.fecha`
- `Ventas.importe`
- `Ventas.canal`
- `Cobros.fecha`
- `Cobros.importe`
- `Cobros.medio_pago`

The repeated `fecha` and `importe` headers remained distinct because their sheet names were preserved.

## Proven behavior of canonical ingestion

The canonical XLSX reader can read a specifically named sheet when called directly, but the canonical product intake boundary does not expose a `sheet_name` selector. Its normal flow selects one default non-empty sheet. Although the product CLI accepts `--sheet-name`, that value is passed to the semantic pipeline after intake and does not select which worksheet the canonical reader loads.

The owner-question packet identifies each question by `column_name` only. It does not include `sheet_name` in the question identity.

The canonical owner-answer connector uses:

```text
{column_name: owner_meaning}
```

It blocks duplicate column names. The canonical semantic bridge then builds every matrix entry with one shared effective sheet name.

Consequently, canonical ingestion cannot currently represent both `Ventas.fecha` and `Cobros.fecha` in one governed owner-confirmation round trip.

## Parity matrix

| Capability | Preserved path | Canonical product path | Parity |
|---|---:|---:|---:|
| Read one selected sheet | Indirectly | Yes | Yes |
| Enumerate all workbook sheets | Yes | Structure metadata only | Partial |
| Build confirmation entries for all sheets | Yes | No | No |
| Preserve `sheet_name + column_name` identity | Yes | No | No |
| Allow repeated header names across sheets | Yes | No; duplicates block | No |
| Derive co-column context per sheet | Yes | No; one effective sheet | No |
| Carry samples for each sheet from the real structure reader | No | Only selected sheet | No |
| Infer types from externally supplied multisheet samples | Yes | Not through product intake | No |
| Reach canonical product execution | No | Yes | Different scope |

## Secondary gap

`service_1_xlsx_structure_v1.py` enumerates all sheets and headers but does not emit `sample_rows`. Therefore, when its real output feeds the preserved chain:

- all `sample_values` are empty;
- `inferred_type` becomes `empty`;
- sample/type enrichment is active only when another source supplies enriched `sample_rows`.

This does not remove the exclusive multisheet identity capability, but it means the preserved path is not a complete real multisheet ingestion solution.

The controlled comparison also exposed an independent Windows resource-handling gap: `read_xlsx_to_normalized_table_v1` opens the workbook but does not explicitly close it. Cleanup of the temporary XLSX raised `WinError 32` after repeated reads. This must be handled in a separate reader-hardening microcycle and is not a reason to alter either preserved module in this audit.

## Consumer audit

Neither preserved module is reachable from the canonical product root.

- `service_1_xlsx_structure_extraction_to_adapter_chain_v1` has no production caller.
- `service_1_xlsx_structure_to_column_confirmation_v1` is called only by the extraction adapter.

This proves isolation, not obsolescence. The modules retain a capability that the canonical root does not yet absorb.

## Conditions required before deletion

Deletion may be reconsidered only after one canonical path demonstrates all of the following:

1. An explicit policy for one sheet, selected sheets, or all sheets.
2. Sheet-qualified column identity throughout intake, questions, answers, evidence, and semantic binding.
3. Correct handling of identical header names in different sheets.
4. Per-sheet sample extraction and inferred data types.
5. Per-sheet co-column context in the understanding engine.
6. Owner reentry using an unambiguous sheet-qualified answer key.
7. Product/CLI round trip over a real multisheet XLSX.
8. Focal parity tests and full regression passing.
9. Zero remaining productive callers of the preserved modules.

## Decision

- Keep both modules as `EXPERIMENTAL_FROZEN`.
- Correct their registry reasons and raise audit confidence to `HIGH`.
- Do not wire either module into the product root.
- Do not delete either module.
- The next implementation front, when authorized, is canonical multisheet identity and ingestion parity—not further cleanup of these two modules.
