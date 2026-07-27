# SERVICE 1 — Bounded Six Physical COMPUTABLE Controls V1

Status: `CLOSED_PASS`

## Scope

Physical end-to-end certification for the six capabilities authorized by the bounded governance expansion:

```text
reorder_point
inventory_turnover
current_ratio
sales_concentration
interest_burden_ratio
index_update_ratio
```

Fixture:

```text
prueba_excels/SERVICE_1_BOUNDED_SIX_PHYSICAL_CONTROLS.xlsx
```

The workbook contains 12 sheets: six positive controls and six matched negative controls with one required variable removed.

## Positive controls

All six follow the canonical route:

```text
physical XLSX
→ canonical intake
→ semantic understanding
→ P6 APPROVED
→ P7 REQUIREMENT_MATCHED
→ P8 COMPUTABLE
→ GovernedComputationInput
→ service_1_product_pipeline_v1
→ EVALUATED
```

Observed deterministic results:

```text
reorder_point
  inputs: average_sales=10, lead_time=5, safety_stock=20
  result: reorder_point_units=70
  classification: REORDER_POINT_CALCULATED

inventory_turnover
  inputs: cost_of_goods_sold=12000, average_stock=3000
  result: inventory_turnover_ratio=4.0
  classification: POSITIVE_RECORDED_TURNOVER

current_ratio
  inputs: current_assets=15000, current_liabilities=10000
  result: current_ratio_value=1.5
  classification: POSITIVE_CURRENT_RATIO

sales_concentration
  inputs: main_sku_sales=4000, total_sales=10000
  result: sales_concentration_percentage=40.0
  classification: CONCENTRATION_WITHIN_RECORDED_TOTAL

interest_burden_ratio
  inputs: interest_expense=1000, ebitda=5000
  result: interest_burden_ratio_value=0.2
  classification: POSITIVE_INTEREST_BURDEN

index_update_ratio
  inputs: closing_index=150, origin_index=100
  result: index_update_ratio=1.5
  classification: INDEX_ABOVE_ORIGIN
```

## Negative controls

For each capability a matched physical sheet omits one mandatory input.

Result for all six:

```text
P8 = NEEDS_EVIDENCE
GovernedComputationInput = absent
execution = not attempted
```

## Metrics

```text
positive controls = 6/6 PASS
negative controls = 6/6 PASS
unsafe executions = 0
```

Together with the previously certified physical controls, current positive physical end-to-end capability coverage is:

```text
LIQ_001 sold_vs_collected_gap
LIQ_002 projected_closing_cash_balance
PYME_011 dso
INV_001 reorder_point
INV_002 inventory_turnover
PYME_024 current_ratio
PYME_033 sales_concentration
PYME_027 interest_burden_ratio
REN_002 index_update_ratio
```

The following remain deliberately outside physical positive certification:

```text
adjusted_operating_cash_flow — CALCULABLE_CON_SUPUESTOS
dpo — canonical prerequisite governance unresolved
payment_collection_gap — depends on governed DPO
```

## Implementation artifacts

```text
tools/service_1_bounded_six_physical_computable_controls_v1.py
tests/smartpyme/test_service_1_bounded_six_physical_computable_controls_v1.py
prueba_excels/SERVICE_1_BOUNDED_SIX_PHYSICAL_CONTROLS.xlsx
```

No runtime authorization, autonomous delivery or global product-ready claim is created by this closeout.

## Next action

```text
CAPABILITY_PHYSICAL_COVERAGE_GATE_V1
```

The next gate should consolidate all nine physically certified positive capabilities, confirm the three deliberate exclusions, and decide whether capability coverage is sufficient to proceed to owner web/delivery hardening.
