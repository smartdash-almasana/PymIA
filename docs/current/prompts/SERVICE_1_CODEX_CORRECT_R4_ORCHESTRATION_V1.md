# Prompt Codex — Corrección de orquestación R4 V1

STATUS: COMPLETED_DOCUMENTATION_CORRECTION

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Rol

Actuá únicamente como corrector de la orquestación documental de R4. **NO implementar R4. NO modificar runtime. NO modificar tests.**

## Motivo

El prompt actual `docs/current/prompts/SERVICE_1_CODEX_R4_EXECUTE_AND_VERIFY_V1.md` quedó sobrecargado porque combina en una sola ejecución:

- lectura arquitectónica extensa;
- implementación completa de R4;
- migración de superficies;
- tests;
- verificación adversarial read-only.

Ese diseño queda **RETIRADO**. No debe ejecutarse.

## Autoridad mínima a leer

1. `docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`
2. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md` — sólo sección R4
3. `docs/current/SERVICE_1_CANONICAL_AXIS.md` — sólo contratos/autoridades relevantes a ProductExecutionRoot
4. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md` — sólo reglas relevantes a R4
5. `docs/current/prompts/SERVICE_1_ORCHESTRATION_CHAIN_V1.md`
6. `docs/current/prompts/README.md`
7. `docs/current/prompts/SERVICE_1_CODEX_R4_EXECUTE_AND_VERIFY_V1.md` — sólo para retirarlo/sustituirlo, no para ejecutarlo

No releer auditorías históricas ni dossier dialéctico.

## Corrección requerida

Crear exactamente dos prompts nuevos, separados:

### A. Ejecución focal

`docs/current/prompts/SERVICE_1_CODEX_R4_IMPLEMENT_V2.md`

Debe:

- verificar precondición `R3 CLOSED_PASS`;
- ejecutar **sólo la implementación R4**;
- usar referencias a los documentos rectores en lugar de copiar toda la arquitectura;
- exigir inspección física previa de callers/surfaces afectados;
- preservar el worktree y `_audit/`;
- prohibir R5+;
- prohibir full suite;
- prohibir commit/push/deploy;
- ejecutar únicamente L0/L1/L2/L3 necesarios para R4;
- persistir evidencia en:
  `docs/current/evidence/SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md`;
- terminar con uno de:
  `IMPLEMENTATION_VERDICT: PASS | FAIL | BLOCKED`;
- si PASS, indicar `NEXT_ALLOWED_ACTION: CODEX_R4_VERIFY_SEPARATE_SESSION`.

Este prompt **NO debe contener fase de auditoría/verificación adversarial**.

### B. Verificación separada

`docs/current/prompts/SERVICE_1_CODEX_R4_VERIFY_V2.md`

Debe:

- ejecutarse en **una sesión nueva/separada de Codex**;
- ser read-only para runtime/tests;
- leer primero `SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md`;
- continuar sólo si `IMPLEMENTATION_VERDICT: PASS`;
- leer únicamente el contrato rector mínimo necesario, el diff R4 y los tests relevantes;
- intentar refutar el PASS de implementación;
- comprobar físicamente los gates R4 definidos en `SERVICE_1_RECONSTRUCTION_PLAN_V1.md` y `SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`;
- no corregir findings;
- no full suite;
- no commit/push/deploy;
- persistir evidencia en:
  `docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md`;
- terminar con:
  `FINAL_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT`;
- sólo con `FINAL_VERDICT: PASS` permitir `NEXT_ALLOWED_NODE: R5`.

## Regla de carga cognitiva

Los dos prompts deben ser **focales y cortos**. No copiar bloques extensos de arquitectura que ya están en documentos rectores. Referenciar secciones concretas. No pedir releer todo el handoff si la información necesaria ya está en R3 closure + R4 plan + lock/canonical axis.

## Actualizaciones documentales obligatorias

Sin tocar runtime/tests:

1. Marcar `SERVICE_1_CODEX_R4_EXECUTE_AND_VERIFY_V1.md` como:
   `RETIRED_DO_NOT_EXECUTE` en su encabezado.
2. Actualizar `docs/current/prompts/README.md` para que el prompt vigente sea primero `SERVICE_1_CODEX_R4_IMPLEMENT_V2.md` y luego, sólo tras PASS, `SERVICE_1_CODEX_R4_VERIFY_V2.md`.
3. Actualizar `SERVICE_1_ORCHESTRATION_CHAIN_V1.md` para dejar explícito:

```text
R4 implementation session
→ implementation evidence
→ NEW Codex session read-only verification
→ verification evidence
→ PASS habilita R5
```

4. No modificar arquitectura normativa ni reconstruction plan.

## Verificación de esta corrección

Comprobar:

- los dos nuevos prompts existen;
- el prompt viejo está marcado RETIRED;
- ningún prompt R4 vigente combina implementación + verificación;
- README y orchestration chain apuntan a los nuevos archivos;
- `git diff` de esta tarea contiene sólo archivos bajo `docs/current/prompts/`.

## Salida

Responder únicamente:

```text
R4_ORCHESTRATION_CORRECTION: PASS | FAIL
RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
OLD_R4_PROMPT_RETIRED: YES | NO
R4_IMPLEMENT_PROMPT_CREATED: YES | NO
R4_VERIFY_PROMPT_CREATED: YES | NO
PROMPT_INDEX_UPDATED: YES | NO
ORCHESTRATION_CHAIN_UPDATED: YES | NO
FILES_CHANGED:
- ...
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

No implementar R4 en esta ejecución.
