# Prompt Codex — Servicio 1 — Sincronización documental posterior a R3

**Rol:** reconciliar exclusivamente documentación de estado con evidencia física ya cerrada.  
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Objetivo

Corregir la contradicción documental detectada después de R3 sin modificar runtime, tests, arquitectura normativa ni ejecutar R4.

La evidencia física ya establece:

```text
R0/R1 = CLOSED_PASS
R2 = CLOSED_PASS
R3 = CLOSED_PASS
NEXT_ALLOWED_NODE = R4
LOST_OR_REVERTED_WORK = NO
WORKTREE_PRESERVED = YES
```

El bloqueo actual es `DOCUMENTATION_STATE_STALE`, no pérdida de integridad del worktree.

## Lectura obligatoria mínima

Leer únicamente:

1. `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`
2. `docs/current/evidence/SERVICE_1_R2_CLOSURE_V1.md`
3. `docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`
4. `docs/current/evidence/SERVICE_1_R3_EXECUTE_VERIFY_EVIDENCE_V1.md`
5. `docs/current/README.md`
6. `docs/current/SERVICE_1_STATUS.md`
7. `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`
8. `docs/current/prompts/SERVICE_1_ORCHESTRATION_CHAIN_V1.md`
9. `docs/current/prompts/README.md`

No releer auditorías históricas salvo contradicción factual estrictamente necesaria.

## Cambios autorizados

Modificar únicamente documentación de estado/orquestación para que refleje la verdad física ya probada.

Archivos autorizados:

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/prompts/SERVICE_1_ORCHESTRATION_CHAIN_V1.md
docs/current/prompts/README.md
docs/current/evidence/SERVICE_1_POST_R3_STATUS_SYNC_V1.md
```

## Resultado requerido

Los tres documentos de estado deben dejar de afirmar que la reconstrucción no empezó o está simplemente pendiente.

Deben expresar de forma consistente, sin declarar certificación integral:

```text
RECONSTRUCTION_IMPLEMENTATION: IN_PROGRESS
R0_R1: CLOSED_PASS
R2: CLOSED_PASS
R3: CLOSED_PASS
NEXT_ALLOWED_NODE: R4
CURRENT_WORKTREE_INTEGRAL_CERTIFICATION: NO
FULL_SUITE_AFTER_RECONSTRUCTION: NOT_YET_RUN
REAL_WORKBOOK_E2E_AFTER_RECONSTRUCTION: NOT_YET_RUN
COMMIT_PUSH_DEPLOY: NOT_AUTHORIZED
```

Usar los nombres de campos ya existentes en cada documento cuando corresponda; no introducir duplicados innecesarios.

La redacción debe distinguir claramente:

```text
arquitectura objetivo cerrada
!= reconstrucción completa
!= certificación integral
!= release autorizado
```

No alterar ni reescribir evidencia histórica de producción/RC salvo para marcarla claramente como histórica si fuera necesario para evitar contradicción con el estado actual.

## Reglas absolutas

- NO modificar `.py`.
- NO modificar tests.
- NO implementar R4.
- NO tocar `SERVICE_1_CANONICAL_AXIS.md` ni `SERVICE_1_ARCHITECTURE_LOCK.md`.
- NO cambiar decisiones arquitectónicas.
- NO borrar evidencias R0–R3.
- NO reset/checkout/restauración masiva.
- NO full suite.
- NO commit, push ni deploy.

## Validación

Después de editar:

1. Buscar en los tres documentos de estado:
   - `NOT_STARTED_FROM_FINAL_CONTRACT`
   - `RECONSTRUCTION_IMPLEMENTATION: PENDING`
   - cualquier afirmación equivalente a que R0–R3 no comenzaron.
2. Deben quedar cero contradicciones activas con las evidencias CLOSED_PASS.
3. Confirmar que siguen presentes las afirmaciones de no certificación integral.
4. Confirmar que R4 queda como único siguiente nodo autorizado.
5. Ejecutar `git diff --check` sólo sobre los documentos tocados si la herramienta lo permite; no ejecutar tests.

## Evidencia obligatoria

Crear:

`docs/current/evidence/SERVICE_1_POST_R3_STATUS_SYNC_V1.md`

con este formato:

```text
# SERVICE_1_POST_R3_STATUS_SYNC_V1

EXECUTOR: CODEX
HEAD:
BRANCH:

VERDICT: PASS | FAIL | BLOCKED

R0_R1_STATUS: CLOSED_PASS
R2_STATUS: CLOSED_PASS
R3_STATUS: CLOSED_PASS
RECONSTRUCTION_IMPLEMENTATION: IN_PROGRESS
NEXT_ALLOWED_NODE: R4
CURRENT_WORKTREE_INTEGRAL_CERTIFICATION: NO
FULL_SUITE_AFTER_RECONSTRUCTION: NOT_YET_RUN
REAL_WORKBOOK_E2E_AFTER_RECONSTRUCTION: NOT_YET_RUN

FILES_CHANGED:
- ...

STALE_STATUS_ASSERTIONS_BEFORE:
- ...

STALE_STATUS_ASSERTIONS_AFTER:
- ...

CONTRADICTIONS_REMAINING:
- ...

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
ARCHITECTURE_CHANGED: NO
R4_IMPLEMENTED: NO
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

## Cierre

Sólo `VERDICT: PASS` si no queda contradicción activa entre `README.md`, `SERVICE_1_STATUS.md`, `SERVICE_1_CURRENT_PRODUCT_STATE_V1.md` y las evidencias R0–R3.

Si PASS, `docs/current/prompts/README.md` debe dejar como siguiente prompt autorizado:

`SERVICE_1_CODEX_R4_IMPLEMENT_V2.md`

La verificación R4 sigue reservada para una segunda sesión separada mediante:

`SERVICE_1_CODEX_R4_VERIFY_V2.md`
