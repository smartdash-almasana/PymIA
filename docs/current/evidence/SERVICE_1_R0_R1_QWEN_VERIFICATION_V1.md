# SERVICE_1_R0_R1_QWEN_VERIFICATION_V1

VERIFIER: QWEN
MODE: READ_ONLY_CODE_AND_TESTS
HEAD: 8d5708e9becdddaa5aa24387b310972643d1ef86
BRANCH: work/service1-cafeteria-flow-v1

R0_VERDICT: PASS
R1_VERDICT: PASS

CONTENT_ADDRESSED_SOURCE_ARTIFACT: PASS
LOCAL_PATH_CONTENT_HASH: PASS
NO_FILENAME_AS_STRUCTURAL_IDENTITY: PASS
WORKBOOK_IDENTITY_FROM_ARTIFACT_SCOPE: PASS
SHEET_REF_EXPLICIT: PASS
NO_NEW_SHEET1_FALLBACK: PASS
CANONICAL_INGESTION_SELF_CONTAINED: PASS
NO_POST_BUILD_CANONICAL_MUTATION: PASS
SECOND_XLSX_READER_ADDED: NO
NEW_COMPATIBILITY_SHIM: NO
NEW_ALIAS: NO
OUT_OF_SCOPE_R2_PLUS_CHANGE: NO

PHYSICAL_EVIDENCE:
- R0 baseline was captured directly: branch and HEAD above; git status showed a pre-existing dirty worktree and no reset/checkout was performed.
- `service_1_web_column_confirmation_intake_boundary_v1.py` hashes local files through `calculate_sha256` over binary bytes and uploaded content through SHA-256 bytes; workbook identity combines artifact ref, ingestion scope, and canonical reader schema; sheet identity combines workbook ref and exact sheet name; case_id is opaque workflow identity.
- The intake boundary calls only `service_1_xlsx_to_normalized_table_v1.py` for XLSX reading. The R1 diff adds no alternate reader/parser.
- `service_1_owner_confirmation_to_canonical_ingestion_output_v1.py` constructs the self-contained V2 envelope with identity-only `workbook_context`, explicit sheet refs, physical lineage, provenance, and fail-closed context requirements.
- `pymia/cli/service_1_product.py` now forwards the constructed canonical envelope directly; the previous post-build normalized-table reinjection is removed. The focal mutation guard observes object identity and sentinel preservation.
- `service_1_workbook_logical_model_v1.py` requires explicit workbook context and blocks filename fallback; no R1 diff adds a sheet1 fallback.
- Existing R1 tests physically cover same basename/different bytes, same bytes/renamed filename, local-vs-uploaded byte identity, scope-sensitive workbook refs, explicit sheet refs, missing-sheet fail-closed behavior, canonical envelope immutability, and D7 filename fallback rejection.
- Pre-existing dirty R2+/Phase 3 files and legacy sheet1/alias paths were observed in git status/diff and were preserved; they are not attributed to this verifier or introduced by the audited R1 delta. Their retirement is explicitly later-plan scope.

TESTS_RUN:
- `python -m pytest -q tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py`
- `python -m pytest -q tests/smartpyme/test_service_1_architecture_lock_v1.py tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py`

TEST_RESULTS:
55 passed in 12.87s; 13 passed in 1.39s; 0 failed.

FINDINGS:
- R0/R1 gates are physically proven by the bounded focal/guard runs above.
- The worktree remains dirty with changes outside R1, including normative/current documents, Phase 1/2/3 modules/tests, `_audit/`, and the untracked request-kind module/test. These changes were pre-existing context and were not modified or staged by the verifier.
- Legacy `sheet1` defaults and transitional canonical aliases remain in pre-existing paths; R1 neither adds nor authorizes them as identity. R5/R10 retirement gates remain future scope.

BLOCKERS:
- NONE for R0/R1. The pre-existing out-of-scope worktree findings are preserved as downstream handoff context, not repaired here.

FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R2

FILES_CHANGED_BY_VERIFIER:
- docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
NORMATIVE_DOCS_CHANGED: NO
COMMIT: NO
PUSH: NO
DEPLOY: NO
