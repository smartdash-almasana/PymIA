# SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1

**Status:** `ACTIVE_OPERATIONAL_LEDGER`  
**Authority scope:** current execution and recovery state only  
**Must not redefine:** product identity, P0–P10 architecture, capability semantics or production criteria  
**Permanent method:** `SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md`  
**State date:** 2026-07-23  
**Update rule:** update after every preservation, audited closure, rollback, stage transition or change in the next authorized action.

---

## 1. Recovery warning

This document must allow Servicio 1 work to continue after total conversational-memory loss.

Before acting, compare every recorded repository fact with Git. If branch, HEAD, worktree cleanliness, safety commit, path scope or test evidence differs, stop and report:

```text
RECOVERY_STATE_MISMATCH
```

Do not repair a mismatch by assumption.

---

## 2. Machine-readable snapshot

```yaml
schema_version: SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1
state_date: 2026-07-23
repository: E:\BuenosPasos\smartbridge\PymIA
main:
  branch: main
  head: 394e302fc972d01ac1247704dd95cecdce9cdac9
  working_tree: CLEAN
  dirty_paths: 0
enterprise_docs:
  worktree: E:\BuenosPasos\smartbridge\PymIA-ENTERPRISE-DOCS
  branch_reported: work/service1-enterprise-governance-20260723
  base_head: 394e302fc972d01ac1247704dd95cecdce9cdac9
  documentation_commit: SELF
  documentation_commit_resolution: git rev-parse HEAD
  writable_paths: 3
  commit_created: true
enterprise_stage: STAGE_0_STABILIZE_AND_BASELINE
safe_to_begin_productive_refactor: false
commit_authorized: true
integration_authorized: false
push_authorized: false
clean_base_full_regression:
  status: NOT_RUN_AFTER_TREE_STABILIZATION
semantic_precision_baseline:
  status: NOT_RECORDED
cold_recovery:
  latest_verdict: PASS_RECOVERABLE_WITHOUT_CHAT
  auditor: OpenCode
  audit_mode: READ_ONLY
  files_modified_by_audit: 0
  commit_created_by_audit: false
  push_performed_by_audit: false
  next_gate: PASSED
next_authorized_action: PREPARE_DOCUMENTATION_INTEGRATION_FOR_OWNER_AUTHORIZATION
```

---

## 3. Certified repository facts

```text
MAIN_BRANCH = main
MAIN_HEAD = 394e302fc972d01ac1247704dd95cecdce9cdac9
MAIN_WORKTREE_CLEAN = true
MAIN_DIRTY_PATHS = 0
GIT_OPERATION_IN_PROGRESS = none reported
PUSH_PERFORMED_DURING_STABILIZATION = false
```

The clean `main` state was reached by preserving four unfinished work packages outside `main`, restoring shared documents and registries from `HEAD`, and verifying the safety commits independently.

The existing `SERVICE_1_STATUS.md` and architecture locks describe the product baseline at `394e302`. They do not certify enterprise readiness, the preserved branches, semantic precision or the future architecture migration.

Current enterprise stage:

```text
STAGE_0 — STABILIZE AND ESTABLISH BASELINE
```

Stage 0 is not complete until:

- this method/state package passes cold recovery;
- the documentation package is integrated as one focal commit;
- a full regression is observed on the clean base with the documentation commit;
- the semantic precision baseline is measured and recorded;
- an independent Stage 0 audit emits `PASS`.

---

## 4. Safety preservation registry

A safety branch preserves recoverable work. It does not authorize integration.

### SAFETY-WS5 — semantic concept metadata

```text
STATE = PRESERVED_OUTSIDE_MAIN
BRANCH = safety/ws5-semantic-catalog-20260723
WORKTREE = E:\BuenosPasos\smartbridge\PymIA-WS5-SAFETY
COMMIT = 521979316d17e57fd96f00d15d05001842c51942
PATHS = 4
FOCAL_TESTS_REPORTED = 27 passed
COPY_HASH_CHECK = PASS
PUSH = not performed
```

Paths:

```text
pymia/smartpyme/service_1_semantic_concept_catalog_contract_v1.py
tests/smartpyme/test_service_1_semantic_concept_catalog_candidate_v1.py
tests/smartpyme/test_service_1_semantic_concept_catalog_contract_v1.py
tests/smartpyme/test_service_1_semantic_concept_catalog_readiness_gate_v1.py
```

Disposition:

```text
CURRENT_STATE = PRESERVED_OUTSIDE_MAIN
TARGET = ABSORB_UNIQUE_METADATA_INTO_CANONICAL_SEMANTIC_AUTHORITY
CANONICAL_TARGETS = service_1_semantic_evidence_binding_contracts_v1.py + service_1_semantic_catalog_loader_v1.py
FINAL_STATE = DELETE_AFTER_ABSORPTION
PRODUCTIVE_CONNECTION_NOW = false
```

The column-understanding engine may recognize observable signals and propose candidates. It must not become the owner of business definitions, exclusions, unit, temporal semantics, formula policy or risk policy.

### SAFETY-WS234 — capability and semantic expansion

```text
STATE = PRESERVED_OUTSIDE_MAIN
BRANCH = safety/ws234-capability-expansion-20260723
WORKTREE = E:\BuenosPasos\smartbridge\PymIA-WS234-SAFETY
COMMIT = 34c94a96c362a393faa008e12af49d0b6e9d0299
PATHS = 25
TESTS_REPORTED = 1435 passed, 8 failed
COPY_HASH_CHECK = PASS
PUSH = not performed
MAIN_INTEGRATION = PROHIBITED
```

Paths:

```text
docs/service_1_product_completion_gate.v1.json
pymia/smartpyme/service_1_physical_evidence_resolution_v1.py
pymia/smartpyme/service_1_transactional_sales_capabilities_v1.py
pymia/smartpyme/service_1_generic_capability_engine_v1.py
pymia/smartpyme/service_1_deterministic_semantic_pipeline_v1.py
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/smartpyme/service_1_liq_001_evaluator_v1.py
pymia/smartpyme/service_1_ren_001_normalized_evidence_v1.py
pymia/smartpyme/service_1_semantic_evidence_binding_engine_v1.py
pymia/smartpyme/service_1_column_understanding_engine_v1.py
pymia/smartpyme/service_1_variable_family_bindings_v1.py
pymia/smartpyme/service_1_column_understanding_corpus_evaluation_v1.py
tests/smartpyme/test_service_1_physical_evidence_resolution_v1.py
tests/smartpyme/test_service_1_transactional_sales_capabilities_v1.py
tests/smartpyme/test_service_1_transactional_sales_semantics_v1.py
tests/smartpyme/test_service_1_distribuidora_transactional_acceptance_v1.py
tests/smartpyme/test_service_1_generic_registry_computation_planning_v1.py
tests/smartpyme/test_service_1_product_pipeline_v1.py
tests/smartpyme/test_service_1_variable_family_bindings_v1.py
tests/smartpyme/test_service_1_column_understanding_canonical_gap_audit_v1.py
tests/smartpyme/test_service_1_column_understanding_corpus_evaluation_v1.py
tests/smartpyme/test_service_1_column_understanding_corpus_report_v1.py
tests/smartpyme/test_service_1_column_understanding_owner_question_corpus_audit_v1.py
tests/smartpyme/test_service_1_column_understanding_owner_question_semantic_audit_v1.py
tests/smartpyme/test_service_1_column_understanding_common_business_roles_v1.py
```

Known blockers:

1. variable-family count changed from seven to eighteen without a settled contract decision;
2. generic numeric columns receive candidates from physical type compatibility without sufficient semantic evidence;
3. lexical tie-breaking allows an unrelated new role to change alternatives for a generic column;
4. variable families consume P3 candidates rather than P6-approved bindings;
5. the package couples recognition, families, execution wiring and corpus changes;
6. the package is not green and cannot be integrated mechanically.

### SAFETY-WS1 — guided assisted web

```text
STATE = PRESERVED_OUTSIDE_MAIN
BRANCH = safety/ws1-guided-assisted-web-20260723
WORKTREE = E:\BuenosPasos\smartbridge\PymIA-WS1-SAFETY
COMMIT = bed473264d9769baca1673e0948411cfadbf56eb
PATHS = 13
COPY_HASH_CHECK = PASS
COMMIT_SCOPE_CHECK = PASS
WORKTREE = CLEAN
PUSH = not performed
MAIN_INTEGRATION = PROHIBITED
```

Paths:

```text
pymia/smartpyme/service_1_assisted_web_v1.py
pymia/smartpyme/static/service_1_assisted_web_v1.css
pymia/smartpyme/service_1_guided_analysis_contract_v1.py
pymia/smartpyme/service_1_guided_column_compatibility_v1.py
pymia/smartpyme/service_1_review_availability_v1.py
tests/smartpyme/test_service_1_assisted_web_http_v1.py
tests/smartpyme/test_service_1_assisted_web_review_catalog_v1.py
tests/smartpyme/test_service_1_assisted_web_vertical_slice_contract_v1.py
tests/smartpyme/test_service_1_cafeteria_owner_followup_web_v1.py
tests/smartpyme/test_service_1_guided_analysis_contract_v1.py
tests/smartpyme/test_service_1_guided_analysis_web_v1.py
tests/smartpyme/test_service_1_guided_column_compatibility_v1.py
tests/smartpyme/test_service_1_review_availability_v1.py
```

Known blocker:

`service_1_assisted_web_v1.py` contains business-value derivation, including quantity/price/discount arithmetic and creation of a synthetic transaction-sales amount. The web surface may collect and project evidence but cannot own business formulas or synthesize economic values. WS-1 must be selectively reconstructed later; it must not be merged as a block.

### SAFETY-WS6 — EvidenceArtifact experiment

```text
STATE = PRESERVED_OUTSIDE_MAIN
BRANCH = safety/ws6-evidence-artifact-spike-20260723
WORKTREE = E:\BuenosPasos\smartbridge\PymIA-WS6-SAFETY
COMMIT = bbd89ce8c277ef9bdddc3cc639989bb89df339f5
PATHS = 3
COPY_HASH_CHECK = PASS
COMMIT_SCOPE_CHECK = PASS
WORKTREE = CLEAN
PUSH = not performed
MAIN_INTEGRATION = PROHIBITED
```

Paths:

```text
docs/current/SERVICE_1_EVIDENCE_ARTIFACT_ACCEPTANCE_V1.md
pymia/smartpyme/service_1_evidence_artifact_spike_v1.py
tests/smartpyme/test_service_1_evidence_artifact_acceptance_v1.py
```

Disposition:

```text
DOCUMENT = TRANSITORY_ACCEPTANCE_EVIDENCE
SPIKE = EXPERIMENTAL_FROZEN
TEST = EXPERIMENTAL_EVIDENCE
PRODUCTIVE_AUTHORITY = false
WEB_INTEGRATION = false
```

The spike demonstrated a useful direction but failed architectural audit because compatibility, operand support and rejection outcomes were partly predeclared; derived values were not carried into a productive approved-binding path; and adversarial proof was incomplete. Valid concepts may be reimplemented only as part of the integrated approval-center and first-pathology closure. The spike itself must not be extended or connected.

---

## 5. Workstream taxonomy and disposition

| Workstream | Scope | Current state | Main integration | Required future action |
|---|---|---|---|---|
| WS-1 | assisted web, guided analysis, review availability | PRESERVED_OUTSIDE_MAIN | prohibited | recover UI/contract value selectively; no formulas in web |
| WS-2 | physical resolution and transactional capabilities | PRESERVED_WITH_WS234 | prohibited | reassess after Stage 1 and architecture consolidation |
| WS-3 | semantic roles and variable families | PRESERVED_WITH_WS234 | prohibited | redesign around stable evidence thresholds and P6-approved bindings |
| WS-4 | semantic corpus and evaluation | PRESERVED_WITH_WS234 | prohibited | recover versioned corpus evidence selectively |
| WS-5 | rich semantic concept metadata | PRESERVED_OUTSIDE_MAIN | prohibited | absorb unique metadata into canonical authority, then delete parallel catalog |
| WS-6 | EvidenceArtifact contract and spike | EXPERIMENTAL_FROZEN | prohibited | absorb validated concepts only during integrated Stage 3/4 closure |

No preserved branch is a pending merge queue.

---

## 6. Active documentation package

```text
CHANGE_ID = S1-E0-ENTERPRISE-GOVERNANCE
TITLE = Establish recoverable enterprise method and execution state
RISK_CLASS = CLASS_0_DOCUMENTATION_STATE_ALIGNMENT
BASE_HEAD = 394e302fc972d01ac1247704dd95cecdce9cdac9
WORKTREE = E:\BuenosPasos\smartbridge\PymIA-ENTERPRISE-DOCS
WRITABLE_PATHS = exactly 3
IMPLEMENTER = ChatGPT with MCP-local file tools
FINAL_AUDITOR = Qwen or another independent read-only agent
DOCUMENTATION_COMMIT = SELF
DOCUMENTATION_COMMIT_RESOLUTION = git rev-parse HEAD
COMMIT_CREATED = true
COMMIT_AUTHORIZED = true
INTEGRATION_AUTHORIZED = false
PUSH_AUTHORIZED = false
```

`SELF` is intentional: this state update is amended into the documentation commit itself, so the authoritative commit identifier is the `HEAD` resolved by Git after the amend rather than a stale pre-amend hash.

Writable paths:

```text
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
docs/current/README.md
```

Non-goals:

- no code changes;
- no test changes;
- no JSON/registry changes;
- no modification of `AGENTS.md`;
- no integration of any safety branch;
- no product readiness claim;
- no push.

Acceptance:

```text
[x] changes limited to the three declared paths
[x] original P0–P10 method preserved
[x] enterprise controls do not redefine architecture
[x] README indexes method and execution state without duplicate authority
[x] all referenced paths and commits resolve
[x] clean main remains unchanged
[x] independent cold-recovery audit reconstructs exact state
[x] audit verdict = PASS_RECOVERABLE_WITHOUT_CHAT
```

---

## 7. Cold-recovery audit result and next authorized action

Observed independent audit:

```text
AUDIT_TYPE = COLD_RECOVERY_DOCUMENTATION_AUDIT
AUDITOR = OpenCode
MODE = READ_ONLY
VERDICT = PASS_RECOVERABLE_WITHOUT_CHAT
PRECONDITIONS = PASS
MODIFIED_PATHS_OBSERVED = 3 exact declared paths
DIFF_CHECK = PASS
README_INDEX_CHECK = PASS
FILES_REQUIRING_CORRECTION = none
FILES_MODIFIED_BY_AUDIT = none
COMMIT_CREATED_BY_AUDIT = false
PUSH_PERFORMED_BY_AUDIT = false
CHAT_DEPENDENCY = none detected
```

The auditor reconstructed without conversation history:

- P0–P10 architecture;
- Stage 0 state;
- clean `main` and base HEAD;
- WS5, WS234, WS1 and WS6 branches, commits, path counts and dispositions;
- S1-DEBT-001 through S1-DEBT-010;
- current prohibitions;
- Stage 0 exit criteria;
- the distinction between permanent method authority and operational-state authority;
- the mandatory `RECOVERY_STATE_MISMATCH` stop on Git divergence.

Current next authorized action:

```text
NEXT_AUTHORIZED_ACTION = PREPARE_DOCUMENTATION_INTEGRATION_FOR_OWNER_AUTHORIZATION
```

Preparation means verifying the documentation commit's exact three-path scope and preparing controlled integration evidence. It does not authorize integration into `main` or push. Those operations require separate explicit owner authorization.

---

## 8. Current prohibitions

```text
DO_NOT_INTEGRATE_WS1
DO_NOT_INTEGRATE_WS234
DO_NOT_INTEGRATE_WS5
DO_NOT_INTEGRATE_WS6
DO_NOT_EXTEND_THE_EVIDENCE_ARTIFACT_SPIKE
DO_NOT_CHANGE_7_TO_18_MECHANICALLY
DO_NOT_FIX_GENERIC_NUMERIC_COLUMNS_WITH_ANOTHER_HARDCODE
DO_NOT_ADD_CAPABILITIES
DO_NOT_MODIFY_FRONTEND
DO_NOT_DELETE_LEGACY_CLUSTERS_YET
DO_NOT_START_STAGE_1
DO_NOT_CREATE_ANOTHER_SEMANTIC_CATALOG
DO_NOT_CREATE_A_SECOND_APPROVAL_CENTER
DO_NOT_PUSH_ANY_SAFETY_BRANCH
DO_NOT_DECLARE_ENTERPRISE_REFACTOR_STARTED
```

---

## 9. Debt register

| Debt ID | Description | Risk | Required disposition | Latest stage |
|---|---|---|---|---|
| S1-DEBT-001 | Variable families consume P3 candidates instead of P6-approved bindings | HIGH | family layer consumes only approved P6 bindings or an unequivocal projection | Stage 4 |
| S1-DEBT-002 | Numeric type-only evidence and lexical tie-breaking destabilize unrelated alternatives | HIGH | stable minimum-evidence and tie-break contract with adversarial tests | Stage 4 |
| S1-DEBT-003 | Generic, transactional and legacy calculation forms coexist | HIGH | one primary engine or narrowly justified bounded exceptions | Stage 6 |
| S1-DEBT-004 | EvidenceArtifact spike contains predeclared compatibility/anchor/rejection decisions | HIGH | keep frozen; reimplement only computed decisions during integrated migration | Stage 4 |
| S1-DEBT-005 | WS-5 duplicates semantic authority while containing unique metadata | HIGH | absorb metadata into canonical catalog/requirements and delete duplicate cluster | Stage 4 |
| S1-DEBT-006 | Semantic precision baseline is absent | HIGH | measure versioned corpus baseline on controlled clean commit | Stage 0 |
| S1-DEBT-007 | Certified dead legacy clusters remain present | MEDIUM | delete one verified cluster at a time after Stage 0 | Stage 1 |
| S1-DEBT-008 | Enterprise resource, recovery, observability and release gates are incomplete | HIGH for release | prove every Stage 7 gate | Stage 7 |
| S1-DEBT-009 | WS-1 places business-value derivation in the web surface | HIGH | reconstruct UI so computation remains exclusively canonical | Stage 5 or earlier UI reconnection |
| S1-DEBT-010 | `SERVICE_1_STATUS.md` does not express the current enterprise recovery state | MEDIUM | execution-state ledger remains the operational source; reconcile status at an authorized closure | Stage 0 |

No debt entry authorizes additional debt.

---

## 10. Known failed evidence

Observed or independently reproduced failures associated with preserved WS234 included:

```text
test_bridge_attaches_five_variable_family_bindings
test_case_001_reinject_then_gate_ready
test_full_chain_case_001_reaches_ready_gate
test_owner_question_surface_uses_safe_option_ids
test_registry_covers_every_service_1_module_exactly_once
```

Interpretation:

- family-count failures require a contract decision;
- owner-option ordering exposes a semantic-stability defect;
- registry failure was associated with unclassified experimental work;
- none authorizes changing tests solely to make them green.

WS234's final reported preservation run recorded eight failures. The complete list must be recovered from its preserved evidence before any future selective reuse.

---

## 11. Stage 0 remaining sequence

```text
1. COMPLETE — three-file enterprise documentation package prepared.
2. COMPLETE — independent cold-recovery audit executed against the enterprise-docs worktree.
3. COMPLETE — no audit-proven documentation defects remained.
4. COMPLETE — PASS_RECOVERABLE_WITHOUT_CHAT obtained.
5. COMPLETE — focal documentation commit created and its exact three-path scope verified.
6. CURRENT — prepare documentation integration for explicit owner authorization.
7. PENDING — after separate integration authorization, integrate the documentation commit into clean main.
8. PENDING — run full regression on the controlled documentation commit.
9. PENDING — measure and record semantic precision baseline.
10. PENDING — obtain independent Stage 0 audit PASS.
```

No productive implementation begins before Stage 0 exits.

---

## 12. Recovery verification

Expected facts:

```text
main branch = main
main HEAD = 394e302fc972d01ac1247704dd95cecdce9cdac9
main working tree = clean
WS5 commit = 521979316d17e57fd96f00d15d05001842c51942
WS234 commit = 34c94a96c362a393faa008e12af49d0b6e9d0299
WS1 commit = bed473264d9769baca1673e0948411cfadbf56eb
WS6 commit = bbd89ce8c277ef9bdddc3cc639989bb89df339f5
push performed = false
```

If any fact differs, update nothing and emit `RECOVERY_STATE_MISMATCH`.

---

## 13. State update protocol

After an authorized action, update:

1. actual branch and HEAD;
2. actual working-tree state;
3. safety branch/worktree/commit registry;
4. tests, actor and command;
5. independent audit verdict;
6. debt added or removed;
7. next authorized action;
8. explicit prohibitions;
9. commit and push status.

Failed evidence remains summarized when it explains a decision or prevents repetition.

---

## 14. Current final status

```text
METHOD_AUTHORITY = SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
ENTERPRISE_STAGE = STAGE_0_STABILIZE_AND_BASELINE
MAIN_CLEAN = true
WS5_PRESERVED = true
WS234_PRESERVED = true
WS1_PRESERVED = true
WS6_PRESERVED = true
SAFE_TO_BEGIN_PRODUCTIVE_REFACTOR = false
CLEAN_BASE_FULL_REGRESSION = not_run
SEMANTIC_BASELINE_RECORDED = false
COLD_RECOVERY = PASS_RECOVERABLE_WITHOUT_CHAT
COLD_RECOVERY_AUDITOR = OpenCode
COLD_RECOVERY_AUDIT_MODE = READ_ONLY
NEXT_AUTHORIZED_ACTION = PREPARE_DOCUMENTATION_INTEGRATION_FOR_OWNER_AUTHORIZATION
COMMIT_CREATED = true
COMMIT_AUTHORIZED = true
INTEGRATION_AUTHORIZED = false
PUSH_AUTHORIZED = false
```
