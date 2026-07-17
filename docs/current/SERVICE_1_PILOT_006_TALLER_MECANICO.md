# Servicio 1 — Pilot 006 Taller Mecánico V1

**Ciclo:** `CYCLE_035_RUN_S1_PILOT_006_TALLER_MECANICO`
**Fecha:** 2026-07-17
**Estado:** `PASS`

## Fuente

```text
fixture: prueba_excels/taller_mecanico_lubricar_srl.xlsx
sheet: ORDENES_TRABAJO
CLI oficial: python -m pymia.cli.service_1_product
work_dir: .tmp\service_1_pilot_006_taller_mecanico
```

## Resultado

```text
primer pase: NEEDS_OWNER_CONFIRMATION
preguntas semánticas: 9
segundo pase: PRODUCT_PIPELINE_READY
tools_executed: True
tool ejecutada: precio_margen_basico
artifact XLSX: first_aid_001_precio_margen_basico.xlsx
```

## Confirmación semántica

```text
respuestas: 9
fuente: allowed_option_ids
texto libre: no usado
```

Columnas que pidieron confirmación semántica:

```text
- orden_id: A
- cliente: A
- tipo_reparacion: A
- horas_mano_obra: A
- valor_hora: A
- ingreso_mano_obra: A
- margen_mano_obra: A
- servicios_tercerizados: A
- forma_pago: A
```

## Checks

```text
first_status_needs_owner: True
first_tools_not_executed: True
semantic_answers_from_allowed_ids: True
final_status_ready: True
semantic_confirmed: True
tools_executed: True
expected_tool_executed: True
xlsx_output_exists: True
```

## Límites honestos

```text
Run uses explicit tool request; it does not claim automatic tool selection.
Run validates product path on a taller mecanico workbook with ordenes de trabajo, mano de obra and pagos, not full workshop profitability diagnosis.
Any stock, client, repuestos or service profitability advanced analysis remains a future governed capability unless explicitly added.
```

## Declaración

Este piloto prueba que Servicio 1 puede operar sobre un Excel nuevo de taller mecánico con órdenes de trabajo, mano de obra, repuestos, tercerizados y forma de pago.

No prueba diagnóstico integral de rentabilidad de taller, stock, clientes ni repuestos. Eso queda fuera hasta crear capacidades gobernadas específicas.
