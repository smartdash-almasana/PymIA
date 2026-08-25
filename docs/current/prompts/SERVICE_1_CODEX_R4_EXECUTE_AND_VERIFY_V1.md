# Prompt Codex — Servicio 1 — R4 Execute + Verify V1

STATUS: RETIRED_DO_NOT_EXECUTE
REPLACED_BY:
- SERVICE_1_CODEX_R4_IMPLEMENT_V2.md
- SERVICE_1_CODEX_R4_VERIFY_V2.md

**Rol:** único agente operativo vigente para Servicio 1. Ejecutar R4 y luego verificarlo en modo read-only.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## 0. Precondición automática

Leer primero:

`docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`

Continuar sólo si contiene simultáneamente:

```text
STATUS: CLOSED_PASS
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R4
```

Si falta cualquier condición:

```text
STOP_PRECONDITION
```

No modificar runtime/tests. Escribir únicamente el archivo de evidencia R4 indicando el bloqueo.

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
9. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — ejecutar exclusivamente R4
10. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
11. `docs/current/evidence/SERVICE_1_R3_EXECUTE_VERIFY_EVIDENCE_V1.md`
12. `docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`

La autoridad normativa es `SERVICE_1_CANONICAL_AXIS.md` + `SERVICE_1_ARCHITECTURE_LOCK.md`.

## 2. Worktree

Antes de editar:

- registrar `git status --short`;
- registrar HEAD y branch;
- preservar todos los cambios preexistentes;
- preservar `_audit/`;
- no `reset --hard`;
- no checkout/restauración masiva;
- no atribuir cambios heredados a R4.

## 3. Alcance

Ejecutar exclusivamente `R4 — ProductExecutionRequest + ProductExecutionRoot + surfaces` de `SERVICE_1_RECONSTRUCTION_PLAN_V1.md`.

No adelantar R5+.

Objetivo contractual obligatorio: una sola raíz productiva, thin dispatcher, con exactamente cuatro command contracts explícitos:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

Dependencies/ports deben quedar separados del request discriminado.

Puede existir como máximo un módulo de contracts dedicado para los cuatro commands si es necesario. No crear un módulo por command.

## 4. Reglas arquitectónicas absolutas

- No dispatch por shape de kwargs, presencia de campos o combinación de flags.
- No conservar `service_1_request_kind_v1.py` como segunda capa de dispatch si ya no tiene responsabilidad propia: absorber/retirar según el contrato rector.
- No conservar `tool_requests -> run_service_1_pipeline_v1` como quinta ruta productiva.
- No crear wrappers de compatibilidad productivos para sostener firmas antiguas.
- No dejar callers productivos usando la firma legacy del Product Root.
- Migrar superficies productivas CLI/Web/HTTP en el mismo ciclo R4.
- `semantic_reception_only`, `use_assisted_semantics`, `semantic_run_override` productivo, `analysis_execution_request` informal, kwargs especializados separados y `tool_requests` como selector productivo deben quedar absorbidos/eliminados según el contrato final.
- `semantic_atomic_confirmation` sólo puede sobrevivir como dato explícito del command semantic start si sigue siendo necesario; nunca como selector de workflow.
- `WorkbookSemanticStartRequest` inicia SEM-8.
- `WorkbookSemanticContinueRequest` consume estado semántico previo + owner evidence/responses por la FSM canónica.
- `WorkbookAnalysisExecuteRequest` exige canonical ingestion + confirmed bindings + analysis identity + tenant context y vuelve a ejecutar el camino gobernado P7/P8 antes de F7/F9.
- `SpecializedDomainExecuteRequest` exige subtype cerrado; no detectar el specialized flow por shape.
- ResultSet read/reentry NO debe meterse en estos cuatro commands. Sigue fuera del ProductExecutionRoot según Architecture Lock.
- No retirar todavía pipeline semántico histórico o sheet1 fallbacks que corresponden a R5, salvo que un caller legacy de root necesariamente deba desaparecer para cerrar R4 y esté expresamente cubierto por la disposición final. No hacer limpieza ciega de R5.
- No tocar matemática, policy, P8/F7 provenance, ResultRead, specialized math convergence ni registry final.
- No LLM math.
- No full suite.
- No commit, push ni deploy.

Ante contradicción física no contemplada:

```text
STOP_ARCHITECTURE
```

Documentar evidencia exacta. No inventar patch.

## 5. Inspección previa obligatoria

Antes de editar, localizar físicamente:

- todos los callers de `run_service_1_product_pipeline_v1`;
- todos los callers productivos de `run_service_1_pipeline_v1` desde Service 1 surfaces;
- usos productivos de `service_1_request_kind_v1`;
- usos de `semantic_reception_only`;
- usos de `use_assisted_semantics`;
- usos de `semantic_run_override`;
- usos de `analysis_execution_request`;
- specialized request kwargs individuales;
- `tool_requests` branch;
- CLI, assisted web, semantic reception server y HTTP paths.

Registrar conteos BEFORE para luego demostrar reducción física.

## 6. Ejecución

Aplicar el cambio mínimo coherente que cierre R4 completo, no una compatibilidad parcial.

El Product Root final debe recibir un request explícito de uno de los cuatro tipos y dependencies separadas. El dispatcher debe ser exhaustivo y fail-closed para tipos/subtypes inválidos.

Migrar todos los callers productivos identificados. Si un caller histórico/support no pertenece a Product Root final, clasificarlo conforme `SERVICE_1_CODE_DISPOSITION_FINAL_V1.md` y evitar mantenerlo artificialmente productivo.

Los tests legacy que invoquen la firma antigua deben migrarse al contrato objetivo cuando representen comportamiento legítimo. No introducir aliases para mantenerlos verdes.

## 7. Validación de ejecución

Ejecutar L0 y los tests prescritos en R4:

```text
python -m pytest -q tests/smartpyme/test_service_1_product_pipeline_v1.py tests/smartpyme/test_service_1_request_kind_dispatch_v1.py tests/smartpyme/test_service_1_assisted_web_http_v1.py tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py
```

Si el test `test_service_1_request_kind_dispatch_v1.py` queda conceptualmente obsoleto por absorción del request-kind module, migrarlo/renombrarlo al contrato de discriminación explícita sin conservar el diseño anterior sólo por compatibilidad.

Ejecutar además:

- syntax/import de módulos tocados;
- architecture guards pertinentes;
- regresión vecina acotada de CLI/Web/HTTP/semantic reception si el diff la afecta;
- búsquedas/call graph para gates arquitectónicos.

No ejecutar full suite.

## 8. Verificación Codex read-only del mismo ciclo

Después de implementación y tests, cambiar de rol:

```text
MODE = CODEX_READ_ONLY_VERIFIER
```

Desde ese punto:

- no modificar runtime;
- no modificar tests;
- no corregir findings;
- inspeccionar diff completo R4;
- intentar refutar el PASS;
- comprobar que existen exactamente cuatro command contracts y una sola ProductExecutionRoot;
- comprobar que no hay shape dispatch ni procedural root switches productivos;
- comprobar zero productive callers de la firma legacy del root;
- comprobar zero fifth `tool_requests` execution path;
- comprobar que CLI/Web/HTTP son surfaces y no roots paralelos;
- comprobar que ResultSet read no fue absorbido como execution command;
- comprobar que no se creó wrapper/alias/fallback/shim nuevo;
- comprobar que R5+ no fue adelantado indebidamente;
- comprobar que los commands ejecutan los authorities correctos sin saltarse SEM/P7/P8/F7/F9 según corresponda.

Si una afirmación no está físicamente probada:

```text
FINAL_VERDICT = FAIL_NOT_PROVEN
```

No reparar durante verificación.

## 9. Gates obligatorios

Sólo puede cerrar PASS si:

```text
FOUR_EXPLICIT_EXECUTION_COMMANDS = PASS
NO_SHAPE_DISPATCH = PASS
NO_PROCEDURAL_ROOT_SWITCHES = PASS
ONE_PRODUCTIVE_EXECUTION_ROOT = PASS
NO_FIFTH_TOOL_REQUESTS_EXECUTION_PATH = PASS
CLI_WEB_ONLY_SURFACES = PASS
ZERO_PRODUCTIVE_LEGACY_ROOT_CALLERS = PASS
RESULT_READ_OUTSIDE_EXECUTION_ROOT = PASS
REQUEST_KIND_LAYER_ABSORBED_OR_NON_DISPATCH = PASS
NEW_WRAPPER = NO
NEW_ALIAS = NO
NEW_FALLBACK = NO
NEW_COMPATIBILITY_SHIM = NO
OUT_OF_SCOPE_R5_PLUS_CHANGE = NO
```

## 10. Evidencia persistida obligatoria

Crear o sobrescribir al cierre:

`docs/current/evidence/SERVICE_1_R4_EXECUTE_VERIFY_EVIDENCE_V1.md`

Formato obligatorio:

```text
# SERVICE_1_R4_EXECUTE_VERIFY_EVIDENCE_V1

EXECUTOR_VERIFIER: CODEX
HEAD:
BRANCH:
PRECONDITION_R3_CLOSED_PASS: YES | NO

EXECUTION_VERDICT: PASS | FAIL | BLOCKED
VERIFICATION_MODE: READ_ONLY
VERIFICATION_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED
FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT

FILES_CHANGED_R4:
- ...

PRODUCT_ROOT_CALLERS_BEFORE:
PRODUCT_ROOT_CALLERS_AFTER:
LEGACY_ROOT_SIGNATURE_CALLERS_AFTER:
TOOL_REQUESTS_PRODUCTIVE_PATHS_AFTER:
PRODUCTIVE_EXECUTION_ROOTS_AFTER:

FOUR_EXPLICIT_EXECUTION_COMMANDS:
NO_SHAPE_DISPATCH:
NO_PROCEDURAL_ROOT_SWITCHES:
ONE_PRODUCTIVE_EXECUTION_ROOT:
NO_FIFTH_TOOL_REQUESTS_EXECUTION_PATH:
CLI_WEB_ONLY_SURFACES:
ZERO_PRODUCTIVE_LEGACY_ROOT_CALLERS:
RESULT_READ_OUTSIDE_EXECUTION_ROOT:
REQUEST_KIND_LAYER_ABSORBED_OR_NON_DISPATCH:
NEW_WRAPPER:
NEW_ALIAS:
NEW_FALLBACK:
NEW_COMPATIBILITY_SHIM:
OUT_OF_SCOPE_R5_PLUS_CHANGE:

TESTS_RUN:
- ...
TEST_RESULTS:

PHYSICAL_EVIDENCE:
- ...

VERIFIER_FINDINGS:
- ...

BLOCKERS:
- ...

NEXT_ALLOWED_NODE: R5 | NONE
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_NODE: R5` sólo si `FINAL_VERDICT: PASS`.

No pedir al usuario que transporte resultados. El archivo persistido es el handoff al ciclo siguiente.
