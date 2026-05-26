# SMARTPYME_ONE_MICROSERVICE_EXECUTION_SMOKE

Estado: DRAFT IMPLEMENTED

## Objetivo

Ejecutar un único microservicio real (`excel_diagnostic`) a partir de un
`RuntimeExecutionCandidate` con `status=READY_TO_EXECUTE`.

## Alcance

- Módulo: `pymia/smartpyme/microservice_dispatcher.py`
- Test smoke: `tests/smartpyme/test_one_microservice_smoke.py`

## Contrato

`MicroserviceExecutionResult` incluye:

- `tenant_id`
- `intake_id`
- `runtime_classification`
- `microservice_name`
- `status`: `EXECUTED | BLOCKED | UNSUPPORTED | FAILED`
- `output_refs`
- `findings_count`
- `raw_result`
- `executed_at`
- `warnings`

API pública:

- `dispatch_candidate(candidate, *, evidence_path, output_dir=None)`

## Reglas de despacho

1. Candidate no ready (`status != READY_TO_EXECUTE`) => `BLOCKED`.
2. `can_dispatch == False` => `BLOCKED`.
3. `runtime_classification != excel_diagnostic` => `UNSUPPORTED`.
4. Si cumple contrato, ejecuta `excel_diagnostic` y devuelve `EXECUTED`.
5. Excepciones en ejecución => `FAILED` (sin re-raise).

## Restricciones verificadas

- Importa `excel_diagnostic`.
- No importa `supplier_duplicate_check`.
- No crea runtime/CLI/job real.

## Validaciones

- Smoke de import.
- Caso READY con Excel sintético en `tmp_path`.
- Bloqueos y unsupported.
- Falla controlada por path inexistente/corrupto.
- Compatibilidad candidate dict/dataclass.
- `to_dict()` serializable y no mutación de inputs.
