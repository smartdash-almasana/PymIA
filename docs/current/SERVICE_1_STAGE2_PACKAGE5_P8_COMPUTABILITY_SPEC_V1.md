# Service 1 Stage 2 Package 5 — P8 Computability V1

## Objective

Establish P8 as the unique authority that decides whether an already-approved semantic interpretation and P7 requirement match are safely computable.

Canonical flow:

```text
P6ApprovalDecision APPROVED
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ GovernedComputationInput
→ deterministic execution
```

## Authorities

### Service1ComputabilityDecisionV1

Decides only one of:
- COMPUTABLE
- NEEDS_EVIDENCE
- UNSUPPORTED_CAPABILITY
- BLOCKED

It does not execute computation and grants no runtime/product/delivery authority.

### Service1GovernedComputationInputV1

P8 output value object. Contains the governed formula identity, required variables/evidence, exact source bindings, grain, catalog versions and provenance required by deterministic execution.

## Inputs

P8 consumes only:
- P6 decisions with status APPROVED
- canonical P7 RequirementMatch objects
- governed formula/pathology/evidence-matrix catalogs

P8 must not consume raw semantic candidates as semantic authority and must not run semantic binding/inference again.

## Semantic rebinding prohibition

`build_computation_plan()` is now a compatibility projection over P8. It must not call `build_service_1_semantic_evidence_binding_result_v1()`.

Legacy `semantic_binding_result` output, while still required by callers, is a compatibility projection derived from P6-approved variable-to-column bindings. It is not an authority.

## Safety invariants

- P6 approval is mandatory before P8.
- P7 requirement matching is mandatory before P8.
- Missing required variables fail closed.
- Catalog/matrix drift fails closed.
- Unknown capability is not inferred.
- GovernedComputationInput must cover exactly the formula required variables.
- No runtime/tool/product/delivery/diagnosis authorization is emitted.

## Migration state

REPLACES: combined P7/P8 logic and semantic rebinding inside `build_computation_plan()`.

CANONICAL_SOURCE: `Service1ComputabilityDecisionV1` and `Service1GovernedComputationInputV1`.

COMPATIBILITY_PROJECTION: legacy computation-plan packet and semantic-binding-result field.

DELETE_WHEN: productive execution consumers accept GovernedComputationInput directly and no caller requires the legacy computation-plan projection.
