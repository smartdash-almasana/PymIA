# Prompt Qwen — Servicio 1 — verificación adversarial R2 V1

**Rol:** verificador independiente de R2.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Precondición

Leer `docs/current/evidence/SERVICE_1_R2_EXECUTION_EVIDENCE_V1.md`.

Sólo verificar R2 si contiene:

```text
R2_VERDICT: PASS
NEXT_ALLOWED_ACTION: QWEN_VERIFY_R2
```

Si no, registrar `BLOCKED_PRECONDITION` y no ejecutar tests.

## Reglas absolutas

- Código y tests: read-only.
- No corregir.
- No refactorizar.
- No reabrir arquitectura.
- No full suite.
- No commit/push/deploy.
- ÚNICA escritura permitida: `docs/current/evidence/SERVICE_1_R2_QWEN_VERIFICATION_V1.md`.

## Lectura obligatoria

1. `AGENTS.md`
2. `ARCHITECTURE_GUARDRAILS.md`
3. `docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md`
4. `docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
5. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
6. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
7. `docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md`
8. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — R2
9. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
10. `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`
11. `docs/current/evidence/SERVICE_1_R2_EXECUTION_EVIDENCE_V1.md`

## Objeto de verificación

Verificar exclusivamente R2 y detectar adelantos R3+.

Comprobar físicamente:

- D7 mantiene la construcción canónica de table-scoped structural evidence.
- SEM no vuelve a construir el mismo table scope.
- provider determinístico y bounded LLM reciben el mismo packet estructural cuando corresponda.
- D7 sigue siendo evidence-only.
- no aparecen authority flags nuevos.
- no se creó un segundo builder, wrapper o compatibility layer.
- no se modificó la FSM más allá de lo estrictamente necesario para consumir el packet R2.
- ningún test fue relajado para preservar duplicación.

## Pruebas

Ejecutar únicamente focales/guards R2 del reconstruction plan cuando sea necesario para corroborar evidencia. No full suite.

## Evidencia persistida

Crear o sobrescribir exclusivamente:

`docs/current/evidence/SERVICE_1_R2_QWEN_VERIFICATION_V1.md`

Formato:

```text
# SERVICE_1_R2_QWEN_VERIFICATION_V1

VERIFIER: QWEN
HEAD:
BRANCH:
PRECONDITION_R2_EXECUTION_PASS:

R2_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED

TABLE_SCOPE_BUILT_ONCE:
SEM_CONSUMES_D7_SCOPE:
D7_EVIDENCE_ONLY_PRESERVED:
SECOND_TABLE_SCOPE_BUILDER_ADDED:
NEW_WRAPPER:
NEW_ALIAS:
NEW_FALLBACK:
OUT_OF_SCOPE_R3_PLUS_CHANGE:

PHYSICAL_EVIDENCE:
- ...

TESTS_RUN:
- ...
TEST_RESULTS:

FINDINGS:
- ...

BLOCKERS:
- ...

FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT
NEXT_ALLOWED_NODE: R3 | NONE

FILES_CHANGED_BY_VERIFIER:
- docs/current/evidence/SERVICE_1_R2_QWEN_VERIFICATION_V1.md

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
NORMATIVE_DOCS_CHANGED: NO
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_NODE: R3` únicamente si `FINAL_VERDICT: PASS`.

No producir instrucciones para el usuario. Persistir el resultado para el siguiente agente.
