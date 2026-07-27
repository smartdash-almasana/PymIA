# SERVICE 1 — Physical P6/P7/P8 Capability Readiness Matrix V1

Status: `READY`

## Goal

Verify automatically, using physical XLSX fixtures and canonical authorities, that semantic evidence which passed the physical corpus behaves correctly downstream:

```text
physical XLSX
→ canonical intake
→ canonical ingestion output
→ semantic bridge
→ P6 semantic approval
→ P7 requirement matching
→ P8 computability
→ product-root execution only when P8 is COMPUTABLE
```

This matrix is not a second product pipeline. It reuses the canonical XLSX intake, semantic bridge, P6, P7, P8 and product root.

## Ground-truth rule

Expected P7 families, P8 statuses and positive execution outputs are explicitly declared in the readiness tools. They are not inferred from runtime output.

Columns marked `unknown` by the approved physical semantic corpus are excluded from this P6/P7 readiness slice, equivalent to owner-scoped non-participation. This matrix does not replace the existing owner-reentry tests.

## Executed scope

```text
physical negative/mixed cases: 7
P6 cases: 7
P7 cases: 7
P8 negative probes: 14
physical COMPUTABLE positive controls: 3
```

Results:

```text
P6 correct: 7/7
P7 correct: 7/7
P8 negative probes correct: 14/14
unsafe executions: 0
structural failures: 0
computable positive physical cases: 3
executed positive physical cases: 3
```

Verdict:

```text
READY
```

## Positive physical controls

The matrix now includes three legitimate `COMPUTABLE` + execution controls:

```text
LIQ_001 sold_vs_collected_gap
  sold_amount = 4600.0
  collected_amount = 4000.0
  gap_amount = 600.0
  classification = SALES_PENDING_COLLECTION

LIQ_002 projected_closing_cash_balance
  initial_balance = 1000.0
  expected_collections = 2500.0
  expected_payments = 1800.0
  projected_closing_balance = 1700.0
  classification = POSITIVE_PROJECTED_BALANCE

PYME_011 dso
  accounts_receivable = 3000.0
  sales = 9000.0
  days = 30.0
  dso_days = 10.0
  classification = DSO_WITHIN_PERIOD
```

All three follow:

```text
P6 APPROVED
→ expected P7 family REQUIREMENT_MATCHED
→ P8 COMPUTABLE
→ GovernedComputationInput present
→ product root
→ EVALUATED
```

The product root derives the values from physical XLSX rows. No runtime fallback or hardcoded computed result is used.

## Negative controls proven

The existing 14 P8 probes continue to prove that:

- sales/margin sheets may satisfy `OPERATION_CORE` and/or `SALES_MARGIN` while still lacking collections evidence;
- purchases can satisfy `PURCHASES_SUPPLIERS` without incorrectly satisfying sales operation requirements;
- stock sheets distinguish incomplete vs complete `INVENTORY_CONTROL` evidence;
- collections-only sheets correctly remain missing sales evidence for `sold_vs_collected_gap`;
- unsupported or not-governed capabilities remain `UNSUPPORTED_CAPABILITY`;
- governed capabilities with missing evidence remain `NEEDS_EVIDENCE`;
- no P8-negative probe carries a governed execution input;
- no execution is attempted when P8 is not `COMPUTABLE`.

## Coverage boundary

This V1 certifies physical positive end-to-end paths for:

```text
sold_vs_collected_gap / LIQ_001
projected_closing_cash_balance / LIQ_002
dso / PYME_011
```

It does not claim physical positive execution coverage for every capability in the generic registry. The remaining capabilities require their own explicit physical controls before production-certification coverage can be claimed.

## Implementation artifacts

```text
tools/service_1_physical_p6_p7_p8_capability_readiness_matrix_v1.py
tools/service_1_physical_computable_positive_controls_v1.py
tests/smartpyme/test_service_1_physical_p6_p7_p8_capability_readiness_matrix_v1.py
tests/smartpyme/test_service_1_physical_computable_positive_controls_v1.py
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_LIQ_001_SOLD_VS_COLLECTED.xlsx
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_LIQ_002_PROJECTED_CASH.xlsx
prueba_excels/SERVICE_1_PHYSICAL_POSITIVE_DSO.xlsx
```

No autonomous delivery, semantic rebinding after P6, alternate execution root or legacy computation-plan authority is introduced.
