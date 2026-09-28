# SERVICE 1 — C2 Semantic Compression F7 — Implementation Evidence V1

STATUS: IMPLEMENTED / VERIFIED / PASS
AUTHORITY: EVIDENCE_ONLY

## Objective
Create an explicit deterministic semantic-compression artifact between validated V2 semantics and owner dialogue so coherent column meanings can be reviewed as business units without losing traceability.

## Implementation
Created:
- `pymia/smartpyme/service_1_semantic_compression_v1.py`

Modified:
- `pymia/smartpyme/service_1_assisted_semantic_product_wiring_v1.py`
- `tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py`

Tests created:
- `tests/smartpyme/test_service_1_semantic_compression_v1.py`

## Contract
Output schema:
`SERVICE_1_SEMANTIC_COMPRESSION_V1`

Authority:
`CONTEXT_ONLY`

A semantic unit preserves:
- proposal refs
- column refs
- evidence refs
- logical table refs
- grain refs
- relationship context refs
- shared V2 axes
- variable V2 axes

Material ambiguities, conflicts and irrelevant legacy decisions are never silently compressed into confident units.

## Causal example
Three labor concepts at the same table/grain/process/object:
- labor duration
- labor cost
- labor margin

compress into one traceable business unit while preserving each proposal and source column.

A separate work-order identifier remains a distinct unit.

## Productive wiring
After deterministic semantic validation:

validated V2 packet
→ semantic compression
→ validated packet enriched with `semantic_compression`
→ owner dialogue planner

The same compression step is rebuilt after a targeted owner semantic correction.

## Verification
Command:
`python -m pytest -q tests/smartpyme/test_service_1_semantic_compression_v1.py tests/smartpyme/test_service_1_owner_semantic_dialogue_v1.py tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py`

Result:
`28 passed / 0 failed`

Real taller flow asserts that the productive validated packet contains a ready `semantic_compression` packet, `authority=CONTEXT_ONLY`, no runtime authority, and complete unit traceability.

## Safety
- no LLM call in compressor
- no semantic mutation
- no owner confirmation
- no mathematics
- no join execution
- no second Product Root
- no second parser
- no runtime/delivery authority
