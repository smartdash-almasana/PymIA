# Prompt Codex — Servicio 1 — R4.5 Integration Checkpoint V1

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`
**Rol:** verificador transversal read-only de R0–R4 antes de cualquier retiro destructivo de R5.

## 0. Precondición

Leer primero:

`docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md`

Continuar sólo si contiene simultáneamente:

```text
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R4_5_INTEGRATION_CHECKPOINT
```

Si no, detenerse con `STOP_R4_NOT_VERIFIED_PASS`.

## 1. Regla de carga

No releer todo Servicio 1. Leer sólo:

1. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
2. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
3. la sección R0–R4 de `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md`
4. `docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md` como evidencia histórica cerrada
5. `docs/current/evidence/SERVICE_1_R2_CLOSURE_V1.md`
6. `docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`
7. `docs/current/evidence/SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md`
8. `docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md`

No usar chat como fuente de verdad.

## 2. Modo

`MODE = READ_ONLY_INTEGRATION_CHECKPOINT`

Prohibido:

- modificar runtime;
- modificar tests;
- corregir findings;
- adelantar R5+;
- full suite;
- commit/push/deploy;
- reset/checkout masivo;
- tocar `_audit/`.

Única escritura permitida:

`docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1.md`

## 3. Objetivo

Demostrar que las convergencias cerradas R0–R4 funcionan juntas en el mismo worktree actual antes de eliminar legacy en R5.

Este checkpoint NO crea arquitectura nueva y NO sustituye R12/R13.

## 4. Verificación transversal mínima

Ejecutar una sola suite combinada, sin full suite:

```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py \
  tests/smartpyme/test_service_1_table_scoped_semantics_d5_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_p6_approval_decision_v1.py \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_architecture_lock_v1.py
```

Si alguno de esos archivos no existe físicamente, registrar `BLOCKED_TEST_CONTRACT_DRIFT`; no sustituirlo silenciosamente.

## 5. Gates físicos obligatorios

Además de la suite combinada, comprobar por búsqueda/call graph:

```text
R1_CONTENT_IDENTITY_STILL_ACTIVE = PASS
CANONICAL_ENVELOPE_POST_BUILD_MUTATIONS = 0
TABLE_SCOPE_PRODUCTIVE_BUILDERS = 1
SEM_TARGET_FSMS = 1
DETERMINISTIC_PROVIDER_PARITY_GATE_PRESERVED = PASS
PRODUCTIVE_EXECUTION_ROOTS = 1
EXPLICIT_EXECUTION_COMMANDS = 4
PRODUCTIVE_TOOL_REQUESTS_EXECUTION_PATHS = 0
PRODUCTIVE_DIRECT_GOVERNED_ANALYSIS_CALLERS_OUTSIDE_ROOT = 0
NEW_COMPATIBILITY_SHIMS_SINCE_R0 = 0
NEW_SHEET1_FALLBACKS_SINCE_R0 = 0
```

No exigir todavía los retiros propios de R5. Legacy que el plan autoriza retirar en R5 puede seguir físicamente presente si ya no contradice los gates R0–R4.

## 6. Interpretación

PASS sólo si:

- la suite combinada termina con 0 fail / 0 error;
- todos los gates transversales anteriores pasan;
- no aparece una regresión entre R0–R4;
- no se descubre pérdida de trabajo o contradicción documental/material.

Si falla un test, no arreglarlo en esta sesión. Identificar el primer contrato roto y devolver `FAIL_INTEGRATION_CHECKPOINT`.

Si aparece una contradicción arquitectónica material no contemplada: `BLOCKED_ARCHITECTURE`.

## 7. Evidencia obligatoria

Crear:

`docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1.md`

Formato mínimo:

```text
# SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1

EXECUTOR: CODEX
MODE: READ_ONLY_INTEGRATION_CHECKPOINT
HEAD:
BRANCH:

R4_VERIFICATION_PRECONDITION: PASS | FAIL

COMBINED_TEST_COMMAND:
TEST_RESULT:

R1_CONTENT_IDENTITY_STILL_ACTIVE:
CANONICAL_ENVELOPE_POST_BUILD_MUTATIONS:
TABLE_SCOPE_PRODUCTIVE_BUILDERS:
SEM_TARGET_FSMS:
DETERMINISTIC_PROVIDER_PARITY_GATE_PRESERVED:
PRODUCTIVE_EXECUTION_ROOTS:
EXPLICIT_EXECUTION_COMMANDS:
PRODUCTIVE_TOOL_REQUESTS_EXECUTION_PATHS:
PRODUCTIVE_DIRECT_GOVERNED_ANALYSIS_CALLERS_OUTSIDE_ROOT:
NEW_COMPATIBILITY_SHIMS_SINCE_R0:
NEW_SHEET1_FALLBACKS_SINCE_R0:

FINDINGS:
- ...

BLOCKERS:
- ...

FINAL_VERDICT: PASS | FAIL_INTEGRATION_CHECKPOINT | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT
NEXT_ALLOWED_NODE: R5 | NONE

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_NODE: R5` sólo si `FINAL_VERDICT: PASS`.
