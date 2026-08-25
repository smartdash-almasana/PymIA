# Prompt verificador — Servicio 1 — R0 + R1 V1

**Uso:** Qwen / Codex / agente independiente read-only después de una implementación R0/R1 declarada PASS.  
**Modo:** verificación adversarial, sin reparar.  

```text
REPO:
E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria

ROL:
Verificador independiente read-only de R0/R1 de Servicio 1.

No corregir.
No refactorizar.
No editar código/tests/docs.
No proponer arquitectura nueva.
No commit/push/deploy.
No full suite.

==================================================
LECTURA OBLIGATORIA
==================================================

1. AGENTS.md
2. ARCHITECTURE_GUARDRAILS.md
3. docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md
4. docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
5. docs/current/SERVICE_1_CANONICAL_AXIS.md
6. docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
7. docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
8. docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
9. docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md

==================================================
OBJETO DE VERIFICACIÓN
==================================================

Verificar exclusivamente R0 y R1.

No evaluar R2+ excepto para detectar si la implementación se adelantó e introdujo entropía fuera de alcance.

==================================================
CHECK R0
==================================================

Observar:
- HEAD.
- branch.
- git status --short.
- si hubo reset/restauración masiva indebida.
- si arquitectura normativa sigue cerrada.

R0 sólo PASS si:
BASELINE_CAPTURED = YES
ARCHITECTURE_REOPENED = NO
WORKTREE_RESET = NO

==================================================
CHECK R1 — EVIDENCIA FÍSICA
==================================================

Inspeccionar implementación y tests.

Verificar:

A. source_artifact_ref
- uploaded bytes y local_path usan SHA-256 de bytes reales.
- local_path no usa basename/path/mtime/size como sustituto.
- formato estable xlsx:sha256:<digest> o equivalente exacto aprobado por docs.

B. workbook_ref
- deriva de artifact identity + ingestion scope + reader/schema version.
- no deriva de case_id/filename.

C. sheet_ref
- deriva de workbook_ref + exact sheet_name.
- no usa sheet1 implícito.

D. case_id
- sigue siendo workflow/case identity y no fuente física.

E. CanonicalIngestionOutput
- self-contained.
- no caller productivo completa/reinyecta datos canónicos luego de construcción.
- no alias nuevo.

F. Reader
- no segundo parser XLSX productivo.

==================================================
PRUEBAS ADVERSARIALES MÍNIMAS
==================================================

Ejecutar sólo si no fueron observadas con evidencia suficiente:

python -m pytest -q \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py

Comprobar casos:

1. same basename, different bytes => different artifact refs.
2. same bytes, renamed file => same artifact ref.
3. same artifact, different selected sheet scope => different workbook refs.
4. local_path hashes file bytes.
5. missing required sheet identity => fail closed.
6. no post-build canonical mutation.

==================================================
BÚSQUEDAS DE REGRESIÓN ARQUITECTÓNICA
==================================================

Buscar en código productivo tocado:

- new `sheet1` fallbacks;
- filename/basename used as workbook identity;
- path/mtime/size identity;
- new compatibility shim;
- new alias;
- second XLSX reader/parser;
- post-construction `ingestion_output[...] = ...` mutation para completar canonical fields;
- cambios prematuros de R2+.

==================================================
VEREDICTO
==================================================

PASS sólo si el código y tests demuestran todos los gates R1.

Si una afirmación del ejecutor no está probada:
FAIL_NOT_PROVEN.

Si aparece contradicción arquitectónica no contemplada:
BLOCKED_ARCHITECTURE.

Si sólo falta dependencia de entorno para una prueba:
BLOCKED_ENVIRONMENT.

No reparar nada.

==================================================
SALIDA OBLIGATORIA
==================================================

R0_R1_INDEPENDENT_VERIFICATION:

HEAD:
BRANCH:
FILES_CHANGED_BY_VERIFIER: NONE

R0:
BASELINE_CAPTURED:
ARCHITECTURE_REOPENED:
WORKTREE_RESET:
R0_VERDICT:

R1:
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

PHYSICAL_EVIDENCE:
TESTS_RUN:
TEST_RESULTS:

OUT_OF_SCOPE_CHANGES_FOUND:
UNPROVEN_CLAIMS:
BLOCKER:

FINAL_VERDICT:
PASS | FAIL | FAIL_NOT_PROVEN | BLOCKED_ARCHITECTURE | BLOCKED_ENVIRONMENT

NEXT_ALLOWED_NODE:
R2 sólo si FINAL_VERDICT = PASS.

FILES_CHANGED_BY_VERIFIER: NONE
COMMIT: NO
PUSH: NO
DEPLOY: NO
```
