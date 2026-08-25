# Servicio 1 — Instrucciones Operativas para Agentes V1

**Estado:** `AUTHORITATIVE_OPERATING_INSTRUCTIONS`  
**Fecha:** 2026-08-23  
**Aplica a:** cualquier LLM/agente que implemente, verifique o continúe Servicio 1.  

## 1. Regla de arranque

Leer obligatoriamente, en este orden:

1. `AGENTS.md`
2. `ARCHITECTURE_GUARDRAILS.md`
3. `docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
4. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
5. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
6. `docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md`
7. `docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`
8. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md`
9. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
10. `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

No reconstruir contexto desde chats. No pedir al usuario que repita historia si estos documentos existen.

## 2. Autoridad

Arquitectura cerrada:

```text
OPEN_ARCHITECTURAL_DECISIONS = 0
TARGET_ARCHITECTURE_CLOSED = YES
```

Durante implementación no se permite reabrir decisiones ya cerradas. Si el código contradice la arquitectura normativa, prevalecen `SERVICE_1_CANONICAL_AXIS.md` y `SERVICE_1_ARCHITECTURE_LOCK.md`.

Si aparece una contradicción real no contemplada:

```text
STOP_ARCHITECTURE
```

El agente debe:

1. detener el cambio;
2. citar archivo/función/contrato afectado;
3. describir la contradicción física;
4. no crear wrapper, alias, fallback, excepción o bypass temporal;
5. esperar nueva decisión normativa.

## 3. Regla de edición

Cada iteración debe ser arquitectónicamente acotada.

```text
1 cambio
→ L0 syntax/import
→ L1 focal
→ L2 architecture guards
→ L3 bounded neighbors cuando corresponda
→ veredicto
```

No agrupar cambios independientes para ahorrar tiempo.

No modificar tests para conservar comportamiento legacy contrario al target.

## 4. Prohibiciones

No crear:

- segunda raíz productiva;
- segundo parser XLSX productivo;
- segunda FSM semántica;
- segundo motor matemático;
- `PrimitiveEngine` nuevo;
- `PolicyRegistry` global;
- DSL general de expresiones;
- alias transitorio sin retiro explícito;
- wrapper de compatibilidad sin fecha/gate de eliminación;
- fallback `sheet1` productivo;
- identidad por filename/basename/path/mtime/size;
- dispatch por shape o combinación de kwargs;
- matemática empresarial en UI/Web/CLI;
- cálculo del LLM;
- join del LLM;
- autoridad de computabilidad del LLM;
- post-construction mutation de `CanonicalIngestionOutput`.

No ejecutar `git reset --hard` ni limpiar el worktree indiscriminadamente.

No commit, push ni deploy sin autorización explícita del usuario.

`_audit/` permanece offline/uncommitted salvo autorización explícita.

## 5. Política de tests

Escalera obligatoria:

```text
L0 = syntax/import
L1 = focal contracts
L2 = architecture/authority guards
L3 = bounded neighboring regression
L4 = integration checkpoint
L5 = full suite sólo en checkpoint mayor/final
L6 = real XLSX E2E
```

No correr full suite después de cada cambio.

No declarar PASS sin salida de tests observada o evidencia física equivalente.

## 6. Política de worktree

Antes de editar:

- registrar `git status --short`;
- identificar archivos ya modificados;
- consultar `SERVICE_1_CODE_DISPOSITION_FINAL_V1.md`;
- no sobrescribir cambios útiles sin inspección;
- si un archivo tiene cambios previos, editar de forma mínima y conservar lo alineado con el target.

## 7. Regla de entropía

Un cambio es `FAIL_ARCHITECTURE` si incrementa cualquiera de:

```text
productive_paths
compatibility_shims
transitional_aliases
root procedural switches
legacy productive callers
sheet1 fallbacks
inline business math
inline business classification
post-construction envelope mutations
parallel semantic FSMs
authority collisions
```

Un test verde no compensa aumento de entropía arquitectónica.

## 8. Formato de salida de cada ciclo

El agente debe devolver únicamente:

```text
CYCLE:
VERDICT: PASS | FAIL | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT
HEAD:
FILES_CHANGED:
TESTS_RUN:
TEST_RESULTS:
ARCHITECTURE_GATES:
RETIREMENTS_COMPLETED:
NEW_LEGACY_OR_COMPAT: NONE | <detalle>
UNRESOLVED_BLOCKER:
NEXT_ALLOWED_NODE:
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

No entregar narrativa extensa salvo bloqueo.

## 9. Verificador independiente

Cuando un ciclo de implementación se declara PASS, un segundo agente puede verificarlo read-only.

El verificador:

- no corrige;
- no refactoriza;
- no modifica tests;
- no propone arquitectura nueva;
- comprueba contratos, callers, imports y gates;
- puede ejecutar sólo tests focales/guards necesarios;
- devuelve PASS/FAIL con evidencia.

## 10. Regla final

```text
No diseñar Servicio 1 mientras se implementa.
No conservar deuda por compatibilidad.
No arreglar síntomas antes de contratos.
No declarar finalización antes del Completion Contract.
```


## Handoff entre agentes — regla vigente

El usuario no debe ser usado como transporte manual de resultados, prompts o evidencia entre Codex, Qwen y dirección técnica.

Cada agente debe persistir su salida operativa en `docs/current/evidence/` y el agente siguiente debe consumirla directamente desde el repo.

La cadena vigente está definida en:

`docs/current/prompts/SERVICE_1_ORCHESTRATION_CHAIN_V1.md`

Ningún prompt nuevo puede depender de información que exista sólo en chat. Si una precondición no está persistida u observable físicamente, el agente debe detenerse y registrar `STOP_PRECONDITION`.


## Override operativo — Codex único agente — 2026-08-23

Desde este punto la cadena operativa de Servicio 1 usa exclusivamente Codex.

```text
CODEX = EXECUTOR + VERIFIER DEL CICLO
QWEN = RETIRED_FROM_ACTIVE_CHAIN
```

Cada prompt nuevo debe obligar a Codex a separar dos fases:

```text
A. ejecución del nodo autorizado
B. verificación read-only del mismo nodo
```

La fase B no puede modificar runtime/tests para conseguir el PASS. Si detecta un defecto, debe devolver FAIL / FAIL_NOT_PROVEN / BLOCKED y cerrar el ciclo sin habilitar el nodo siguiente.

Las evidencias históricas producidas por Qwen siguen siendo válidas como evidencia ya emitida, pero ningún ciclo nuevo puede depender de una futura ejecución de Qwen.

El usuario no debe actuar como intermediario de instrucciones ni resultados entre agentes. Toda continuidad se persiste en `docs/current/evidence/` y `docs/current/prompts/`.
