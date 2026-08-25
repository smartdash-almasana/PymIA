# Prompt Codex — Servicio 1 — R4 Verify V2

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Sesión y precondición

Ejecutar en una **nueva sesión separada de Codex**, después de la sesión de implementación. Leer primero:

`docs/current/evidence/SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md`

Continuar sólo si contiene `IMPLEMENTATION_VERDICT: PASS`. Si no, detenerse como `STOP_IMPLEMENTATION_NOT_PASS`.

Leer únicamente el contrato mínimo necesario: sección R4 de `SERVICE_1_RECONSTRUCTION_PLAN_V1.md`, `SERVICE_1_CANONICAL_AXIS.md`, `SERVICE_1_ARCHITECTURE_LOCK.md`, `SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`, el diff R4 y los tests relevantes.

## Rol read-only

Desde el inicio de la verificación:

- no modificar runtime, tests ni arquitectura;
- no corregir findings;
- preservar `_audit/` y cambios preexistentes;
- no full suite, Playwright, smoke, commit, push ni deploy.

Intentar refutar el PASS de implementación mediante inspección física, búsquedas de callers/call graph y los tests focales ya definidos para R4, sin convertir la verificación en otra implementación.

## Gates R4

Comprobar físicamente los gates del plan y del contrato de completion:

```text
FOUR_EXPLICIT_EXECUTION_COMMANDS
NO_SHAPE_DISPATCH
NO_PROCEDURAL_ROOT_SWITCHES
ONE_PRODUCTIVE_EXECUTION_ROOT
NO_FIFTH_TOOL_REQUESTS_EXECUTION_PATH
CLI_WEB_ONLY_SURFACES
ZERO_PRODUCTIVE_LEGACY_ROOT_CALLERS
RESULT_READ_OUTSIDE_EXECUTION_ROOT
REQUEST_KIND_LAYER_ABSORBED_OR_NON_DISPATCH
NEW_WRAPPER = NO
NEW_ALIAS = NO
NEW_FALLBACK = NO
NEW_COMPATIBILITY_SHIM = NO
OUT_OF_SCOPE_R5_PLUS_CHANGE = NO
```

Verificar también que SEM/P7/P8/F7/F8/F9 y ResultRead conserven sus autoridades y que no se haya adelantado R5+.

## Evidencia obligatoria

Persistir únicamente:
`docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md`

Registrar precondición, archivos inspeccionados, comandos/tests observados, evidencia física por gate, findings y blockers. Terminar con:

```text
FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT
NEXT_ALLOWED_NODE: R4_5_INTEGRATION_CHECKPOINT | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

Sólo `FINAL_VERDICT: PASS` permite `NEXT_ALLOWED_NODE: R4_5_INTEGRATION_CHECKPOINT`. No reparar durante esta sesión. R5 queda bloqueado hasta que el checkpoint transversal R0–R4 cierre PASS.
