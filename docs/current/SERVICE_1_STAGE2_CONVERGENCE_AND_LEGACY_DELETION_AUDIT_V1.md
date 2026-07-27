# Servicio 1 — Stage 2 Convergence and Legacy Deletion Audit V1

**Status:** `PASS_AUDIT_WITH_ACTIONABLE_CONVERGENCE_GAPS`  
**Date:** 2026-07-26  
**Scope:** post-Package-7 convergence only. No deletion or runtime refactor is authorized by this document alone.

## 1. Canonical execution state

The canonical epistemic/execution sequence is now:

```text
P6 semantic approval
→ P7 RequirementMatch + Grain
→ P8 ComputabilityDecision
→ Service1GovernedComputationInputV1
→ deterministic execution
```

Package 7 removed `SERVICE_1_COMPUTATION_PLAN_V1` as an execution authority. The remaining computation-plan object is compatibility/output transport only.

## 2. Audit verdict

```text
STAGE2_CORE_DIRECTION: ALIGNED
OWNER_QUESTION_BOUNDARY: NOT_CONVERGED
ROOT_CAPABILITY_DISPATCH: NOT_CONVERGED
LEGACY_PROJECTIONS: MIGRATION_REQUIRED
SPECIALIZED_PARALLEL_EXECUTION: REMOVED_FROM_PRODUCTIVE_ROOT
DELETION_CANDIDATES: PRESENT
```

The two baseline blockers are real in the current source; they are not merely concurrent-worktree noise:

1. `OWNER_CONFIRMATION_NOT_OWNED_BY_CONTROLLED_EXECUTION_GATE`
2. `CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION`

## 3. Real blocker — owner-question ownership

`service_1_semantic_bridge_to_controlled_execution_gate_v1.py` still calls its private `_owner_questions(...)` builder when canonical P6 returns `NEEDS_OWNER_CONFIRMATION` or `AMBIGUOUS`.

This violates the intended boundary:

```text
P6 decides semantic state.
Owner-question composition belongs outside the controlled-execution gate.
The gate must not own dialogue construction.
```

The gate may expose unresolved P6 decisions and references needed by the dialogue layer, but must not construct owner-facing questions itself.

### Required convergence

```text
P6 unresolved decisions
→ owner-question adapter / owner-confirmation loop
→ OwnerConfirmationEventV1
→ P6 re-evaluation
```

No new question authority should be created if the existing owner-question adapter/loop can own this responsibility.

## 4. Real blocker — product-root branch proliferation

Current `service_1_product_pipeline_v1.py` contains 14 `requested_capability == ...` branches.

The generic kernel and capability registry already provide the extensible execution abstraction for most capabilities. Therefore the root still encodes capability-specific orchestration that should be registry/kernel driven.

Target invariant:

```text
Adding a new pathology/capability must not require a new product-root branch.
```

A small number of genuinely different delivery/execution classes may remain only if their responsibility cannot be represented through existing canonical contracts without mixing concerns.

## 5. Legacy projection — `confirmed_answers`

`confirmed_answers` remains active in:

- `service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1.py`
- `service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py`

The reinjection module explicitly treats the map as a compatibility projection/checksum while `OwnerConfirmationEventV1` is canonical evidence.

Current behavior is fail-closed on event/projection mismatch.

### Classification

`TEMPORARY_COMPATIBILITY_PROJECTION`

### Delete when

- all consumers read canonical owner-confirmation events directly;
- no productive module requires the map as input;
- projection-mismatch tests are replaced by event-integrity/provenance tests.

Do not delete before those consumers migrate.

## 6. Legacy projection — candidate reinjection

`service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py` still reconstructs/re-packs semantic candidates after owner answers and then re-enters the controlled-execution gate.

This is transitional because canonical P6 can already consume `OwnerConfirmationEventV1` as evidence. Rewriting candidate state after owner confirmation is not the desired final architecture.

### Classification

`TEMPORARY_MIGRATION_ADAPTER`

### Delete/absorb when

```text
original semantic hypotheses
+ OwnerConfirmationEventV1
→ P6 decision directly
```

and the deterministic semantic pipeline no longer requires rewritten candidate state.

## 7. Legacy projection — `variable_family_bindings`

P7 authority is now `Service1RequirementMatchV1` + `Service1GrainV1`, but the controlled-execution gate still projects `variable_family_bindings`, and deterministic/reinjection packets continue carrying it.

No evidence in this audit shows that `variable_family_bindings` is still needed as a productive decision authority.

### Classification

`COMPATIBILITY_PROJECTION_PENDING_CALLER_MIGRATION`

### Delete when

- every productive consumer reads `requirement_matches` directly;
- packet schemas/tests no longer require `variable_family_bindings` or `ready_variable_family_ids`;
- the compatibility builder in `service_1_variable_family_bindings_v1.py` has zero productive callers.

## 8. Legacy projection — ComputationPlanV1

`SERVICE_1_COMPUTATION_PLAN_V1` is no longer execution authority after Package 7, but remains as compatibility/output transport around P8-governed state.

### Classification

`LEGACY_READ_MODEL / OUTPUT_PROJECTION`

### Not yet deletable

Do not delete until:

- product/public packet consumers no longer require it;
- tests and CLI contract are migrated to an explicit P8 execution/read model;
- no external compatibility commitment depends on its schema.

It must never regain execution authority.

## 9. Specialized LIQ_002 / PYME_011 modules

The following specialized modules were removed from the PRODUCTIVE root closure in Package 7 and are now `SUPPORT_NECESSARY`:

```text
service_1_liq_002_evaluator_v1
service_1_liq_002_normalized_evidence_v1
service_1_liq_002_outcome_v1
service_1_pyme_011_evaluator_v1
service_1_pyme_011_normalized_evidence_v1
service_1_pyme_011_outcome_v1
```

Package-7 caller audit reported zero PRODUCTIVE callers.

### Classification

`DELETION_CANDIDATE_AFTER_FULL_CALLER_AND_TEST_AUDIT`

They should not return to PRODUCTIVE. A deletion package may remove them only after checking non-product code/tests/docs and proving the generic kernel provides the required behavior.

## 10. Non-candidates

Do not delete or merge merely to reduce file count:

- `Service1OwnerConfirmationEventV1` — canonical EVENT authority.
- `Service1P6ApprovalDecisionV1` — canonical semantic DECISION.
- `Service1RequirementMatchV1` / `Service1GrainV1` — canonical P7 authority.
- `Service1ComputabilityDecisionV1` — canonical P8 DECISION.
- `Service1GovernedComputationInputV1` — canonical governed execution value object.
- capability registry/contracts — productive generic execution foundation.

These represent distinct truth types and responsibilities.

## 11. Recommended convergence sequence

Do not perform all cleanup in one package.

### Package 8 — Owner-question boundary convergence

```text
P6 unresolved decision
→ question composition outside controlled-execution gate
→ OwnerConfirmationEvent
→ P6 re-evaluation
```

Exit condition:

`OWNER_CONFIRMATION_NOT_OWNED_BY_CONTROLLED_EXECUTION_GATE = PASS`

### Package 9 — Root dispatch convergence

Replace per-capability branches with registry/kernel-driven dispatch wherever behavior is equivalent.

Exit condition:

`CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION = PASS`

Strong test:

```text
A new generic capability requires registry/config changes and tests,
not a new branch in service_1_product_pipeline_v1.py.
```

### Package 10 — Legacy projection/deletion cleanup

After Packages 8–9:

1. remove `confirmed_answers` projection if zero productive consumers;
2. delete/absorb owner-confirmation reinjection adapter if direct event→P6 re-evaluation is complete;
3. remove `variable_family_bindings` projection after consumer migration;
4. audit/delete specialized LIQ_002/PYME_011 support modules;
5. evaluate final removal/replacement of `ComputationPlanV1` read model.

## 12. Stage 2 closure condition

Stage 2 should not be declared architecturally converged until all are true:

```text
ONE_CANONICAL_PRODUCT_ROOT
OWNER_QUESTIONS_OUTSIDE_CONTROLLED_EXECUTION_GATE
NO_ROOT_BRANCH_PROLIFERATION_FOR_GENERIC_CAPABILITIES
OWNER_CONFIRMATION_EVENT_IS_CANONICAL_EVIDENCE
NO_CANDIDATE_REWRITE_REQUIRED_AFTER_OWNER_CONFIRMATION
P7_REQUIREMENT_MATCH_IS_CANONICAL
P8_GOVERNS_ALL_EXECUTION
NO_LEGACY_PROJECTION_HAS_DECISION_AUTHORITY
TEMPORARY_ADAPTERS_HAVE_ZERO_PRODUCTIVE_CALLERS_OR_A_DELETE_CONDITION
```

## 13. Next action

```text
STAGE2_PACKAGE8_OWNER_QUESTION_BOUNDARY_CONVERGENCE
```
