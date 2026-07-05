# OPERATOR_RESCUE_AND_DEATH_BOUNDARY_V1

## VERDICT

```text
STATUS: BOUNDARY_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
PURPOSE: separate rescued conversational functions from killed operator semantics
```

## SOURCE_CONTEXT

```text
Base audit:
docs/auditoria/OPERATOR_PARASITE_FULL_AUDIT_V1.txt

Current owner decision:
The project must rescue useful owner-facing conversational functions, but kill the operator figure as autonomous/intermediate authority.
```

## CORE DECISION

```text
The function is rescued.
The operator figure is killed.
```

More precisely:

```text
Owner-facing explanation may exist.
Owner evidence clarification may exist.
Delivery reading may exist.
Runtime authority may not exist.
Autonomous operator supervision may not exist.
Operator as sovereign intermediary may not exist.
```

## RESCUED FUNCTIONS

The following functions are valid only when renamed and constrained as owner-facing or delivery-facing layers:

```text
1. Read already-generated Service 1 outputs.
2. Explain generated outputs in owner-facing PyME language.
3. Render missing-evidence questions.
4. Summarize received evidence and missing evidence.
5. Present caveats and uncertainty explicitly.
6. Guide the next human question.
7. Prepare delivery package summaries.
8. Route to owner, accountant, or human responsible when evidence is insufficient.
```

Allowed names:

```text
OWNER_CONVERSATION_LAYER
OWNER_DELIVERY_READER
OWNER_EVIDENCE_CLARIFIER
OWNER_FACING_EXPLANATION_LAYER
DELIVERY_EXPLANATION_LAYER
```

## KILLED FUNCTIONS

The following functions are not allowed under any name unless a new explicit contract is created and owner-approved:

```text
1. Operator as autonomous actor.
2. Operator as supervisor.
3. Operator as release approver.
4. Operator as runtime executor.
5. Operator as tool selector with authority.
6. Operator as human-review substitute.
7. Operator as intermediary between owner and PymIA with decision power.
8. Operator harness as shadow runtime authority.
9. Human review gate as fake sovereign layer.
10. Assisted/autonomous ambiguity used to bypass gates.
```

## TERMS TO RETIRE OR MIGRATE

```text
operator -> owner-facing layer / delivery reader / evidence clarifier, depending on context
operator_packet -> delivery_packet or owner_delivery_packet, only if it is a passive artifact
operator_harness -> killed unless proven to be a non-runtime test fixture
operator_supervision -> killed
human_review -> owner_confirmation / evidence_gate / release_gate, depending on real function
reviewer -> explicit human role only, never runtime authority
assisted -> avoid; replace with controlled, owner-facing, or human-confirmed as applicable
```

## IMPLEMENTATION RULE

```text
Do not rename mechanically.
Classify each reference by function first.
Then apply one of four outcomes:
- RESCUE_RENAME
- KILL_DELETE
- QUARANTINE_DOC
- KEEP_EXCEPTION
```

## PRIORITY PLAN

### P0 — Critical live code

```text
Goal: remove or neutralize live code where operator/human_review acts as authority.
Action: audit file by file before delete.
No bulk removal.
```

### P1 — Core rename

```text
Goal: rename useful passive functions into owner-facing or delivery-facing names.
Action: preserve behavior only if tests prove it is passive, deterministic, and non-authoritative.
```

### P2 — Contract migration

```text
Goal: update live contracts so no operator semantic governs future implementation.
Action: replace terms with explicit owner/evidence/delivery/release concepts.
```

### P3 — Historical docs

```text
Goal: prevent obsolete operator docs from guiding development.
Action: delete when replacement is explicit; otherwise quarantine as non-governing until owner decision.
```

## NON_NEGOTIABLE RULES

```text
The owner talks to PymIA.
PymIA processes evidence.
Tools execute deterministic work.
Gates block unsafe transitions.
The conversation layer explains outputs.
No operator governs anything.
```

## FIRST SAFE NEXT STEP

```text
Create a P0 audit matrix for the five files listed under P0_CRITICAL in OPERATOR_PARASITE_FULL_AUDIT_V1.txt.
Do not delete them yet.
For each file decide: KILL_DELETE, RESCUE_RENAME, or KEEP_EXCEPTION.
```

## FINAL_STATUS

```text
OPERATOR_RESCUE_AND_DEATH_BOUNDARY_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: P0_OPERATOR_CRITICAL_FILE_MATRIX_AUDIT_ONLY
```
