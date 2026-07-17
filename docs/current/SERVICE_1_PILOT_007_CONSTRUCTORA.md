# Servicio 1 — Pilot 007 Constructora V1

**Ciclo:** `CYCLE_036_RUN_S1_PILOT_007_CONSTRUCTORA`
**Fecha:** 2026-07-17
**Estado:** `PASS`

## Caso

```text
fixture: prueba_excels/constructora_nueva_era_srl.xlsx
sheet: OBRAS
CLI: python -m pymia.cli.service_1_product
work_dir: .tmp/service_1_pilot_007_constructora
```

## Primer pase

```text
returncode: 2
status: NEEDS_OWNER_CONFIRMATION
owner_questions_count: 16
tools_executed: false
```

## Reentry semántico

```text
semantic_owner_answers_count: 16
fuente: allowed_option_ids
texto libre: no usado
```

## Segundo pase

```text
returncode: 0
status: PRODUCT_PIPELINE_READY
semantic_bindings_confirmed: true
tools_executed: true
executed_tool_refs: ['precio_margen_basico']
xlsx_outputs: ['first_aid_001_precio_margen_basico.xlsx']
```

## Límites honestos

```text
No prueba diagnóstico integral de obra.
No prueba análisis avanzado presupuesto vs gasto.
No prueba rentabilidad de obra ni desvíos de imprevistos.
No prueba selección automática de tool.
```
