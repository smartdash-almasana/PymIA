# Prompt Codex — Servicio 1 — R4.5 Repair stale CLI test V1

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`
**Rol:** reparación focal de una incompatibilidad de test detectada por R4.5.

## Precondición

Leer:

`docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1.md`

Continuar sólo si registra simultáneamente:

```text
FINAL_VERDICT: FAIL_INTEGRATION_CHECKPOINT
FIRST_FAILURE: test_cli_does_not_mutate_canonical_envelope_after_build
unexpected keyword argument 'tool_requests'
```

Si no coincide, detenerse con `STOP_PRECONDITION_MISMATCH`.

## Alcance estricto

Modificar únicamente:

`tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py`

No modificar runtime, contratos, arquitectura, otros tests ni documentación normativa.

El fallo es una incompatibilidad del test con el contrato R4 ya verificado. El runtime productivo no debe recuperar `tool_requests`, kwargs legacy ni wrappers de compatibilidad.

## Objetivo del test

Preservar exactamente la intención original de:

`test_cli_does_not_mutate_canonical_envelope_after_build`

La prueba debe demostrar con el contrato R4 vigente que:

1. el canonical ingestion envelope construido por el connector llega al Product Root sin mutación post-build;
2. el objeto `ingestion_output` recibido dentro del request explícito es el mismo objeto sentinel construido por el connector;
3. `normalized_tables` conserva el sentinel sin reinyección/copia/modificación por CLI;
4. el CLI usa el request explícito R4 y dependencies separadas;
5. no reaparece `tool_requests`, shape dispatch, wrapper, alias, fallback o compatibility shim.

Para `semantic_owner_answers=None`, capturar el `request` explícito que el CLI pasa a `run_service_1_product_pipeline_v1(request, dependencies=...)` y verificar el envelope a través de ese request. No volver a probar la firma antigua.

## Reglas

- No cambiar el nombre ni reducir la fuerza semántica del test.
- No borrar assertions de inmutabilidad para hacerlo pasar.
- No alterar el CLI para satisfacer el test viejo.
- No adelantar R5.
- No full suite.
- No commit, push ni deploy.
- Preservar worktree y `_audit/`.

## Validación

Primero:

```bash
python -m pytest -q tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py::test_cli_does_not_mutate_canonical_envelope_after_build
```

Si PASS, ejecutar el archivo focal completo:

```bash
python -m pytest -q tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
```

También:

```bash
git diff --check -- tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
```

No ejecutar todavía el checkpoint R4.5 combinado; eso corresponde a una sesión separada posterior.

## Evidencia

Persistir:

`docs/current/evidence/SERVICE_1_R4_5_STALE_CLI_TEST_REPAIR_V1.md`

Formato mínimo:

```text
REPAIR_SCOPE: R4_5_STALE_CLI_TEST_ONLY
HEAD:
BRANCH:
PRECONDITION_MATCHED: YES | NO

FILES_CHANGED:
- ...

RUNTIME_CHANGED: NO
OTHER_TESTS_CHANGED: NO
LEGACY_TOOL_REQUESTS_REINTRODUCED: NO
TEST_INTENT_PRESERVED: YES | NO
EXPLICIT_R4_REQUEST_CAPTURED: YES | NO
SAME_CANONICAL_ENVELOPE_OBJECT_PROVEN: YES | NO
NORMALIZED_TABLES_SENTINEL_PRESERVED: YES | NO

TESTS_RUN:
- ...
TEST_RESULTS:

REPAIR_VERDICT: PASS | FAIL | BLOCKED
NEXT_ALLOWED_ACTION: R4_5_INTEGRATION_CHECKPOINT_RETRY | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

Sólo `REPAIR_VERDICT: PASS` habilita el retry del checkpoint R4.5.
