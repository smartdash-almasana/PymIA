# SERVICE 1 — Stage 2 Package 3 — P6 Approval Decision V1

## Status

`CLOSED_PASS`

## Purpose

Package 3 establishes one canonical authority for semantic approval after semantic hypothesis generation and optional owner-confirmation evidence.

Canonical authority:

`Service1P6ApprovalDecisionV1`

P6 decides meaning only. It does not select capabilities, pathologies or formulas; does not decide computability; and never authorizes runtime, tool execution, product readiness, delivery or diagnosis.

## Canonical outcomes

- `APPROVED`
- `NEEDS_OWNER_CONFIRMATION`
- `AMBIGUOUS`
- `BLOCKED`

Only `APPROVED` may carry `approved_role` / `approved_variable`.

## Inputs

P6 may consume:

- `Service1ColumnSemanticCandidateV1` as semantic hypothesis state;
- canonical `OwnerConfirmationEventV1` evidence when available.

Owner evidence does not itself grant approval. P6 validates that a confirmed role belongs to the candidate hypothesis before approving it. Free-text owner evidence remains `AMBIGUOUS` until governed normalization occurs.

## Productive integration

`service_1_semantic_bridge_to_controlled_execution_gate_v1` is retained temporarily as a compatibility module. It delegates semantic approval classification to `build_service_1_p6_approval_decisions_v1`.

The gate must no longer independently infer whether candidate semantics are approved, ambiguous or require owner confirmation.

The gate still contains two legacy responsibilities that are outside Package 3 closure and remain explicit convergence debt:

1. construction of owner-question surfaces;
2. P7-adjacent variable-family matching.

These responsibilities must not be interpreted as P6 authority.

## Reentry migration

`service_1_owner_confirmation_reinjection_to_semantic_gate_v1` remains a temporary compatibility projection. Package 2 owner events are forwarded into the repacked semantic bridge so P6 consumes canonical human evidence during recheck.

Candidate mutation performed by reinjection remains compatibility behavior until its consumers can consume P6 decisions directly.

## Invariants

- Owner confirmation is evidence only.
- P6 approval is a deterministic system decision.
- P6 cannot carry formula/pathology/capability authority.
- P6 cannot carry computation readiness or execution authority.
- A free-text owner meaning cannot silently become approved semantics.
- An owner-confirmed role outside the semantic hypothesis blocks fail-closed.
- Multiple owner events targeting the same column block fail-closed.
- Existing productive behavior must remain stable during migration.

## Convergence classification

- `service_1_p6_approval_decision_v1`: `DEEP_AUTHORITY`
- `service_1_semantic_bridge_to_controlled_execution_gate_v1`: `MIXED_RESPONSIBILITY` / compatibility surface pending P5/P7 extraction
- `service_1_owner_confirmation_reinjection_to_semantic_gate_v1`: `TEMPORARY_MIGRATION_ADAPTER`

## Migration discipline

`CREATE → MIGRATE → VERIFY → DELETE`

### REPLACES

Distributed P6-like semantic approval decisions previously inferred from candidate flags/state inside the controlled execution gate and reinjection flow.

### CONSUMERS_TO_MIGRATE

- controlled execution compatibility gate: migrated to canonical P6 classification;
- owner reentry: forwards canonical owner events to P6 through compatibility bridge;
- future P7 boundary must consume approved P6 meaning instead of reinterpreting candidate state.

### COMPATIBILITY_PROJECTION

Reinjected `Service1ColumnSemanticCandidateV1` objects remain temporarily required by current P7/family-binding consumers.

### DELETE_WHEN

`service_1_owner_confirmation_reinjection_to_semantic_gate_v1` may be deleted when productive P7 consumers accept canonical P6-approved meaning directly and no productive caller requires candidate mutation/rerun.

The controlled execution gate may be split/retired when owner-question construction and variable-family matching have migrated to their canonical adjacent authorities.

## Package 3 closure criteria

- P6 authority implemented and registered productive;
- gate delegates semantic approval to P6;
- canonical owner events reach P6 on reentry;
- P6 focal tests pass;
- gate/reentry neighbor tests pass;
- registry/architecture checks pass;
- architecture certifier reports `P6_APPROVAL_DECISION_AUTHORITY_PRESENT = PASS`;
- no changes to formula selection or computability logic.
