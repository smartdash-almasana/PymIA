# PymIA — Reconciliación Documental Servicio 1 — Recepción Semántica Secuencial

**Fecha:** 2026-08-16  
**Estado:** DOCUMENTATION RECONCILIATION / PRE-DEPLOY  
**Alcance:** Servicio 1 únicamente  
**Main integrado:** `26ef6c8c57bb201da1a36a1073147c641d1309f4`

## Propósito

Este documento reconcilia la autoridad documental de Servicio 1 después de integrar en `main`:

```text
LLM_COLUMN_INTERPRETER_V1
+
SEQUENTIAL_OWNER_CORROBORATION_V1
```

No certifica producción. No autoriza nuevas capacidades. No modifica la raíz productiva canónica. No autoriza PymiaRadar.

## Estado técnico confirmado

```text
MAIN_HEAD: 26ef6c8c57bb201da1a36a1073147c641d1309f4
LLM_COLUMN_INTERPRETER_IMPLEMENTATION: MERGED_IN_MAIN
SEQUENTIAL_OWNER_CORROBORATION: MERGED_IN_MAIN
FOCUSED_TESTS: 7 PASS / 0 FAIL
SECOND_XLSX_PARSER: ABSENT
PRODUCT_ROOT_CHANGED: NO
LLM_AUTHORITY: NONE
OWNER_CONFIRMATION_FLOW: SEQUENTIAL
QUESTIONS_VISIBLE_AT_ONCE: 1
DETERMINISTIC_FALLBACK: PRESERVED
PRODUCTION_DEPLOYMENT_OF_THIS_CUT: PENDING
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_YET_PROVEN
```

## Qué cambió

```text
WorkbookProfiler / evidencia física
↓
LLM_COLUMN_INTERPRETER_V1
↓
propuesta semántica tipada
↓
SEQUENTIAL_OWNER_CORROBORATION_V1
↓
una duda
↓
una pregunta
↓
una respuesta
↓
actualización de contexto
↓
siguiente duda
```

La recepción deja de exigir confirmación masiva y pasa a corroborar dudas relevantes una por vez.

## Responsabilidad del LLM

El LLM puede interpretar nombres de columnas, proponer significado, proponer un `canonical_role` permitido, expresar incertidumbre y formular una pregunta de corroboración.

El LLM no puede calcular, ejecutar capacidades, autorizar runtime, tools o delivery, crear evidencia, persistir decisiones por sí mismo, inventar resultados, modificar la raíz productiva, reemplazar P6/P7/P8 ni reemplazar el kernel matemático.

```text
LLM interpreta.
LLM NO calcula.
LLM NO autoriza.
```

## Autoridades vigentes

```text
provider / LLM → propone significado de columnas
owner → confirma significado empresarial
P6 / P7 / P8 → gobiernan aprobación, requisitos y computabilidad
Derived Evidence → transforma evidencia confirmada cuando corresponde
kernel → única autoridad matemática
delivery → controla salida autorizada
```

La confirmación del dueño sigue siendo:

```text
EVIDENCE
NOT PERMISSION
```

## Invariantes preservados

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
NO_LLM_RUNTIME_AUTHORITY
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
SEMANTIC_ASSISTANCE_IS_NOT_AUTHORITY
P8_IS_COMPUTABILITY_AUTHORITY
KERNEL_IS_FORMULA_EXECUTION_AUTHORITY
```

Raíz productiva canónica:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

No fue modificada por este corte.

## Evidencia del corte

```text
branch: work/llm-column-interpreter-sequential-v1
pre-integration head: 9a196ffdb89daa22c3f6eef931e863a73799e8f6
integrated main head: 26ef6c8c57bb201da1a36a1073147c641d1309f4
provider tests: PASS
sequential reception tests: PASS
cafeteria semantic scope: PASS
browser/local smoke: PASS
cards_per_page: [1,1]
batch form: absent
second XLSX parser: absent
product root diff: 0
```

Sanidad semántica observada:

```text
Hora != Nombre del producto
MetodoPago != Nombre del producto
Ciudad != Proveedor
```

## Main versus producción

No confundir:

```text
MAIN = nuevo corte semántico integrado
PRODUCCIÓN = última revisión previamente certificada
```

Estado actual:

```text
SEMANTIC_RECEPTION_SEQUENTIAL_CUT: MERGED_IN_MAIN
PRODUCTION_DEPLOYMENT: PENDING
PRODUCTION_SMOKE: PENDING
EXTERNAL_LLM_RUNTIME_ACTIVATION: NOT_PROVEN
```

No declarar el provider externo activo en producción antes de deploy y smoke reales.

## Provider semántico

Implementación:

```text
pymia/smartpyme/service_1_pydantic_ai_column_semantic_provider_v1.py
```

Propiedades:

```text
PydanticAI
output tipado
extra="forbid"
sin tools
roles permitidos cerrados
sin lectura XLSX propia
sin autoridad matemática
sin autoridad de runtime
sin autoridad de delivery
```

Fallback:

```text
SAFE_DETERMINISTIC_PROVIDER: PRESERVED
```

## Recepción secuencial

Implementación:

```text
pymia/smartpyme/service_1_assisted_web_semantic_reception_v1.py
```

Contrato:

```text
UNA DUDA
→ UNA PREGUNTA
→ UNA RESPUESTA
→ ACTUALIZAR CONTEXTO
→ SIGUIENTE DUDA
```

Invariante:

```text
QUESTIONS_SHOWN_SIMULTANEOUSLY = 1
```

## Estado de Servicio 1

El cierre técnico previo permanece válido para las capacidades ya certificadas. Este corte no agrega una capacidad matemática ni un nuevo pipeline productivo; mejora la recepción semántica previa a la ejecución gobernada.

```text
SERVICE_1_TECHNICAL_BASELINE: PRESERVED
SEMANTIC_RECEPTION_SEQUENTIAL_CUT: MERGED_IN_MAIN
PRODUCTION_CERTIFICATION_OF_NEW_CUT: PENDING
```

## Frente actual único

```text
DEPLOY_SEMANTIC_RECEPTION_SEQUENTIAL_CUT
↓
PRODUCTION_SMOKE
↓
CONFIRM_RUNTIME_PROVIDER_STATE
↓
UPDATE_CURRENT_AUTHORITY_DOCS
↓
CLOSE_CUT
```

No abrir nuevas capacidades antes de cerrar este ciclo.

## PymiaRadar

```text
PYMIARADAR: FUTURE_REFERENCE_ONLY
```

Regla:

```text
FINALIZAR SERVICIO 1
→ recién después
PYMIARADAR
```

Su documentación conceptual no gobierna Servicio 1.

## Documentos rectores a reconciliar localmente

```text
docs/current/README.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
```

Sólo deben modificarse donde contradigan la verdad actual.

```text
CORRECT_EXISTING_CANONICAL_DOCS_BEFORE_CREATING_NEW_ONES
```

## Próxima evidencia necesaria

```text
DEPLOY: PASS
SERVICE: HEALTHY
AUTH: PASS
UPLOAD: PASS
SEMANTIC_INTERPRETATION: PASS
SEQUENTIAL_OWNER_CONFIRMATION: PASS
DETERMINISTIC_EXECUTION: PASS
DELIVERY: PASS
SECOND_XLSX_PARSER: ABSENT
LLM_RUNTIME_AUTHORITY: NONE
```

Sólo entonces:

```text
PRODUCTION_DEPLOYMENT_OF_SEMANTIC_RECEPTION_CUT: PASS
```

## Regla de continuidad

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
→ documento rector actualizado si cambia la verdad
```

No repetir verificaciones ya cerradas sin nueva evidencia causal. No ampliar alcance. No iniciar PymiaRadar.

## Estado final

```text
DOCUMENTATION_RECONCILIATION: READY_TO_APPLY_LOCALLY
MAIN_HEAD: 26ef6c8c57bb201da1a36a1073147c641d1309f4
SEMANTIC_CUT: MERGED_IN_MAIN
PRODUCTION: PENDING_DEPLOY
LLM_AUTHORITY: NONE
PRODUCT_ROOT: UNCHANGED
PYMIARADAR: OUT_OF_CURRENT_SCOPE
```
