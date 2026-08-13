# SERVICE_1_CURRENT_PRODUCT_STATE_V1

## Estado vigente

```text
CURRENT_PRODUCT_STATE: TECHNICAL_CLOSURE_PASS
CURRENT_HEAD: 13e3247402ad4543f683d56666de2fbc3127fa0d
FULL_SUITE: 3538 passed / 0 failed / 6 skipped
STAGE_2: CLOSED_PASS
CURRENT_FRONT: PRODUCT_AND_OPERATIONAL_CLOSURE
NEW_PRODUCTIVE_CAPABILITY_AUTHORIZED: NO
NEXT_GATE: FREEZE_SELLABLE_PRODUCT
```

Este documento fija el estado actual de Servicio 1 para decisiones de continuidad. Los closeouts históricos siguen siendo evidencia de los cortes que certificaron, pero no reemplazan este estado vigente cuando describen una etapa anterior.

## Producto actual

```text
12/12 patologías productivas conectadas
una raíz productiva canónica
P0→P10 vigente
web asistida activa
identidad tenant Supabase activa
persistencia tenant durable activa
owner confirmation y reentry activos
P6/P7/P8 gobernados
P9 determinístico
P10 controla QA/delivery
```

Raíz productiva canónica:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

## Superficie operativa actual

Servicio 1 reutiliza la cadena canónica para:

```text
intake web/XLSX
contexto de negocio
identidad tenant
persistencia y reentrada
confirmación explícita del dueño
computabilidad gobernada
cálculo determinístico
presentación/descarga controlada por P10
```

Los flujos XLSX-first y carpetas de operador certificados previamente permanecen como evidencia histórica y soporte operativo; ya no describen por sí solos la superficie completa del producto.

## Límites no bloqueantes

```text
sin delivery autónomo soberano
sin LLM runtime authority
sin diagnóstico definitivo
sin cierre contable automático
sin OCR/PDF parser
sin segundo parser XLSX
sin segunda raíz productiva
sin nueva capacidad antes de certificación
```

## Expansión prohibida antes de certificación

```text
nueva capacidad productiva
segundo pipeline semántico
segundo gate de computabilidad
segunda raíz de ejecución
API/worker/queue como nueva autoridad
persistencia alternativa como autoridad
LLM con autoridad runtime
bypass de P6/P7/P8/P10
refactor sin blocker causal de producto
```

## Secuencia única de cierre

```text
0. RECONCILE_SERVICE_1_CURRENT_PRODUCT_AUTHORITY_V1
1. FREEZE_SELLABLE_PRODUCT
2. PROVE_REAL_SELLABLE_JOURNEY
3. CLOSE_REAL_PRODUCTION_BLOCKERS + PRODUCTION_SMOKE
4. REAL_CLIENT_CASE_001 + PRODUCTION_CERTIFICATION
```

## Política de QA

```text
cambio pequeño → test focal
cambio de integración → focal + una regresión relevante
deployment → smoke real
certificación mayor → full suite una sola vez
```

## Criterio de bloqueo

Bloquea el cierre únicamente aquello que impide uso seguro, ejecución, entrega, operación productiva, seguridad o cobro del producto definido. Deuda estética, refactors, capacidades futuras y documentación histórica no bloquean salvo que creen una contradicción activa de autoridad.

## Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
NO_PARALLEL_PRODUCTIVE_PIPELINE
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
P7_REQUIREMENT_MATCH_PRECEDES_P8
P9_EXECUTION_ONLY_FROM_GOVERNED_INPUT
P10_CONTROLS_DELIVERY_QUALITY
```
