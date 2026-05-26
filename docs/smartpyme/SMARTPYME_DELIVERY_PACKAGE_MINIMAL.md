# SMARTPYME_DELIVERY_PACKAGE_MINIMAL

Estado: DRAFT IMPLEMENTED

## Objetivo

Construir un `DeliveryPackage` puro para tenant a partir de:

- `MicroserviceExecutionResult`
- `ExecutionResultGateVerdict`

Sin ejecutar de nuevo, sin revalidar filesystem y sin escribir archivos.

## Archivo

- `pymia/smartpyme/delivery_package.py`

## Contrato

`DeliveryPackage`:

- `tenant_id`
- `intake_id`
- `runtime_classification`
- `output_refs`
- `summary`
- `warnings`
- `reasons`
- `gate_verdict`
- `status`: `READY_TO_DELIVER | BLOCKED | FAILED`
- `created_at`
- `to_dict()`

API pública:

- `build_delivery_package(result, verdict)`

## Reglas

- `verdict PASS` -> `READY_TO_DELIVER`
- `verdict BLOCKED` -> `BLOCKED`
- `verdict FAILED` o `UNDELIVERABLE` -> `FAILED`
- Inputs inválidos -> `ValueError`
- No muta inputs

## Restricciones

- No ejecuta microservicios.
- No importa `excel_diagnostic` ni `supplier_duplicate_check`.
- No escritura / red / DB.

## Validación

- `tests/smartpyme/test_delivery_package.py`
- `tests/smartpyme/test_execution_result_gate.py + test_delivery_package.py`
- `tests/smartpyme/test_one_microservice_smoke.py + test_execution_result_gate.py + test_delivery_package.py`
