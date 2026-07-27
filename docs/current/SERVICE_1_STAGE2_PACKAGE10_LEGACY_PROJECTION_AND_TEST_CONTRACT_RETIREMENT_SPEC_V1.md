# SERVICE_1_STAGE2_PACKAGE10_LEGACY_PROJECTION_AND_TEST_CONTRACT_RETIREMENT_SPEC_V1

## Status

CLOSED_PASS

## Goal

Retire the remaining legacy `ComputationPlanV1` execution contract from productive Service 1 execution and migrate historical generic-kernel test fixtures to the canonical P8 authority without restoring any legacy fallback.

Package 10 does **not** claim deletion of every historical projection or SUPPORT module. It closes legacy **execution authority** and the stale test contract that still depended on it.

## Canonical result

The productive execution boundary is now:

```text
P6 Approval
→ P7 RequirementMatch
→ P8 ComputabilityDecision
→ Service1GovernedComputationInputV1
→ specialized evaluator or GenericCapabilityEngine
→ deterministic outcome
```

`SERVICE_1_COMPUTATION_PLAN_V1` is not accepted as productive execution authority.

## Generic kernel

`service_1_generic_capability_engine_v1.py` now resolves execution input only from explicit `governed_computation_input`.

Removed:

- `legacy_computation_plan` fallback resolution;
- nested governed-input extraction from a legacy plan container;
- any `SERVICE_1_COMPUTATION_PLAN_V1` reference in the generic engine.

The historical `computation_plan` function argument remains in the public signature only as a compatibility parameter for callers during convergence. It is ignored by execution authority and cannot authorize computation.

## Product root

`service_1_product_pipeline_v1.py` builds P8 authority directly through:

```text
build_computability_decision_from_confirmed_bindings_v1(...)
```

The root consumes `computability_decision.governed_computation_input` and no longer builds or consumes `ComputationPlanV1` for productive execution.

## Test-contract migration

The remaining historical generic-engine suites were migrated from legacy computation-plan authority to governed P8 fixtures:

- DPO
- PYME_026 adjusted operating cash flow
- PYME_027 interest burden
- PYME_033 sales concentration
- REN_002 index update

The shared P8 test support now converts historical fixture shapes into explicit governed-input test payloads only for fixture migration. It does not alter productive runtime behavior.

Generic-kernel and shadow-equivalence tests were also updated so legacy top-level plan state no longer controls the generic kernel.

## Legacy references still retained

Source search after convergence finds `SERVICE_1_COMPUTATION_PLAN_V1` only in:

- `service_1_deterministic_semantic_pipeline_v1.py` — compatibility/read projection;
- `service_1_liq_002_evaluator_v1.py` — historical SUPPORT cluster;
- `service_1_pyme_011_evaluator_v1.py` — historical SUPPORT cluster.

These references are explicitly outside productive execution authority.

The specialized LIQ_002 and PYME_011 clusters remain `SUPPORT_NECESSARY`, not `PRODUCTIVE`, and the canonical product root uses the governed generic kernel for those capabilities.

## Architecture invariants certified

- one canonical product root;
- P6 meaning authority precedes P7 requirement matching;
- P7 and P8 remain separate boundaries;
- P8 is required before productive computation;
- GenericCapabilityEngine has no legacy computation-plan fallback;
- product root executes P8 governed input directly;
- legacy plan references are bounded to projection/SUPPORT locations;
- LIQ_002/PYME_011 specialized historical paths are outside productive closure;
- no semantic rebinding after P6;
- owner confirmation remains evidence, not execution permission;
- generic capabilities do not proliferate product-root branches;
- safety/runtime/product/delivery/diagnosis flags remain fail-closed.

## Validation

Package migration suites:

```text
67 passed
```

Generic-kernel + migrated legacy-contract regression:

```text
90 passed
```

Broad Stage 2 execution regression:

```text
192 passed
```

Architecture baseline certifier behavior suite:

```text
70 passed
```

Architecture baseline verdict:

```text
PASS_ARCHITECTURE_BASELINE_V1
blockers: []
productive modules: 27
support necessary modules: 27
canonical product roots: 1
```

The certifier includes explicit checks for:

- `GENERIC_KERNEL_HAS_NO_LEGACY_PLAN_FALLBACK`;
- `PRODUCT_ROOT_EXECUTES_P8_DIRECTLY`;
- `LEGACY_PLAN_REFERENCES_BOUNDED_TO_PROJECTION_OR_SUPPORT`;
- `LEGACY_COMPUTATION_PLAN_NOT_EXECUTION_AUTHORITY`;
- `NO_PRODUCTIVE_SPECIALIZED_LIQ002_PYME011_PARALLEL_PATH`.

## Remaining debt / next architectural decision

Package 10 does not delete the compatibility/read projection in the deterministic semantic pipeline and does not delete the two historical SUPPORT specialized clusters.

Their future deletion must be based on caller/disposition evidence, not performed merely to reduce file count.

A separate Stage 2 closure certification should decide whether those retained compatibility artifacts are acceptable for Stage 2 closure or require a final deletion package.

## Verdict

```text
PASS_STAGE2_PACKAGE10_LEGACY_EXECUTION_AUTHORITY_AND_TEST_CONTRACT_RETIREMENT
```
