# Servicio 1 — Controlled Pilot Series Plan V1

**Ciclo:** `CYCLE_032_SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN`  
**Fecha inicial:** 2026-07-16  
**Última actualización:** 2026-07-20  
**Estado:** `ACTIVE`

## Propósito

Madurar Servicio 1 usando los Excel existentes de `prueba_excels/`, sin abrir Servicio 2 ni inventar capacidades no soportadas.

## Reglas

```text
Cada piloto parte de un XLSX existente en prueba_excels.
Cada piloto declara sheet, columnas observadas, objetivo operativo y alcance permitido.
No hay selección automática de tool desde Excel.
Las tools se ejecutan sólo con tool_requests explícitos.
Las capacidades formulaicas sólo se declaran cuando el product gate actual las soporta.
Un XLSX vacío o de salida generada no puede ser piloto activo.
```

## Guarda anti-deriva

```text
Tener headers válidos no autoriza un piloto.
La autoridad depende de origen productivo vigente, no de forma tabular.
Fixtures BEM, legacy, sintéticos descartados o salidas generadas no pueden promoverse por perfil superficial.
Toda promoción desde cuarentena requiere evidencia nueva explícita y test de no-deriva.
```

Caso trampa registrado:

```text
simple_bem_test.xlsx tiene columnas válidas, pero es fixture BEM descartado.
Por lo tanto queda en cuarentena y no puede ser próximo piloto.
```

## Serie controlada y estado actual

| Piloto | Archivo | Hoja primaria | Caso | Estado |
|---|---|---|---|---|
| S1-PILOT-001 | `cafeteria_abc.xlsx` | `Ventas` | cafetería ventas/productos/sucursales | `PASS` |
| S1-PILOT-003 | `pyme_textil_compleja.xlsx` | `VENTAS` | textil ventas/costos/margen | `PASS` |
| S1-PILOT-004 | `distribuidora_mayorista_compleja.xlsx` | `OPERACION` | distribuidora ruta/SKU/margen | `PASS` |
| S1-PILOT-005 | `fabrica_industrial_compleja.xlsx` | `PRODUCCION` | producción/scrap/OEE | `NEXT` |
| S1-PILOT-006 | `taller_mecanico_lubricar_srl.xlsx` | `ORDENES_TRABAJO` | taller servicios/stock | `PASS` |
| S1-PILOT-007 | `constructora_nueva_era_srl.xlsx` | `OBRAS` | constructora presupuesto/gasto/cobro | `PASS` |
| S1-PILOT-008 | `la_textil_cosida_srl_mar_abr_may_2026.xlsx` | `ventas` | textil completa multihoja | `PASS` |

`S1-PILOT-001` permanece como control de regresión ya probado.

## Piloto 008 cerrado

```text
Ciclo: CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA
Primer pase: NEEDS_OWNER_CONFIRMATION
Preguntas al dueño: 4
Segundo pase: PRODUCT_PIPELINE_READY
Tool explícita: precio_margen_basico
Salida: first_aid_001_precio_margen_basico.xlsx
```

La evidencia está en:

```text
docs/current/SERVICE_1_PILOT_008_TEXTIL_COMPLETA.md
docs/service_1_pilot_008_textil_completa.v1.json
tests/smartpyme/test_service_1_pilot_008_textil_completa_v1.py
```

El piloto prueba el recorrido canónico sobre la hoja `ventas` de un workbook textil completo multihoja. No declara diagnóstico textil integral, selección automática de tool ni nuevas fórmulas.

## Orden pendiente

```text
1. S1-PILOT-005 fabrica_industrial_compleja.xlsx
```

El Piloto 005 conserva explícitamente el límite de no inventar diagnóstico de scrap/OEE ni incorporar fórmulas industriales no soportadas.

## Cuarentena

```text
simple_bem_test.xlsx — fixture BEM descartado; no gobierna Servicio 1 productivo.
CASE_001_ventas_junio_2026_margin_leak.xlsx
cobros_marzo_2026.xlsx
ventas_marzo_2026.xlsx
first_aid_pilot_002_lista_precios_costos_demo.xlsx
first_aid_pilot_003_stock_inventory_demo.xlsx
SERVICE_1_SYNTHETIC_CASE_001_CAFETERIA_CASH_MARGIN.xlsx
SERVICE_1_SYNTHETIC_CASE_001_CAFETERIA_CASH_MARGIN_AUDITABLE/...xlsx
```

Motivo: fixture BEM descartado, hojas vacías o legacy sintético. No entran como pilotos activos hasta reparar, reexportar o demostrar autoridad productiva actual.

## Próximo ciclo autorizado

```text
CYCLE_038:
RUN_S1_PILOT_005_FABRICA_INDUSTRIAL
```

Alcance permitido:

```text
Ejecutar el recorrido canónico sobre la hoja PRODUCCION.
Registrar primer pase, preguntas del dueño, reentry canónico y segundo pase.
Ejecutar únicamente una tool solicitada explícitamente y ya soportada.
No declarar diagnóstico industrial integral, scrap u OEE.
No seleccionar tools automáticamente.
No agregar fórmulas ni capacidades durante el piloto.
```
