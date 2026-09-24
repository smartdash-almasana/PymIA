# SERVICE 1 — C2 Workbook Business Understanding — F3 Evidence V1

STATUS: IMPLEMENTED / VERIFIED
RESULT: PASS
DATE: 2026-09-02

## Objective
Insert a context-only whole-workbook business-understanding pass before individual column interpretation.

## Productive sequence
canonical ingestion -> workbook profile -> workbook semantic context -> semantic knowledge context -> whole-workbook business understanding -> column semantic provider -> deterministic semantic proposal validation -> owner dialogue.

## Safety
- no XLSX reparse;
- no calculations;
- no owner auto-confirmation;
- no runtime/tool/product/delivery authority;
- business understanding authority is CONTEXT_ONLY;
- invented sheet references fail closed before the column pass;
- deterministic fallback remains callable and does not gain a second semantic engine.

## Files
Created:
- pymia/smartpyme/service_1_workbook_business_understanding_v1.py
- tests/smartpyme/test_service_1_workbook_business_understanding_v1.py

Modified:
- pymia/smartpyme/service_1_pydantic_ai_column_semantic_provider_v1.py
- pymia/smartpyme/service_1_llm_semantic_interpreter_v1.py

## Verification
Focused causal suite: 12 passed / 0 failed.

Verified:
- workbook pass runs before column pass;
- structured hypothesis is injected into the column prompt;
- workbook and semantic-knowledge contexts are actually present in provider reasoning context;
- invalid/invented sheet reference blocks before column interpretation;
- F1/F2/provider/taller regression tests remain green.
