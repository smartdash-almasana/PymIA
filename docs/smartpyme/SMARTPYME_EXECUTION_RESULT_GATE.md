# SMARTPYME_EXECUTION_RESULT_GATE

Estado: DRAFT IMPLEMENTED

## Objetivo

Validar de forma determinística si un `MicroserviceExecutionResult` ejecutado
es útil, trazable y entregable.

## Archivo

- `pymia/smartpyme/execution_result_gate.py`

## Contrato

`ExecutionResultGateVerdict`:

- `verdict`: `PASS | BLOCKED | FAILED | UNDELIVERABLE`
- `reasons`: lista de motivos
- `warnings`: warnings propagados
- `to_dict()`

API pública:

- `validate_execution_result(result)`

## Reglas

- `status == BLOCKED` -> `BLOCKED`
- `status == FAILED` -> `FAILED`
- `status == UNSUPPORTED` -> `BLOCKED`
- `status != EXECUTED` -> `UNDELIVERABLE`
- `tenant_id` vacío -> `UNDELIVERABLE`
- `intake_id` vacío -> `UNDELIVERABLE`
- `runtime_classification` vacío -> `UNDELIVERABLE`
- `output_refs` vacío -> `UNDELIVERABLE`
- `output_ref` local inexistente -> `UNDELIVERABLE`
- `findings_count < 0` -> `UNDELIVERABLE`
- `raw_result` vacío -> `UNDELIVERABLE`
- `raw_result` no serializable -> `UNDELIVERABLE`
- `warnings` se propagan y no bloquean
- todo válido -> `PASS`

## Restricciones

- Gate puro: sin escritura, sin red, sin DB.
- No crea CLI ni jobs.
- No importa `excel_diagnostic` ni `supplier_duplicate_check`.

## Validación

- `tests/smartpyme/test_execution_result_gate.py`
- `tests/smartpyme/test_one_microservice_smoke.py + test_execution_result_gate.py`
- `tests/smartpyme/test_runtime_bridge.py + test_one_microservice_smoke.py + test_execution_result_gate.py`
