# Performance Baseline

## Scope

This report-only baseline measures three deterministic local boundaries:

1. `XLSX bytes -> canonical ingestion output` using the existing canonical
   intake and owner-confirmation boundary over the bytes of the real
   `la_textil_cosida_srl_mar_abr_may_2026.xlsx` workbook.
2. `canonical ingestion output -> workbook profile` using
   `build_service_1_workbook_profile_v1`.
3. `FormulaEngineService.calculate` for the representative deterministic
   `ganancia_bruta` formula.

The benchmarks exclude LLMs, external providers, Supabase, network, and UI.
They do not change product code or behavior.

## Reproduction

Install the exact quality-tool pin and run:

```text
python -m pip install -r requirements-quality.txt
python -m pytest -q -m performance
```

On this host the known `logfire/OpenTelemetry` pytest plugin conflict
requires retaining benchmark plugin loading explicitly:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
python -m pytest -q -p pytest_benchmark.plugin -m performance
```

The custom report is written outside the repository at
`E:\BuenosPasos\smartbridge\PYMIA_PERFORMANCE_BASELINE_V1.json`.

## Metrics and thresholds

`pytest-benchmark` supplies the recorded `min`, `max`, `mean`, `stddev`,
`median`, `rounds`, `iterations`, and `ops` values when available. Values in
the report are in seconds. No metric is synthesized by the test code. This
phase intentionally enables no
fail-if-slower rule, percentage threshold, or blocking performance gate.

Results from different machines, Python builds, operating-system states, or
workloads are not directly comparable. A later threshold decision requires a
stable environment and an explicit acceptance contract.

## Report-only policy

This baseline measures the current implementation only. It must not be used
to justify optimization, algorithm changes, parser changes, formula changes,
cache changes, or other product modifications in this phase.
