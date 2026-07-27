# SERVICE 1 — Remaining Capability Governance Convergence Audit V1

Status: `GOVERNANCE_GAPS_REMAIN`

## Purpose

Determine whether the remaining productive registry capabilities can legitimately receive physical end-to-end controls through the canonical path:

```text
XLSX
→ semantic understanding
→ P6
→ P7
→ P8
→ GovernedComputationInput
→ product root
```

The audit prevents a false readiness result caused by testing the generic kernel directly while bypassing canonical governance.

## Current certified positive physical controls

Outside the generic registry, specialized LIQ_001 is physically certified end-to-end.

Inside the registry, the following capabilities are fully aligned across formula catalog, enriched pathology catalog, P7 and P8 evidence matrix and have positive physical controls:

```text
projected_closing_cash_balance / LIQ_002
dso / PYME_011
```

Together with specialized LIQ_001, current positive physical coverage is:

```text
LIQ_001 sold_vs_collected_gap
LIQ_002 projected_closing_cash_balance
PYME_011 dso
```

## Remaining registry gaps

After the bounded governance expansion, three registry capabilities remain outside canonical P8 governance:

```text
adjusted_operating_cash_flow
dpo
payment_collection_gap
```

The following six are now governance-aligned and ready for physical positive controls:

```text
reorder_point
inventory_turnover
current_ratio
sales_concentration
interest_burden_ratio
index_update_ratio
```

Observed gap types include:

```text
registry formula_ref differs from formula catalog id
pathology missing from pathology_catalog.enriched.v1.json
no P7 target capability/family
no P8 evidence-matrix mapping
```

`dpo` additionally has no corresponding formula entry in `formula_catalog.v1.json` under its registry prerequisite pathology code.

`adjusted_operating_cash_flow` is present in the formula catalog under `PYME_026_flujo_operativo`, but its calculation state is:

```text
CALCULABLE_CON_SUPUESTOS
```

Therefore P8 must not be changed merely to force a positive COMPUTABLE control.

## Governance guardrail

The enriched pathology catalog currently declares:

```text
scope_fixed = true
scope_not_reopened = true
```

For that reason this work does not silently add the nine remaining pathologies or reinterpret their governance status.

Creating XLSX positive fixtures before resolving those governance gaps would produce a test that bypasses P7/P8 rather than certifying the product.

## Automated audit

Implementation:

```text
tools/service_1_remaining_capability_governance_convergence_audit_v1.py
tests/smartpyme/test_service_1_remaining_capability_governance_convergence_audit_v1.py
```

Current result:

```text
registry capabilities = 11
registry capabilities with positive physical certification = 2
remaining governance gaps = 3
scope_fixed = true
scope_not_reopened = true
```

LIQ_001 is specialized outside this generic registry count and remains independently physically certified.

## Next required decision

Before physical positive controls can be expanded to the remaining capabilities, governance scope must be explicitly reopened or superseded by a new governed catalog version.

Recommended next engineering action:

```text
DEFINE_AND_AUTHORIZE_REMAINING_CAPABILITY_GOVERNANCE_EXPANSION_V1
```

That action must define, capability by capability:

```text
canonical formula id
pathology code
calculation state
required semantic variables
P7 requirement family
P8 evidence-matrix mapping
required evidence
whether assumptions prevent COMPUTABLE status
```

Only after that convergence should physical XLSX controls be generated for those capabilities.

No runtime authorization, delivery authorization or global product-ready claim is created by this audit.
