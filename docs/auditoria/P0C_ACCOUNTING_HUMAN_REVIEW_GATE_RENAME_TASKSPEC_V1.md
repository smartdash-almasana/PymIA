# P0C_ACCOUNTING_HUMAN_REVIEW_GATE_RENAME_TASKSPEC_V1

## VERDICT

```text
STATUS: TASKSPEC_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
TARGET_BATCH: P0-C
SOURCE_AUDIT: docs/auditoria/P0C_HUMAN_REVIEW_REVIEWER_ASSISTED_SITUATIONAL_AUDIT_V1.md
```

## OBJECTIVE

Rename the accounting `human_review` gate into a sandbox release gate while preserving the fail-closed behavior.

```text
The accounting gate function is rescued.
The human_review sovereign wording is killed for this accounting sandbox gate.
```

## TARGET RENAME

Runtime:

```text
PymIA-Live/pymia/smartpyme/accounting_human_review_gate_v1.py
->
PymIA-Live/pymia/smartpyme/accounting_sandbox_release_gate_v1.py
```

Test:

```text
PymIA-Live/tests/smartpyme/test_accounting_human_review_gate_v1.py
->
PymIA-Live/tests/smartpyme/test_accounting_sandbox_release_gate_v1.py
```

## SYMBOL MIGRATION

```text
GATE_REF = "service_1_accounting_human_review_gate_v1"
-> GATE_REF = "service_1_accounting_sandbox_release_gate_v1"

evaluate_accounting_human_review_gate_v1
-> evaluate_accounting_sandbox_release_gate_v1

reviewer_role
-> responsible_role

human_review_gate
-> sandbox_release_gate

human_review_gate_result
-> sandbox_release_gate_result

human_review_gate_status
-> sandbox_release_gate_status

human_review_gate_not_passed
-> sandbox_release_gate_not_passed

BLOCKED_HUMAN_REVIEW_NOT_PASSED
-> BLOCKED_SANDBOX_RELEASE_GATE_NOT_PASSED

complete_human_review_gate_first
-> complete_sandbox_release_gate_first

request_human_accounting_review_decision
-> request_accounting_sandbox_release_decision
```

## FILES TO TOUCH

Runtime/code:

```text
PymIA-Live/pymia/smartpyme/accounting_human_review_gate_v1.py
PymIA-Live/pymia/smartpyme/accounting_workpaper_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/accounting_workpaper_draft_packet_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_contract_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_fixture_handoff_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_review_packet_v1.py
PymIA-Live/pymia/smartpyme/invoice_collection_matching_sandbox_completion_slice_v1.py
```

Tests:

```text
PymIA-Live/tests/smartpyme/test_accounting_human_review_gate_v1.py
PymIA-Live/tests/smartpyme/test_accounting_workpaper_completion_slice_v1.py
PymIA-Live/tests/smartpyme/test_accounting_workpaper_draft_packet_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_completion_slice_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_fixture_handoff_v1.py
PymIA-Live/tests/smartpyme/test_bank_reconciliation_sandbox_review_packet_v1.py
```

## PRESERVE EXACT BEHAVIOR

The rename must preserve:

```text
- pure deterministic gate
- no IO
- no API
- no LLM
- no runtime authorization
- runtime_authorized always False
- live_use=True blocks
- forbidden claims block
- scope_ok=False blocks
- evidence_ok=False blocks
- decision=REJECTED blocks
- decision=APPROVED allows sandbox candidate only
- pending decision remains non-deliverable/non-release
```

## STATUS SEMANTICS

Current statuses:

```text
PASS
PENDING
REJECTED
BLOCKED
INVALID_INPUT
```

Keep statuses unchanged for this batch unless tests force explicit rename. Reason: status strings are low-risk compared to function/module names and may be consumed by accounting slices.

Allowed semantic changes only in reason/action strings:

```text
Human review gate has not passed.
-> Sandbox release gate has not passed.

Human review passed for sandbox candidate only.
-> Sandbox release gate passed for sandbox candidate only.

Human review is pending.
-> Sandbox release decision is pending.
```

## FOCAL TEST PLAN

From `PymIA-Live`:

```bash
python -m pytest tests/smartpyme/test_accounting_sandbox_release_gate_v1.py tests/smartpyme/test_accounting_workpaper_completion_slice_v1.py tests/smartpyme/test_accounting_workpaper_draft_packet_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_completion_slice_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_contract_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_fixture_handoff_v1.py tests/smartpyme/test_bank_reconciliation_sandbox_review_packet_v1.py -q
```

Expected baseline to preserve:

```text
60 passed before rename
```

## RESIDUE CHECKS REQUIRED IN PYMIA-LIVE

After patch:

```text
accounting_human_review_gate_v1: 0
 evaluate_accounting_human_review_gate_v1: 0
service_1_accounting_human_review_gate_v1: 0
BLOCKED_HUMAN_REVIEW_NOT_PASSED: 0
complete_human_review_gate_first: 0
human_review_gate_status: 0 in touched accounting files
human_review_gate_not_passed: 0 in touched accounting files
```

Acceptable remaining terms in this batch:

```text
human_review in non-accounting S1 release/signoff files
human_review in column confirmation / owner prompt flags
human_review in web-test / registry / activation flags
human_review in S2 files
```

## DO NOT TOUCH

```text
- service_1_human_review_release_integration_gate_v1.py
- service_1_human_review_signoff_flow_v1.py
- service_1_final_owner_release_decision_gate_v1.py
- service_1_case_delivery_folder_v1.py
- service_1_microservice_registry_contract_v1.py unless focal tests require it
- S2 assisted review files
- global human_review cleanup
- CLI service_1_operator.py
```

## ACCEPTANCE CRITERIA

```text
1. Old accounting_human_review_gate module no longer exists in PymIA-Live.
2. New accounting_sandbox_release_gate module exists.
3. All direct accounting consumers import the new module and symbol.
4. Focal tests pass.
5. Residue checks for old accounting gate names return 0 in PymIA-Live.
6. No S1 release/signoff, S2, registry/global cleanup is mixed into this batch.
```

## RECOMMENDED COMMIT MESSAGE

```bash
git commit -m "refactor(pymia-live): replace accounting human review gate with sandbox release gate"
```

## FINAL STATUS

```text
P0C_ACCOUNTING_HUMAN_REVIEW_GATE_RENAME_TASKSPEC_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: IMPLEMENT_P0C_ACCOUNTING_GATE_RENAME_ONLY
```
