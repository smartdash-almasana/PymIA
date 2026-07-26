# PymIA Architecture Convergence Skill

## Purpose

Use this skill to reduce structural complexity in PymIA without weakening epistemic authority, provenance, deterministic safety, or the single productive architecture.

This skill is for architecture convergence, not greenfield redesign.

Primary objective:

```text
reduce complexity
without collapsing distinct kinds of truth
without creating parallel productive routes
without weakening fail-closed behavior
without layering new abstractions over replaced ones
```

## Core doctrine

PymIA must preserve the distinction between:

```text
what the source data physically contains
what the system hypothesizes it means
what the owner explicitly says
what PymIA deterministically approves
what a capability requires
what is computable safely
what is actually executed
```

Never optimize away these distinctions merely to reduce module count.

The target is not fewer concepts. The target is fewer shallow or duplicated software structures per concept.

## Mandatory architectural invariants

### Product root

Servicio 1 has exactly one productive composition root:

```text
service_1_product_pipeline_v1
```

No new product root, side route, alternative pipeline, runtime bypass, or capability-specific product flow may be introduced.

### Runtime

Runtime remains deterministic.

Do not introduce LLM authority for semantic approval, computability, formula selection, execution authorization, diagnosis authorization, or delivery authorization.

### Epistemic separation

Treat these as different authorities unless the repository proves a newer canonical decision:

```text
PhysicalEvidence
SemanticHypothesis
OwnerConfirmationEvent
P6ApprovalDecision
RequirementMatch
ComputabilityDecision
GovernedComputationInput
ExecutionResult
```

Do not merge two concepts merely because they travel together.

### Owner confirmation

Owner confirmation is evidence. It is never equivalent to runtime, product, tool, computation, or delivery permission.

### P6

P6 decides meaning only.

Canonical outcomes:

```text
APPROVED
NEEDS_OWNER_CONFIRMATION
AMBIGUOUS
BLOCKED
```

P6 must not select formulas, pathologies, capabilities, or execution.

### P7

P7 matches approved meaning to requirements. It must not re-approve semantics and must not execute.

### P8

P8 decides computability and safety. Only P8 may produce governed computation input for execution.

### Execution

Execution accepts governed computation input only. It must not consume raw semantic candidates, raw owner-answer maps, ambiguous evidence, or unapproved bindings.

### Provenance

Every governed assertion must remain traceable through the relevant chain, for example:

```text
result
→ governed computation input
→ approved semantic binding
→ owner/physical evidence
→ region/sheet/column/rows
→ source file
```

Reject a refactor that breaks traceability even if it reduces code.

## Target topology

Prefer three implementation domains:

```text
UNDERSTANDING
COMPUTABILITY
EXECUTION
```

UNDERSTANDING may contain Region, PhysicalEvidence, SemanticHypothesis, OwnerConfirmationEvent, and P6ApprovalDecision.

COMPUTABILITY may contain Grain, RequirementMatch, ComputabilityDecision, and GovernedComputationInput.

EXECUTION may contain Capability, Formula, Evaluator, Outcome, and Delivery.

Do not create another architectural domain unless concrete evidence proves none of these can own the responsibility cleanly.

## P0–P10 rule

P0–P10 is a decision/order model, not a mandate for 11 modules, 11 engines, 11 packets, or 11 subsystems.

Preserve conceptual boundaries while physically compressing implementation wherever doing so does not merge distinct authorities.

## Deep-module principles

### Deep module

Prefer modules that hide meaningful complexity behind a small, stable interface.

A small module is not automatically a good module.

### Interface as test surface

A healthy module should be testable primarily through its public interface. Repeated private-internal testing is evidence that the seam may be wrong.

### Locality

Keep behavior close to the authority that owns it. Do not distribute one decision across several gates, adapters, metadata fields, and re-entry maps.

### Leverage

Prefer extraction when a module centralizes important invariants reused by several consumers. Do not extract merely to move code elsewhere.

### Real seams only

Do not retain an adapter permanently when both sides are internal representations of the same concept and one can replace the other.

## PymIA authority test

Before merging, deleting, or absorbing a module, answer:

```text
Do these components represent the same type of truth?
```

Examples:

```text
PhysicalEvidence != SemanticHypothesis
SemanticHypothesis != OwnerConfirmationEvent
OwnerConfirmationEvent != P6ApprovalDecision
P6ApprovalDecision != RequirementMatch
RequirementMatch != ComputabilityDecision
```

If the answer is no, preserve the conceptual authority boundary.

A tiny module may still be architecturally deep if it owns an important truth boundary.

## Truth ownership test

For every concept identify:

```text
CONCEPT
CANONICAL_AUTHORITY
PRODUCERS
CONSUMERS
DUPLICATE_REPRESENTATIONS
DERIVED_PROJECTIONS
```

Rule:

```text
ONE CONCEPT → ONE CANONICAL AUTHORITY
```

Derived projections are allowed only if they are non-authoritative, traceable to the canonical authority, and explicitly deletable after consumer migration.

A projection must never silently become a second source of truth.

## Authorization separation test

Reject designs that contaminate responsibilities.

Strong smell examples:

```text
OwnerConfirmationEvent -> runtime_authorized
SemanticHypothesis -> computation_ready
P6ApprovalDecision -> formula_id
RequirementMatch -> execution_authorized
```

## Event / Decision / Projection separation

Use an event-sourcing discipline selectively for facts and derived state. Do not convert the whole system to event sourcing.

Three categories must remain distinct:

```text
EVENT      = immutable fact that happened
DECISION   = deterministic conclusion produced from governed evidence/events
PROJECTION = derived compatibility/read model reconstructed from canonical facts or decisions
```

Examples:

```text
OwnerConfirmationEvent      = EVENT
P6ApprovalDecision          = DECISION
confirmed_answers           = PROJECTION
candidate metadata flags    = PROJECTION when derived from canonical authority
```

Rules:

- Events are historical facts and must never be rewritten to reflect a later decision.
- Decisions must reference the evidence/events they consumed through provenance.
- Projections must be derivable from canonical authority and must never become an independent source of truth.
- A projection may be cached for compatibility/performance, but mismatch with canonical authority must fail closed.
- New behavior must not depend on mutating an event to represent a later decision.
- Do not infer that an EVENT grants authorization. Authorization is a separate deterministic decision.

Before introducing a mutable packet/metadata flag, ask:

```text
Is this a fact, a decision, or merely a projection?
```

If it is a projection, declare its canonical source and deletion condition.

## Provenance test

For every proposed simplification ask:

```text
Can PymIA still explain where this assertion came from?
```

If no, reject the refactor.

## Deletion test — PymIA version

For each candidate module evaluate three questions.

### A. Complexity displacement

If deleted, does meaningful complexity reappear across several callers?

If yes, the module may be deep.

### B. Pass-through detection

Does the module mainly transform:

```text
A → A' → A''
```

without owning invariants, policy, authority, or reusable complexity?

If yes, classify it as a shallow pass-through candidate.

### C. Truth-boundary preservation

Would deleting it erase a distinct epistemic boundary?

If yes, do not delete the authority merely because its implementation is small.

## Mandatory module classification

Every reviewed module receives exactly one primary classification:

```text
DEEP_AUTHORITY
DEEP_OPERATIONAL_MODULE
LEGITIMATE_ADAPTER
TEMPORARY_MIGRATION_ADAPTER
SHALLOW_PASS_THROUGH
DUPLICATED_AUTHORITY
MIXED_RESPONSIBILITY
LEGACY_PARALLEL_PATH
```

### DEEP_AUTHORITY
Owns a canonical concept/truth boundary and its invariants.

### DEEP_OPERATIONAL_MODULE
Hides meaningful operational complexity behind a narrow interface without being a truth authority.

### LEGITIMATE_ADAPTER
Bridges genuinely distinct external/internal shapes or independent stable producers/consumers.

### TEMPORARY_MIGRATION_ADAPTER
Exists only during convergence and has an explicit deletion condition.

### SHALLOW_PASS_THROUGH
Forwards or renames data without owning invariants or a legitimate seam.

### DUPLICATED_AUTHORITY
Represents a concept already owned elsewhere and can independently influence behavior.

### MIXED_RESPONSIBILITY
Combines decisions belonging to different authorities or P0–P10 boundaries.

### LEGACY_PARALLEL_PATH
Implements an alternate productive route around canonical authorities or the canonical root.

## No new architecture for a capability

A new pathology/capability should add primarily:

```text
requirements
formula/rule
thresholds
bindings/configuration
evaluator
outcome
```

It should not require a new semantic pipeline, owner-confirmation loop, P6 gate, computability pipeline, product root, or execution architecture.

If a capability requires new topology, treat it as an architecture smell and prove necessity before accepting it.

## Migration discipline

Use:

```text
CREATE
→ MIGRATE
→ VERIFY
→ DELETE
```

Never accept indefinite layering.

Treat canonical representations and contracts as append-only migration surfaces once consumed productively. Do not silently redefine an old representation in place when callers already depend on its semantics.

Preferred migration pattern:

```text
ADD new authority/field/contract
→ MIGRATE producers
→ MIGRATE consumers
→ DUAL-READ only if strictly necessary and temporary
→ VERIFY equivalence/invariants
→ DEPRECATE legacy representation
→ DELETE legacy path
```

Rules:

- Never mutate historical event semantics to fit a new model version.
- Prefer additive schema evolution over destructive reinterpretation.
- Compatibility projections must declare which canonical authority generates them.
- Dual-read/dual-write phases require an explicit convergence check and termination condition.
- Migration code must be idempotent where repeated execution is possible.
- A consumer must not choose arbitrarily between old and new authorities; canonical precedence must be explicit.
- Once all productive consumers have migrated and equivalence is verified, keeping the old authority is a defect, not caution.

Every temporary authority/adapter/projection must declare:

```text
REPLACES
CANONICAL_SOURCE
CONSUMERS_TO_MIGRATE
COMPATIBILITY_PROJECTION
MIGRATION_INVARIANT
DELETE_WHEN
```

If `DELETE_WHEN` cannot be stated concretely, the adapter is not accepted as temporary.

Prefer converging each authority before stacking another package.

## Current convergence sequence

Unless the repository proves a newer canonical decision, prefer:

```text
Region + PhysicalEvidence
→ SemanticHypothesis
→ OwnerConfirmationEvent
→ P6ApprovalDecision
→ RequirementMatch
→ ComputabilityDecision
→ GovernedComputationInput
→ DeterministicExecution
```

## Bounded experimentation

Do not explore indefinitely.

Maximum architecture alternatives for one unresolved decision:

```text
3
```

Score, select, and proceed.

Do not redesign simply because another elegant decomposition exists.

After a baseline passes acceptance, freeze it unless real evidence demonstrates it cannot solve a required case.

## Architecture scoring

Score substantive proposals out of 100:

```text
Epistemic correctness       25
Authority uniqueness        20
Provenance preservation     15
Module depth                10
Responsibility locality     10
Deterministic safety        10
Deletion/convergence         5
Extensibility                5
```

Decision bands:

```text
<80     REJECT
80–89   REVIEW
90–94   ACCEPT
95–100  STRONG_ACCEPT
```

Automatic rejection:

```text
Epistemic correctness < 25
Deterministic safety < 10
```

Do not let fewer modules or maintainability compensate for broken truth semantics or runtime safety.

## Property-based adversarial verification

Use property-based testing for invariants that must hold across many malformed, contradictory, boundary, or combinatorial inputs. Prefer this over manually enumerating dozens of similar examples.

Use Hypothesis-style property tests by default for domain invariants. Use coverage-guided fuzzing such as Atheris only for parser/decoder or crash-resistance surfaces where byte-level exploration is materially useful.

Core PymIA properties should include, where applicable:

```text
UNAPPROVED_SEMANTICS_NEVER_REACH_COMPUTATION
OWNER_EVENT_NEVER_GRANTS_RUNTIME_AUTHORITY
P6_NEVER_SELECTS_FORMULA_OR_CAPABILITY
PROJECTION_MISMATCH_FAILS_CLOSED
CONTRADICTORY_OWNER_EVENTS_NEVER_APPROVE
MALFORMED_PROVENANCE_NEVER_PRODUCES_GOVERNED_OUTPUT
P8_IS_REQUIRED_BEFORE_GOVERNED_COMPUTATION_INPUT
EXECUTION_REJECTS_UNGOVERNED_INPUT
IRRELEVANT_UNKNOWN_COLUMN_DOES_NOT_BLOCK_UNRELATED_CAPABILITY
SAME_CANONICAL_INPUT_PRODUCES_SAME_DETERMINISTIC_DECISION
```

Generate adversarial combinations of:

```text
missing/empty fields
unknown roles
multiple candidate roles
contradictory events
out-of-scope events
mismatched projections
forbidden authorization flags
invalid statuses
invalid provenance references
duplicate identifiers
unexpected ordering
boundary numeric/date values
```

Property tests must assert architecture invariants, not merely absence of exceptions.

When a property-based test finds a counterexample:

```text
preserve minimal failing example as regression test
fix canonical authority or invariant
rerun property test
```

Do not use fuzzing as a substitute for representative business cases or explicit contract tests.

## Architecture acceptance cases

Prefer three representative product cases.

### Case A — clean
Well-structured evidence. Little or no owner clarification; valid governed computation reached.

### Case B — ambiguous
Usable evidence with ambiguous semantics. Ask only materially necessary questions; continue after governed confirmation.

### Case C — incomplete or contradictory
Identify what can and cannot be computed, fail closed where necessary, and avoid blocking unrelated computations.

Then add a second pathology/capability through the same architecture.

Passing these cases is stronger evidence than endless synthetic architecture experimentation.

## Automated certification

Architecture opinions are insufficient. Encode important conclusions as automated checks whenever practical.

Representative checks:

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_PARALLEL_PRODUCT_PATHS
NO_DUPLICATED_AUTHORITIES
OWNER_CONFIRMATION_EVENT_AUTHORITY_PRESENT
NO_SEMANTIC_REBIND_AFTER_P6
P7_P8_BOUNDARIES_NOT_FUSED
NO_PERMANENT_COMPATIBILITY_PROJECTIONS
TEMPORARY_ADAPTERS_HAVE_DELETE_CONDITION
EVENT_DECISION_PROJECTION_SEPARATION
CANONICAL_PRECEDENCE_EXPLICIT_DURING_MIGRATION
PROPERTY_BASED_FAIL_CLOSED_INVARIANTS
CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION
PROVENANCE_CHAIN_PRESERVED
```

Prefer extending the existing architecture certifier rather than creating another certification framework.

## Workflow

### 1. Establish baseline

Read current authoritative architecture sources before proposing changes.

At minimum inspect, when present/relevant:

```text
AGENTS.md
ARCHITECTURE_GUARDRAILS.md
docs/current/README.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/service_1_module_disposition.v1.json
docs/service_1_architecture_lock.v1.json
tools/service_1_architecture_baseline_v1.py
```

Do not let historical docs override current canonical docs.

### 2. Verify repository state

Before edits inspect:

```text
git status
git diff
HEAD
```

If the worktree contains concurrent unrelated work, do not clean, revert, reformat, absorb, or silently fix it.

Restrict edits to authorized scope.

### 3. Map authorities

Build an authority table for the target area.

Identify canonical authority, producers, consumers, duplicate representations, mixed responsibilities, and productive callers.

### 4. Classify modules

Use the mandatory classification vocabulary. Do not recommend deletion without checking productive callers.

### 5. Apply deletion and authority tests

For each candidate change answer:

```text
what complexity disappears?
what complexity moves?
what truth boundary is preserved?
what authority becomes unique?
what projection becomes deletable?
```

### 6. Design no more than three alternatives

Only when a real architecture decision remains unresolved. Score each with the PymIA scoring model.

### 7. Select minimal convergent change

Prefer deepening or replacing an existing module over adding a new one.

Before proposing a new module, explicitly prove why no existing authority can absorb the responsibility without violating epistemic separation or becoming mixed-responsibility.

### 8. Implement convergence

Use:

```text
CREATE → MIGRATE → VERIFY → DELETE
```

Do not stop at CREATE if two active authorities remain.

### 9. Test interfaces and neighbors

Run focal tests for the changed authority and neighboring productive consumers. When possible run the canonical governed suite.

For truth/safety boundaries, add property-based invariants when a finite example set would leave combinatorial gaps. Preserve any discovered minimal counterexample as a normal regression test.

Do not attribute concurrent/legacy failures to the change without evidence.

### 10. Verify migration convergence

If old and new representations coexist, verify canonical precedence, projection equivalence, productive callers, and the declared `DELETE_WHEN` condition. Do not close with unexplained dual authority.

### 11. Update certification

If the change resolves a recurring architecture risk, add or update an automated certifier check.

### 12. Close only with evidence

A package/step can be closed only if:

```text
canonical authority exists
actual producer uses it
actual consumers use it
replaced authority is removed or explicitly temporary
productive route remains singular
focal/neighbor tests pass
certifier does not regress
```

## Do not do

Do not:

- create another product root
- create permanent adapters between equivalent internal representations
- use owner confirmation as runtime permission
- allow semantic candidates directly into computation
- re-bind semantic meaning after P6
- move P7/P8 logic into P6 for convenience
- add capability-specific mini-pipelines
- preserve legacy modules merely because tests exist
- delete modules solely to reduce module count
- merge distinct truth authorities solely for interface simplicity
- use an LLM as runtime semantic authority
- broaden scope to frontend, OCR/PDF, or unrelated services during architecture convergence unless explicitly authorized
- clean up concurrent changes outside scope

## Expected output format

Return architecture audits/decisions in this compact structure:

```text
VERDICT:

CONCEPTUAL_MODEL_STATUS:

MODULE_MATRIX:
- module:
  classification:
  authority:
  problem:
  target:
  delete_condition:

AUTHORITY_DUPLICATIONS:

EVENT_DECISION_PROJECTION_MAP:

MIXED_RESPONSIBILITIES:

TEMPORARY_ADAPTERS:

MIGRATION_STATE:

PROPERTY_INVARIANTS:

PROVENANCE_BREAKS:

PRODUCTIVE_PARALLEL_PATHS:

TARGET_ARCHITECTURE:

MIGRATION_SEQUENCE:

AUTOMATED_CHECKS:

SCORE:

DO_NOT_CHANGE:

NEXT_ACTION:
```

Keep results evidence-driven. Do not produce a large speculative redesign when one convergent edit is sufficient.

## Final rule

Before adding any new module, answer:

```text
Why can no existing canonical authority be deepened to own this responsibility without violating epistemic separation or becoming mixed-responsibility?
```

If this cannot be demonstrated, do not create the module.
