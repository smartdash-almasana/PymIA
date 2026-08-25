# Prompt Codex — Servicio 1 — R4.5 Integration Checkpoint Retry V2

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`
**Modo:** READ_ONLY_INTEGRATION_CHECKPOINT

## Precondiciones

Leer:

1. `docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md`
2. `docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1.md`
3. `docs/current/evidence/SERVICE_1_R4_5_STALE_CLI_TEST_REPAIR_V1.md`

Continuar sólo si:

```text
R4 FINAL_VERDICT: PASS
R4.5 V1 FINAL_VERDICT: FAIL_INTEGRATION_CHECKPOINT
repair REPAIR_VERDICT: PASS
repair NEXT_ALLOWED_ACTION: R4_5_INTEGRATION_CHECKPOINT_RETRY
```

Si falta alguna condición, detenerse con `STOP_PRECONDITION_NOT_MET`.

## Rol

Read-only desde el inicio:

- no modificar runtime;
- no modificar tests;
- no reparar findings;
- no modificar arquitectura;
- no implementar R5;
- preservar worktree y `_audit/`;
- no full suite;
- no commit, push ni deploy.

## Objetivo

Repetir el checkpoint transversal R0–R4 completo después de la reparación focal del test stale. Debe probar que los contratos cerrados R0/R1, R2, R3 y R4 coexisten en el mismo worktree.

## Suite combinada obligatoria

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

No detener la suite a propósito después del primer PASS; registrar cualquier failure/error real. Si falla, no reparar.

## Gates físicos obligatorios

Después de tests, inspeccionar read-only y registrar:

```text
R1_CONTENT_IDENTITY_STILL_ACTIVE
CANONICAL_ENVELOPE_POST_BUILD_MUTATIONS = 0
TABLE_SCOPE_PRODUCTIVE_BUILDERS = 1 authority path via D7
SEM_TARGET_FSMS = 1 target composition
DETERMINISTIC_PROVIDER_PARITY_GATE_PRESERVED
PRODUCTIVE_EXECUTION_ROOTS = 1
EXPLICIT_EXECUTION_COMMANDS = 4
PRODUCTIVE_TOOL_REQUESTS_EXECUTION_PATHS = 0
PRODUCTIVE_DIRECT_GOVERNED_ANALYSIS_CALLERS_OUTSIDE_ROOT = 0
NEW_COMPATIBILITY_SHIMS_SINCE_R0 = 0
NEW_SHEET1_FALLBACKS_SINCE_R0 = 0
```

Pre-existing R5 legacy semantic/sheet1 debt is not counted as new debt, but must remain clearly identified as pending R5 scope.

## Veredicto

Persistir:

`docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V2.md`

Formato mínimo:

```text
R4_5_INTEGRATION_CHECKPOINT: PASS | FAIL_INTEGRATION_CHECKPOINT | BLOCKED
FINAL_VERDICT: PASS | FAIL_INTEGRATION_CHECKPOINT | BLOCKED
HEAD:
BRANCH:

TESTS:
ARCHITECTURE_GATES:
- ...

BLOCKERS:
- ...

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO

NEXT_ALLOWED_NODE: R5 | NONE
```

Sólo `FINAL_VERDICT: PASS` habilita R5.
