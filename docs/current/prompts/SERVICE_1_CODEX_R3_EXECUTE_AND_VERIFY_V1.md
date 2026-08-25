# Prompt Codex — Servicio 1 — R3 Execute + Verify V1

**Rol:** único agente operativo vigente para Servicio 1. Ejecutar R3 y luego verificarlo en modo read-only.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## 0. Precondición automática

Leer primero:

`docs/current/evidence/SERVICE_1_R2_CLOSURE_V1.md`

Continuar sólo si contiene simultáneamente:

```text
STATUS: CLOSED_PASS
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R3
```

Si falta cualquier condición:

```text
STOP_PRECONDITION
```

No modificar runtime/tests. Escribir únicamente el archivo de evidencia de R3 indicando el bloqueo.

Qwen está retirado de la cadena operativa. No generar dependencias, handoffs ni prompts hacia Qwen.

## 1. Lectura obligatoria

Leer físicamente, en este orden:

1. `AGENTS.md`
2. `ARCHITECTURE_GUARDRAILS.md`
3. `docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md`
4. `docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
5. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
6. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
7. `docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md`
8. `docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`
9. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — ejecutar exclusivamente la sección R3
10. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
11. `docs/current/evidence/SERVICE_1_R2_EXECUTION_EVIDENCE_V1.md`
12. `docs/current/evidence/SERVICE_1_R2_CLOSURE_V1.md`

La autoridad normativa es `SERVICE_1_CANONICAL_AXIS.md` + `SERVICE_1_ARCHITECTURE_LOCK.md`. El pipeline determinístico histórico puede leerse como oracle de paridad, pero R3 no autoriza conservarlo como segunda FSM objetivo ni agregarle funcionalidad.

## 2. Worktree

Antes de editar:

- registrar `git status --short`;
- registrar HEAD y branch;
- preservar todos los cambios preexistentes;
- preservar `_audit/`;
- no `reset --hard`;
- no checkout/restauración masiva;
- no atribuir cambios heredados a R3.

## 3. Alcance

Ejecutar exclusivamente `R3 — Una sola FSM semántica + parity proof` de `SERVICE_1_RECONSTRUCTION_PLAN_V1.md`.

No adelantar R4+.

Archivos primarios definidos por el plan:

```text
pymia/smartpyme/service_1_assisted_semantic_product_wiring_v1.py
pymia/smartpyme/service_1_deterministic_semantic_proposal_provider_v1.py
pymia/smartpyme/service_1_deterministic_semantic_pipeline_v1.py  # oracle read-only salvo test wiring estrictamente necesario; no nueva funcionalidad
pymia/smartpyme/service_1_owner_semantic_evidence_reentry_v1.py
pymia/smartpyme/service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py
pymia/smartpyme/service_1_p6_approval_decision_v1.py
```

Tests correspondientes según el plan y el test de parity explícito requerido.

## 4. Reglas arquitectónicas absolutas

- Una sola FSM target.
- Provider determinístico = provider de esa FSM, no segunda FSM.
- Preservar owner confirmation explícita, follow-up, correction, skip, decomposition, relationships, P6 decisions, requirement matches y reproducibilidad offline.
- No borrar todavía `service_1_deterministic_semantic_pipeline_v1.py`; su retiro corresponde a R5 después de paridad probada.
- No agregar wrapper, alias, fallback o compatibility shim.
- No introducir nueva semántica hardcodeada para hacer verde la paridad.
- No modificar matemática.
- No modificar ProductExecutionRoot contract; eso corresponde a R4.
- No tocar ResultRead, P8/F7 provenance, specialized convergence ni registry final.
- No LLM math.
- No commit, push ni deploy.
- No full suite.

Si el código físico demuestra una contradicción no contemplada por los documentos rectores:

```text
STOP_ARCHITECTURE
```

Documentar evidencia exacta y no inventar patch.

## 5. Ejecución

Aplicar el cambio mínimo coherente prescrito por R3.

La paridad debe comparar comportamiento legítimo, no detalles incidentales del legacy. Debe quedar físicamente probado que el provider determinístico dentro de SEM-8 produce el mismo resultado canónico relevante para los mismos inputs/evidencia owner, particularmente `CONFIRMED_BINDINGS`, sin saltarse el ciclo humano ni P6.

No modificar tests para bendecir una divergencia que contradiga el target. Si el legacy test codifica una conducta incompatible con arquitectura cerrada, reportar el conflicto; no crear compatibilidad nueva.

## 6. Validación de ejecución

Ejecutar L0 y los tests prescritos en R3:

```text
python -m pytest -q tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py tests/smartpyme/test_service_1_deterministic_semantic_pipeline_v1.py tests/smartpyme/test_service_1_deterministic_semantic_computation_plan_v1.py tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py tests/smartpyme/test_service_1_p6_approval_decision_v1.py
```

Agregar/ejecutar el test explícito de parity de `CONFIRMED_BINDINGS` requerido por el plan.

Ejecutar architecture guards y regresión vecina acotada sólo donde el diff de R3 lo justifique.

No ejecutar full suite.

## 7. Verificación Codex read-only del mismo ciclo

Después de terminar la implementación y los tests, cambiar de rol:

```text
MODE = CODEX_READ_ONLY_VERIFIER
```

Desde ese punto:

- no modificar runtime;
- no modificar tests;
- no corregir findings;
- inspeccionar el diff R3 completo;
- comprobar físicamente call paths y contracts;
- intentar refutar el PASS del ejecutor;
- verificar que el deterministic provider es realmente provider de SEM-8 y no una segunda ruta/FSM disfrazada;
- verificar que el pipeline histórico no recibió nueva funcionalidad productiva;
- verificar que owner/P6/follow-up/correction/skip/decomposition/relationships siguen cubiertos;
- verificar reproducibilidad offline;
- verificar que no hubo R4+ prematuro;
- verificar que no apareció wrapper/alias/fallback/shim nuevo.

Si una afirmación no está físicamente probada:

```text
FINAL_VERDICT = FAIL_NOT_PROVEN
```

No reparar en la fase de verificación.

## 8. Gates obligatorios

Sólo puede cerrar PASS si:

```text
ONE_FSM_TARGET_BEHAVIOR_PROVEN = PASS
DETERMINISTIC_PROVIDER_OFFLINE = PASS
FIRST_CONTACT_OWNER_CONFIRMATION = PASS
PARITY_CONFIRMED_BINDINGS = PASS
SECOND_SEMANTIC_FSM_ADDED = NO
LEGACY_PIPELINE_NEW_FUNCTIONALITY = NO
NEW_WRAPPER = NO
NEW_ALIAS = NO
NEW_FALLBACK = NO
NEW_COMPATIBILITY_SHIM = NO
OUT_OF_SCOPE_R4_PLUS_CHANGE = NO
```

## 9. Evidencia persistida obligatoria

Crear o sobrescribir únicamente al cierre del ciclo:

`docs/current/evidence/SERVICE_1_R3_EXECUTE_VERIFY_EVIDENCE_V1.md`

Formato obligatorio:

```text
# SERVICE_1_R3_EXECUTE_VERIFY_EVIDENCE_V1

EXECUTOR_VERIFIER: CODEX
HEAD:
BRANCH:
PRECONDITION_R2_CLOSED_PASS: YES | NO

EXECUTION_VERDICT: PASS | FAIL | BLOCKED
VERIFICATION_MODE: READ_ONLY
VERIFICATION_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED
FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT

FILES_CHANGED_R3:
- ...

ONE_FSM_TARGET_BEHAVIOR_PROVEN:
DETERMINISTIC_PROVIDER_OFFLINE:
FIRST_CONTACT_OWNER_CONFIRMATION:
PARITY_CONFIRMED_BINDINGS:
SECOND_SEMANTIC_FSM_ADDED:
LEGACY_PIPELINE_NEW_FUNCTIONALITY:
NEW_WRAPPER:
NEW_ALIAS:
NEW_FALLBACK:
NEW_COMPATIBILITY_SHIM:
OUT_OF_SCOPE_R4_PLUS_CHANGE:

TESTS_RUN:
- ...
TEST_RESULTS:

PHYSICAL_EVIDENCE:
- ...

VERIFIER_FINDINGS:
- ...

BLOCKERS:
- ...

NEXT_ALLOWED_NODE: R4 | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_NODE: R4` sólo si `FINAL_VERDICT: PASS`.

No pedir al usuario que transporte resultados. El archivo persistido es el handoff al ciclo siguiente.
