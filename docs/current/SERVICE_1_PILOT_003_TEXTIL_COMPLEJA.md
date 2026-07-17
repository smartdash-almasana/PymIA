# Servicio 1 — Pilot 003 Textil Compleja V1

**Ciclo:** `CYCLE_033_RUN_S1_PILOT_003_TEXTIL_COMPLEJA`
**Fecha:** 2026-07-17
**Estado:** `PASS`

## Propósito

Ejecutar el primer piloto nuevo posterior al operatorless baseline usando un Excel activo de `prueba_excels/`, sin reutilizar fixtures BEM descartados ni abrir capacidades no autorizadas.

## Fuente

```text
fixture: prueba_excels/pyme_textil_compleja.xlsx
sheet: VENTAS
CLI oficial: python -m pymia.cli.service_1_product
work_dir: .tmp\service_1_pilot_003_textil_compleja
```

## Primer pase

```text
returncode: 2
status: NEEDS_OWNER_CONFIRMATION
owner_questions_count: 2
tools_executed: false
```

Interpretación: el sistema bloqueó correctamente antes de ejecutar tools porque todavía requería confirmación semántica del dueño.

## Reentry semántico

```text
semantic_owner_answers_count: 2
source_rule: selected from product_pipeline.owner_questions[].allowed_option_ids; no free text
selected: {"descuento": "A", "margen": "A"}
```

No se usó texto libre. Las respuestas salieron de `allowed_option_ids` emitidos por el propio producto.

## Segundo pase

```text
returncode: 0
status: PRODUCT_PIPELINE_READY
semantic_bindings_confirmed: true
tools_executed: true
executed_tool_refs: ["precio_margen_basico"]
xlsx_outputs: ["first_aid_001_precio_margen_basico.xlsx"]
```

## Límites

```text
No prueba selección automática de tool.
No prueba diagnóstico textil completo.
No autoriza análisis avanzado de margen fuera del catálogo vigente.
No usa fixtures BEM descartados.
```

## Veredicto

```text
PASS: Servicio 1 ejecuta el recorrido operativo sobre pyme_textil_compleja.xlsx.
```
