# SERVICE_1 — C2 Deterministic Validation Gate F6 — Implementation Evidence V1

STATUS: IMPLEMENTED / VERIFIED
RESULT: PASS
DATE: 2026-09-02

## Scope
F6 hardens the deterministic semantic proposal validator. No LLM authority, mathematics, join execution, Product Root, XLSX ingestion or delivery authority was added.

## Changes
- Added strict V2 descriptor `field_ref` binding to exactly one target column.
- Added strict equality between descriptor-internal evidence and proposal `evidence_refs`.
- Added strict relationship-evidence binding so a relationship proposal must cite evidence belonging to the same structural relationship.
- Preserved existing fail-closed checks for real column refs, evidence registry membership, V2 taxonomy, logical table scope, structural relationship existence/type, and authority flags.
- Did not invent a mapping between structural `grain_ref` and V2 `grain`; they are distinct namespaces. Existing D5 scope/grain resolution remains the deterministic structural gate.

## Tests
Command:
`python -m pytest -q tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py tests/smartpyme/test_service_1_pydantic_ai_column_semantic_provider_v1.py tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py tests/smartpyme/test_service_1_semantic_coordinate_model_v2.py`

Result:
`29 passed / 0 failed`

## F6-specific regression coverage
- V2 descriptor bound to another real column => BLOCKED.
- V2 descriptor internal evidence differs from proposal evidence => BLOCKED.
- Relationship cites real but unrelated evidence => BLOCKED.
- Properly bound V2 descriptor => READY.

## Authority
All runtime/tool/product/delivery/diagnosis authority flags remain false.
