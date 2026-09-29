# Import Linter baseline — NOP3-HEALTH-010

## Scope

This is a `REPORT_ONLY` baseline. Import Linter measures the current import graph;
it does not remediate or block on existing violations.

Observed top-level packages under `pymia/`:

- Present: `services`, `smartpyme`, `audit_result`, `domain`, `application`.
- Not present as top-level packages: `adapters`, `delivery`, `web`.
- Web and delivery responsibilities are represented by modules inside
  `pymia.smartpyme` and `pymia.audit_result`; they are not modeled as invented
  top-level layers.

## Contracts

`docs/quality/importlinter.ini` defines four import-expressible checks:

1. The canonical Service 1 product root does not import outer application surfaces.
2. `pymia.services` does not import application, CLI, microsaas, or product surfaces.
3. `pymia.domain` does not import higher-level runtime surfaces.
4. The `pymia` top-level package graph is checked for cycles.

The baseline evidence is written outside the repository at:

`E:\BuenosPasos\smartbridge\PYMIA_IMPORT_LINTER_BASELINE_V1.json`

## Import-only limitation

Import Linter cannot prove semantic authority, evidence sufficiency, P0–P10 state
transitions, formula authority, delivery authorization, or LLM behavior. Those
rules remain governed by the existing architecture, contracts, and tests.
