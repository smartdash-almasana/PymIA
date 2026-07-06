# P0B_OPERATOR_HARNESS_V2_RENAME_TASKSPEC_V1

## VERDICT

```text
STATUS: TASKSPEC_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
TARGET_BATCH: P0-B
SOURCE_AUDIT: docs/auditoria/P0B_OPERATOR_HARNESS_V2_FUNCTION_AUDIT_ONLY_V1.md
```

## OBJECTIVE

Rename the contaminated Service 1 `operator_harness_v2` contract into an owner/release action gate while preserving behavior and tests.

```text
The function is rescued.
The operator identity is killed.
```

## TARGET RENAME

Preferred runtime rename:

```text
PymIA-Live/pymia/smartpyme/service_1_operator_harness_v2_contract.py
->
PymIA-Live/pymia/smartpyme/service_1_owner_release_action_gate_v1.py
```

Preferred test rename:

```text
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_v2_contract.py
->
PymIA-Live/tests/smartpyme/test_service_1_owner_release_action_gate_v1.py
```

## SYMBOL MIGRATION

```text
Service1OperatorHarnessV2Contract
-> Service1OwnerReleaseActionGateV1

build_service_1_operator_harness_v2_contract
-> build_service_1_owner_release_action_gate_v1

operator_input
-> release_input

operator_requested_action
-> requested_release_action

allowed_operator_actions
-> allowed_release_actions

blocked_operator_actions
-> blocked_release_actions

ALLOWED_OPERATOR_ACTIONS
-> ALLOWED_RELEASE_ACTIONS

NON_DELIVERY_ACTIONS
-> NON_DELIVERY_RELEASE_ACTIONS

fix_operator_input
-> fix_release_input

provide_valid_operator_input
-> provide_valid_release_input

request_allowed_operator_action
-> request_allowed_release_action

prepare_operator_notes
-> prepare_delivery_notes

send_to_human_review
-> send_to_owner_or_responsible_review

READY_FOR_HUMAN_REVIEW
-> READY_FOR_OWNER_OR_RESPONSIBLE_REVIEW

BLOCKED_BY_MISSING_HUMAN_REVIEW
-> BLOCKED_BY_MISSING_RELEASE_REVIEW

human_reviewer_present
-> release_responsible_present

human_review_status
-> release_review_status

VALID_HUMAN_REVIEW_STATUSES
-> VALID_RELEASE_REVIEW_STATUSES

required_human_actions
-> required_responsible_actions

assign_human_reviewer
-> assign_release_responsible

complete_human_review_before_delivery
-> complete_release_review_before_delivery
```

## COMPATIBILITY POLICY

Preferred approach:

```text
Hard rename module and imports in one focused batch.
Do not keep active compatibility shim unless tests reveal external coupling not found by reference audit.
```

Fallback if coupling is wider than expected:

```text
Create new owner_release_action_gate module.
Keep old module only as a temporary deprecated import shim.
Shim must not contain operator semantics beyond import aliases.
Shim must be removed in the same or next micro-batch.
```

## FILES TO TOUCH

Runtime/code:

```text
PymIA-Live/pymia/smartpyme/service_1_operator_harness_v2_contract.py
PymIA-Live/pymia/smartpyme/service_1_synthetic_real_case_pilot_v1.py
PymIA-Live/pymia/smartpyme/service_1_microservice_registry_contract_v1.py
```

Tests:

```text
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_v2_contract.py
PymIA-Live/tests/smartpyme/test_service_1_microservice_chain_dry_run_v1.py
PymIA-Live/tests/smartpyme/test_service_1_end_to_end_dry_run_v1.py
PymIA-Live/tests/smartpyme/test_service_1_synthetic_real_case_pilot_v1.py
PymIA-Live/tests/smartpyme/test_service_1_microservice_registry_contract_v1.py
```

Docs/audit follow-up:

```text
docs/auditoria/P0B_OPERATOR_HARNESS_V2_FUNCTION_AUDIT_ONLY_V1.md
```

## PRESERVE EXACT BEHAVIOR

The rename must preserve:

```text
- no IO
- no XLSX parsing
- no API calls
- no LLM/chatbot/OCR/parser
- no vertical_slice import
- no tool execution
- no runtime authorization
- same fail-closed invalid input behavior
- same missing fields behavior
- same case manifest block behavior
- same delivery audit block behavior
- same stop condition block behavior
- same missing release review block behavior
- same forbidden claims block behavior
- same forbidden action block behavior
- delivery_allowed=True only when all current preconditions pass and requested action is deliver_operational_draft
```

## REQUIRED REGISTRY MIGRATION

In `service_1_microservice_registry_contract_v1.py`, migrate the active registry entry:

```text
operator_harness
-> owner_release_action_gate
```

Recommended spec migration:

```text
allowed_inputs:
  ["case_manifest_status", "delivery_audit_status", "requested_release_action"]

allowed_outputs:
  ["release_action_decision"]

next_allowed_action:
  "gate_owner_release_action"
```

Blocked capabilities remain equivalent:

```text
chatbot_autonomo
llm_runtime
ocr
parser
api
final_accounting_claim
```

## REQUIRED TEST SEMANTICS

Rename tests from operator-language to release-language without reducing coverage:

```text
test_valid_delivery_action_allows_operational_draft_delivery
-> test_valid_release_action_allows_operational_draft_delivery

test_forbidden_operator_action_blocks_delivery
-> test_forbidden_release_action_blocks_delivery

test_prepare_operator_notes_is_allowed_but_does_not_allow_delivery
-> test_prepare_delivery_notes_is_allowed_but_does_not_allow_delivery
```

The forbidden autonomous chatbot case must remain.

## FOCAL TEST PLAN

From `PymIA-Live`:

```bash
python -m pytest tests/smartpyme/test_service_1_owner_release_action_gate_v1.py tests/smartpyme/test_service_1_microservice_chain_dry_run_v1.py tests/smartpyme/test_service_1_end_to_end_dry_run_v1.py tests/smartpyme/test_service_1_synthetic_real_case_pilot_v1.py tests/smartpyme/test_service_1_microservice_registry_contract_v1.py -q
```

Expected baseline to preserve:

```text
56 passed before rename
```

## RESIDUE CHECKS REQUIRED

After patch, inside `PymIA-Live`:

```text
service_1_operator_harness_v2_contract: 0
build_service_1_operator_harness_v2_contract: 0
Service1OperatorHarnessV2Contract: 0
operator_harness_v2: 0
operator_requested_action: 0
allowed_operator_actions: 0
blocked_operator_actions: 0
prepare_operator_notes: 0
```

Acceptable remaining terms in this batch:

```text
human_review: may remain outside this target batch.
operator_notes_* artifacts in unrelated sandbox routes may remain outside this target batch.
operator_harness old references in historical docs/audit/quarantine may remain outside PymIA-Live.
```

## DO NOT TOUCH

```text
- S2 files
- accounting_human_review_gate_v1.py
- service_1_human_review_release_integration_gate_v1.py
- global human_review cleanup
- owner conversation layer
- CLI service_1_operator.py
- unrelated docs/producto
- runtime XLSX delivery behavior
```

## ACCEPTANCE CRITERIA

```text
1. Worktree before patch is clean except the audit docs for P0-B.
2. Old operator_harness_v2 module no longer exists in PymIA-Live.
3. New owner_release_action_gate module exists and passes tests.
4. Direct consumers import the new module and symbols.
5. Registry no longer exposes microservice_id operator_harness.
6. Focal tests pass.
7. Residue checks listed above return 0 in PymIA-Live.
8. No S2/gate/global cleanup is mixed into this batch.
```

## RECOMMENDED COMMIT MESSAGE

```bash
git commit -m "refactor(pymia-live): replace operator harness v2 with owner release action gate"
```

## FINAL STATUS

```text
P0B_OPERATOR_HARNESS_V2_RENAME_TASKSPEC_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: IMPLEMENT_P0B_RENAME_ONLY
```
