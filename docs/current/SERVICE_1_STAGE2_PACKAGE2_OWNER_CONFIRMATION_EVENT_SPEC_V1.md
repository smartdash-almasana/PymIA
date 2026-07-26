# SERVICE 1 — STAGE 2 PACKAGE 2 — OWNER CONFIRMATION EVENT V1

## Status

`IMPLEMENTED_PENDING_CLOSURE_VALIDATION`

## Objective

Establish one canonical immutable representation for owner-confirmation evidence without granting semantic approval or any execution authority.

## Canonical authority

`Service1OwnerConfirmationEventV1`

Module:

`pymia/smartpyme/service_1_owner_confirmation_event_v1.py`

## Meaning

An event records **what the owner answered** to a specific question about a specific column. It is evidence only.

It does not mean that the semantic binding is approved, that requirements are satisfied, that computation is safe, or that runtime/delivery is authorized.

## Required identity and traceability

The event carries:

- `case_id`
- `file_ref`
- `region_ref`
- `sheet_ref`
- `column_ref`
- `question_ref`
- `proposed_role`
- `proposed_variable`
- `owner_answer`
- `confirmed_role`
- `corrected_meaning`
- `confirmation_scope`
- `confirmed_by_owner=true`
- `timestamp`
- `provenance`

`region_ref` and `proposed_variable` may be unavailable in the current productive legacy path. They remain explicit nullable fields until Package 1 region evidence and the semantic proposal boundary are integrated into the productive path. They may not be invented.

## Confirmation scopes

- `SEMANTIC_ROLE`: the owner selected one governed semantic role.
- `COLUMN_EXCLUSION`: the owner explicitly excluded the column from the analysis.
- `FREE_TEXT_MEANING`: the owner supplied free text that still requires normalization and cannot be treated as semantic approval.

## Safety invariants

The event can never authorize:

- runtime
- tool execution
- product readiness
- delivery
- diagnosis
- computation readiness

Authorization-like fields are forbidden in provenance and emitted safety flags remain false.

## Migration

Current productive path before Package 2:

`owner_questions -> owner_answers -> confirmed_answers map -> candidate metadata -> reinjection`

Package 2 target transition:

`owner_questions -> owner answer -> OwnerConfirmationEventV1 -> P6 (future Package 3)`

Implemented migration step:

1. owner-confirmation loop emits `owner_confirmation_events`;
2. reinjection derives canonical semantic answers from those events;
3. `confirmed_answers` remains temporarily as a compatibility projection/checksum for existing callers and adversarial tests;
4. malformed or drifting compatibility projection still fails closed;
5. free-text events remain evidence and never become semantic truth.

## Deletion condition

`confirmed_answers` and `owner_confirmed` / `owner_confirmation_answer` candidate metadata cease to be architectural authorities when Package 3 P6 consumes `OwnerConfirmationEventV1` directly and all productive callers are migrated.

At that point the compatibility projection must be removed rather than retained as a second truth.

## Boundary with Package 3

Package 2 does not decide whether a meaning is approved.

Package 3 must consume semantic hypotheses plus owner-confirmation events and emit the single P6 semantic approval authority.

## Closure gate

Package 2 closes only if:

- event contract invariants pass;
- owner loop emits events for governed role selections and free-text responses;
- reinjection uses events as canonical evidence while compatibility projection is checked fail-closed;
- current productive behavior remains unchanged;
- module registry and architecture lock remain consistent;
- full suite passes;
- root remains `service_1_product_pipeline_v1`.
