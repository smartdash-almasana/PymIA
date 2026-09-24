# SERVICE 1 — C2 F10 Legacy Retirement — Implementation Evidence V1

STATUS: IMPLEMENTED / VERIFIED / PASS
TASK: SERVICE_1_C2_LEGACY_RETIREMENT_F10

## Scope
F10 retires productive semantic authority from the old C2 path without deleting historical contracts or downstream compatibility data still needed for migration and reentry.

## Productive changes
- `service_1_pydantic_ai_column_semantic_provider_v1.py`
  - Productive contexts containing F1 workbook semantic context or F3 workbook business understanding are V2-only.
  - Legacy `semantic_role` / `variable_name` output is not promoted to a concept; lack of V2 becomes explicit material ambiguity.
  - `semantic_provider_from_environment_v1()` no longer falls back to the deterministic semantic proposal provider when `PYMIA_SEMANTIC_LLM_MODEL` is absent. It returns a fail-closed provider that raises at semantic execution.
  - Direct-provider compatibility remains only when neither F1 nor F3 context is supplied; this surface is not connected to the Product Root.
- `service_1_assisted_web_v1.py`
  - Removed both automatic defaults to `build_service_1_deterministic_semantic_proposal_v1`.
  - Default semantic provider now resolves through `semantic_provider_from_environment_v1()`.

## Explicitly retained as non-authoritative compatibility/evidence
- deterministic column hypotheses;
- historical semantic roles/contracts;
- deterministic semantic provider as explicit test/helper surface;
- legacy owner-dialogue compatibility for packets that do not contain F7 compression.

These retained surfaces are not automatic productive semantic authority.

## Verification
Focused F10/C2 gate:
`59 passed / 0 failed`

Additional assisted-web transition gate:
`2 passed / 0 failed`

Search evidence:
- `service_1_assisted_web_v1.py`: 0 occurrences of `build_service_1_deterministic_semantic_proposal_v1`.
- smartpyme productive source: 0 occurrences of `or build_service_1_deterministic_semantic_proposal_v1`.

A broader legacy web vertical-slice test run reported 2 failures on stale static UI expectations (`Leer mi Excel`, `owner_answers`). These assertions are outside F10 semantics and were not modified.

## Safety
- No second Product Root.
- No second XLSX parser.
- No second semantic engine.
- No mathematics, joins, findings or delivery authority changed.
- No Git/commit/push/deploy.
- Fail-closed preserved.
