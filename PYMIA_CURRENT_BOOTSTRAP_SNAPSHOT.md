# PYMIA_CURRENT_BOOTSTRAP_SNAPSHOT

```text
STATUS: MIRROR_SNAPSHOT_NON_NORMATIVE
SOURCE_OF_TRUTH: NOTION
PROJECT: PymIA
SCOPE: SERVICE 1
CURRENT_STATE_CUT: 2026-09-02
SNAPSHOT_GENERATED: 2026-09-02 15:37 ART
ACTIVE_NOP3: NOP3-S1-003
```

> **Propósito:** este archivo es un espejo de reentrada para chats, agentes o entornos que no tengan acceso a Notion.
> **No es una segunda fuente normativa.**
> Si Notion está disponible, debe prevalecer la lectura directa de las fuentes canónicas.
> Si este snapshot contradice Notion, **manda Notion**.
> Si existe evidencia de que este snapshot quedó desactualizado, el agente debe responder `BLOCKED_SOURCE_OF_TRUTH_UNAVAILABLE` para cualquier afirmación sobre CURRENT STATE hasta obtener una fuente vigente.

---

# 1. Fuentes canónicas de origen

## NOP-1 VIGENTE — 13 reglas constitucionales

```text
PAGE_ID: 3cc96ce8-a064-81cd-8fee-f3366dcfd811
STATUS: VIGENTE
RULE_COUNT: 13
```

## NOP-2 VIGENTE — SERVICE 1 CURRENT SPEC

```text
PAGE_ID: 3cc96ce8-a064-814c-a8c1-ec719a82cfe0
STATUS: VIGENTE
CUT: 2026-08-30
```

## SERVICE 1 — KNOWN STATE

```text
PAGE_ID: 3cc96ce8-a064-8127-b6d7-f94188b725ed
STATUS: KNOWN_STATE_CURRENT
CUT: 2026-08-31
```

## NOP_INDEX

```text
DATA_SOURCE: collection://97356721-335e-4254-99b3-f054fe0b0949
CURRENT_ROWS: 26
NOP1_VIGENTE: 13
NOP2_VIGENTE: 10
NOP3_SUPERSEDED: 2
ACTIVE_NOP3: 1
ACTIVE_NOP3_ID: NOP3-S1-003
ACTIVE_NOP3_SOURCE_PAGE_ID: 3cd96ce8-a064-813e-9c56-d95c6a0bb741
```

## Fuentes auxiliares

```text
GOLD_REGISTRY_PAGE_ID: 9a222a20311a41fa832a11b9cf1463d6
ARTIFACT_REGISTRY_PAGE_ID: c431e0685dce48e682ea6229ad2e02b6
ARTIFACT_REGISTRY_DATA_SOURCE: collection://877b0b7e-de36-4f9e-a0f8-a595f4516939
BITACORA_PAGE_ID: 3c996ce8-a064-81e3-8c40-c2819827e22e
```

---

# 2. Regla de reentrada

Al iniciar un chat o agente de PymIA:

```text
SI NOTION ESTÁ DISPONIBLE
→ leer NOP-1
→ leer NOP-2
→ leer KNOWN STATE
→ consultar NOP_INDEX por NOP-3 VIGENTE
→ si existe, leer su Source Notion Page completa

SI NOTION NO ESTÁ DISPONIBLE
→ leer este archivo completo
→ verificar que no haya señal de obsolescencia
→ usarlo como espejo de reentrada, no como autoridad superior

SI NOTION NO ESTÁ DISPONIBLE Y ESTE SNAPSHOT FALTA,
ESTÁ OBSOLETO O ES INCONSISTENTE
→ BLOCKED_SOURCE_OF_TRUTH_UNAVAILABLE
```

No reconstruir CURRENT STATE desde chats, prompts, memoria del modelo, README antiguos, auditorías históricas ni código legacy.

Reglas:

```text
CHAT != SPEC
PROMPT != SPEC
AUDIT != SPEC
ADR != CURRENT STATE
TEST HISTÓRICO != CURRENT PRODUCT STATE
```

---

# 3. Jerarquía de autoridad

## Autoridad normativa

```text
NOP-1 VIGENTE
→ NOP-2 VIGENTE
→ NOP-3 VIGENTE sólo para el cambio activo autorizado
```

`KNOWN STATE` es punto de reentrada operativa y está subordinado a NOP-1/NOP-2.

La evidencia no reescribe automáticamente la norma.

Si código/runtime/evidencia contradicen la spec vigente:

```text
STATE = NO_CONVERGENTE
```

---

# 4. NOP-1 — 13 invariantes constitucionales vigentes

## NOP1-C-001 — Evidencia antes que resultado

Servicio 1 sólo produce evaluaciones y hallazgos sustentados por evidencia disponible. Si una capacidad, formato o medida no está soportado, debe limitar o bloquear; nunca fabricar un resultado.

## NOP1-C-002 — Una única raíz productiva autorizada

Servicio 1 debe tener una sola raíz productiva y todas las superficies de entrada deben subordinarse a ella. No se permiten pipelines productivos paralelos con autoridad equivalente.

## NOP1-C-003 — Límites de autoridad del LLM

El LLM puede proponer significados, expresar incertidumbre y explicar. No puede validar por sí solo semántica ambigua, decidir matemática ni confirmar hallazgos o decisiones.

## NOP1-C-004 — Autoridad matemática determinística

La matemática crítica debe permanecer bajo una única autoridad determinística, tipada y reproducible. Fórmulas no soportadas, entradas inválidas o desvíos deben bloquear.

## NOP1-C-005 — Fail-closed

Ante ambigüedad material, conflicto, referencias inválidas, formatos no soportados o incapacidad de demostrar seguridad/computabilidad, Servicio 1 debe bloquear.

## NOP1-C-006 — Autoridad explícita del owner

La confirmación explícita del owner resuelve ambigüedad empresarial material. Ausencia de respuesta o alta confianza del modelo no equivalen a confirmación.

## NOP1-C-007 — Aislamiento por tenant

Datos, eventos, memoria y resultados deben quedar aislados por el tenant autenticado. Cualquier cruce o mismatch de tenant debe rechazarse de forma fail-closed.

## NOP1-C-008 — Provenance y evidencia append-only

Fuente, filas, relaciones, fórmulas y decisiones owner forman parte del resultado. La evidencia debe conservarse íntegra, verificable y append-only.

## NOP1-C-009 — Relaciones y joins gobernados

Las relaciones se gobiernan por identidad de fuente, grano y cardinalidad. Riesgo de fanout, duplicación o double-counting debe bloquear antes del cálculo.

## NOP1-C-010 — Ingestión canónica XLSX-first

La entrada canónica es XLSX-first, multi-sheet, con identidad de hoja preservada y una única lectura normalizada productiva.

## NOP1-C-011 — Findings como candidatos trazables

Los findings son candidatos sustentados por evidencia y reglas gobernadas, no diagnósticos autónomos del LLM.

## NOP1-C-012 — Reentrada e integridad del ResultSet

La memoria debe permitir recuperar exactamente el ResultSet con integridad verificable y contexto suficiente. Proyecciones incompletas deben declararse como brecha, no ocultarse.

## NOP1-C-013 — Web/UI/delivery como adapters

Web, UI y entrega solicitan análisis a la raíz autorizada y renderizan resultados. No pueden convertirse en una autoridad analítica paralela.

---

# 5. NOP-2 — SERVICE 1 CURRENT SPEC

## Matriz de convergencia vigente

| Área | Estado | Autoridad / frontera vigente | Brecha vigente |
|---|---|---|---|
| Product Intent | PARTIAL | Laboratorio operacional XLSX/tabular, evidence-governed y owner-assisted | El intent excede algunas proyecciones actuales |
| Product Root | PARTIAL | `pymia/smartpyme/service_1_product_pipeline_v1.py` | Subordinación total de superficies/reentry/delivery no demostrada universalmente |
| Ingestion | PARTIAL | XLSX-first, parser normalizado único, identidad multi-sheet | Cobertura de layouts reales todavía limitada |
| Semantics | PARTIAL | Comprensión gobernada; LLM propone; owner resuelve ambigüedad material | Cobertura horizontal no universal |
| Owner/HITL | YES | Confirmación explícita del owner | Sin brecha material declarada en perímetro cerrado |
| Relationships/JOIN | YES | Cardinalidad/fanout gobernados; P8 computabilidad; F7 join | Sin brecha material declarada en perímetro cerrado |
| Mathematics | PARTIAL | F8 + `FormulaEngineService` | Catálogo de medidas/fórmulas incompleto |
| Findings | PARTIAL | F9 / findings trazables | `ActionableFinding` y proyección incompletos |
| Persistence/Memory | PARTIAL | F13 / Result Memory | Proyección longitudinal/F9 completa no demostrada |
| Delivery/UI | PARTIAL | Web/entrega como adapters/renderers | Gaps de historial/período y entrega descargable |

Totales:

```text
YES: 2
PARTIAL: 8
NO: 0
```

---

# 6. Autoridades productivas conocidas

## Entrada / ingestión

```text
CANONICAL_INPUT: XLSX
CANONICAL_PARSER:
pymia/smartpyme/service_1_xlsx_to_normalized_table_v1.py
```

- Una única ingestión normalizada.
- Identidad multi-sheet preservada.
- Ambigüedad física relevante bloquea antes de semántica.

## Product Root

```text
ROOT:
pymia/smartpyme/service_1_product_pipeline_v1.py

CANONICAL_CALLABLE:
run_service_1_product_pipeline_v1

CLI_ADAPTER:
pymia/cli/service_1_product.py
```

No existe una segunda raíz productiva autorizada.

## Semántica / LLM

El LLM:
- puede proponer significados;
- puede expresar incertidumbre;
- puede redactar explicaciones.

El LLM no:
- calcula matemática crítica;
- valida solo una semántica ambigua;
- auto-confirma;
- se convierte en autoridad factual final.

## Owner / HITL

```text
NO_RESPONSE != ACCEPTANCE
HIGH_CONFIDENCE != OWNER_CONFIRMATION
```

El owner puede corregir la propuesta. La confirmación relevante debe conservarse como evidencia.

## Relaciones / JOIN

- La coincidencia nominal de columnas no autoriza una relación.
- Fuente, grano y cardinalidad gobiernan.
- Fanout/double-counting bloquea.
- P8 gobierna computabilidad.
- F7 materializa el join autorizado.

## Matemática

```text
AUTHORITY:
F8 + FormulaEngineService
```

No se autoriza:
- segundo motor matemático;
- matemática crítica en LLM;
- fórmula ad hoc no gobernada.

## Findings

Finding = candidato trazable.

F9 no puede inventar:
- causalidad;
- severidad;
- recomendaciones arbitrarias.

## Persistence / Memory

Result Memory conserva identidad, tenant, integridad y ResultSet.

La reentrada exacta del ResultSet pertenece a Servicio 1.

No se presume completa una experiencia histórica/longitudinal más amplia.

## Delivery / UI

Web/UI/entrega:
- piden análisis a la raíz autorizada;
- renderizan resultados;
- no coordinan una segunda lógica analítica.

---

# 7. Estado consolidado vigente

```text
NOP-1: VIGENTE
NOP-2: VIGENTE
ACTIVE_NOP3: 1
ACTIVE_NOP3_ID: NOP3-S1-003
ACTIVE_NOP3_SCOPE: SERVICE 1 — reparación causal del flujo real end-to-end

KNOWN_STATE: CURRENT / content synchronized 2026-09-02

M4_DOCUMENTARY_CLEANUP: CLOSED
M5_ENTRY_INTO_REGIME: ENABLED

GOLD_REGISTRY:
394 unique claims

NOP_INDEX:
26 rows
13 NOP-1 VIGENTE
10 NOP-2 VIGENTE
2 NOP-3 SUPERSEDED
1 NOP-3 VIGENTE
```

## NOP-3 activo

```text
NOP3-S1-003
SERVICE_1_REAL_FLOW_REPAIR
STATUS: VIGENTE
SOURCE_PAGE_ID: 3cd96ce8-a064-813e-9c56-d95c6a0bb741
AUTHORITY_SCOPE: SERVICE 1 — reparación causal del flujo real end-to-end
CURRENT_CONVERGENCE: PARTIAL
SUPERSEDES: NOP3-S1-002
```

### Objetivo autorizado

Restaurar localmente el flujo real de Servicio 1:

```text
login
→ autenticación / tenant
→ POST /upload
→ XLSX ingestion
→ semántica / owner confirmation cuando corresponda
→ Product Root
→ análisis
→ resultado
```

### Evidencia de partida

1. Runtime/config no convergente:
   `PYMIA_SUPABASE_*` esperado por código frente a nombres locales legacy `SUPABASE_*`.

2. Web/catálogo/tests con referencias legacy:
   - `sold_vs_collected_gap`
   - `net_margin_real`
   - `working_capital`

   Evidencia focal declarada:

   ```text
   9 failed / 3 passed
   ```

3. Error real visible:

   ```text
   No se pudo leer el envío. Probá de nuevo.
   ```

   La causa funcional final debe reproducirse después de restaurar un runtime local legítimo.

### Reglas de reparación

- lectura amplia permitida dentro de Servicio 1 sólo por causalidad;
- modificación multiarchivo permitida sólo con justificación causal por archivo;
- una única raíz productiva;
- una única ingestión XLSX canónica;
- una única autoridad matemática determinística;
- LLM sin autoridad matemática ni semántica final;
- fail-closed;
- tenant isolation;
- sin hardcodes por rubro/tenant;
- sin segundo pipeline, parser o motor;
- sin aliases/fallbacks de compatibilidad que oculten divergencias;
- tests/oráculos no se debilitan para forzar PASS;
- secretos no se exponen.

### Gates autorizados

```text
A — runtime/config legítimo
B — Web/catálogo/tests convergentes
C — reproducción del flujo real
D — reparación del primer bloqueo causal real
E — demostración E2E
```

PASS final requiere demostrar:

```text
login
→ auth/tenant
→ POST /upload
→ XLSX ingestion
→ semántica/owner confirmation cuando aplique
→ Product Root
→ análisis
→ resultado
```

más tests focales convergentes y:

```text
NEW_PRODUCT_ROOTS = 0
NEW_XLSX_PARSERS = 0
NEW_MATH_ENGINES = 0
SECRET_EXPOSURE = NO
UNAUTHORIZED_FILES = NONE
```

### Git / deploy

```text
GIT: NOT_AUTHORIZED
WORKTREE_ACTIONS: NOT_AUTHORIZED
COMMIT: NOT_AUTHORIZED
PUSH: NOT_AUTHORIZED
PR: NOT_AUTHORIZED
MERGE: NOT_AUTHORIZED
DEPLOY: NOT_AUTHORIZED
```

Cualquier acción Git requiere decisión owner separada.

### Checkpoint técnico C2 — 2026-09-02

```text
C2_F0_F11: CONVERGENTES
C2_F12: PASS_INDEPENDIENTE
FOCAL_TESTS: 94/94
BLOCKERS_MATERIALES: NONE
LEGACY_BUILDER_PRODUCTIVE_REFERENCES: 0
LEGACY_BUILDER_CALLS_PER_PROVIDER_INVOCATION: 0
SECOND_SEMANTIC_ENGINE_PRODUCTIVE: NO
```

Consecuencia gobernada:
- C2 queda técnicamente convergente dentro del perímetro F0–F12 reportado.
- El builder lexical legacy no conserva autoridad productiva dentro del perímetro verificado.
- No corresponde abrir otra fase técnica de C2 por inercia.
- `Semantics` permanece `PARTIAL` en NOP-2 porque la cobertura horizontal no se declara universal.
- Este checkpoint **no cierra `NOP3-S1-003`**: el Change Contract exige evidencia E2E explícita de login real, tenant validado, upload XLSX real, ingestión canónica alcanzada, owner confirmation cuando aplique, Product Root alcanzado, análisis completado y resultado observado.

Evidencia registrada en Notion:
`EVIDENCE — SERVICE 1 C2 F12 post-F10 independent recheck — PASS — 2026-09-02`.

Artefacto físico declarado:
```text
docs/current/SERVICE_1_C2_F12_POST_F10_INDEPENDENT_RECHECK_EVIDENCE_V1.md
```

---

## NOP-3 anteriores

```text
NOP3-S1-002
Diagnóstico observable de error POST /upload
STATUS: SUPERSEDED
SUPERSEDED_BY: NOP3-S1-003
```

Su evidencia diagnóstica se conserva como historia/evidencia. Ya no autoriza trabajo nuevo.

```text
NOP3-S1-001
Current Tenant GET Authorization
STATUS: CLOSED_AND_ABSORBED
```

Cerró la revalidación de identidad actual en GET sensibles:

```text
/download-sales-collections
/download-net-margin
/download-reconciliation-workpaper
```

Evidencia reportada:

```text
26 passed / 0 failed
CROSS_TENANT_REJECTED: YES
STALE_SESSION_REJECTED: YES
CURRENT_IDENTITY_REVALIDATED: YES
```

Esta brecha está cerrada. `Delivery/UI` permanece `PARTIAL` por otras brechas.

---

# 8. Brechas abiertas oficiales

Estas brechas existen, pero **no constituyen autorización automática de trabajo**:

1. Product Intent — PARTIAL.
2. Product Root — PARTIAL.
3. Ingestion — PARTIAL.
4. Semantics — PARTIAL.
5. Mathematics — PARTIAL.
6. Findings — PARTIAL.
7. Persistence/Memory — PARTIAL.
8. Delivery/UI — PARTIAL.

El owner decide cuál problema abordar.

No abrir NOP-3 automáticamente.

---

# 9. Régimen obligatorio de cambio

Todo cambio material:

```text
PROBLEMA / DECISIÓN OWNER
→ CHECK CONTRA NOP-1
→ UN NOP-3 / CHANGE CONTRACT
→ IMPLEMENTACIÓN ACOTADA
→ EVIDENCIA
→ CONVERGENCIA
→ ABSORCIÓN EN NOP-2
→ ACTUALIZACIÓN DE KNOWN STATE
→ CIERRE/SUPERSEDE DEL NOP-3
→ STOP
```

Regla operacional:

```text
UNA TAREA
→ UNA VERIFICACIÓN
→ UN RESULTADO
→ UNA DECISIÓN
→ STOP
```

Una tarea no autoriza automáticamente la siguiente.

---

# 10. Desarrollo con IA / antideriva

Documento metodológico de origen:

```text
PAGE_ID:
3cd96ce8-a064-817a-bc49-d62700bb2402

STATUS:
NON_NORMATIVE
```

Principios de trabajo:

- la IA nunca amplía su propio mandato;
- Implementer != Verifier;
- salir del perímetro => `BLOCKED` + STOP;
- mejora arquitectónica no solicitada => scope violation;
- no modificar tests/oráculos para hacer pasar una implementación;
- contexto mínimo autorizado;
- controlar blast radius;
- evidencia estructurada;
- verificación independiente;
- proteger deriva de intención;
- proteger deriva arquitectónica;
- proteger deriva semántica;
- proteger coherencia sistémica acumulativa.

La función constitucional ya pertenece a NOP-1.

No crear otra `CONSTITUTION` paralela.

ADR conserva razones/historia, subordinado a NOP vigente.

---

# 11. Arquitectura modular / verticales

Propuesta conceptual de origen:

```text
PAGE_ID:
3cd96ce8-a064-8145-8609-e464a2d715f7

STATUS:
PROPOSAL_CONCEPTUAL
NON_NORMATIVE
NOT_IMPLEMENTED
```

Tesis conceptual:

```text
PYMIA CORE
+
VERTICAL CAPABILITY PACK
+
TENANT PROFILE
```

Objetivo:
- Core horizontal;
- verticales con semánticas, fórmulas declarativas, findings y diálogo propios;
- misma ingestión;
- misma raíz productiva;
- misma autoridad matemática;
- módulos verticales aislados;
- Ports & Adapters / contratos como frontera;
- Fitness Functions para evitar corrupción de dependencias.

Esta propuesta **no está implementada** y no autoriza refactor sin un futuro NOP-3.

---

# 12. Git / GitHub

Fuera de alcance por defecto.

No:
- consultar repositorios por iniciativa propia;
- revisar ramas/commits;
- branch;
- commit;
- push;
- PR;
- merge;
- deploy.

Sólo con autorización explícita del owner para esa acción concreta.

---

# 13. OpenCode / ejecución local

Los cambios físicos locales se ejecutan mediante OpenCode/local cuando el owner lo disponga.

ChatGPT:
- define microtask;
- fija perímetro;
- define PASS/BLOCKED;
- revisa salida;
- contrasta contra NOP;
- actualiza Notion cuando corresponda.

Todo prompt de ejecución debe tener:

```text
ONE_MICROTASK
ALLOWED_SCOPE
FORBIDDEN_SCOPE
PASS_CRITERIA
BLOCKED_CRITERIA
NO_COMMIT_PUSH_DEPLOY
STOP_AFTER
```

Si necesita salir del perímetro:

```text
BLOCKED
STOP
```

---

# 14. Señales que invalidan este snapshot

Este snapshot debe considerarse obsoleto si ocurre cualquiera de estas condiciones:

- se promueve o modifica NOP-1;
- se absorbe un cambio nuevo en NOP-2;
- cambia `KNOWN STATE`;
- se abre un NOP-3 VIGENTE;
- se cierra o supersede un NOP-3 que estaba activo;
- el owner informa un cambio de CURRENT STATE posterior al 2026-08-31;
- existe una fuente de Notion con fecha/corte posterior incompatible con este archivo.

Ante cualquiera de estas señales:

```text
SNAPSHOT_STATUS = STALE
```

Si Notion no está disponible:

```text
BLOCKED_SOURCE_OF_TRUTH_UNAVAILABLE
```

hasta reemplazar este archivo por un snapshot vigente.

---

# 15. Regla de mantenimiento

Debe existir **un solo snapshot activo** con este nombre:

```text
PYMIA_CURRENT_BOOTSTRAP_SNAPSHOT.md
```

Cuando cambie CURRENT STATE:

1. leer fuentes canónicas de Notion;
2. regenerar este archivo;
3. reemplazar la versión anterior;
4. no mantener dos snapshots activos;
5. registrar la nueva fecha de corte;
6. verificar que `ACTIVE_NOP3` sea correcto.

---

# 16. Principio final

Este archivo no existe para que una IA “recuerde PymIA”.

Existe para que un chat sin Notion pueda volver a una **fotografía gobernada y explícita del estado vigente**, sin reconstruirlo desde memoria, historia o documentos superseded.

```text
NOTION = SOURCE OF TRUTH
THIS FILE = GOVERNED REENTRY MIRROR
MEMORY / CHAT / HISTORY = NOT CURRENT STATE AUTHORITY
```

---

## Snapshot integrity

```text
BODY_SHA256_BEFORE_THIS_SECTION: e597ea5971c6ebd5b82a359a22d0e9dba3fd5a0406299dd923ca6c8a9ee59caa
```
