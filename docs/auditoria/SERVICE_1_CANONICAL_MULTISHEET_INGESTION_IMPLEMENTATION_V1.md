# SERVICE 1 — CANONICAL MULTISHEET INGESTION IMPLEMENTATION V1

## Status

**IMPLEMENTED_PENDING_REGRESSION**

Canonical Servicio 1 ingestion now represents multiple workbook sheets without losing column identity. The two frozen legacy modules remain present until focal tests, the full suite, and a fresh parity audit pass.

## Baseline

- Branch: `main`
- Baseline commit: `001be79`
- Baseline full regression: `2113 passed, 1 skipped`
- Productive modules deleted in this slice: none
- Frozen modules deleted in this slice: none

## Selection policy

The canonical intake boundary now exposes four mutually exclusive modes:

1. No selection: preserve historical behavior and read the first non-empty worksheet.
2. `sheet_name`: read one explicitly named worksheet.
3. `sheet_names`: read an ordered explicit subset of worksheets.
4. `include_all_sheets=True`: read every non-empty worksheet in workbook order.

The CLI maps these modes as follows:

- no flag: historical first non-empty worksheet;
- one `--sheet-name`: one selected worksheet;
- repeated `--sheet-name`: ordered selected worksheets;
- `--all-sheets`: every non-empty worksheet.

Combining selection modes is fail-closed with `SHEET_SELECTION_CONFLICT`.

## Canonical reader

`service_1_xlsx_to_normalized_table_v1.py` now exports:

- `read_xlsx_to_normalized_table_v1`: legacy-compatible single-sheet read;
- `read_xlsx_to_normalized_tables_v1`: selected/all-sheet canonical read.

Both functions use the same parser. No second XLSX parser was introduced.

The workbook is closed in a `finally` block on every opened path, including missing-sheet and invalid-sheet outcomes. Empty worksheets are excluded only in the implicit all-sheet mode; explicitly selected empty worksheets remain blocking.

## Sheet-qualified identity

The intake packet now carries:

- `sheet_names`;
- `column_refs`;
- `normalized_tables`;
- owner questions containing `question_id`, `field_id`, `sheet_name`, `column_name`, and `normalized_column_name`.

For one worksheet, `field_id == column_name`, preserving existing answer files.

For multiple worksheets, `field_id == question_id`. Therefore identical headers such as `Ventas.fecha` and `Cobros.fecha` remain distinct without exposing an invented renamed business column.

## Owner answer contract

Single-sheet packets continue accepting:

```text
{column_name: owner_meaning}
```

Multisheet packets require:

```text
{question_id: owner_meaning}
```

Unknown keys, missing answers, duplicate answers, duplicate sheet-qualified identities, and malformed column references block before semantic processing.

## Evidence and semantic bridge

The canonical owner connector now carries one evidence record per `field_id` with:

- `sheet_name`;
- `column_name`;
- up to five sample values;
- deterministic inferred type.

The semantic bridge consumes `column_refs` and creates each `ColumnConfirmationEntry` with its real worksheet and original column name. Co-column context therefore remains scoped per sheet in the existing understanding engine.

Semantic candidates retain the canonical `field_id` and `question_id` in metadata while owner-visible column names remain unchanged.

The controlled semantic gate, owner option loop, and reinjection connector also use that canonical ID. Two ambiguous columns with the same visible name in different sheets therefore produce distinct questions, bindings, answers, and reinjected candidates.

An empty owner-column answer object is treated as a clean intake first pass: the product entrypoint returns `NEEDS_OWNER_CONFIRMATION` with the canonical sheet-qualified questions and does not invoke the connector prematurely.

## Compatibility evidence

Direct controlled checks completed before pytest:

- CASE_001 remains one sheet, 10 questions, same legacy answer keys.
- `cafeteria_abc.xlsx` remains on `Ventas`, 11 questions, unless a multisheet mode is explicitly requested.
- A synthetic `Ventas + Cobros` workbook produced:
  - 2 sheets;
  - 6 unique questions;
  - repeated `fecha` and `importe` columns preserved;
  - samples and `date/number/text` types preserved;
  - 6 sheet-qualified semantic matrix entries.
- The XLSX temporary file was removable after canonical reading on Windows.

## Fail-closed guarantees

This slice does not:

- authorize runtime, product, tools, or delivery at intake;
- infer an answer for the owner;
- merge same-named columns across sheets;
- silently include auxiliary sheets under the default mode;
- delete the preserved legacy path before parity certification.

## Regression required

Before commit and before reconsidering the two frozen modules:

1. Run the focal multisheet, reader, intake, connector, semantic bridge, product pipeline, and CLI tests.
2. Run the complete suite.
3. Verify `git diff --check`.
4. Reaudit exact behavioral parity against:
   - `service_1_xlsx_structure_extraction_to_adapter_chain_v1.py`;
   - `service_1_xlsx_structure_to_column_confirmation_v1.py`.
5. Delete those modules only if no capability remains exclusive.

## Post-regression deletion audit

After commit `247a309`, canonical multisheet ingestion passed the complete regression reported by the operator:

```text
2125 passed, 1 skipped
```

The preserved legacy multisheet structure chain was then reaudited:

- `service_1_xlsx_structure_extraction_to_adapter_chain_v1.py` had zero productive callers;
- `service_1_xlsx_structure_to_column_confirmation_v1.py` was only called by that extraction adapter;
- their exclusive multisheet identity behavior had been absorbed by the canonical intake path;
- focal deletion-registry validation is required before commit.

Deletion is now authorized for both frozen modules and their dedicated tests.
