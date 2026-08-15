# SERVICE_1_EXCEL_REALITY_LAB_A2_CALCULATION_MATRIX_V1

## Status

LOCAL_PASS

## Purpose

Verify governed calculation paths over physical XLSX controls without treating every structural corpus case as calculation-applicable.

Canonical chain exercised:

```text
physical XLSX
→ canonical intake
→ owner confirmation / P6
→ P7 requirement match
→ P8 computability
→ governed computation input
→ deterministic kernel
→ bounded numeric result
```

## Targets

```text
sold_vs_collected_gap
net_margin_real
projected_closing_cash_balance
dso
current_ratio
```

These correspond to LIQ_001, REN_001 and the three currently certified Working Capital component controls.

## Result

```text
targets = 5
targets_passed = 5
P8_COMPUTABLE = 5/5
governed_input_present = 5/5
kernel_evaluated = 5/5
failures = 0
```

Verified reference outputs include:

```text
sold_vs_collected_gap.gap_amount = 600.0
projected_closing_cash_balance.projected_closing_balance = 1700.0
dso.dso_days = 10.0
current_ratio.current_ratio_value = 1.5
net_margin_real = EVALUATED with net_margin_amount + net_margin_percentage
```

## Scope boundary

The 23-case A1 structural corpus is not automatically a 23-case calculation corpus.

```text
STRUCTURALLY_INGESTIBLE != COMPUTABLE
```

Cases without a governed capability target remain outside A2 rather than being misclassified as failures.

A2 does not authorize runtime, delivery, new capabilities, new formula authorities, or production claims.

## Evidence

Evaluator:

`tools/service_1_excel_reality_lab_a2_calculation_matrix_v1.py`

Regression:

`tests/smartpyme/test_service_1_excel_reality_lab_a2_calculation_matrix_v1.py`

Validation:

```text
A2 focal: 2 passed
A0+A1+A2+positive controls partition: 18 passed
physical corpus + architecture partition: 15 passed
architecture baseline: PASS_ARCHITECTURE_BASELINE_V1 / BLOCKERS NONE
```

The combined one-shot pytest attempt received an MCP 502 before a test result; the same gate was then executed in two successful partitions.

## Next cut

`EXCEL_REALITY_LAB_A3_RUBRO_MATRIX_V1`
