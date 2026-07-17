# Servicio 1 — Pilot 004 Distribuidora Mayorista V1

**Ciclo:** `CYCLE_034_RUN_S1_PILOT_004_DISTRIBUIDORA_MAYORISTA`
**Fecha:** 2026-07-17
**Estado:** `PASS`

## Fuente

```text
fixture: prueba_excels/distribuidora_mayorista_compleja.xlsx
sheet: OPERACION
CLI oficial: python -m pymia.cli.service_1_product
work_dir: .tmp\service_1_pilot_004_distribuidora_mayorista
```

## Resultado

Primer pase:

```text
returncode: 2
status: NEEDS_OWNER_CONFIRMATION
owner_questions_count: 3
tools_executed: false
```

Reentry semántico:

```text
semantic_owner_answers_count: 3
selected: {"cliente": "A", "ruta": "A", "margen": "A"}
source_rule: allowed_option_ids; no free text
```

Segundo pase:

```text
returncode: 0
status: PRODUCT_PIPELINE_READY
semantic_bindings_confirmed: true
tools_executed: true
executed_tool_refs: ["precio_margen_basico"]
xlsx_outputs: ["first_aid_001_precio_margen_basico.xlsx"]
```

## Interpretación

Este piloto confirma que Servicio 1 corre sobre un workbook de distribuidora mayorista con columnas de cliente, ruta, SKU, cantidad, venta, costo y margen.

La ejecución no implica selección automática de tool desde el Excel. La tool fue autorizada explícitamente mediante `tool_requests.json`.

## Límites

```text
No prueba diagnóstico integral de rentabilidad por ruta.
No prueba ranking de clientes o SKU.
No prueba análisis avanzado de margen.
No habilita capacidades fuera del catálogo vigente.
```
