# SERVICE 1 — Physical COMPUTABLE Positive Controls V1

Status: `CLOSED_PASS`

Verdict: `PASS_PHYSICAL_COMPUTABLE_POSITIVE_CONTROLS_V1`

## Purpose

Provide physical XLSX evidence that the canonical product path moves from approved semantics to deterministic execution only after P8 returns `COMPUTABLE`.

Canonical path under test:

```text
physical XLSX
→ canonical intake
→ canonical ingestion
→ semantic bridge
→ P6 APPROVED
→ P7 REQUIREMENT_MATCHED
→ P8 COMPUTABLE
→ GovernedComputationInput
→ product root
→ deterministic evaluation
```

## Positive controls

### S1-POS-001 — LIQ_001

Fixture:

```text
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_LIQ_001_SOLD_VS_COLLECTED.xlsx
```

Capability:

```text
sold_vs_collected_gap
```

Expected and observed evidence:

```text
sold_amount = 4600.0
collected_amount = 4000.0
```

Result:

```text
gap_amount = 600.0
classification = SALES_PENDING_COLLECTION
```

### S1-POS-002 — LIQ_002

Fixture:

```text
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_LIQ_002_PROJECTED_CASH.xlsx
```

Capability:

```text
projected_closing_cash_balance
```

Expected and observed evidence:

```text
initial_balance = 1000.0
expected_collections = 2500.0
expected_payments = 1800.0
```

Result:

```text
projected_closing_balance = 1700.0
classification = POSITIVE_PROJECTED_BALANCE
```

### S1-POS-003 — PYME_011 / DSO

Fixture:

```text
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_DSO.xlsx
```

Capability:

```text
dso
```

Expected and observed evidence:

```text
accounts_receivable = 3000.0
sales = 9000.0
days = 30.0
```

Result:

```text
dso_days = 10.0
classification = DSO_WITHIN_PERIOD
```

## Canonical semantic completion required by the controls

The controls exposed canonical roles already required by P7/P8 but not yet recognized by the column-understanding engine:

```text
initial_balance
expected_collections
expected_payments
period_days
```

They were added to the existing deterministic semantic catalog only. No alternate semantic layer was created.

DSO also exposed a historical variable-name mismatch:

```text
sales_amount role
→ sold_amount for LIQ_001
→ sales for DSO
```

P8 now normalizes `sales_amount` evidence to the governed formula-variable alias `sales` when required. The P6 semantic role remains unchanged; this is variable normalization, not semantic rebinding.

## Result

```text
controls = 3
controls_passed = 3
computable_positive_cases = 3
executed_positive_cases = 3
failures = 0
```

## Safety

```text
runtime_authorized = false
delivery_authorized = false
product_ready = false
```

No fallback, inferred missing variable, semantic rebinding after P6, alternate product root, autonomous delivery or hardcoded computed result is used.

## Coverage boundary

This closure proves physical positive end-to-end execution for:

```text
LIQ_001 sold_vs_collected_gap
LIQ_002 projected_closing_cash_balance
PYME_011 dso
```

It does not claim physical positive coverage for every capability in the generic registry.
