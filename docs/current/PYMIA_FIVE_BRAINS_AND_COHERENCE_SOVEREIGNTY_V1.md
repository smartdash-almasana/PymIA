# PymIA — Arquitectura de cinco cerebros y soberanía por coherencia V1

**Fecha:** 2026-08-19
**Estado:** `ARCHITECTURAL_MODEL_ALIGNED_WITH_CURRENT_RUNTIME`  
**Autoridad:** conceptual y de diseño. No crea por sí solo una nueva autoridad de runtime ni modifica la cadena productiva vigente de Servicio 1.

## 1. Propósito

Este documento nombra y ordena, como arquitectura cognitivo-operacional de PymIA, capacidades que hoy existen en distinto grado dentro del sistema.

La idea central es:

```text
LA SOBERANÍA NO PERTENECE A UN CEREBRO AISLADO.
LA SOBERANÍA ES LA COHERENCIA DEL CONJUNTO.
```

Cada cerebro posee una competencia acotada. Ninguno puede, por sí solo, declarar la verdad completa de PymIA.

En Servicio 1, este principio debe convivir con las autoridades locales ya vigentes:

```text
P6/P7/P8 gobiernan aprobación, requisitos y computabilidad.
Kernel / FormulaEngineService gobierna la ejecución matemática.
Owner confirmation aporta evidencia empresarial, no permiso universal.
La capa semántica propone y valida significado, sin autoridad de ejecución.
La capa narrativa/cognitiva explica, pregunta y organiza, sin autoridad operacional.
```

Por lo tanto, `SOBERANÍA_POR_COHERENCIA` no reemplaza ninguna de esas autoridades. Las integra a nivel de sistema.

## 2. Los cinco cerebros

### 2.1 Cerebro determinístico / de gobierno

**Función:** controlar estados, contratos, precondiciones, límites y transiciones válidas.

En la arquitectura actual de Servicio 1 se materializa principalmente en:

```text
P6 ApprovalDecision
P7 RequirementMatch + Grain
P8 ComputabilityDecision + GovernedComputationInput
FAIL_CLOSED
controlled delivery
architecture invariants
```

No calcula fórmulas ni inventa semántica. Decide, dentro de su competencia, si existe evidencia suficiente y si una operación puede avanzar.

### 2.2 Cerebro matemático

**Función:** ejecutar cálculos reproducibles sobre inputs gobernados.

Autoridad actual:

```text
pymia/services/formula_engine_service.py
Kernel / FormulaEngineService
```

Principio vigente:

```text
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
```

El cerebro matemático no decide qué significa una columna, no completa datos ausentes y no autoriza su propia ejecución.

### 2.3 Cerebro semántico

**Función:** establecer qué significan los datos empresariales y cómo se vinculan con variables canónicas.

La arquitectura actual ya posee el carril SEM-1 → SEM-9, incluyendo:

```text
WorkbookProfiler
provider-neutral semantic context
semantic provider
semantic deterministic validator
OwnerDialoguePlan
owner semantic evidence
TenantSemanticContractV1
structural compatibility
```

La semántica puede proponer. El dueño confirma o corrige significado empresarial material. La confirmación del dueño se transforma en evidencia canónica.

Principios vigentes:

```text
SEMANTIC_ASSISTANCE_IS_NOT_AUTHORITY
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
AUTOMATIC_REUSE: FORBIDDEN
SEMANTIC_REBIND: FORBIDDEN
```

### 2.4 Cerebro memoria

**Función:** conservar de forma gobernada la historia útil del tenant y ponerla a disposición de los demás cerebros sin convertir el pasado en autoridad automática sobre el presente.

Debe distinguir al menos tres memorias:

#### A. Memoria semántica

Conserva qué significados fueron confirmados por el dueño, bajo qué contexto, con qué identidad, fecha, revisión y provenance.

**Estado actual:** `IMPLEMENTED`.

Evidencia física vigente:

```text
Service1TenantSemanticContractV1
append-only tenant store
revision / supersession lineage
tenant isolation
structural compatibility
compatible memory = hint only
```

#### B. Memoria de ejecución y resultados

Debe conservar cada resultado material producido por PymIA como hecho histórico reproducible:

```text
tenant_id
case_id
service/capability
executed_at
periodo analizado
resultado y unidad
inputs gobernados / evidencia referenciada
owner evidence aplicada
versión de cálculo / versión de contrato
provenance
referencia al artefacto de entrega cuando exista
```

Regla:

```text
UN_RESULTADO_HISTÓRICO_NO_SE_REESCRIBE_SILENCIOSAMENTE
```

Si una fórmula cambia en el futuro, el resultado histórico conserva la versión con la que fue producido. Una nueva versión genera una nueva ejecución comparable; no modifica la anterior.

**Estado actual:** `F13_DURABLE_RESULT_MEMORY_IMPLEMENTED`.

Servicio 1 ya conserva ResultSets gobernados como snapshots tenant-scoped, content-addressed y append-only. RC3 implementa la reentrada de esos snapshots desde `Mis análisis` validando identidad e integridad y sin recalcular.

```text
F13_DURABLE_RESULT_MEMORY: PASS
RC3_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
REAL_RESTART_ONLINE_ACCEPTANCE: PENDING
```

El XLSX no necesita restaurarse para reabrir un ResultSet histórico; la prueba online después de restart real sigue pendiente.

#### C. Memoria longitudinal empresarial

Construye series temporales sobre ejecuciones históricas gobernadas:

```text
margen por período
saldo de caja proyectado por período
DSO por período
brecha vendido/cobrado por período
otros resultados comparables
```

Su función futura es permitir evolución, tendencia, deterioro, mejora y comparación temporal sin depender de recuerdos del LLM.

**Estado actual:** `NOT_IMPLEMENTED_AS_EXPLICIT_ENGINE`.

### 2.5 Cerebro cognitivo / IA

**Función:** conversar, formular hipótesis, organizar preguntas, interpretar lenguaje, explicar resultados y coordinar la interacción humana con los otros cerebros.

No posee soberanía sobre datos, semántica, computabilidad, cálculo ni delivery.

Frontera actual de Servicio 1:

```text
EXTERNAL_LLM_PROVIDER_IMPLEMENTATION: AVAILABLE
EXTERNAL_LLM_PROVIDER_CURRENT_RC_RUNTIME: NOT_PROVEN
SAFE_DETERMINISTIC_SEMANTIC_PROVIDER: PRESERVED
NO_LLM_RUNTIME_AUTHORITY
```

La arquitectura admite provider externo para asistencia semántica, pero su activación real sobre el release candidate actual todavía debe demostrarse mediante deploy y smoke. Aun activo, el LLM no forma parte de la autoridad matemática ni de computabilidad.

Principio:

```text
EL COGNITIVO PUEDE PROPONER, PREGUNTAR Y EXPLICAR.
NO PUEDE INVENTAR EVIDENCIA NI SOBRESCRIBIR A LOS OTROS CEREBROS.
```

## 3. Soberanía por coherencia

La soberanía del sistema surge cuando las distintas competencias convergen sin contradicción sobre una misma afirmación, cálculo o acción.

Cadena conceptual:

```text
dato real del tenant
→ identidad y provenance válidas
→ significado confirmado o gobernadamente validado
→ requisitos satisfechos
→ computabilidad autorizada
→ cálculo reproducible
→ resultado trazable
→ memoria histórica consistente
→ explicación cognitiva fiel al resultado
```

Una afirmación de PymIA es válida sólo dentro del alcance para el cual existe coherencia suficiente entre esas piezas.

Ejemplo:

```text
"Tu margen cayó respecto del período anterior"
```

requiere, como mínimo:

```text
1. dos resultados históricos del mismo tenant;
2. períodos identificables;
3. magnitudes semánticamente comparables;
4. evidencia de las ejecuciones que produjeron ambos resultados;
5. fórmula/versiones identificables;
6. reglas que permitan la comparación;
7. narrativa que no exceda lo demostrado por esos datos.
```

Si una de esas condiciones materiales falla, el cerebro cognitivo no debe completar la conclusión por plausibilidad.

## 4. Conflicto entre cerebros

Cuando dos componentes producen estados incompatibles, PymIA no debe resolver la contradicción por preferencia heurística del LLM ni por conveniencia de UX.

Regla:

```text
INCOHERENCIA_MATERIAL
→ NO CLAIM SOBERANO
→ FAIL_CLOSED O OWNER_CONFIRMATION SEGÚN CONTRATO
```

Ejemplos:

- memoria histórica dice que una columna antes significó `ventas`, pero la estructura actual cambió → la memoria es antecedente, no rebind automático;
- semántica propone `descuento`, pero la unidad no está confirmada → el matemático no ejecuta con una unidad inventada;
- existe un cálculo numérico, pero P8 no declara computabilidad → el resultado no se convierte en outcome productivo;
- el cognitivo formula una explicación incompatible con el bounded outcome → prevalece la evidencia gobernada; la narrativa debe corregirse.

## 5. Relación con la arquitectura actual de Servicio 1

Este modelo se sincroniza con la arquitectura vigente sin introducir una segunda raíz ni una autoridad paralela.

Mapa de correspondencia:

| Cerebro conceptual | Arquitectura física actual | Estado |
|---|---|---|
| Determinístico / gobierno | P6 / P7 / P8, fail-closed, delivery gates, contracts | EXISTENTE |
| Matemático | FormulaEngineService / kernel | EXISTENTE |
| Semántico | SEM-1 → SEM-9, owner evidence, TenantSemanticContractV1 | EXISTENTE |
| Memoria | F13 durable ResultSet memory + reentrada RC3 + tenant semantic store + persisted owner evidence | F13 IMPLEMENTADO; RC3 CERRADO/CONGELADO; MEMORIA SEMÁNTICA/LONGITUDINAL MÁS AMPLIA PARCIAL |
| Cognitivo / IA | provider-neutral semantic boundary + external provider implementation + narrative/conversational boundary | FRONTERA Y PROVIDER EXISTENTES; ACTIVACIÓN LLM EXTERNO EN RC ACTUAL: NOT_PROVEN / PENDING |
| Soberanía por coherencia | división de autoridad + source-of-truth hierarchy + invariantes | PRINCIPIO IMPLÍCITO, AHORA EXPLICITADO |

## 6. Compatibilidad con los invariantes actuales

Este modelo preserva:

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
DERIVED_EVIDENCE_NEVER_INVENTS_MISSING_MATERIAL_INPUTS
```

La soberanía por coherencia no significa crear un `CoherenceEngine` central que sustituya P6/P7/P8/kernel. Es una propiedad sistémica verificable mediante contratos y evidencia distribuida.

## 7. Consecuencia arquitectónica principal

La memoria durable de resultados gobernados ya no es una pieza ausente del **Cerebro Memoria**.

F13 conserva ResultSets históricos gobernados y RC3 cerró y congeló su reentrada sin recalcular ni restaurar el XLSX.

La frontera todavía pendiente es completar el alcance longitudinal del Cerebro Memoria y observar la prueba online y de release del RC actual; no implementar de nuevo la base durable F13. Cualquier evolución debe respetar este límite:

```text
NO nueva raíz productiva
NO memoria como autoridad automática
NO dependencia de recuerdos del LLM
NO reescritura de resultados históricos
SÍ tenant isolation
SÍ append-only / versionado cuando corresponda
SÍ provenance
SÍ resultado fechado y reproducible
SÍ vínculo con evidencia y versión matemática
```

## 8. Frase rectora

```text
Cada cerebro tiene competencia.
Ningún cerebro tiene soberanía aislada.
La soberanía de PymIA es la coherencia verificable del conjunto.
```

## 9. Estado de sincronización al 2026-08-19

```text
CONCEPTUAL_MODEL: DOCUMENTED
CURRENT_ARCHITECTURE_CONFLICT: NONE FOUND
CURRENT_RUNTIME_REPLACED: NO
NEW_AUTHORITY_CREATED: NO
F13_DURABLE_RESULT_MEMORY: IMPLEMENTED
RC3_RESULTSET_REENTRY: CLOSED_COMMITTED_FROZEN
TENANT_REENTRY_HARDENING: CLOSED_COMMITTED
MEMORY_BRAIN_FULLY_IMPLEMENTED: NO
COGNITIVE_LLM_RUNTIME_CURRENT_RC_PROVEN: NO
COHERENCE_PRINCIPLE: ALIGNED_WITH_EXISTING_AUTHORITY_CHAIN
```

Fuentes de contraste arquitectónico usadas para este documento:

```text
ARCHITECTURE_GUARDRAILS.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
pymia/smartpyme/service_1_tenant_semantic_contract_v1.py
pymia/smartpyme/service_1_tenant_semantic_contract_store_v1.py
```
