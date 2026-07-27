# SERVICE 1 — Remaining Capability Governance Expansion V1

Status: `CLOSED_PASS`

## Purpose

Define the smallest safe governance expansion required to move additional productive registry capabilities through the canonical path:

```text
XLSX
→ SemanticHypothesis
→ P6ApprovalDecision
→ P7 RequirementMatch
→ P8 ComputabilityDecision
→ GovernedComputationInput
→ service_1_product_pipeline_v1
```

This decision does not reopen runtime authority, delivery authority or product-ready status.

## Migration policy

The existing V1 catalog scope remains historical evidence. It is not silently reinterpreted in place.

Migration discipline:

```text
CREATE
→ MIGRATE
→ VERIFY
→ DELETE legacy mismatch only after equivalence is proven
```

A later governed catalog/matrix version may supersede the current fixed-scope V1 artifacts. Existing consumers must not choose arbitrarily between versions.

## Authorized now

Six capabilities have deterministic formulas already present in the canonical formula catalog with `CALCULABLE` state. Their current gaps are governance alignment gaps, not missing mathematics.

| capability | pathology | canonical formula | required variables |
|---|---|---|---|
| `reorder_point` | `INV_001` | `INV_001_punto_reposicion` | `average_sales`, `lead_time`, `safety_stock` |
| `inventory_turnover` | `INV_002` | `INV_002_rotacion_stock` | `cost_of_goods_sold`, `average_stock` |
| `current_ratio` | `PYME_024` | `PYME_024_liquidez_corriente` | `current_assets`, `current_liabilities` |
| `sales_concentration` | `PYME_033` | `PYME_033_concentracion_sku` | `main_sku_sales`, `total_sales` |
| `interest_burden_ratio` | `PYME_027` | `PYME_027_intereses_ebitda` | `interest_expense`, `ebitda` |
| `index_update_ratio` | `REN_002` | `REN_002_coeficiente_reposicion` | `closing_index`, `origin_index` |

For these six, the next migration may add governed pathology entries, P7 requirement families and P8 evidence-matrix mappings, while aligning registry formula references to the canonical formula IDs.

## Deferred — fail closed

### `adjusted_operating_cash_flow`

Current formula catalog state:

```text
CALCULABLE_CON_SUPUESTOS
```

It remains outside positive `COMPUTABLE` certification until the assumptions around `working_capital_change` are explicitly governed. No threshold or P8 rule may be weakened to make it pass.

### `dpo`

The registry prerequisite exists, but no canonical formula entry currently exists under its prerequisite pathology identity.

Required before promotion:

```text
canonical DPO formula identity
pathology/prerequisite governance
required evidence
P7 requirement family
P8 mapping
```

### `payment_collection_gap`

This composite depends on governed results from DSO and DPO. DSO is governed; DPO is not. The composite remains deferred until DPO is independently governed and certified.

## Invariants

```text
NO_LLM_RUNTIME_AUTHORITY
ONE_CANONICAL_PRODUCT_ROOT
NO_SEMANTIC_REBIND_AFTER_P6
P7_AND_P8_REMAIN_SEPARATE
P8_REQUIRED_BEFORE_GOVERNED_INPUT
NO_RUNTIME_OR_DELIVERY_AUTHORIZATION_FROM_THIS_DECISION
FAIL_CLOSED_FOR_DEFERRED_CAPABILITIES
```

## Automated authority

Executable decision artifact:

```text
tools/service_1_remaining_capability_governance_expansion_plan_v1.py
```

Regression contract:

```text
tests/smartpyme/test_service_1_remaining_capability_governance_expansion_plan_v1.py
```

## Implementation result

The bounded expansion is implemented.

```text
registry formula refs aligned to canonical formula catalog ids
P7 families added: 6
pathology_catalog.enriched.v2.json created additively
service_1_formula_pathology_evidence_matrix.v2.json created additively
P8 default governance source migrated to V2
six authorized capabilities reach P8 COMPUTABLE with GovernedComputationInput
remaining governance gaps: 3
```

The deferred set remains unchanged and fail-closed:

```text
adjusted_operating_cash_flow
dpo
payment_collection_gap
```

## Next action

```text
BUILD_PHYSICAL_COMPUTABLE_CONTROLS_FOR_BOUNDED_SIX_V1
```

Only the six newly governed capabilities are in scope for physical positive controls. The three deferred capabilities remain blocked unless a later explicit governance decision resolves their stated gaps.
