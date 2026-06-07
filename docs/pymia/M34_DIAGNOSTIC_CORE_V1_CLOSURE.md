# M34 — DiagnosticCoreV1 Closure

Fecha: 2026-06-07
Estado: CERRADO EN CÓDIGO / pendiente commit documental de cierre
HEAD verificado por usuario: `b05c368`
Remote: `main...origin/main`

---

## Resultado del ciclo

M34 deja creado y validado el primer núcleo calculador determinístico de PymIA.

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

## Fórmulas cerradas

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

## Tests focales acumulados

Último estado informado por usuario para M34-S11:

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

M34 no resuelve todavía:

```text
- lectura real de Excel hacia variables del core;
- mapeo semántico automático columna → variable;
- evidence refs generados desde documentos reales;
- confirmación diagnóstica final;
- thresholds clínico-operativos;
- reporte final al dueño;
- integración de resultados con entrega de caso completo.
```

---

## Próximo ciclo recomendado

```text
M35 — Evidence-to-Core Binding
```

Objetivo:

```text
Excel / StructuredEvidence / semantic fields
→ variables normalizadas del DiagnosticCoreInput
→ fórmulas ejecutables
→ blocked/missing explícito cuando falte evidencia
```

Primer slice sugerido:

```text
M35-S1 — mapear StructuredEvidence/computed_variables a DiagnosticCoreInput para REN_001, LIQ_001 e INV_002.
```

---

## Estado de cierre

```text
M34 = CERRADO EN CÓDIGO
M34 closure doc = pendiente de commit
M35 = NO INICIADO
```
