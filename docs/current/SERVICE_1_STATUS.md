# Servicio 1 — estado actual

**Fecha de corte:** 2026-07-14

**Baseline estructural comprometida:** `c4834a8`

**Regresión del corte P7/P8:** `2823 passed, 1 skipped` en Python 3.11 limpio

## Estado

```text
RAÍZ PRODUCTIVA CANÓNICA: ACTIVA
CLI CANÓNICO: ACTIVO
XLSX REAL → COMPRENSIÓN → CONFIRMACIÓN → PLAN COMPUTABLE: PROBADO
CASH_COLLECTIONS → LIQ_001_vendido_cobrado: PROBADO
PLAN COMPUTABLE SIN EJECUCIÓN: PROBADO
RUTA EXPLÍCITA TOOL → XLSX: CONSERVADA
FAIL-CLOSED SEMÁNTICO Y DE POLÍTICA: PROBADO
SERVICIO 1 COMPLETO EN TODA SU AMPLITUD: NO
```

## Qué hace hoy

Servicio 1 puede:

- leer un XLSX real por la ruta canónica;
- conservar encabezados, muestras y contexto de hoja;
- proponer significados semánticos mediante el motor de comprensión de columnas;
- bloquear y preguntar al dueño cuando existe ambigüedad;
- aceptar únicamente una opción semántica canónica o `IGNORED_NOT_RELEVANT`;
- hacer prevalecer una confirmación explícita del dueño sobre hipótesis secundarias del matcher;
- agrupar evidencia confirmada en familias de variables;
- recibir una capacidad empresarial explícita y buscar una única relación gobernada familia–patología–fórmula;
- construir un plan computable para `sold_vs_collected_gap` mediante `LIQ_001_vendido_cobrado`;
- conservar la ruta anterior de tools explícitamente solicitadas y generación física XLSX.

## Recorridos actuales

### Plan computable, sin ejecución

```text
Excel
→ lectura estructural
→ comprensión de columnas
→ confirmación del dueño, solo cuando hace falta
→ familia de variables confirmada
→ capacidad empresarial solicitada
→ matriz gobernada fórmula–patología–evidencia
→ binding semántico de variables
→ plan READY_FOR_COMPUTATION
→ computation_executed=false
```

### Ejecución física explícita existente

```text
Excel
→ comprensión y confirmación
→ tool request explícita y permitida
→ ejecución determinística
→ archivo XLSX de entrega
```

## Raíz técnica

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
```

P7/P8 se integra en esa raíz mediante:

```text
service_1_deterministic_semantic_pipeline_v1.py
service_1_variable_family_bindings_v1.py
service_1_semantic_catalog_loader_v1.py
service_1_semantic_evidence_binding_engine_v1.py
docs/service_1_formula_pathology_evidence_matrix.v1.json
```

## Evidencia P7/P8

```text
FAMILIA: CASH_COLLECTIONS
CAPACIDAD: sold_vs_collected_gap
PATOLOGÍA: LIQ_001
FÓRMULA: LIQ_001_vendido_cobrado
VARIABLES: sold_amount + collected_amount
BINDINGS: venta_total + cobrado
ESTADO: READY_FOR_COMPUTATION
RUNTIME_AUTHORIZED: false
TOOL_EXECUTION_AUTHORIZED: false
COMPUTATION_EXECUTED: false
DIAGNOSIS_GENERATED: false
```

## Límites honestos

- `READY_FOR_COMPUTATION` no autoriza runtime, ejecución, entrega ni diagnóstico.
- Solo `sold_vs_collected_gap` está habilitada como capacidad formulaica computable en este corte.
- `REN_001_margen_neto_real` puede considerarse semánticamente, pero permanece bloqueada como candidato computable por política y vocabulario incompleto.
- No existe todavía selección automática de tool a partir del contenido del Excel.
- El universo completo de patologías, fórmulas y microservicios no está conectado a la raíz productiva.
- No hay LLM con autoridad de decisión dentro del pipeline.
- No hay autorización para una cadena paralela, un segundo parser XLSX ni una arquitectura SaaS alternativa.

## Próximo frente

```text
P9_CONTROLLED_FORMULA_EXECUTION
→ consumir exclusivamente un plan READY_FOR_COMPUTATION
→ ejecutar LIQ_001 con el motor determinístico existente
→ conservar runtime_authorized=false y diagnosis_generated=false
→ producir resultado computacional trazable, todavía sin delivery automático
```
