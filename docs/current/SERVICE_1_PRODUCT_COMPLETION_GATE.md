# Servicio 1 — Product Completion Gate V1

**Ciclo:** `CYCLE_029_SERVICE_1_PRODUCT_COMPLETION_GATE`  
**Fecha:** 2026-07-16  
**Estado:** `PASS_PRODUCT_MVP_COMPLETE`

## Declaración

Servicio 1 queda completo como **MVP determinístico asistido** para este alcance:

```text
XLSX real
→ confirmación de columnas por el dueño
→ salida canónica de ingesta
→ comprensión semántica determinística
→ confirmación semántica del dueño cuando hace falta
→ plan gobernado o ejecución explícita de tool
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

### Recorrido 1 — XLSX real con ejecución explícita

```text
fixture: prueba_excels/cafeteria_abc.xlsx
sheet: Ventas
primer pase: NEEDS_OWNER_CONFIRMATION
reentry semántico: opciones canónicas, no texto libre
estado final: PRODUCT_PIPELINE_READY
tool ejecutada: precio_margen_basico
artifact: XLSX generado
```

### Recorrido 2 — XLSX real con plan gobernado sin ejecución

```text
capability: sold_vs_collected_gap
estado final: COMPUTATION_PLAN_READY
formula: LIQ_001_vendido_cobrado
familia: CASH_COLLECTIONS
computation_executed: false
runtime_authorized: false
tool_execution_authorized: false
```

## Guardas obligatorias

```text
EXPERIMENTAL_FROZEN: 0
operator legacy: ausente
runtime bridge legacy: ausente
Exceland/lab legacy: ausente
```

## Límites honestos

```text
No hay autoridad LLM en runtime.
No hay selección automática de tool desde el Excel.
LIQ_001 llega a plan computable, no a ejecución.
Servicio 2/3 queda fuera de alcance.
No se declara conectado todo el universo futuro de patologías y fórmulas.
```

## Criterio de cierre

El gate pasa sólo si:

```text
1. El registry tiene cero EXPERIMENTAL_FROZEN.
2. La CLI oficial existe y las entradas legacy no existen.
3. El caso real cafeteria_abc.xlsx bloquea primero y ejecuta después de reentry.
4. El plan LIQ_001 se construye sin ejecución.
5. Los tests focales y la regresión completa pasan.
```
