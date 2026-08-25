# Prompt ejecutor — Servicio 1 — R0 + R1 V1

**Uso:** Codex / OpenCode / agente de implementación con acceso read-write al repo.  
**Modo:** implementación acotada, sin rediseño arquitectónico.  

```text
REPO:
E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria

BRANCH ESPERADA:
work/service1-cafeteria-flow-v1

ROL:
Ejecutor de reconstrucción de Servicio 1.

La arquitectura está cerrada. No la rediseñes.
No busques una alternativa mejor. Implementá exactamente el primer nodo incompleto autorizado por el plan vigente.

==================================================
LECTURA OBLIGATORIA ANTES DE EDITAR
==================================================

Leer completos y en este orden:

1. AGENTS.md
2. ARCHITECTURE_GUARDRAILS.md
3. docs/current/SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md
4. docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
5. docs/current/SERVICE_1_CANONICAL_AXIS.md
6. docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
7. docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
8. docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md
9. docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
10. docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md

No usar documentos de auditoría/dialéctica como autoridad si contradicen los rectores.

==================================================
AUTORIZACIÓN
==================================================

Autorizado:
- R0 completo.
- R1 completo si R0 no detecta bloqueo.
- modificar sólo código/tests/docs estrictamente necesarios para R1.
- ejecutar L0/L1/L2/L3 acotados.

No autorizado:
- R2 o posteriores.
- full suite.
- commit.
- push.
- deploy.
- reset masivo.
- wrappers de compatibilidad nuevos.
- aliases nuevos.
- fallbacks nuevos.
- rediseño de arquitectura.

==================================================
R0 — BASELINE LOCK
==================================================

1. Ejecutar:
   git status --short
   git rev-parse HEAD
   git branch --show-current

2. Registrar el worktree recibido.
3. No restaurar ni borrar cambios existentes por defecto.
4. Confirmar documentalmente:
   OPEN_ARCHITECTURAL_DECISIONS = 0
   TARGET_ARCHITECTURE_CLOSED = YES
5. Confirmar:
   COMMIT = NO
   PUSH = NO
   DEPLOY = NO

Si aparece una contradicción entre código y target conocida por el delta, NO es bloqueo: forma parte de la reconstrucción.

Si aparece una contradicción arquitectónica no contemplada:
STOP_ARCHITECTURE y no editar runtime.

R0 PASS obligatorio:
BASELINE_CAPTURED = YES
ARCHITECTURE_REOPENED = NO
WORKTREE_RESET = NO

==================================================
R1 — IDENTIDAD + CANONICAL INGESTION FOUNDATION
==================================================

Trabajar sólo sobre R1 del documento:
docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md

Archivos primarios:

pymia/smartpyme/service_1_web_column_confirmation_intake_boundary_v1.py
pymia/smartpyme/service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
pymia/smartpyme/service_1_workbook_logical_model_v1.py
pymia/smartpyme/service_1_workbook_schema_identity_v1.py
pymia/smartpyme/pipeline_registration.py

Callers/tests vecinos sólo si son necesarios para el contrato R1.

CONTRATO OBLIGATORIO:

A. source_artifact_ref
- formato: xlsx:sha256:<digest>
- uploaded_bytes: SHA-256 de bytes reales.
- local_path: SHA-256 streaming del archivo real.
- no basename/path/mtime/size como identidad.

B. workbook_ref
- identidad determinística derivada de:
  source_artifact_ref
  + ingestion_scope
  + canonical reader/schema version
- misma fuente + mismo scope => mismo workbook_ref.
- misma fuente + scope diferente => workbook_ref distinto.

C. sheet_ref
- derivado de workbook_ref + exact sheet_name.
- no fallback sheet1.
- evidencia faltante requerida => fail closed.

D. case_id
- identidad de workflow/caso.
- no usar como identidad física del workbook.

E. filename
- display/provenance únicamente.

F. CanonicalIngestionOutput V2
- debe permanecer self-contained.
- no permitir post-construction mutation para completar campos canónicos.
- no crear aliases nuevos.
- aliases viejos con consumers se retiran recién en R10.

G. XLSX reader
- no crear segundo parser/reader.
- reutilizar infraestructura existente de hashing cuando corresponda.

==================================================
PRUEBAS OBLIGATORIAS
==================================================

L0:
- compile/import de módulos tocados.

L1:
python -m pytest -q \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py

L2:
Agregar/actualizar tests focales que prueben físicamente:

1. mismo basename + bytes distintos => source_artifact_ref distinto.
2. mismos bytes + filename distinto => source_artifact_ref igual.
3. mismos bytes + scope de sheets distinto => workbook_ref distinto.
4. filename no participa como structural identity.
5. local_path usa bytes reales.
6. sheet identity explícita.
7. ausencia de sheet requerida => fail closed, no sheet1.
8. no post-build canonical envelope mutation.

L3:
Ejecutar sólo vecinos directamente afectados por los imports/callers modificados.
No full suite.

==================================================
REGLAS DE IMPLEMENTACIÓN
==================================================

- Preferir modificar contratos/módulos existentes antes que crear componentes nuevos.
- No introducir un IdentityEngine nuevo si helpers puros o contratos existentes alcanzan.
- No tocar semántica, math, P8/F7, Consorcios, ResultRead ni registry salvo import mínimo inevitable.
- No migrar comportamiento de R2+ anticipadamente.
- Si un test legacy contradice el target, no parchear runtime para satisfacerlo: clasificar el test y reportarlo.
- Cada cambio debe reducir o mantener entropía; nunca aumentarla.

==================================================
EXIT GATES R1
==================================================

CONTENT_ADDRESSED_SOURCE_ARTIFACT = PASS
LOCAL_PATH_CONTENT_HASH = PASS
NO_FILENAME_AS_STRUCTURAL_IDENTITY = PASS
WORKBOOK_IDENTITY_FROM_ARTIFACT_SCOPE = PASS
SHEET_REF_EXPLICIT = PASS
NO_NEW_SHEET1_FALLBACK = PASS
CANONICAL_INGESTION_SELF_CONTAINED = PASS
NO_POST_BUILD_CANONICAL_MUTATION = PASS
SECOND_XLSX_READER_ADDED = NO
NEW_COMPATIBILITY_SHIM = NO
NEW_ALIAS = NO

Si cualquiera falla:
R1 = FAIL/BLOCKED y detenerse. No avanzar a R2.

==================================================
SALIDA OBLIGATORIA
==================================================

R0_R1_EXECUTION_RESULT:

HEAD:
BRANCH:
R0_VERDICT:
R1_VERDICT:

FILES_CHANGED:

IDENTITY_CONTRACT:
SOURCE_ARTIFACT_REF:
WORKBOOK_REF:
SHEET_REF:
CASE_ID_ROLE:
FILENAME_ROLE:

TESTS_RUN:
TEST_RESULTS:

ARCHITECTURE_GATES:
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

LEGACY_TEST_CONFLICTS:
UNRESOLVED_BLOCKER:
NEXT_ALLOWED_NODE:

COMMIT: NO
PUSH: NO
DEPLOY: NO

No incluir recomendaciones para R2 salvo NEXT_ALLOWED_NODE = R2 si R1 PASS.
```
