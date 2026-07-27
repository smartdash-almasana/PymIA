# SERVICE_1_STAGE2_PACKAGE9_PRODUCT_ROOT_DISPATCH_CONVERGENCE_SPEC_V1

## Status

CLOSED_PASS

## Goal

Eliminate capability-specific branch proliferation from the canonical Service 1 product root without introducing a second dispatcher or weakening P8 governance.

## Canonical result

The productive execution shape is now:

```text
requested_capability
→ P8 / GovernedComputationInput
→ specialized exception if and only if behavior is genuinely specialized
→ otherwise CapabilityRegistry + GenericCapabilityEngine
```

The root keeps exactly two capability identity branches:

- LIQ_001 (`sold_vs_collected_gap`)
- REN_001 (`net_margin_real`)

These remain specialized because they still own distinct evaluator/outcome behavior and LIQ_001 owns an authorized XLSX delivery path.

All registry-governed generic capabilities use one generic execution path. The product root no longer duplicates constants or branches for:

- LIQ_002 projected_closing_cash_balance
- PYME_011 dso
- DPO prerequisite
- INV_001 reorder_point
- INV_002 inventory_turnover
- PYME_013 payment_collection_gap
- PYME_024 current_ratio
- PYME_033 sales_concentration
- REN_002 index_update_ratio
- PYME_027 interest_burden_ratio
- PYME_026 adjusted_operating_cash_flow

## Composite behavior

Composite dispatch is selected from the canonical registry contract:

```text
CapabilityDefinitionV1.kind == COMPOSITE
```

The root does not special-case PYME_013 by identity. Composite governed input is built through the existing P8 authority and executed by the generic kernel using governed upstream results.

## Delivery closure

Generic capabilities remain delivery-closed. Delivery blocking is derived from the governed capability definition rather than one literal branch per pathology.

DPO remains a prerequisite rather than a thirteenth pathology; its external delivery block identifier remains `DPO_DELIVERY_NOT_AUTHORIZED`.

## Technical-debt reduction

Removed from the canonical root:

- ten generic capability constants duplicated from the registry;
- ten generic identity branches;
- the identity-specific PYME_013 execution branch;
- source-inspection tests that required all generic constants/branch-specific delivery literals in the product root.

Updated PYME_011 test governance from legacy variable-family projection construction to canonical P6 decisions + P7 RequirementMatch + P8.

## Architecture invariants

- one canonical product root;
- no new dispatcher module;
- P8 remains required before generic execution;
- generic kernel never accepts a pure legacy ComputationPlan as execution authority;
- capability extension does not require adding a new product-root branch;
- specialized branches exist only for demonstrably specialized behavior;
- composite dispatch is contract-driven, not identity-driven;
- owner confirmation remains outside the controlled-execution gate.

## Validation

Canonical architecture behavior suite plus certifier:

```text
71 passed
```

Package-focused convergence suite previously reached 51/52 after removing branch duplication; the remaining PYME_011 fixture was then migrated from legacy P7 construction to canonical P6→P7→P8 and passed 4/4.

## Known legacy-test debt outside Package 9

A broader sweep exposed historical direct-engine tests that still call `GenericCapabilityEngine` with `SERVICE_1_COMPUTATION_PLAN_V1` and no `SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1`.

Those failures are consistent with the Package 7 decision that legacy ComputationPlan is not an execution authority. They must be migrated to governed-input fixtures; the runtime fallback must NOT be restored to satisfy them.

This debt is test-contract debt, not a productive runtime bypass.

Recommended next cleanup front:

```text
STAGE2_PACKAGE10_LEGACY_PROJECTION_AND_TEST_CONTRACT_RETIREMENT
```

Package 10 should migrate remaining direct generic-engine fixtures to governed input, then retire compatibility projections/adapters and specialized modules already proven to have zero productive callers where safe.
