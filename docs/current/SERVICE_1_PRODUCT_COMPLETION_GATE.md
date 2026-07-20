# Servicio 1 — Product Completion Gate V1

**Ciclo:** `CYCLE_029_SERVICE_1_PRODUCT_COMPLETION_GATE`  
**Fecha de reconciliación:** 2026-07-20  
**Estado:** `PASS_PRODUCT_MVP_COMPLETE`

## Declaración

Servicio 1 queda completo como **MVP determinístico asistido** para este alcance:

```text
XLSX real
→ confirmación de columnas por el dueño
→ salida canónica de ingesta
→ comprensión semántica determinística
→ confirmación semántica del dueño cuando hace falta
→ plan gobernado
→ cálculo absorbido o ejecución explícita de tool
→ hallazgo acotado cuando corresponda
→ salida trazable
```

Esto no declara completo el universo futuro de patologías, fórmulas, CRM, SaaS, Servicio 2/3 ni automatización LLM.

## Autoridad técnica

```text
CLI oficial: pymia/cli/service_1_product.py
Raíz canónica: pymia/smartpyme/service_1_product_pipeline_v1.py
```

No hay otra entrada oficial de Servicio 1.

## Evidencia aceptada

### Recorrido 1 — XLSX real con ejecución explícita de tool

```text
fixture: prueba_excels/cafeteria_abc.xlsx
sheet: Ventas
primer pase: NEEDS_OWNER_CONFIRMATION
reentry semántico: opciones canónicas, no texto libre
estado final: PRODUCT_PIPELINE_READY
tool ejecutada: precio_margen_basico
artifact: XLSX generado
```

### Recorrido 2 — LIQ_001 absorbido por la raíz

```text
capability: sold_vs_collected_gap
estado final: COMPUTATION_PLAN_READY
formula: LIQ_001_vendido_cobrado
computation_executed: true
bounded_finding_generated: true
causal diagnosis: false
delivery: sólo con --deliver-result
runtime_authorized: false
tool_execution_authorized: false
product_ready: false
delivery_authorized: false
diagnosis_generated: false
```

El hallazgo LIQ_001 cuantifica la diferencia entre vendido y cobrado. No atribuye morosidad, fraude, error contable, incobrabilidad ni responsabilidad causal.

### Evidencia fuera del gate productivo — REN_001

```text
module: service_1_ren_001_evaluator_v1
classification: SUPPORT_NECESSARY
isolated evaluator tests: PASS
reachable from canonical root: false
CLI connected: false
product capability accepted: false
```

REN_001 no amplía el alcance del gate y no puede ser conectado sin un ciclo documental explícito.

## Guardas obligatorias

```text
EXPERIMENTAL_FROZEN: 0
operator legacy: ausente
runtime bridge legacy: ausente
Exceland/lab legacy: ausente
una sola raíz productiva
una sola CLI oficial
```

## Límites honestos

```text
No hay autoridad LLM en runtime.
No hay selección automática de tool desde el Excel.
LIQ_001 produce evidencia y hallazgo acotado, no diagnóstico causal.
La entrega LIQ_001 exige --deliver-result.
REN_001 permanece fuera de la raíz productiva.
Servicio 2/3 queda fuera de alcance.
No se declara conectado todo el universo futuro de patologías y fórmulas.
```

## Criterio de cierre

El gate pasa sólo si:

```text
1. El registry tiene cero EXPERIMENTAL_FROZEN.
2. La CLI oficial existe y las entradas legacy no existen.
3. El caso real cafeteria_abc.xlsx bloquea primero y ejecuta después de reentry.
4. LIQ_001 calcula únicamente con bindings confirmados y filas completas.
5. El hallazgo LIQ_001 permanece acotado y sin atribución causal.
6. La entrega LIQ_001 requiere solicitud explícita.
7. Los módulos de soporte no aparecen en la clausura productiva.
8. Los tests focales y la regresión completa pasan.
```

**Última regresión completa observada:** `1644 passed in 175.30s`.
