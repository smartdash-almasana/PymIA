# SERVICE_1_C2_F12_POST_F10_INDEPENDENT_RECHECK_EVIDENCE_V1

STATUS: EVIDENCE
AUTHORITY: NON_NORMATIVE
TASK: SERVICE_1_C2_F12_POST_F10_INDEPENDENT_RECHECK
VERDICT: PASS

## Independent verifier result

- PRODUCT_ROOT_UNIQUE: PASS
- CANONICAL_XLSX_INGESTION_UNIQUE: PASS
- SECOND_XLSX_PARSE: NO
- LEGACY_BUILDER_PRODUCTIVE_REFERENCES: 0
- LEGACY_BUILDER_CALLS_PER_PROVIDER_INVOCATION: 0
- SECOND_SEMANTIC_ENGINE_PRODUCTIVE: NO
- RELATIONSHIPS_FROM_STRUCTURAL_EVIDENCE: PASS
- RELATIONSHIP_V2_ENDPOINT_GATING: PASS
- F5_V2_ONLY_PRODUCTIVE_SEMANTICS: PASS
- F6_DETERMINISTIC_VALIDATION: PASS
- F7_SEMANTIC_COMPRESSION: PASS
- F8_OWNER_DIALOGUE: PASS
- F9_TENANT_LEARNING: PASS
- F10_LEGACY_AUTHORITY_RETIRED: PASS
- F11_GOLDEN_BUSINESS_CORPUS: PASS
- VERTICAL_HARDCODES_PRODUCTIVE: NO
- AUTOMATIC_OWNER_CONFIRMATION: NO
- TENANT_ISOLATION: PASS
- FAIL_CLOSED: PASS
- TESTS: 94 passed / 0 failed
- FILES_MODIFIED_BY_VERIFIER: NONE
- MATERIAL_BLOCKERS: NONE

## Key evidence reported by verifier

- `service_1_pydantic_ai_column_semantic_provider_v1.py:550-606`: structural relationship projection requires registered evidence, both V2 endpoints, matching identity/entity, and profile relationship data.
- Runtime monkeypatch against the legacy builder: `LEGACY_CALLS_PRODUCTIVE_CONTEXT 0`.
- Adversarial relationship probes: valid=1; missing evidence, missing V2 endpoint, identity mismatch, entity mismatch, nonexistent relation = 0.
- D5 probe: `BLOCKED_LOGICAL_TABLE_SCOPE_UNRESOLVED`.
- F11 evaluator: 7 cases, 26 V2 coordinate columns, 4 safe-unknown columns, runtime flags false.

## Conclusion

The prior F10 blocker is physically absent from the productive provider and is not invoked at runtime. Relationships are projected only from structural evidence plus compatible V2 endpoint semantics. F5-F9 and F11 remain intact. C2 F0-F11 is technically convergent according to the independent F12 recheck.

## Governance note

This file records evidence only. It does not update NOP-2, KNOWN STATE, or close NOP3-S1-003. Those normative actions require the Notion source of truth and explicit absorption/closure under the active governance regime.
