# SMARTPYME_RUNTIME_BRIDGE_MINIMAL

Estado: DRAFT IMPLEMENTED

## Propósito

Traducir `AnalysisReadinessResult` a un `RuntimeExecutionCandidate` para un despacho futuro.

Este slice no ejecuta runtime, no despacha jobs y no importa módulos de análisis.

## Archivo

- `pymia/smartpyme/runtime_bridge.py`

## API

- `prepare_runtime_execution(readiness_result)`
- `RuntimeExecutionCandidate`

## Estados del candidato

- `READY_TO_EXECUTE`
- `BLOCKED`
- `UNSUPPORTED`

## Reglas

1. Si `readiness.status != READY_FOR_ANALYSIS` => `BLOCKED`.
2. Si `readiness.can_execute == False` => `BLOCKED`.
3. Si `runtime_classification` no está soportada => `UNSUPPORTED`.
4. Si todo está OK => `READY_TO_EXECUTE` con `can_dispatch=True`.

## Runtime classification soportadas

- `excel_diagnostic` -> `excel_diagnostic_worker`
- `supplier_duplicate_check` -> `supplier_duplicate_check_worker`

## Guardrails

- No importa ni llama `excel_diagnostic`.
- No importa ni llama `supplier_duplicate_check`.
- No abre archivos ni ejecuta procesos.
- No modifica estado persistido.

## Validación mínima

- `tests/smartpyme/test_runtime_bridge.py`
- `tests/smartpyme/test_readiness.py + test_runtime_bridge.py`
- `tests/smartpyme/test_e2e_non_executing_flow.py + test_runtime_bridge.py`
