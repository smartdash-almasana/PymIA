# Vulture Dead-Code Baseline

## Scope

This is a report-only baseline for the `pymia/` package. It does not delete,
move, or refactor product code.

## Reproducible command

```text
vulture pymia --min-confidence 100
```

- Tool: Vulture `2.16`
- Confidence threshold: `100%`
- Scanned path: `pymia`
- Mode: `REPORT_ONLY`

The baseline report is written outside the repository at
`E:\BuenosPasos\smartbridge\PYMIA_VULTURE_BASELINE_V1.json`.

## Classification criteria

Every raw Vulture candidate is treated as a `DEAD_CODE_CANDIDATE`, not as
proof of dead code. Candidates are deduplicated by root cause and classified
only after checking imports, call sites, registries, decorators, dynamic
loading, framework entrypoints, type-only usage, `__all__`, and CLI/runtime
entrypoints. `CONFIRMED_DEAD` requires no detectable reference in any of
those categories.

The report uses these categories: `CONFIRMED_DEAD`, `TYPE_ONLY_OR_DYNAMIC`,
`FRAMEWORK_ENTRYPOINT`, `REGISTRY_OR_PLUGIN_REFERENCED`, `FALSE_POSITIVE`,
and `REQUIRES_REVIEW`.

## Why a Vulture finding is not automatically dead code

Vulture uses static analysis. Python code can be reached through imports that
are resolved dynamically, registries, decorators, framework discovery,
`__all__`, type checking, or external entrypoints that are not visible to a
single static scan. A finding therefore requires repository-context evidence
before it can be called dead code.

## Why nothing is deleted in this phase

This phase measures the current baseline only. Deleting or refactoring a
candidate would change product behavior and would make the baseline unable to
describe the pre-remediation state. Any future removal requires a separate,
scoped change with focused tests and review.
