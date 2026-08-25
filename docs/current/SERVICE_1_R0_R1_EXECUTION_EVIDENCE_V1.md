# Servicio 1 — R0/R1 Execution Evidence V1

**Estado:** `CLOSED_PASS / INDEPENDENTLY_VERIFIED`  
**Fecha:** 2026-08-23  
**Ejecutor:** Codex  
**Alcance:** R0 + R1 solamente  
**Autoridad:** evidencia de ejecución; no sustituye `SERVICE_1_CANONICAL_AXIS.md`, `SERVICE_1_ARCHITECTURE_LOCK.md` ni la verificación independiente.

## Resultado reportado por el ejecutor

```text
R0_R1_EXECUTION_RESULT: PASS
HEAD: 8d5708e9becdddaa5aa24387b310972643d1ef86
BRANCH: work/service1-cafeteria-flow-v1

R0_VERDICT: PASS
ARCHITECTURE_REOPENED: NO
WORKTREE_RESET: NO
PREEXISTING_WORKTREE_PRESERVED: YES
_audit/: preserved untracked

R1_VERDICT: PASS
```

## Archivos reportados como tocados en R1

```text
pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py
pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
pymia/smartpyme/service_1_workbook_logical_model_v1.py
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
focal R1 tests
neighbor Product Root fixture
```

El worktree ya estaba sucio antes de R0/R1. Por tanto un verificador NO debe atribuir automáticamente todo `git diff HEAD` a Codex. Debe verificar comportamiento físico R1 y distinguir evidencia heredada de cambios atribuibles al ciclo cuando sea posible.

## Contrato de identidad reportado

```text
source_artifact_ref = xlsx:sha256:<SHA-256 actual bytes>
workbook_ref = digest(source_artifact_ref + ingestion_scope + canonical reader/schema version)
sheet_ref = digest(workbook_ref + exact sheet_name)
case_id = opaque workflow identity
filename = display/provenance only
```

## Tests reportados por Codex

```text
L0 py_compile: PASS
L1 focal R1/D3: 55 passed
L2 architecture/D7: 13 passed
L3 bounded neighbors: 44 passed
TOTAL: 112 passed / 0 failed
FULL_SUITE: NOT RUN
```

## Gates reportados por Codex

```text
CONTENT_ADDRESSED_SOURCE_ARTIFACT: PASS
LOCAL_PATH_CONTENT_HASH: PASS
NO_FILENAME_AS_STRUCTURAL_IDENTITY: PASS
WORKBOOK_IDENTITY_FROM_ARTIFACT_SCOPE: PASS
SHEET_REF_EXPLICIT: PASS
NO_NEW_SHEET1_FALLBACK: PASS
CANONICAL_INGESTION_SELF_CONTAINED: PASS
NO_POST_BUILD_CANONICAL_MUTATION: PASS
SECOND_XLSX_READER_ADDED: NO
NEW_COMPATIBILITY_SHIM: NO
NEW_ALIAS: NO
```

## Legacy test conflict reportado

Un fixture manual de Product Root carecía de identidad R1 explícita y fue actualizado al contrato canónico. El ejecutor declara que no se relajó runtime.

## Estado de gobierno

```text
EXECUTOR_VERDICT: PASS
CHATGPT_PRELIMINARY_CONTROL: NO_IMMEDIATE_BLOCK_FOUND
INDEPENDENT_VERIFIER: QWEN_PASS
R0_R1_FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R2
```

Qwen debe ejecutar exclusivamente:

```text
docs/current/prompts/SERVICE_1_QWEN_VERIFY_R0_R1_V2.md
```

Ese prompt persiste su veredicto en `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md` para que el siguiente agente lo consuma directamente. No avanzar a R2 hasta que la verificación independiente termine en `PASS`.

```text
COMMIT: NO
PUSH: NO
DEPLOY: NO
```
