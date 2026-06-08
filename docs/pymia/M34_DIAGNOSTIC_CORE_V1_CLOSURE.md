# M34 — DiagnosticCoreV1 Closure

Fecha original de cierre: 2026-06-07
Fecha de reconciliación: 2026-06-08
Estado: CERRADO / RECONCILIADO
HEAD local de reconciliación: `c6d1131`
Alcance: cierre histórico de M34 reconciliado contra el estado real posterior de M35

---

## Resultado del ciclo

M34 dejó creado y validado el primer núcleo calculador determinístico de PymIA.

El ciclo no integra canales, runtime externo ni evidencia documental real. Su alcance fue estrictamente:

```text
input estructurado
→ FormulaEngineService
→ DiagnosticCoreV1
→ resultado estructurado
→ bloqueo honesto si faltan inputs
→ source_refs preservados
→ CANDIDATE, nunca CONFIRMED
```

---

## Commits principales del ciclo

```text
38a1f3f feat(diagnostic-core): add v1 skeleton
e87c8a1 feat(diagnostic-core): support REN001 net margin formula
8e20f2d test(diagnostic-core): cover REN001 missing taxes input
4edaf04 feat(diagnostic-core): support LIQ001 sold collected formula
241dcf9 feat(diagnostic-core): support INV002 stock rotation formula
a894ffa feat(diagnostic-core): support PYME011 dso formula
5e760ed feat(diagnostic-core): support PYME013 dso dpo gap formula
3cb2c85 feat(diagnostic-core): support LIQ002 projected ending balance formula
f5652a3 test(diagnostic-core): cover LIQ002 zero and negative balances
888ac9d feat(diagnostic-core): support PYME024 current ratio formula
4276996 feat(diagnostic-core): support PYME017 pricing drift formula
a8d66be feat(diagnostic-core): support INV001 reorder point formula
314d721 test(diagnostic-core): cover INV001 zero and decimal inputs
4f21f16 feat(diagnostic-core): support break even sales formula
b05c368 fix(diagnostic-core): guard break even invalid margin inputs
```

---

## Fórmulas cerradas en M34

| # | formula_id | Eje | Fórmula |
|---|---|---|---|
| 1 | `REN_001_margen_neto_real` | rentabilidad | `((sale_price - costs - taxes) / sale_price) * 100` |
| 2 | `LIQ_001_vendido_cobrado` | liquidez | `sold_amount - collected_amount` |
| 3 | `INV_002_rotacion_stock` | inventario | `cost_of_goods_sold / average_stock` |
| 4 | `PYME_011_dso` | cobranzas | `accounts_receivable / sales * days` |
| 5 | `PYME_013_dso_dpo_gap` | liquidez/capital de trabajo | `dso - dpo` |
| 6 | `LIQ_002_saldo_final_proyectado` | liquidez | `initial_balance + expected_collections - expected_payments` |
| 7 | `PYME_024_liquidez_corriente` | solvencia operativa | `current_assets / current_liabilities` |
| 8 | `PYME_017_pricing_drift` | pricing | `(own_price - market_price) / market_price * 100` |
| 9 | `INV_001_punto_reposicion` | inventario | `(average_sales * lead_time) + safety_stock` |
| 10 | `punto_equilibrio_ventas` | costos fijos / equilibrio | `fixed_costs / contribution_margin_rate` |

---

## Contratos preservados

Durante M34 se sostuvo:

```text
- no confirmar patologías;
- no inventar inputs;
- bloquear inputs faltantes;
- bloquear divisiones por cero;
- bloquear margen de contribución negativo para punto de equilibrio;
- preservar source_refs;
- devolver estructuras serializables;
- mantener DiagnosticCoreV1 en estado CANDIDATE para fórmulas OK;
- no alterar capas fuera del slice activo.
```

---

## Evidencia focal acumulada en M34

Último estado informado por usuario durante el ciclo M34:

```text
tests/services/test_formula_engine_service.py: 41 passed
tests/diagnosticcore/test_diagnostic_core_v1.py: 13 passed
```

Total focal informado:

```text
54/54 passed
```

---

## Archivos centrales del núcleo

```text
pymia/contracts/formula_contract.py
pymia/services/formula_engine_service.py
pymia/diagnostic_core/__init__.py
pymia/diagnostic_core/models.py
pymia/diagnostic_core/core.py
tests/services/test_formula_engine_service.py
tests/diagnosticcore/test_diagnostic_core_v1.py
```

---

## No resuelto en M34

M34 no resolvió por diseño:

```text
- binding de evidencia estructurada hacia `DiagnosticCoreInput`;
- cobertura extendida de fórmulas adicionales ya soportadas por el core;
- reporte puro de suficiencia de evidencia por fórmula;
- cualquier integración conversacional, runtime o Telegram.
```

---

## Relación con el estado posterior del repositorio

Los puntos no resueltos en M34 fueron abordados después en M35.

Al momento de esta reconciliación documental, el repositorio ya contiene:

```text
- DiagnosticCoreV1 implementado;
- evidence binding implementado;
- source_refs scoped por fórmula;
- extensión del binding a más fórmulas;
- evidence sufficiency report implementado.
```

Por lo tanto, M34 debe leerse como cierre histórico del núcleo base, no como fotografía actual del proyecto.

## Estado reconciliado

```text
M34 = CERRADO
M34 conserva valor como cierre histórico del núcleo base
La continuación metodológica efectiva ocurrió en M35
Este documento ya no debe usarse para afirmar "M35 = no iniciado"
```
