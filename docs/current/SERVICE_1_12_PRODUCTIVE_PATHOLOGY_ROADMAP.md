# Servicio 1 — Hoja de ruta de 12 patologías productivas

**Ciclo:** `CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP`  
**Estado:** `DECIDED`  
**Fecha:** 2026-07-20

## Objetivo

Fijar el conjunto exacto de doce patologías productivas de Servicio 1 y el orden de implementación, preservando una raíz productiva única y ejecución determinística.

## Base ya productiva

| Orden | Patología | Capacidad | Estado |
|---|---|---|---|
| 1 | `LIQ_001` | `sold_vs_collected_gap` | productiva con cálculo, hallazgo, tratamiento y entrega XLSX explícita |
| 2 | `REN_001` | `net_margin_real` | productiva con cálculo, hallazgo y tratamiento; entrega XLSX no autorizada |
| 3 | `LIQ_002` | `projected_closing_cash_balance` | productiva con cálculo, hallazgo y tratamiento; entrega XLSX no autorizada |
| 4 | `PYME_011` | `dso` | productiva con cálculo, hallazgo y tratamiento; entrega XLSX no autorizada |

## Ocho patologías restantes seleccionadas

| Prioridad | Patología | Fórmula | Variables mínimas | Evidencia mínima | Estado de fórmula |
|---:|---|---|---|---|---|
| 5 | `PYME_013` | `dso - dpo` | `dso`, `dpo` | DSO calculado, DPO calculado | `DEFERRED_AS_FIRST_COMPOSITE_CAPABILITY` |
| 6 | `INV_001` | `(average_sales * lead_time) + safety_stock` | `average_sales`, `lead_time`, `safety_stock` | historial por SKU, lead time, política de stock | `CALCULABLE` |
| 7 | `INV_002` | `cost_of_goods_sold / average_stock` | `cost_of_goods_sold`, `average_stock` | CMV, inventario inicial, inventario final | `CALCULABLE` |
| 8 | `PYME_024` | `current_assets / current_liabilities` | `current_assets`, `current_liabilities` | balance, activo corriente, pasivo corriente | `CALCULABLE` |
| 9 | `PYME_033` | `main_sku_sales / total_sales * 100` | `main_sku_sales`, `total_sales` | ventas por SKU, ventas totales | `CALCULABLE` |
| 10 | `REN_002` | `closing_index / origin_index` | `closing_index`, `origin_index` | índices y fechas de origen/cierre | `CALCULABLE` |
| 11 | `PYME_027` | `interest_expense / ebitda` | `interest_expense`, `ebitda` | estado de resultados, intereses, EBITDA | `CALCULABLE` |
| 12 | `PYME_026` | `net_income + depreciation + amortization - working_capital_change` | `net_income`, `depreciation`, `amortization`, `working_capital_change` | estado de resultados y balances de dos períodos | `CALCULABLE_CON_SUPUESTOS` |

## Transición arquitectónica

`CYCLE_044_CONNECT_PYME_013_TO_PRODUCTIVE_ROOT` queda `SUSPENDED_BY_ARCHITECTURAL_DECISION`.

`PYME_013` no se elimina del roadmap. Se difiere para implementarse como primera capacidad `COMPOSITE` sobre el Generic Productive Capability Kernel, consumiendo resultados gobernados de `dso` y `dpo` y sin reconstruirlos implícitamente.

## Dominio matemático mínimo

- Todo valor debe ser numérico y finito.
- Los importes, días, cantidades, índices y saldos no pueden ser negativos salvo autorización explícita.
- Todo denominador debe ser estrictamente mayor que cero.
- `average_stock` debe derivarse de inventario inicial y final o recibirse como evidencia explícita gobernada.
- `dso` y `dpo` deben provenir de resultados gobernados o evidencia explícita; no se reconstruyen implícitamente durante `PYME_013`.
- `working_capital_change` exige dos períodos comparables y convención de signo documentada.
- Ningún umbral orientativo confirma por sí solo una patología.

## Definition of Done por patología

1. contrato de capacidad y plan gobernado;
2. variables canónicas y evidencia mínima;
3. dominio matemático, cero, negativos y denominadores;
4. agregación determinística desde tablas normalizadas cuando corresponda;
5. evaluador o ejecución genérica con clasificaciones explícitas;
6. hallazgo acotado y tratamiento sin causalidad inventada;
7. integración en la raíz única mediante solicitud explícita;
8. decisión explícita sobre entrega XLSX;
9. tests focales, guards y regresión completa;
10. ejecución observada sobre evidencia autorizada;
11. actualización de locks, gates, disposición y estado rector.

## Exclusiones

- No se habilita selección automática de capacidad.
- No se incorporan LLM, runtime autónomo ni diagnóstico causal.
- Scrap y OEE quedan fuera de esta hoja de ruta.
- Las fórmulas fiscales o normativas no entran sin validación externa vigente.

## Próximo ciclo autorizado

```text
CYCLE_044A_DEFINE_GENERIC_PRODUCTIVE_CAPABILITY_KERNEL_ARCHITECTURE
```

Alcance:

```text
Definir arquitectura, contratos, inventario de duplicación y criterios de aceptación.
No implementar código productivo.
No modificar la raíz productiva.
No conectar PYME_013.
No eliminar módulos existentes.
```