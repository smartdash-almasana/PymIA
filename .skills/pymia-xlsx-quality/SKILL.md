# PymIA XLSX Quality Skill

## Purpose

Use this skill when creating, modifying, validating, or delivering XLSX artifacts for PymIA.

This skill is a tooling/QA discipline. It does not grant semantic, runtime, computation, diagnosis, or delivery authority.

## Core rules

```text
ONE_CANONICAL_XLSX_READER
NO_SECOND_RUNTIME_PARSER
NO_DERIVED_HARDCODES_WHEN_FORMULAS_ARE_REQUIRED
ZERO_VISIBLE_EXCEL_ERRORS_BEFORE_DELIVERY
VERIFY_AFTER_SAVE
FAIL_CLOSED_ON_CORRUPT_XLSX
PRESERVE_PROVENANCE
```

## Required workflow

1. Build or modify the workbook using the existing PymIA delivery/Excel authority for the task.
2. Save the XLSX.
3. Run the PymIA XLSX quality gate.
4. Verify ZIP/package integrity and workbook readability.
5. Verify expected worksheets when the delivery contract defines them.
6. Inspect formulas and formula-error values.
7. Reject workbook artifacts that expose Excel error tokens such as `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#NUM!`, `#NULL!`, or `#N/A`.
8. Record QA evidence separately from business computation evidence.
9. If visual QA is needed, use an external inspector only as a P10 laboratory tool; it must never become an ingestion or semantic authority.

## Formula discipline

When a workbook intentionally contains formulas:

```text
source values -> explicit cells
assumptions -> explicit cells
formula -> formula cell
result -> recalculated/verified output
```

Do not replace a required derived formula with a hardcoded computed result merely to make a workbook look correct.

For Service 1 deterministic delivery artifacts that intentionally contain no formulas, preserve that property and verify it explicitly.

## Adversarial workbook cases

Use representative cases inspired by spreadsheet-agent benchmarks:

```text
multi-sheet workbook
empty cells
merged headers
unexpected header row
formula cells
cached formula errors
broken references
cross-sheet references
hidden sheets
very wide sheets
very tall sheets
weird but valid workbook names
corrupt ZIP/package
```

The canonical reader remains the system under test. Do not introduce a benchmark parser as a runtime dependency.

## External tools policy

### negokaz/excel-mcp-server

Allowed only for isolated QA experiments such as:

```text
sheet inspection
formula inspection
style inspection
Windows Excel screen capture
live workbook review
```

Forbidden uses:

```text
canonical ingestion
semantic hypothesis authority
P6/P7/P8 decisions
runtime execution authorization
business computation authority
```

### BenchFlow SkillsBench / xlsx skills

Use as a source of workflow patterns and adversarial test ideas. Do not import its parser as a second productive XLSX path.

### XSpreadsheet MCP and generic Excel agents

Do not integrate by default. Evaluate only if a concrete QA capability is missing from the chosen inspector stack.

## Quality gate

Canonical local quality gate:

```text
pymia.smartpyme.service_1_xlsx_quality_gate_v1
```

Expected outcome before delivery:

```text
verdict = PASS
zip_integrity = true
workbook_readable = true
missing_expected_sheets = []
excel_error_cells = []
```

## Separation of truth

```text
Business result != XLSX QA result
```

The QA gate proves that the artifact is structurally safe to deliver. It does not prove that the business interpretation, formula selection, or diagnosis is correct; those remain governed by P6/P7/P8 and deterministic execution.
