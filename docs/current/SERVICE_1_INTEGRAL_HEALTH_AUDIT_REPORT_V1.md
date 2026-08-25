# Servicio 1 — Informe de Auditoría Integral de Salud V1

**Estado:** `CLOSED_AUDIT_EVIDENCE / SUPERSEDED_FOR_TARGET_DECISIONS`  
**Fecha:** 2026-08-23  
**Autoridad:** `EVIDENCE_ONLY` — los hallazgos físicos se conservan; las decisiones target finales están en CANONICAL_AXIS / ARCHITECTURE_LOCK y el handoff ejecutable.  
**Baseline:** `8d5708e9becdddaa5aa24387b310972643d1ef86` + worktree local no committeado.  

## 1. Propósito

Consolidar y revisar críticamente la primera auditoría forense ejecutada por Codex contra el plan `SERVICE_1_INTEGRAL_HEALTH_AUDIT_PLAN_V1.md`, separando:

- evidencia física confirmada;
- conclusiones todavía no suficientemente demostradas;
- clasificaciones incorrectas o demasiado amplias;
- requisitos de auditoría omitidos;
- condiciones necesarias antes de diseñar ciclos de reconstrucción.

Este documento no autoriza reparación, refactor, commit, push ni deploy.

## 2. Veredicto provisional

La salida primaria de Codex concluyó:

```text
SERVICE_1_INTEGRAL_HEALTH_VERDICT: FAIL_ARCHITECTURE_NOT_CERTIFIED
```

Ese veredicto general es compatible con la evidencia revisada. Sin embargo, **la auditoría integral todavía no está cerrada** porque la ejecución no cubrió todos los requisitos del plan vigente y algunas clasificaciones necesitan depuración antes de convertirse en decisiones de reconstrucción.

Estado de este informe:

```text
INTEGRAL_HEALTH: FAIL / NOT_CERTIFIED
AUDIT_FORENSIC_PRIMARY: COMPLETED
AUDIT_PROMPTS: MISSING
AUDIT_ARCHITECTURAL_CROSSCHECK: IN_PROGRESS
ARCHITECTURE_DELTA_LEDGER: NOT_FINAL
WORKTREE_DECISION_LEDGER: NOT_FINAL
READY_FOR_RECONSTRUCTION: NOT_YET
READY_FOR_CERTIFICATION: NO
```

## 3. Evidencia primaria reportada por Codex

Codex reportó, entre otros:

```text
ONE_PRODUCTIVE_ROOT: PASS scoped
ONE_PRODUCTIVE_XLSX_READER: PASS scoped
WORKBOOK_D1_D7_MANDATORY: PASS for WORKBOOK
D7_EVIDENCE_ONLY: PASS
ONE_PRODUCTIVE_D7_CALLER: PASS
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE: FAIL
NO_SHEET1_FALLBACK: FAIL
NO_PRODUCTIVE_LEGACY_SHIMS: FAIL
NO_TRANSITIONAL_ALIASES: FAIL
MODULE_REGISTRY_COMPLETE: FAIL
F13_NO_RECALCULATION: PASS
NO_LLM_MATH: PASS
```

También reportó:

```text
ARCHITECTURE_TESTS: 124 passed / 0 failed
FULL_SUITE: 3806 passed / 77 failed / 7 skipped / 3 errors
```

Los 3 errores E2E fueron atribuidos a Chromium ausente. Esta full suite se conserva como evidencia de este worktree, pero **no debe repetirse durante cada ciclo de saneamiento**.

## 4. Hallazgos físicamente cross-checkeados

### 4.1 Semantic legacy sigue productivo — CONFIRMADO

Callers físicos actuales de `resolve_service_1_legacy_semantic_run_v1`:

```text
pymia/cli/service_1_product.py:111
pymia/smartpyme/service_1_assisted_web_v1.py:2276
```

Por tanto:

```text
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE: FAIL
NO_PRODUCTIVE_LEGACY_SHIMS: FAIL
```

La existencia del shim no es sólo histórica o de tests; tiene callers productivos reales.

### 4.2 CLI recompone el CanonicalIngestionOutput — CONFIRMADO

El CLI hace actualmente:

```text
ingestion_output = dict(connector["ingestion_output"])
normalized_tables = boundary.get("normalized_tables")
if isinstance(normalized_tables, list):
    ingestion_output["normalized_tables"] = normalized_tables
```

Luego resuelve semántica legacy y usa `sheet_name or "sheet1"`.

Esto contradice la regla normativa vigente según la cual un caller productivo no debe completar ni recomponer el envelope después del constructor canónico.

Clasificación correcta provisional:

```text
CONTRACT_VIOLATION
CANONICAL_ENVELOPE_MUTATION
```

No debe clasificarse automáticamente como `AUTHORITY_COLLISION`: mutar un contrato canónico y duplicar una autoridad son defectos distintos.

### 4.3 `sheet1` productivo — CONFIRMADO

La auditoría primaria reporta diez ocurrencias productivamente relevantes, incluyendo CLI, Product Root, semantic legacy, P6 y owner reentry.

Los callers CLI/web legacy fueron verificados físicamente.

Por tanto:

```text
NO_SHEET1_FALLBACK: FAIL
```

La auditoría de cada ocurrencia debe conservar la distinción `fallback de identidad` vs `valor de compatibilidad no productivo` para no eliminar mecánicamente strings sin entender su función.

### 4.4 D4 → F7 provenance incompleta — CONFIRMADO COMO GAP

En `service_1_analysis_evidence_preparation_v1.py`, `_validate_relationship_bindings` valida actualmente:

```text
relationship_ref
confirmed_by_owner
absence of forbidden authority flags
left/right sheet refs
left/right column refs
relationship_kind
```

No se observa allí validación completa de:

```text
d4_graph_ref
schema fingerprint
D4 relationship status RESOLVED
fanout certificate
read-only dereference against the authoritative D4 graph
```

Por tanto la conclusión correcta es:

```text
D4_TO_F7_PROVENANCE_ENFORCEMENT: INCOMPLETE / NOT_PROVEN
```

Esto no constituye por sí mismo una segunda autoridad de joins. Es un **provenance/enforcement gap**.

### 4.5 Registry incompleto — EVIDENCIA CONSISTENTE

La auditoría primaria reporta:

```text
LIVE_PYTHON_MODULES: 112
REGISTERED: 101
MISSING: 11
```

El inventario físico actual de `service_1_*` bajo `pymia/smartpyme` es consistente con 112 módulos Python más archivos estáticos/template que comparten prefijo.

El registry debe reconciliarse sólo después de cerrar la clasificación arquitectónica de cada módulo; no antes.

## 5. Hallazgo que requiere redefinición antes de aceptarse

### 5.1 `F8_ONLY_MATH_AUTHORITY: FAIL global` — NO ACEPTAR TODAVÍA COMO CLASIFICACIÓN FINAL

Existe matemática física fuera de F8. Ejemplo confirmado:

`service_1_liq_001_evaluator_v1.py` agrega valores de filas mediante `Decimal` antes de evaluar LIQ_001.

Sin embargo, el `SERVICE_1_ARCHITECTURE_LOCK.md` contiene actualmente dos formulaciones que deben reconciliarse:

1. sección histórica de ejecución productiva: conserva LIQ_001 y REN_001 como excepciones especializadas justificadas;
2. sección `13.6 Authority lock`: declara `F8 = math authority`.

Por tanto primero debe documentarse una definición exacta de `math authority` que distinga al menos:

```text
numeric parsing/normalization
bounded evidence aggregation
formula/business computation
classification
specialized historical evaluator
canonical F8 execution
```

Hasta resolver esta contradicción normativa no debe ordenarse una migración masiva de toda operación `Decimal` hacia F8 ni declararse simplemente `PRODUCTIVE_MATH_AUTHORITY_COUNT = 2`.

Estado correcto provisional:

```text
F8_ONLY_MATH_AUTHORITY: NOT_PROVEN / NORMATIVE_SCOPE_CONTRADICTION
```

## 6. Clasificaciones de la auditoría primaria que deben depurarse

### 6.1 `AUTHORITY_COLLISION_COUNT = 3`

No debe aceptarse literalmente.

Los tres hechos agrupados no pertenecen necesariamente a la misma categoría:

```text
CLI envelope mutation          = contract violation
D4→F7 provenance gap           = evidence/provenance enforcement gap
specialized math outside F8    = possible authority overlap, pending definition
```

La auditoría final debe contar `AUTHORITY_COLLISION` sólo cuando dos componentes puedan tomar soberanamente la misma decisión de dominio/runtime.

### 6.2 `READY_FOR_RECONSTRUCTION: YES`

Debe degradarse a:

```text
READY_FOR_RECONSTRUCTION: NOT_YET
```

Razones:

- falta auditoría de prompts;
- falta Prompt Decision Ledger;
- falta cerrar la definición normativa de autoridad matemática;
- Architecture Delta Ledger todavía no está revisado;
- Worktree Decision Ledger todavía no está revisado;
- varias clasificaciones requieren separación semántica.

### 6.3 `ONE_CANONICAL_INGESTION: PARTIAL / FAIL`

Para gates arquitectónicos finales debe normalizarse a:

```text
FAIL
```

La existencia de un constructor canónico no alcanza mientras un caller productivo pueda recomponer su output. `PARTIAL` puede usarse como explicación, no como valor final del gate.

## 7. Requisito omitido: auditoría de prompts

La salida primaria no contiene ninguna sección `PROMPT`, `Prompt Decision Ledger` ni `NO_UNDOCUMENTED_PROMPT_ARCHITECTURE`.

El plan vigente exige analizar:

```text
PROMPT_REFERENCE
ARCHITECTURAL_DECISION_IMPLIED
PRE_DOCUMENTED
RESULTING_CHANGE
RESULTING_TEST_CHANGE
ENTROPY_EFFECT
CLASSIFICATION
CORRECTIVE_GOVERNANCE_ACTION
```

Por tanto:

```text
AUDIT_PROMPTS: MISSING
NO_UNDOCUMENTED_PROMPT_ARCHITECTURE: NOT_PROVEN
```

La auditoría integral no puede cerrarse hasta ejecutar esta pasada sobre los prompts relevantes de la convergencia reciente.

## 8. Full suite — política

La full suite ejecutada por Codex queda registrada como evidencia del estado actual:

```text
3806 passed
77 failed
7 skipped
3 errors
```

No se autoriza repetirla por cada hallazgo o ciclo local.

La secuencia de reconstrucción utilizará:

```text
L0 syntax/import
L1 focal contract
L2 architecture/authority guards
L3 bounded neighbor regression
L4 integration checkpoint
L5 full suite only at meaningful convergence checkpoint
L6 real XLSX E2E
```

## 9. Próximo paso permitido

No implementar reparaciones.

Completar únicamente:

1. auditoría de prompts y Prompt Decision Ledger;
2. cross-check dirigido de findings críticos todavía `NOT_PROVEN`;
3. Architecture Delta Ledger depurado;
4. Worktree Decision Ledger depurado;
5. dependency graph de saneamiento;
6. actualizar documentos normativos sólo para decisiones arquitectónicas explícitamente resueltas.

Después de estos pasos podrá definirse la secuencia real de reconstrucción.

## 10. Estado

```text
SERVICE_1_INTEGRAL_HEALTH: FAIL / NOT_CERTIFIED
PRIMARY_FORENSIC_AUDIT: USEFUL_BUT_INCOMPLETE
PHYSICAL_CROSSCHECK: PARTIAL_COMPLETE
PROMPT_AUDIT: MISSING
MATH_AUTHORITY_SCOPE: UNRESOLVED_NORMATIVE_CONTRADICTION
FULL_SUITE: OBSERVED_ONCE / DO_NOT_REPEAT_PER_CYCLE
RECONSTRUCTION: FROZEN
CERTIFICATION: NOT_READY
```


## 11. Red-team independiente Qwen — 2026-08-23

Qwen ejecutó una revisión adversarial read-only sobre la auditoría primaria y el repositorio. El red-team confirma el veredicto general `FAIL / NOT_CERTIFIED`, pero corrige varias clasificaciones y evita convertir defectos distintos en una sola categoría.

### 11.1 Hallazgos confirmados por dos revisiones independientes

```text
ONE_PRODUCTIVE_SEMANTIC_STATE_MACHINE: FAIL
NO_PRODUCTIVE_LEGACY_SHIMS: FAIL
ONE_CANONICAL_INGESTION: FAIL
NO_SHEET1_FALLBACK: FAIL
D4_TO_F7_PROVENANCE: PARTIAL / INCOMPLETE
MODULE_REGISTRY_COMPLETE: FAIL
```

Evidencia convergente:

- `service_1_legacy_semantic_reentry_compat_v1.py` tiene callers productivos en CLI y web;
- CLI muta/recompone el envelope luego del constructor canónico;
- existen fallbacks `sheet1` alcanzables en semántica legacy/owner flow;
- F7 materializa joins pero no valida todavía provenance completa contra el grafo D4 autoritativo;
- el registry no representa todos los módulos live actuales.

### 11.2 Clasificaciones corregidas por red-team

```text
CLI envelope mutation       → CONTRACT_VIOLATION
D4→F7 incomplete checking   → PROVENANCE_GAP / CONTRACT_GAP
legacy semantic shim        → LEGACY_PRODUCTIVE
assisted vs deterministic   → PARALLEL_PRODUCTIVE_PATH
registry omissions          → REGISTRY_DRIFT hasta clasificar cada módulo
math outside F8             → NOT_PROVEN / DOCUMENTATION_CONTRADICTION
```

`AUTHORITY_COLLISION` se reserva para dos componentes con soberanía real sobre la misma decisión. El red-team no demostró una colisión estricta actual y propone `AUTHORITY_COLLISIONS: 0 strict` hasta nueva evidencia.

### 11.3 Product Root

Qwen confirma entropía elevada de interfaz, pero evita usar el número de kwargs como prueba suficiente. La conclusión relevante es:

```text
PRODUCT_ROOT_REDESIGN_REQUIRED: YES
```

porque conviven inputs de dominio, dependencies, flags procedurales, compatibilidad legacy y modos mutuamente excluyentes en una misma firma. Especialmente quedan bajo revisión:

```text
analysis_execution_request
semantic_reception_only
semantic_atomic_confirmation
semantic_run_override
owner_answers
sheet_name
```

### 11.4 Matemática — decisión normativa pendiente

El red-team refuta la inferencia `Decimal usage = segunda autoridad matemática`.

Distingue:

```text
numeric parsing
normalization
evidence aggregation
business formula execution
result classification
```

Confirma además una contradicción documental entre:

- `SERVICE_1_ARCHITECTURE_LOCK.md` §5: excepciones especializadas históricas LIQ_001 / REN_001;
- §13.6: `F8 = math authority` sin calificación.

Y detecta matemáticas de negocio propias en evaluadores de consorcios que no están documentadas como excepciones.

Estado correcto:

```text
F8_ONLY_MATH_AUTHORITY: NOT_PROVEN
DOCUMENTATION_CONTRADICTION: YES
ARCHITECTURAL_DECISION_REQUIRED: YES
```

No debe modificarse matemática hasta resolver documentalmente qué significa `math authority` y qué excepciones, si alguna, son legítimas.

### 11.5 Worktree provisionalmente clasificado por Qwen

```text
KEEP:
- workbook_ref separado de filename
- D7 grain_authorized=False
- web semantic reception pasando por Product Root
- gobierno documental reciente

REDESIGN:
- request_kind migration
- CanonicalIngestionOutput V2 por aliases transitorios
- Product Root request/mode interface

DELETE_AFTER_DEPENDENCY_CLOSURE:
- legacy semantic reentry compatibility

OFFLINE:
- evidencia _audit/
```

Estas clasificaciones siguen siendo evidencia provisional; no autorizan implementación hasta cerrar las decisiones normativas pendientes.

## 12. Auditoría de prompts — alcance real disponible

### 12.1 Limitación física

Qwen no encontró transcripts de prompts de implementación almacenados en el repositorio. Por tanto no pudo reconstruir causalmente:

```text
prompt histórico
→ decisión implícita
→ cambio de código
→ cambio de test
→ aumento/reducción de entropía
```

No es válido inventar esa causalidad a partir del código resultante.

### 12.2 Prompts completos disponibles en la conversación actual

Se pueden auditar con certeza dos instrucciones completas recientes:

#### PROMPT-AUD-001 — auditoría forense Codex

```text
TIPO: AUDIT_ONLY
ARCHITECTURAL_DECISION_IMPLIED: NONE
PRE_DOCUMENTED: YES — Audit Plan + Canonical Axis + Architecture Lock
RESULTING_CODE_CHANGE: NONE
RESULTING_TEST_CHANGE: NONE
ENTROPY_EFFECT: NONE
CLASSIFICATION: ALIGNED_WITH_ARCHITECTURE
```

El prompt prohibió modificaciones, wrappers, migraciones de tests, commit/push/deploy y pidió evidencia física. No introdujo arquitectura runtime.

#### PROMPT-REDTEAM-001 — red-team Qwen

```text
TIPO: AUDIT_ONLY / ADVERSARIAL
ARCHITECTURAL_DECISION_IMPLIED: NONE
PRE_DOCUMENTED: YES
RESULTING_CODE_CHANGE: NONE
RESULTING_TEST_CHANGE: NONE
ENTROPY_EFFECT: NONE
CLASSIFICATION: ALIGNED_WITH_ARCHITECTURE
```

El prompt prohibió full suite, modificaciones y reparaciones, y exigió refutar la auditoría primaria.

### 12.3 Prompts de implementación Phase 1–4

Los transcripts completos que produjeron los cambios Phase 1–4 no están físicamente disponibles en el repo auditado. Por tanto:

```text
PROMPTS_PHASE1_4_FULLY_AUDITED: NO
PATCH_INDUCING_PROMPTS: NOT_PROVEN
LEGACY_PRESERVING_PROMPTS: NOT_PROVEN
TEST_DRIVEN_RUNTIME_DISTORTION_FROM_PROMPTS: NOT_PROVEN
NO_UNDOCUMENTED_PROMPT_ARCHITECTURE: NOT_PROVEN
```

Sí existe evidencia de que varios mecanismos introducidos durante esas fases están ahora correctamente marcados `UNDER_REVIEW` en la autoridad documental; eso no prueba el contenido causal del prompt que los originó.

### 12.4 Regla para cerrar esta limitación

Si se recuperan los prompts originales de implementación, deben incorporarse al Prompt Decision Ledger. Si no son recuperables, la auditoría final debe conservar explícitamente `HISTORICAL_PROMPT_CAUSALITY: NOT_PROVEN` y no usar supuestas intenciones de los agentes para decidir arquitectura.

## 13. Decisiones arquitectónicas que deben resolverse antes de reconstruir

Después de Codex + cross-check + Qwen, las decisiones pendientes reales se reducen a:

### AD-01 — alcance de autoridad matemática

Definir normativamente si:

```text
F8 = única autoridad matemática de negocio
```

o si existen excepciones especializadas legítimas y cuáles son sus límites exactos.

No tocar LIQ_001, REN_001, generic engine ni consorcios antes de esta decisión.

### AD-02 — convergencia semántica final

Determinar cuál es la única ruta semántica productiva final y el destino de la ruta determinística/legacy. El shim legacy no puede permanecer productivo indefinidamente.

### AD-03 — modelo final de ProductRequest / Product Root

Definir si `request_kind` es contrato de dominio y cuál es el modelo explícito por tipo de request, evitando flags procedurales para representar estados de workflow.

### AD-04 — retiro de aliases del CanonicalIngestionOutput V2

Definir consumers canónicos y gate de retiro. Ningún alias `transitional` puede quedar sin condición de salida.

### AD-05 — identidad de sheet

Eliminar el uso de `sheet1` como fallback implícito mediante evidencia de sheet explícita o fail-closed. Esto depende parcialmente de AD-02 porque varias ocurrencias pertenecen al camino semántico legacy.

### AD-06 — provenance D4→F7

Cerrar contractualmente qué referencias e invariantes debe validar F7 antes de materializar un join, sin convertir F7 en una segunda autoridad de relaciones.

## 14. Estado consolidado después del red-team

```text
SERVICE_1_INTEGRAL_HEALTH: FAIL / NOT_CERTIFIED
PRIMARY_AUDIT_RELIABILITY: HIGH_ENOUGH_FOR_FINDINGS / NOT_ENOUGH_FOR_RECONSTRUCTION
RED_TEAM: COMPLETED
PROMPT_AUDIT_CURRENT_THREAD: COMPLETED
PROMPT_AUDIT_PHASE1_4: NOT_PROVEN
ARCHITECTURE_DELTA_LEDGER: PARTIAL
WORKTREE_DECISION_LEDGER: PARTIAL
TARGET_ARCHITECTURE_UNAMBIGUOUS: NO
READY_FOR_RECONSTRUCTION: NO
READY_FOR_CERTIFICATION: NO
```

No iniciar saneamiento hasta resolver AD-01 a AD-06 en autoridad documental y convertir los ledgers provisionales en una secuencia causal cerrada.


## 15. Cierre posterior de arquitectura y handoff — 2026-08-23

Las secciones anteriores registran el estado de la auditoría antes del cierre dialéctico. Ese estado fue consumido por cuatro rondas adversariales ChatGPT ↔ Qwen más una micro-ronda final, con cross-check físico del repositorio.

Resultado final de diseño:

```text
DIALECTICAL_REVIEW_COMPLETE: PASS
OPEN_ARCHITECTURAL_DECISIONS: 0
TARGET_ARCHITECTURE_CLOSED: YES
```

Las decisiones normativas finales fueron incorporadas a:

```text
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
```

El paquete ejecutable de reconstrucción quedó en:

```text
docs/current/SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md
docs/current/SERVICE_1_ARCHITECTURE_TO_CODE_DELTA_V1.md
docs/current/SERVICE_1_CODE_DISPOSITION_FINAL_V1.md
docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md
```

Por tanto, quedan superseded como decisiones abiertas los estados históricos de este informe tales como:

```text
MATH_AUTHORITY_SCOPE: UNRESOLVED
TARGET_ARCHITECTURE_UNAMBIGUOUS: NO
READY_FOR_RECONSTRUCTION: NO
AD-01..AD-06 pending
```

El estado correcto posterior es:

```text
ARCHITECTURE_AUDIT: CLOSED
TARGET_ARCHITECTURE: CLOSED
RECONSTRUCTION_HANDOFF: COMPLETE
RECONSTRUCTION_IMPLEMENTATION: PENDING
CURRENT_WORKTREE_INTEGRAL_HEALTH: NOT_CERTIFIED
CERTIFICATION: NOT_READY UNTIL RECONSTRUCTION + TEST GATES
```

Los hallazgos físicos del informe siguen siendo evidencia válida cuando no fueron explícitamente corregidos por el dossier dialéctico o por los documentos rectores posteriores.
