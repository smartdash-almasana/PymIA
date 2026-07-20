# Servicio 1 — Hoja de ruta de 12 patologías productivas

**Ciclo:** `CYCLE_041_DEFINE_12_PRODUCTIVE_PATHOLOGY_ROADMAP`  
**Estado:** `DECIDED`  
**Fecha:** 2026-07-20

## Objetivo

Fijar el conjunto exacto de doce patologías productivas de Servicio 1 y el orden de implementación posterior a `LIQ_001` y `REN_001`.

Esta decisión no implementa nuevas capacidades. Autoriza únicamente ciclos individuales, uno por patología, con regresión y cierre documental propios.

## Base ya productiva

| Orden | Patología | Capacidad | Estado |
|---|---|---|---|
| 1 | `LIQ_001` | `sold_vs_collected_gap` | productiva con cálculo, hallazgo, tratamiento y entrega XLSX explícita |
| 2 | `REN_001` | `net_margin_real` | productiva con cálculo, hallazgo y tratamiento; entrega XLSX no autorizada |

## Diez patologías adicionales seleccionadas

| Prioridad | Patología | Fórmula | Variables mínimas | Evidencia mínima | Estado de fórmula |
|---:|---|---|---|---|---|
| 3 | `LIQ_002` | `initial_balance + expected_collections - expected_payments` | `initial_balance`, `expected_collections`, `expected_payments` | saldo inicial, cobranzas esperadas, pagos esperados | `CALCULABLE` |
| 4 | `PYME_011` | `accounts_receivable / sales * days` | `accounts_receivable`, `sales`, `days` | cuentas por cobrar, ventas del período, días del período | `CALCULABLE` |
| 5 | `PYME_013` | `dso - dpo` | `dso`, `dpo` | DSO calculado, DPO calculado | `CALCULABLE` |
| 6 | `INV_001` | `(average_sales * lead_time) + safety_stock` | `average_sales`, `lead_time`, `safety_stock` | historial por SKU, lead time, política de stock | `CALCULABLE` |
| 7 | `INV_002` | `cost_of_goods_sold / average_stock` | `cost_of_goods_sold`, `average_stock` | CMV, inventario inicial, inventario final | `CALCULABLE` |
| 8 | `PYME_024` | `current_assets / current_liabilities` | `current_assets`, `current_liabilities` | balance, activo corriente, pasivo corriente | `CALCULABLE` |
| 9 | `PYME_033` | `main_sku_sales / total_sales * 100` | `main_sku_sales`, `total_sales` | ventas por SKU, ventas totales | `CALCULABLE` |
| 10 | `REN_002` | `closing_index / origin_index` | `closing_index`, `origin_index` | índices y fechas de origen/cierre | `CALCULABLE` |
| 11 | `PYME_027` | `interest_expense / ebitda` | `interest_expense`, `ebitda` | estado de resultados, intereses, EBITDA | `CALCULABLE` |
| 12 | `PYME_026` | `net_income + depreciation + amortization - working_capital_change` | `net_income`, `depreciation`, `amortization`, `working_capital_change` | estado de resultados y balances de dos períodos | `CALCULABLE_CON_SUPUESTOS` |

## Criterio de orden

1. Primero liquidez y cobranzas, porque reutilizan evidencia y contratos cercanos a `LIQ_001`.
2. Luego inventario, porque requiere agregaciones determinísticas por SKU y períodos.
3. Después solvencia, concentración y reposición, que introducen denominadores y límites adicionales.
4. Finanzas corporativas y flujo operativo quedan al final por dependencia contable y mayor riesgo de supuestos.

## Dominio matemático mínimo por patología

- Todo valor debe ser numérico y finito.
- Los importes, días, cantidades, índices y saldos no pueden ser negativos salvo que la definición contable de la patología lo autorice explícitamente.
- Todo denominador debe ser estrictamente mayor que cero.
- `average_stock` debe derivarse de inventario inicial y final o recibirse como evidencia explícita gobernada; no se inventa.
- `dso` y `dpo` deben venir de cálculos certificados o evidencia explícita; no se reconstruyen implícitamente durante `PYME_013`.
- `working_capital_change` exige dos períodos comparables y convención de signo documentada.
- Ningún umbral orientativo confirma por sí solo una patología.

## Definition of Done por patología

Cada ciclo individual debe cerrar:

1. contrato de capacidad y plan gobernado;
2. variables canónicas y evidencia mínima;
3. dominio matemático, cero, negativos y denominadores;
4. agregación determinística desde tablas normalizadas cuando corresponda;
5. evaluador con clasificaciones explícitas;
6. hallazgo acotado y tratamiento sin causalidad inventada;
7. integración en la raíz única mediante solicitud explícita;
8. decisión explícita sobre entrega XLSX;
9. tests focales, guards y regresión completa;
10. ejecución observada sobre evidencia autorizada;
11. actualización de locks, gates, disposición y estado rector.

## Exclusiones

- No se implementan las diez patologías en este ciclo.
- No se habilita selección automática de capacidad.
- No se incorporan LLM, runtime autónomo ni diagnóstico causal.
- Scrap y OEE quedan fuera de las doce patologías de esta hoja de ruta.
- Las fórmulas fiscales o normativas no entran en esta serie sin validación externa vigente.

## Próximo ciclo autorizado

```text
CYCLE_042_CONNECT_LIQ_002_TO_PRODUCTIVE_ROOT
```

Alcance del siguiente ciclo:

```text
Conectar exclusivamente LIQ_002.
Reutilizar la raíz, plan, guards y contrato de outcome existentes.
Definir saldo final proyectado, clasificación y límites.
No implementar PYME_011 ni otra patología en paralelo.
No autorizar entrega XLSX hasta decisión explícita del propio ciclo.
```
