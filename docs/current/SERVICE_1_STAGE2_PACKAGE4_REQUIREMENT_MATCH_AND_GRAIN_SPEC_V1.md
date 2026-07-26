# Servicio 1 Stage 2 — Package 4: RequirementMatch + Grain V1

## Objective

Establish one canonical P7 requirement-matching authority after P6 semantic approval, without creating a new module or a parallel productive path.

Canonical sequence:

```text
P6ApprovalDecision
→ RequirementMatch + Grain
→ P8 Computability
```

P7 answers only whether approved semantics satisfy the requirements of a governed business family/capability. It does not decide semantic meaning, computability, formula execution, runtime authorization, product readiness, delivery, or diagnosis.

## Canonical authority

The existing module `service_1_variable_family_bindings_v1` is deepened instead of adding another architecture layer.

Canonical P7 values:

- `Service1GrainV1`
- `Service1RequirementMatchV1`

Canonical builder:

- `build_service_1_requirement_matches_v1(...)`

The input is exclusively `Service1P6ApprovalDecisionV1` decisions with status `APPROVED`.

Any non-approved P6 decision is rejected before P7 matching.

## P7 statuses

```text
REQUIREMENT_MATCHED
MISSING_REQUIREMENTS
REQUIREMENTS_NOT_OBSERVED
BLOCKED
```

These states describe requirement matching only. They do not authorize computation.

## Grain

`Service1GrainV1` preserves an explicit grain contract with four dimensions:

```text
structural_scope
business_entity_grain
temporal_grain
aggregation_grain
```

Package 4 does not infer business or temporal grain that is not yet governed. The current requirement-family projection operates at REGION structural scope with unknown business/temporal grain represented explicitly as `NONE`, and atomic aggregation.

P8 may later reject or refine compatibility when formula/capability grain requirements are evaluated.

## Legacy projection

`Service1VariableFamilyBindingV1` remains temporarily for compatibility with current downstream consumers.

It is no longer the canonical P7 authority in the migrated gate path.

Projection function:

- `project_service_1_requirement_matches_to_variable_family_bindings_v1(...)`

Projection metadata must declare:

```text
compatibility_projection = true
canonical_source = Service1RequirementMatchV1
```

### Migration declaration

```text
REPLACES:
  candidate-driven P7 family matching inside the controlled-execution gate

CANONICAL_SOURCE:
  Service1RequirementMatchV1

CONSUMERS_TO_MIGRATE:
  deterministic semantic pipeline / computation planning consumers that still read Service1VariableFamilyBindingV1

COMPATIBILITY_PROJECTION:
  Service1VariableFamilyBindingV1

MIGRATION_INVARIANT:
  projected family readiness must remain behaviorally equivalent for already-P6-approved semantics

DELETE_WHEN:
  no productive consumer requires Service1VariableFamilyBindingV1 as authoritative input and P8 consumes RequirementMatch directly
```

## Gate convergence

`service_1_semantic_bridge_to_controlled_execution_gate_v1` must:

1. run/consume canonical P6 decisions;
2. stop if any active column is not P6-approved;
3. invoke canonical RequirementMatch only after P6 approval;
4. expose legacy variable-family bindings only as a projection;
5. remain non-authorizing.

The gate must not call `build_service_1_variable_family_bindings_v1(...)` on semantic candidates in the migrated path.

## Non-goals

Package 4 does not:

- separate P8 yet;
- select formulas or pathologies;
- decide computability;
- execute calculations;
- change the product root;
- add a capability-specific pipeline;
- delete the legacy variable-family public API yet.

## Architectural effect

Module count must remain unchanged from Package 3.

The intended convergence is:

```text
P6 APPROVED
→ RequirementMatchV1
→ legacy VariableFamilyBinding projection (temporary)
→ current downstream consumers
```

not:

```text
P6
→ old family authority
+ new requirement authority
```

## Acceptance

Package 4 passes when:

- `Service1GrainV1` exists as a validated value object;
- `Service1RequirementMatchV1` is the canonical P7 representation;
- P7 consumes only APPROVED P6 decisions;
- requirement matching is deterministic;
- P7 contains no formula/computability/execution authority;
- gate uses RequirementMatch after P6;
- legacy family binding is marked compatibility projection;
- existing gate behavior is preserved;
- product root remains `service_1_product_pipeline_v1`;
- certifier recognizes P7 authority and continues exposing unrelated later blockers.
