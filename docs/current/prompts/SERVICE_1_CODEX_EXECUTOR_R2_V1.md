# Prompt Codex — Servicio 1 — R2 V1

**Rol:** ejecutor de reconstrucción R2.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Precondición automática

Antes de modificar código, leer:

`docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`

Sólo continuar si contiene simultáneamente:

```text
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R2
```

Si el archivo no existe, está incompleto o no contiene ambos valores:

```text
STOP_PRECONDITION
```

No modificar runtime/tests. Escribir únicamente `docs/current/evidence/SERVICE_1_R2_EXECUTION_EVIDENCE_V1.md` indicando el bloqueo.

## Lectura obligatoria

1. `AGENTS.md`
2. `ARCHITECTURE_GUARDRAILS.md`
3. `docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md`
4. `docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
5. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
6. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
7. `docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md`
8. `docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`
9. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — ejecutar exclusivamente R2
10. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
11. `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`

## Reglas

- Ejecutar exclusivamente R2.
- No adelantar R3+.
- No reabrir arquitectura.
- No crear wrappers, aliases, fallbacks o compatibility shims.
- No crear una segunda FSM ni un segundo builder de table scope.
- No full suite.
- No commit, push ni deploy.
- Preservar worktree previo y `_audit/`.

## Implementación

Seguir exactamente la sección `R2 — Table-scoped structural evidence construido una vez` de `SERVICE_1_RECONSTRUCTION_PLAN_V1.md`.

No reinterpretar el objetivo. La autoridad normativa es `SERVICE_1_CANONICAL_AXIS.md` + `SERVICE_1_ARCHITECTURE_LOCK.md`.

## Validación

Ejecutar los L0/L1/L2/L3 prescritos para R2 en el reconstruction plan.

Además comprobar físicamente el número de call paths productivos hacia `build_service_1_table_scoped_semantic_context_v1` y demostrar que el target final tiene una sola construcción de evidencia y que SEM consume el packet ya construido.

## Criterio de PASS

Sólo PASS si todos los gates R2 prescritos pasan y no aparece entropía nueva.

Ante contradicción arquitectónica no contemplada:

```text
STOP_ARCHITECTURE
```

y no inventar solución.

## Evidencia persistida obligatoria

Crear o sobrescribir:

`docs/current/evidence/SERVICE_1_R2_EXECUTION_EVIDENCE_V1.md`

Formato:

```text
# SERVICE_1_R2_EXECUTION_EVIDENCE_V1

EXECUTOR: CODEX
HEAD:
BRANCH:
PRECONDITION_R0_R1_QWEN_PASS: YES | NO

R2_VERDICT: PASS | FAIL | BLOCKED

FILES_CHANGED:
- ...

TABLE_SCOPE_BUILDER_PRODUCTIVE_PATHS_BEFORE:
TABLE_SCOPE_BUILDER_PRODUCTIVE_PATHS_AFTER:
SEM_CONSUMES_D7_TABLE_SCOPE:
D7_AUTHORITY_FLAGS_PRESERVED_FALSE:
NEW_WRAPPER: NO | YES
NEW_ALIAS: NO | YES
NEW_FALLBACK: NO | YES
OUT_OF_SCOPE_R3_PLUS_CHANGE: NO | YES

TESTS_RUN:
- ...
TEST_RESULTS:

PHYSICAL_EVIDENCE:
- ...

BLOCKERS:
- ...

NEXT_ALLOWED_ACTION: QWEN_VERIFY_R2 | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_ACTION: QWEN_VERIFY_R2` sólo si `R2_VERDICT: PASS`.

No pedir al usuario que transporte resultados. El archivo de evidencia es el handoff.
