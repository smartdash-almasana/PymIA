# SERVICE 1 — C2 Semantic Knowledge F2 — Implementation Evidence V1

STATUS: IMPLEMENTED_PENDING_INDEPENDENT_VERIFICATION
TASK: SERVICE_1_C2_SEMANTIC_KNOWLEDGE_F2

## Scope implemented

- Added `pymia/smartpyme/service_1_semantic_knowledge_context_v1.py`.
- Explicit source: `docs/catalogo/SERVICE_1_BUSINESS_COLUMN_CATALOG_V1.md`.
- Source classification: `LEXICAL_REFERENCE_ONLY`.
- Knowledge authority: `CONTEXT_ONLY`.
- Deterministic bounded retrieval from workbook semantic context.
- Provenance preserved with `source_ref`.
- Added `semantic_knowledge_context` to `Service1LLMSemanticContextV1` and `to_provider_payload()`.
- Productive assisted semantic wiring now builds workbook semantic context, retrieves knowledge, then calls the provider.
- No XLSX reparse, no math authority, no owner auto-confirmation, no runtime/delivery authority.

## Tests

Command:

`python -m pytest -q tests/smartpyme/test_service_1_semantic_knowledge_context_v1.py tests/smartpyme/test_service_1_workbook_semantic_context_v1.py tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py`

Result: `15 passed / 0 failed`.

## Required independent gate

F2 is not closed until an independent read-only verifier confirms:
- one context-only knowledge contract;
- provenance preserved;
- retrieval is bounded/scoped;
- provider payload receives knowledge;
- workshop and non-workshop generality;
- no vertical runtime hardcodes;
- no second semantic engine;
- no authority escalation.
