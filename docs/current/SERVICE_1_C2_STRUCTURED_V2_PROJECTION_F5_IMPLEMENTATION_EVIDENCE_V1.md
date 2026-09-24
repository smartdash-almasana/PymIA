# SERVICE_1 C2 — Structured V2 Projection F5 — Implementation Evidence V1

STATUS: IMPLEMENTED / VERIFIED
RESULT: PASS
TASK: SERVICE_1_C2_STRUCTURED_V2_PROJECTION_F5

## Objective
Require the productive post-F3 LLM semantic path to express understood business meaning only through the governed 12-axis V2 compositional semantic contract.

## Product behavior
When workbook_business_understanding from F3 is present:
- concept proposals require compositional_semantic V2;
- top-level semantic_role / variable_name are not promoted into productive concepts;
- role-only or otherwise unprojected semantic output becomes material ambiguity instead of a parallel semantic authority;
- V2 descriptors remain constrained by the governed taxonomy and deterministic validator.

Pre-F3 provider compatibility is intentionally preserved until F10, where retirement of the old semantic authority is planned. This avoids prematurely breaking historical isolated-provider contracts while ensuring the new productive path is V2-only.

## Governed axes
entity, object, process, measure, state, grain, scope, time, identity, relation, unit, aggregation.

## Files modified
- pymia/smartpyme/service_1_pydantic_ai_column_semantic_provider_v1.py
- tests/smartpyme/test_service_1_pydantic_ai_column_semantic_provider_v1.py

## Verification
Focused suite:
- provider semantic tests
- semantic proposal validator
- real workshop C2 V2 flow
- semantic coordinate V2 tests

Result: 25 passed / 0 failed.

## Safety / authority
No XLSX parser added.
No Product Root added.
No mathematical authority added.
No runtime/delivery authority added.
No owner confirmation bypass added.

STOP_AFTER: F5
