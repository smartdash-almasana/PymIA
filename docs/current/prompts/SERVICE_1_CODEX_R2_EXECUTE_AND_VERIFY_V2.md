# Prompt Codex — Servicio 1 — R2 Execute + Verify V2

**Rol único vigente:** Codex = ejecutor + verificador del ciclo.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Precondición

Leer `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md` únicamente como evidencia histórica ya emitida. Continuar sólo si contiene:

```text
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R2
```

Qwen ya no forma parte de la operación futura. No generar dependencias nuevas hacia Qwen.

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

## Reglas absolutas

- Ejecutar exclusivamente R2.
- No adelantar R3+.
- No reabrir arquitectura.
- No crear wrappers, aliases, fallbacks o compatibility shims.
- No crear una segunda FSM ni un segundo builder de table scope.
- No full suite.
- No commit, push ni deploy.
- Preservar worktree previo y `_audit/`.
- No pedir al usuario que transporte evidencia.

## Fase A — ejecución

Seguir exactamente `R2 — Table-scoped structural evidence construido una vez` de `SERVICE_1_RECONSTRUCTION_PLAN_V1.md`.

Aplicar la regla:

```text
1 cambio arquitectónicamente acotado
→ L0
→ L1
→ L2
→ L3 si corresponde
→ veredicto
```

## Fase B — verificación Codex obligatoria

Después de terminar la ejecución, cambiar de rol a VERIFICADOR READ-ONLY DEL PROPIO CICLO.

En esta fase:
- no modificar runtime;
- no modificar tests;
- inspeccionar `git diff` de los archivos tocados;
- verificar callers productivos;
- verificar que el builder de `table_scoped_semantics` tenga una sola construcción productiva autorizada vía D7;
- verificar que SEM consuma el packet D7 ya construido;
- verificar que no aparecieron rutas paralelas, wrappers, aliases, fallbacks ni cambios R3+;
- volver a correr únicamente los focales/guards necesarios si falta evidencia;
- si una afirmación no está demostrada, usar `FAIL_NOT_PROVEN`.

## Evidencia persistida única

Crear o sobrescribir:

`docs/current/evidence/SERVICE_1_R2_CODEX_EXECUTE_VERIFY_V1.md`

Formato mínimo obligatorio:

```text
# SERVICE_1_R2_CODEX_EXECUTE_VERIFY_V1

AGENT: CODEX
MODE: EXECUTE_THEN_READ_ONLY_VERIFY
HEAD:
BRANCH:
PRECONDITION_R0_R1_PASS: YES | NO

EXECUTION_VERDICT: PASS | FAIL | BLOCKED
VERIFICATION_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED
FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED

FILES_CHANGED:
- ...

TABLE_SCOPE_BUILDER_PRODUCTIVE_PATHS_BEFORE:
TABLE_SCOPE_BUILDER_PRODUCTIVE_PATHS_AFTER:
SEM_CONSUMES_D7_TABLE_SCOPE:
D7_AUTHORITY_FLAGS_PRESERVED_FALSE:
NEW_WRAPPER:
NEW_ALIAS:
NEW_FALLBACK:
OUT_OF_SCOPE_R3_PLUS_CHANGE:

TESTS_RUN:
- ...
TEST_RESULTS:

PHYSICAL_EVIDENCE:
- ...

FINDINGS:
- ...

BLOCKERS:
- ...

NEXT_ALLOWED_NODE: R3 | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_NODE: R3` sólo si `FINAL_VERDICT: PASS`.

Ante contradicción arquitectónica no contemplada:

```text
STOP_ARCHITECTURE
```

No reparar mediante patch improvisado.
