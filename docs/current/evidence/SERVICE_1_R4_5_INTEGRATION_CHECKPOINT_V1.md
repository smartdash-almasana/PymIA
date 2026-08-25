# SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1

EXECUTOR: CODEX
MODE: READ_ONLY_INTEGRATION_CHECKPOINT
HEAD: 8d5708e9becdddaa5aa24387b310972643d1ef86
BRANCH: work/service1-cafeteria-flow-v1

R4_VERIFICATION_PRECONDITION: PASS

COMBINED_TEST_COMMAND:
```bash
python -m pytest -q \
  tests/smartpyme/test_service_1_web_column_confirmation_intake_boundary_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py \
  tests/smartpyme/test_service_1_workbook_schema_identity_d3_v1.py \
  tests/smartpyme/test_service_1_table_scoped_semantics_d5_v1.py \
  tests/smartpyme/test_service_1_workbook_logical_model_d7_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_p6_approval_decision_v1.py \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_architecture_lock_v1.py
```

TEST_RESULT: `134 passed, 1 failed, 0 errors in 56.40s`

FIRST_FAILURE:

- `tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py::test_cli_does_not_mutate_canonical_envelope_after_build`
- Failure: `TypeError: run_service_1_product_entrypoint_v1() got an unexpected keyword argument 'tool_requests'`.
- Physical cause: the current R4 CLI entrypoint has the explicit request/dependencies contract and no longer accepts the removed `tool_requests` argument, while this test still invokes the retired keyword.
- This checkpoint stopped at the first integration regression. No test or runtime repair was attempted.

R1_CONTENT_IDENTITY_STILL_ACTIVE: DEFERRED_AFTER_FIRST_FAILURE
CANONICAL_ENVELOPE_POST_BUILD_MUTATIONS: DEFERRED_AFTER_FIRST_FAILURE
TABLE_SCOPE_PRODUCTIVE_BUILDERS: DEFERRED_AFTER_FIRST_FAILURE
SEM_TARGET_FSMS: DEFERRED_AFTER_FIRST_FAILURE
DETERMINISTIC_PROVIDER_PARITY_GATE_PRESERVED: DEFERRED_AFTER_FIRST_FAILURE
PRODUCTIVE_EXECUTION_ROOTS: DEFERRED_AFTER_FIRST_FAILURE
EXPLICIT_EXECUTION_COMMANDS: DEFERRED_AFTER_FIRST_FAILURE
PRODUCTIVE_TOOL_REQUESTS_EXECUTION_PATHS: DEFERRED_AFTER_FIRST_FAILURE
PRODUCTIVE_DIRECT_GOVERNED_ANALYSIS_CALLERS_OUTSIDE_ROOT: DEFERRED_AFTER_FIRST_FAILURE
NEW_COMPATIBILITY_SHIMS_SINCE_R0: DEFERRED_AFTER_FIRST_FAILURE
NEW_SHEET1_FALLBACKS_SINCE_R0: DEFERRED_AFTER_FIRST_FAILURE

FINDINGS:
- R0–R4 combined integration is not proven because one modified focal test remains on the retired CLI `tool_requests` contract.
- The R4 verification precondition itself is PASS and all required checkpoint test files exist physically.
- The worktree was preserved; `_audit/` remains untracked and no files are staged.

BLOCKERS:
- `FAIL_INTEGRATION_CHECKPOINT`: update/align the stale test contract in a separately authorized implementation session before rerunning this checkpoint. No repair was made here.

FINAL_VERDICT: FAIL_INTEGRATION_CHECKPOINT
NEXT_ALLOWED_NODE: NONE

RUNTIME_CHANGED: NO
TESTS_CHANGED: NO
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
