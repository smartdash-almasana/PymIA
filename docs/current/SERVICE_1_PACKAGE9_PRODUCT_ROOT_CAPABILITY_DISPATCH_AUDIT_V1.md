# Service 1 — Package 9 Product Root Capability Dispatch Audit V1

## Status

`PASS_AUDIT_WITH_IMPLEMENTABLE_CONVERGENCE_PLAN`

## Objective

Audit `service_1_product_pipeline_v1` after Packages 7–8 to determine why capability extension still requires product-root edits and distinguish legitimate specialization from duplicated dispatch.

## Canonical invariant

A new generic capability described by the governed capability registry must not require a new branch in the canonical product root.

Target:

```text
P6 -> P7 -> P8 -> GovernedComputationInput
                    |
                    v
            product execution dispatch
              |                 |
       specialized only     generic registry
       when justified          kernel
```

The product root remains the single composition root. The registry describes generic capability behavior; the generic kernel executes that behavior.

## Evidence read

- `pymia/smartpyme/service_1_product_pipeline_v1.py`
- `pymia/smartpyme/service_1_generic_capability_engine_v1.py`
- `pymia/smartpyme/service_1_capability_registry_v1.py`
- Product-root and capability tests, including delivery guards.

## Current root structure

The root contains capability-specific dispatch branches for:

1. `payment_collection_gap` / PYME_013
2. `sold_vs_collected_gap` / LIQ_001
3. `net_margin_real` / REN_001
4. `projected_closing_cash_balance` / LIQ_002
5. `dso` / PYME_011
6. `dpo`
7. `reorder_point` / INV_001
8. `inventory_turnover` / INV_002
9. `current_ratio` / PYME_024
10. `sales_concentration` / PYME_033
11. `index_update_ratio` / REN_002
12. `interest_burden_ratio` / PYME_027
13. `adjusted_operating_cash_flow` / PYME_026

Most generic branches repeat the same structure:

```text
execute_generic_capability_v1
-> require EVALUATED
-> require OUTCOME_READY
-> reject deliver_result
-> return common packet
```

The repetition differs mainly in pathology-specific error strings.

## Registry coverage

The governed registry already contains these generic definitions:

- LIQ_002
- INV_001
- INV_002
- DPO
- PYME_011
- PYME_013 (COMPOSITE)
- PYME_024
- PYME_033
- PYME_027
- PYME_026
- REN_002

Their formulas, variable contracts, classifications, outcome policies, limitations and forbidden claims are registry-owned and executed by `service_1_generic_capability_engine_v1`.

Therefore root-level branches for these capabilities duplicate registry/kernel authority.

## Classification of current branches

### A. Legitimate specialized execution — retain explicitly for now

#### LIQ_001

Reason:

- specialized normalized-evidence evaluator;
- specialized outcome builder;
- specialized XLSX delivery path;
- delivery semantics differ from generic capabilities.

Verdict: `LEGITIMATE_SPECIALIZED_HANDLER`.

#### REN_001

Reason:

- specialized normalized-evidence evaluator;
- specialized bounded outcome builder;
- delivery explicitly forbidden.

Verdict: `LEGITIMATE_SPECIALIZED_HANDLER` for current Stage 2. It may be independently audited later for promotion to registry/kernel, but Package 9 must not force that migration.

### B. Generic atomic branches — eliminate from root

- LIQ_002
- PYME_011
- DPO
- INV_001
- INV_002
- PYME_024
- PYME_033
- REN_002
- PYME_027
- PYME_026

Verdict: `DUPLICATED_DISPATCH`.

They are fully registry-described and generic-kernel-executable. Their root branches contain no legitimate capability-specific execution algorithm.

### C. PYME_013 composite branch — split the concerns

PYME_013 is legitimately `COMPOSITE`, but the root should not know its identity.

Current root special-cases PYME_013 twice:

1. to build `_build_pyme_013_composite_plan_v1`;
2. to execute the generic kernel with `governed_results` instead of row evidence.

The registry already declares `PYME_013.kind == "COMPOSITE"` and each variable declares its governed source capability/result contract.

Verdict:

- identity-specific branch: `DUPLICATED_DISPATCH`;
- composite preparation semantics: `LEGITIMATE_GENERIC_KIND_BEHAVIOR`.

The converged root should branch on governed capability kind, not on `PYME_013_CAPABILITY_REF`.

## Root/registry duplication

The root defines capability constants for generic registry capabilities independently from the registry and does not call `get_capability_definition_v1()` for dispatch.

This creates two extension surfaces:

```text
registry addition
+
product-root constant/branch addition
```

That directly violates:

`CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION`.

## Target dispatch model

Package 9 should converge to this shape:

```text
requested_capability
    |
    +--> specialized handler registry/map?
    |      LIQ_001
    |      REN_001
    |
    +--> governed generic capability definition
           |
           +--> ATOMIC
           |      build P8 governed input
           |      require normalized row evidence
           |      generic kernel
           |
           +--> COMPOSITE
                  build composite P8 governed input from definition
                  require governed_results
                  generic kernel
```

Important: a dispatch map for legitimate specialized handlers is acceptable because it contains specialization policy, not one branch per generic capability. It must remain small and explicit.

## Recommended implementation boundary

### 1. Resolve specialization first

Use one explicit specialization lookup for capabilities whose execution truly differs from the generic contract.

Current allowed set:

```text
LIQ_001
REN_001
```

Do not encode the other generic capabilities in the product root.

### 2. Registry-driven generic fallback

For every non-specialized capability:

```text
definition = get_capability_definition_v1(requested_capability)
```

If absent: fail closed as unsupported.

If present: dispatch generically based on `definition.kind`.

### 3. Remove identity-specific PYME_013 logic

Generalize composite governed-input construction so it consumes a registry capability definition or capability ref whose `kind == COMPOSITE`.

The product root must not contain `if requested_capability == PYME_013_CAPABILITY_REF`.

### 4. Common generic result handling

All generic capabilities can share one result policy:

```text
require engine status EVALUATED
require outcome.status OUTCOME_READY
if deliver_result: fail closed
return common computation packet
```

If callers require pathology-specific delivery block identifiers, derive them from the governed definition's `pathology_code`; do not create a branch solely to emit a string.

### 5. No hidden auto-delivery

Generic fallback must keep delivery closed unless a separately governed delivery policy explicitly exists.

Package 9 is dispatch convergence, not delivery generalization.

## Test impact identified

Several tests assert pathology-specific delivery identifiers such as:

- `LIQ_002_DELIVERY_NOT_AUTHORIZED`
- `PYME_011_DELIVERY_NOT_AUTHORIZED`
- `DPO_DELIVERY_NOT_AUTHORIZED`
- `INV_001_DELIVERY_NOT_AUTHORIZED`
- `INV_002_DELIVERY_NOT_AUTHORIZED`
- `PYME_024_DELIVERY_NOT_AUTHORIZED`
- `PYME_033_DELIVERY_NOT_AUTHORIZED`
- `REN_002_DELIVERY_NOT_AUTHORIZED`
- `PYME_027_DELIVERY_NOT_AUTHORIZED`
- `PYME_026_DELIVERY_NOT_AUTHORIZED`
- `PYME_013_DELIVERY_NOT_AUTHORIZED`

These do not require separate root branches. They can be deterministically derived from `definition.pathology_code`.

A Cycle 053 test also appears to inspect source text for literal delivery strings. That is an architectural anti-pattern for this convergence and should be updated to test behavior/registry coverage instead of branch literals.

## Proposed Package 9 invariants

```text
ONE_CANONICAL_PRODUCT_ROOT
GENERIC_CAPABILITY_EXTENSION_REQUIRES_REGISTRY_ONLY
NO_IDENTITY_BRANCH_FOR_GENERIC_CAPABILITY
COMPOSITE_DISPATCH_USES_CAPABILITY_KIND_NOT_CAPABILITY_ID
SPECIALIZED_HANDLER_SET_IS_EXPLICIT_AND_BOUNDED
P8_IS_REQUIRED_BEFORE_EXECUTION
EXECUTION_REJECTS_UNGOVERNED_INPUT
GENERIC_DELIVERY_REMAINS_FAIL_CLOSED
```

## Certifier target

`CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION` should PASS when:

- no root branch names generic registry capability IDs;
- adding a synthetic governed atomic capability to registry/kernel test fixtures can execute without editing product-root dispatch;
- composite selection depends on `kind`, not PYME_013 identity;
- only justified specialized handlers remain explicit.

## Deletion candidates after Package 9

Once generic dispatch is proven:

- generic capability constants duplicated in `service_1_product_pipeline_v1`;
- `_build_pyme_013_composite_plan_v1` if replaced by generic composite P8 construction;
- repeated generic execution/outcome/delivery branch blocks;
- tests that assert branch/source literals rather than behavior.

Do not delete LIQ_001/REN_001 specialized execution in Package 9.

## Verdict

`PACKAGE9_IMPLEMENTATION_READY`

There is sufficient technical certainty to implement dispatch convergence without another architecture audit.

The correct implementation is not a new dispatcher architecture. It is a simplification of the canonical root using authorities that already exist: capability registry, P8 governed computation input, and generic capability kernel.
