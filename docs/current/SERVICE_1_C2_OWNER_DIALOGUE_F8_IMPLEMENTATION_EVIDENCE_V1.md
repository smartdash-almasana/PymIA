# SERVICE 1 — C2 Owner Dialogue F8 — Implementation Evidence V1

STATUS: IMPLEMENTED / VERIFIED / PASS
AUTHORITY: EVIDENCE
DATE: 2026-09-02

## Objective
Consume deterministic F7 semantic units in the owner dialogue so the owner reviews business units rather than column-by-column semantics, while preserving exact proposal/column traceability and decomposing only on rejection/correction or material ambiguity.

## Implementation
Modified:
- `pymia/smartpyme/service_1_owner_semantic_dialogue_v1.py`
- `pymia/smartpyme/service_1_assisted_semantic_product_wiring_v1.py`

Tests modified:
- `tests/smartpyme/test_service_1_owner_semantic_dialogue_v1.py`
- `tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py`

## Product behavior
When a ready F7 `SERVICE_1_SEMANTIC_COMPRESSION_V1` packet is present, workbook-first owner dialogue consumes its `semantic_units` directly.

A compressed semantic unit becomes one owner review decision when it contains multiple validated proposals. The decision retains:
- every `proposal_ref`;
- every `column_ref`;
- atomic children for deterministic decomposition.

Rejecting a group decomposes only that semantic unit. Targeted correction remains a proposal and does not create owner confirmation by itself.

Material ambiguities remain outside silent compression and continue to be surfaced explicitly.

Legacy callers that do not supply semantic compression keep the previous planner behavior. Atomic-confirmation flows remain atomic.

## Authority safety
Semantic compression remains `CONTEXT_ONLY`.
Owner dialogue does not grant runtime, delivery, mathematical, semantic-reuse or owner-confirmation authority.

## Verification
Executed:
`python -m pytest -q tests/smartpyme/test_service_1_owner_semantic_dialogue_v1.py tests/smartpyme/test_service_1_semantic_compression_v1.py tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py`

Result:
`29 passed / 0 failed`

The real workshop flow asserts that productive owner questions include `dialogue:semantic-unit:*` decisions with non-empty proposal and column traceability.

## Verdict
F8 PASS.
