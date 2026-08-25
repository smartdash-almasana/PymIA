# Prompt Qwen — verificación adversarial R0/R1 V2

**Rol:** verificador independiente read-only de implementación R0/R1.
**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`
**Objetivo:** verificar físicamente el resultado de Codex y persistir el veredicto para que el siguiente agente no dependa del chat ni del usuario como intermediario.

## Reglas absolutas

- No modificar runtime.
- No modificar tests.
- No modificar documentos normativos.
- No refactorizar.
- No corregir defectos encontrados.
- No reabrir arquitectura.
- No full suite.
- No commit, push ni deploy.
- ÚNICA escritura permitida: `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`.

## Lectura obligatoria

1. `AGENTS.md`
2. `ARCHITECTURE_GUARDRAILS.md`
3. `docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md`
4. `docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
5. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
6. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
7. `docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md`
8. `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md`
9. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`
10. `docs/current/SERVICE_1_R0_R1_EXECUTION_EVIDENCE_V1.md`
11. `docs/current/prompts/SERVICE_1_VERIFIER_PROMPT_R0_R1_V1.md`

## Fuente de verdad física

Inspeccionar directamente:
- `git status --short`
- `git diff` de archivos R1
- callers relevantes
- tests focales relevantes
- contratos de identidad y canonical ingestion

No aceptar afirmaciones de `SERVICE_1_R0_R1_EXECUTION_EVIDENCE_V1.md` sin evidencia física.

## Verificación

Ejecutar exactamente la verificación definida en `SERVICE_1_VERIFIER_PROMPT_R0_R1_V1.md`, con estas adiciones:

1. Verificar que ningún cambio R1 introdujo decisiones R2+ no autorizadas.
2. Verificar que ningún caller productivo recompone o completa `CanonicalIngestionOutput` luego de su construcción.
3. Verificar que `source_artifact_ref` para `local_path` usa bytes reales del archivo.
4. Verificar que renombrar el mismo archivo no cambia artifact identity.
5. Verificar que dos archivos con mismo basename y bytes distintos no colisionan.
6. Verificar que `workbook_ref` cambia con `ingestion_scope`.
7. Verificar que `sheet_ref` deriva de `workbook_ref + exact sheet_name`.
8. Verificar que no se agregó parser XLSX alternativo.
9. Verificar que cualquier fixture actualizado fue migrado al contrato target y no relajó runtime.
10. Verificar que no se introdujeron aliases o compatibility shims nuevos.

## Tests permitidos

Sólo focales/guards R1. No full suite.

## Salida persistida obligatoria

Crear o sobrescribir exclusivamente:

`docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md`

con este formato exacto:

```text
# SERVICE_1_R0_R1_QWEN_VERIFICATION_V1

VERIFIER: QWEN
MODE: READ_ONLY_CODE_AND_TESTS
HEAD:
BRANCH:

R0_VERDICT: PASS | FAIL | BLOCKED
R1_VERDICT: PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED

CONTENT_ADDRESSED_SOURCE_ARTIFACT:
LOCAL_PATH_CONTENT_HASH:
NO_FILENAME_AS_STRUCTURAL_IDENTITY:
WORKBOOK_IDENTITY_FROM_ARTIFACT_SCOPE:
SHEET_REF_EXPLICIT:
NO_NEW_SHEET1_FALLBACK:
CANONICAL_INGESTION_SELF_CONTAINED:
NO_POST_BUILD_CANONICAL_MUTATION:
SECOND_XLSX_READER_ADDED:
NEW_COMPATIBILITY_SHIM:
NEW_ALIAS:
OUT_OF_SCOPE_R2_PLUS_CHANGE:

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
NEXT_ALLOWED_NODE: R2 | NONE

FILES_CHANGED_BY_VERIFIER:
- docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
NORMATIVE_DOCS_CHANGED: NO
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

## Regla de cierre

- `NEXT_ALLOWED_NODE: R2` únicamente si `FINAL_VERDICT: PASS`.
- Si falla, describir evidencia exacta y no reparar.
- No producir instrucciones para el usuario. El archivo persistido es el handoff al siguiente agente.
