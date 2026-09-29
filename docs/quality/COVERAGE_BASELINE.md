# PymIA Coverage Baseline

Status: REPORT_ONLY / NON_BLOCKING.

Purpose: measure how much of the productive Python package is exercised by the existing pytest suite before any coverage-driven remediation.

Rules:
- source target: `pymia`;
- branch coverage enabled;
- no `fail-under`;
- no automatic test generation;
- no product edits to raise the percentage during baseline;
- JSON artifact stays outside the repository by default;
- coverage is evidence, not product authority.

Runner:

```text
python scripts/quality/coverage_baseline.py
```

Default artifact:

```text
E:\BuenosPasos\smartbridge\PYMIA_COVERAGE_BASELINE_V1.json
```
