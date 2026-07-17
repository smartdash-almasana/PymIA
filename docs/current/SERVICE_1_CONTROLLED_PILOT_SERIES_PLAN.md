# Servicio 1 — Controlled Pilot Series Plan V1

**Ciclo:** `CYCLE_032_SERVICE_1_CONTROLLED_PILOT_SERIES_PLAN`
**Fecha:** 2026-07-16
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

## Pilotos activos

| Piloto | Archivo | Hoja primaria | Caso | Motivo |
|---|---|---|---|---|
| S1-PILOT-001 | `cafeteria_abc.xlsx` | `Ventas` | cafetería ventas/productos/sucursales | baseline operatorless ya PASS |
| S1-PILOT-003 | `pyme_textil_compleja.xlsx` | `VENTAS` | textil ventas/costos/margen | stress margen descuento canal |
| S1-PILOT-004 | `distribuidora_mayorista_compleja.xlsx` | `OPERACION` | distribuidora ruta/SKU/margen | stress comercial 5000 filas |
| S1-PILOT-005 | `fabrica_industrial_compleja.xlsx` | `PRODUCCION` | producción/scrap/OEE | límite semántico sin fórmula inventada |
| S1-PILOT-006 | `taller_mecanico_lubricar_srl.xlsx` | `ORDENES_TRABAJO` | taller servicios/stock | PyME servicios multihoja |
| S1-PILOT-007 | `constructora_nueva_era_srl.xlsx` | `OBRAS` | constructora presupuesto/gasto/cobro | costos reales y cobros |
| S1-PILOT-008 | `la_textil_cosida_srl_mar_abr_may_2026.xlsx` | `ventas` | textil completa multihoja | late-stage workbook completo |

## Orden de ejecución

```text
1. S1-PILOT-003 pyme_textil_compleja.xlsx
2. S1-PILOT-004 distribuidora_mayorista_compleja.xlsx
3. S1-PILOT-006 taller_mecanico_lubricar_srl.xlsx
4. S1-PILOT-007 constructora_nueva_era_srl.xlsx
5. S1-PILOT-008 la_textil_cosida_srl_mar_abr_may_2026.xlsx
6. S1-PILOT-005 fabrica_industrial_compleja.xlsx
```

`S1-PILOT-001` queda como control de regresión ya probado.

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

## Próximo ciclo

```text
CYCLE_033:
RUN_S1_PILOT_003_TEXTIL_COMPLEJA
```
