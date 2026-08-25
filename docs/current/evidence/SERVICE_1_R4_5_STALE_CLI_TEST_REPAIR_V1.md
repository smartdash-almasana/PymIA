# SERVICE_1_R4_5_STALE_CLI_TEST_REPAIR_V1

REPAIR_SCOPE: R4_5_STALE_CLI_TEST_ONLY
HEAD: 8d5708e9becdddaa5aa24387b310972643d1ef86
BRANCH: work/service1-cafeteria-flow-v1
PRECONDITION_MATCHED: YES

FILES_CHANGED:
- tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
- docs/current/evidence/SERVICE_1_R4_5_STALE_CLI_TEST_REPAIR_V1.md

RUNTIME_CHANGED: NO
OTHER_TESTS_CHANGED: NO
LEGACY_TOOL_REQUESTS_REINTRODUCED: NO
TEST_INTENT_PRESERVED: YES
EXPLICIT_R4_REQUEST_CAPTURED: YES
SAME_CANONICAL_ENVELOPE_OBJECT_PROVEN: YES
NORMALIZED_TABLES_SENTINEL_PRESERVED: YES

REPAIR_DETAIL:
- Removed the stale `tool_requests=[]` argument from the CLI test invocation.
- Replaced legacy kwargs capture with capture of the explicit `WorkbookSemanticStartRequestV1` positional request and separated `Service1ProductExecutionDependenciesV1` dependencies.
- Preserved the original invariant: the exact sentinel canonical `ingestion_output` object reaches Product Root without CLI copy/reinjection/mutation, and its `normalized_tables` sentinel remains unchanged.
- Runtime was not modified.

TESTS_RUN:
- python -m pytest -q tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py::test_cli_does_not_mutate_canonical_envelope_after_build
- python -m pytest -q tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py
- focal test rerun after formatting-only blank-line adjustment

TEST_RESULTS:
- focal: 1 passed / 0 failed
- full focal file: 22 passed / 0 failed
- post-format focal: 1 passed / 0 failed
- targeted diff inspected through repository diff; no new trailing-whitespace defect observed in the changed block. Connector command allowlist did not permit direct `git diff --check` invocation from this worktree path, so no claim beyond inspected targeted diff is made.

REPAIR_VERDICT: PASS
NEXT_ALLOWED_ACTION: R4_5_INTEGRATION_CHECKPOINT_RETRY
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
