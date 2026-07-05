# P0_OPERATOR_CRITICAL_FILE_MATRIX_AUDIT_ONLY_V1

## VERDICT

```text
STATUS: AUDIT_CREATED
SCOPE: DOC_ONLY
RUNTIME_CHANGE: NO
TEST_CHANGE: NO
DELETE_CHANGE: NO
FILES_AUDITED: 5
SOURCE_AUDIT: docs/auditoria/OPERATOR_PARASITE_FULL_AUDIT_V1.txt
BOUNDARY_DOC: docs/auditoria/OPERATOR_RESCUE_AND_DEATH_BOUNDARY_V1.md
```

## PURPOSE

Classify the P0 critical files before any deletion, rename, or runtime patch.

Rule applied:

```text
Do not delete by keyword.
Classify by real function.
Rescue passive owner-facing/delivery-facing functions.
Kill operator/human_review as autonomous authority.
```

## P0 FILE MATRIX

### 1. PymIA-Live/pymia/smartpyme/accounting_human_review_gate_v1.py

```text
CURRENT_FUNCTION: accounting gate for sandbox candidate scope
DANGEROUS_TERMS: human_review, reviewer_role
AUTHORITY_RISK: MEDIUM
RUNTIME_RISK: LOW_MEDIUM
OBSERVED_SAFETY: runtime_authorized is always False; live_use=True blocks; forbidden claims block
DECISION: RESCUE_RENAME
```

Rationale:

```text
The module is not an autonomous human reviewer.
It is a deterministic blocking gate that prevents live accounting use and forbidden claims.
The function is useful, but the name human_review is genetically dangerous.
```

Target migration:

```text
accounting_human_review_gate_v1 -> accounting_evidence_release_gate_v1 or accounting_sandbox_release_gate_v1
reviewer_role -> responsible_role or review_responsible_role
human_review language -> evidence/release/signoff language
```

Do not delete first.

---

### 2. PymIA-Live/pymia/smartpyme/service_1_human_review_release_integration_gate_v1.py

```text
CURRENT_FUNCTION: large integration candidate gate for delivery release, owner packet, endpoint/auth/storage/worker boundaries
DANGEROUS_TERMS: human_review, reviewer_role, operator_or_accountant
AUTHORITY_RISK: HIGH_BY_NAME / LOW_BY_FLAGS
RUNTIME_RISK: HIGH_IF_DELETED
OBSERVED_SAFETY: publish/runtime/storage/db/worker/queue/mutation/llm authorization flags are false; status remains pending/signoff-oriented
DECISION: RESCUE_RENAME_WITH_DEEP_MIGRATION
```

Rationale:

```text
This file has dangerous semantics but appears structurally fail-closed.
It integrates release evidence and blocks unsafe publish flags.
Deleting blindly can break current Service 1 boundary chain.
```

Target migration:

```text
service_1_human_review_release_integration_gate_v1
-> service_1_owner_release_signoff_gate_v1
or service_1_evidence_release_integration_gate_v1

human_review_required -> owner_signoff_required / release_signoff_required
reviewer_role -> signoff_responsible_role
operator_or_accountant -> owner_or_accountant / responsible_human_role
PENDING_HUMAN_REVIEW -> PENDING_OWNER_SIGNOFF or PENDING_RELEASE_SIGNOFF
```

Do not delete first.

---

### 3. PymIA-Live/pymia/smartpyme/service_1_operator_harness_v1.py

```text
CURRENT_FUNCTION: demo harness that executes Service 1 pipeline into delivery folder and writes summary/operator_report
DANGEROUS_TERMS: operator_harness, operator_notes, operator_report
AUTHORITY_RISK: HIGH
RUNTIME_RISK: MEDIUM
OBSERVED_SAFETY: runtime_authorized returned False, but function performs IO and runs pipeline
DECISION: KILL_OR_RENAME_AFTER_REFERENCE_CHECK
```

Rationale:

```text
This is the closest P0 file to the dead operator figure.
It performs IO and invokes pipeline under operator harness naming.
The useful function is not operator authority; it is a controlled demo/delivery harness.
```

Target outcomes:

```text
If still used by tests/runtime: RESCUE_RENAME to service_1_controlled_delivery_demo_harness_v1.py
If obsolete: KILL_DELETE after reference check and tests
```

Mandatory rename if rescued:

```text
operator_harness -> controlled_delivery_demo_harness
operator_notes -> delivery_notes
operator_report.txt -> delivery_report.txt or owner_delivery_report.txt
_build_operator_report -> _build_delivery_report
```

Do not keep name.

---

### 4. PymIA-Live/pymia/smartpyme/service_2_reconciliation_assisted_review_block_v1.py

```text
CURRENT_FUNCTION: builds reconciliation review block from match candidates with owner/accountant summaries, caveats, no IO, no LLM
DANGEROUS_TERMS: assisted_review, operator audience, requires_human_review
AUTHORITY_RISK: MEDIUM
RUNTIME_RISK: MEDIUM_IF_DELETED
OBSERVED_SAFETY: states caveats; no definitive reconciliation; io_performed False; api_used False; llm_used False
DECISION: RESCUE_RENAME
```

Rationale:

```text
The function is useful: it prepares a review block with caveats for owner/accountant.
The dangerous part is the assisted/operator vocabulary.
```

Target migration:

```text
service_2_reconciliation_assisted_review_block_v1
-> service_2_reconciliation_owner_review_block_v1
or service_2_reconciliation_evidence_review_block_v1

assisted_review -> owner_review / evidence_review
operator_brief -> responsible_brief or internal_brief
requires_human_review -> requires_responsible_review / requires_accountant_review
```

Do not delete first.

---

### 5. PymIA-Live/pymia/smartpyme/service_2_reconciliation_assisted_review_delivery_packet_v1.py

```text
CURRENT_FUNCTION: compatibility shim around current assisted review block
DANGEROUS_TERMS: assisted_review
AUTHORITY_RISK: LOW
RUNTIME_RISK: LOW_MEDIUM_IF_REFERENCED
OBSERVED_SAFETY: deprecated=True; deprecation_reason says merged into block; no IO; no API; no LLM
DECISION: KILL_DELETE_AFTER_REFERENCE_CHECK or KEEP_TEMP_COMPAT_SHIM_RENAMED
```

Rationale:

```text
This is already marked deprecated and is not a real processing layer.
It can probably die once references are checked.
If active callers remain, keep temporarily as compatibility shim with non-operator naming.
```

Target migration:

```text
Preferred: delete after reference check.
Fallback: rename to service_2_reconciliation_owner_review_delivery_packet_compat_v1.py
```

## ORDER OF EXECUTION RECOMMENDED

```text
1. Reference-check P0 files and tests.
2. Patch service_1_operator_harness_v1 first, because it contains the strongest dead operator identity and performs IO.
3. Patch service_2 delivery packet shim if references are low.
4. Rename service_2 assisted review block to owner/evidence review block.
5. Rename accounting human review gate to evidence/sandbox release gate.
6. Rename service_1 human review release integration gate last, because it is larger and likely coupled.
```

## DO NOT DO

```text
Do not bulk delete all P0 files.
Do not mechanically replace operator strings everywhere.
Do not preserve operator_harness naming.
Do not keep human_review as a sovereign runtime concept.
Do not touch P1/P2/P3 until P0 reference matrix is complete.
```

## NEXT ACTION

```text
P0_REFERENCE_CHECK_AUDIT_ONLY
```

Required output:

```text
For each P0 file:
- imports/references in code
- imports/references in tests
- docs references
- safe rename/delete path
- minimal focal test list
```

## FINAL_STATUS

```text
P0_OPERATOR_CRITICAL_FILE_MATRIX_AUDIT_ONLY_V1: CREATED
CODE_CHANGE_AUTHORIZED: NO
NEXT_ACTION: P0_REFERENCE_CHECK_AUDIT_ONLY
```
