# Servicio 1 — R6 Implementation Evidence

## Scope

R6 closes the D4 → P8 → F7 relationship provenance and runtime-safety
contract. R7 and later nodes were not implemented.

## Preconditions and preservation

- Branch: `work/service1-cafeteria-flow-v1`
- HEAD: `8d5708e9becdddaa5aa24387b310972643d1ef86`
- R5 evidence preserved at `docs/current/evidence/SERVICE_1_R5_IMPLEMENTATION_EVIDENCE_V1.md`.
- Existing dirty worktree changes and `_audit/` were preserved. No reset,
  checkout, discard, commit, push, or deploy was performed.

## Implementation

- D4 relationship records now expose graph/schema/workbook/artifact identity,
  physical and logical endpoints, cardinality, fanout evidence, and the
  owner confirmation event reference without granting runtime or join authority.
- Owner relationship events now expose a deterministic, content-addressed
  `owner_confirmation_event_ref`, distinct from `relationship_ref` and
  `question_ref`, with optional D4/workbook provenance metadata.
- P8 now provides `Service1GovernedRelationshipBindingV1` and validates a
  D4 relationship through the D7 logical-model carrier before emitting a
  governed binding with an integrity digest.
- F7 now performs read-only D7→D4 dereference and validates graph/schema,
  endpoints, cardinality, resolved state, safe fanout, owner event identity,
  P8 governance, workbook/artifact identity, and binding integrity before any
  relationship materialization. Existing row-level cardinality and join
  conflict checks remain in F7.
- No second relationship registry, graph copy, parser, pipeline, math engine,
  semantic engine, or downstream authority was introduced.

## Exit gates

```text
D4_P8_F7_PROVENANCE = PASS
F7_ONLY_JOIN_MATERIALIZATION = PASS
F7_RUNTIME_CARDINALITY_SAFETY = PASS
```

## Verification

Command executed:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_logical_relationship_graph_d4_v1.py \
  tests/smartpyme/test_service_1_analysis_computability_f5_v1.py \
  tests/smartpyme/test_service_1_computability_v1.py \
  tests/smartpyme/test_service_1_analysis_evidence_preparation_f7_v1.py \
  tests/smartpyme/test_service_1_semantic_dimensions_relationships_f6_v1.py
```

Result: **60 passed / 0 failed**.

The focal set includes a valid D4→D7→P8→F7 chain and fail-closed coverage
for a missing D4 graph reference. No full suite, Playwright, smoke, Cloud Run,
Gemma, R7+, commit, push, or deploy was executed.

## Verdict

```text
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R7
BLOCKERS: NONE
```
