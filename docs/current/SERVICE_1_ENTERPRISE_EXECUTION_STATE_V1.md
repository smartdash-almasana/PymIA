# SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1

**Status:** `ACTIVE_OPERATIONAL_LEDGER`  
**Authority scope:** current execution and recovery state only  
**Must not redefine:** product identity, P0–P10 architecture, capability semantics or production criteria  
**Permanent method:** `SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md`  
**State date:** 2026-07-25
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
state_date: 2026-07-25
repository: E:\BuenosPasos\smartbridge\PymIA
main:
  branch: main
  head: SELF
  head_resolution: git rev-parse HEAD
  working_tree: CLEAN
  dirty_paths: 0
enterprise_docs:
  worktree: E:\BuenosPasos\smartbridge\PymIA-ENTERPRISE-DOCS
  branch_reported: work/service1-enterprise-governance-20260723
  base_head: 394e302fc972d01ac1247704dd95cecdce9cdac9
  documentation_commit: 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
  writable_paths: 3
  commit_created: true
enterprise_stage: STAGE_1_REMOVE_CERTIFIED_DEAD_CLUSTERS
stage_0_status: PASS
safe_to_begin_productive_refactor: true
commit_authorized: true
integration_authorized: true
documentation_integration:
  status: COMPLETED
  command: git merge --ff-only work/service1-enterprise-governance-20260723
  integrated_commit: 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
clean_base_full_regression:
  status: PASS
  command: python -m pytest -q
  result: 1869 passed in 338.25s (0:05:38)
  passed: 1869
  skipped: 0
  failed: 0
  duration_seconds: 338.25
semantic_precision_baseline:
  status: RECORDED
  command: python -c "import json; from pymia.smartpyme.service_1_column_understanding_corpus_report_v1 import build_service_1_column_understanding_corpus_report_v1; print(json.dumps(build_service_1_column_understanding_corpus_report_v1().to_dict(), ensure_ascii=False, indent=2))"
  cases_count: 6
  columns_count: 38
  exact_matches: 22
  safe_questions: 16
  safe_unknowns: 0
  false_confident: 0
  missed_questions: 0
  dangerous_errors: 0
  exact_match_rate: 0.5789
  safe_resolution_rate: 1.0
  evaluation_verdict: READY_WITH_FIXES
push_authorized: true
cold_recovery:
  latest_verdict: PASS_RECOVERABLE_WITHOUT_CHAT
  auditor: OpenCode
  audit_mode: READ_ONLY
  files_modified_by_audit: 0
  commit_created_by_audit: false
  push_performed_by_audit: false
  next_gate: PASSED
stage_0_independent_audit:
  status: PASS
  verdict: PASS_STAGE0_INDEPENDENT_AUDIT
  auditor: ChatGPT
  tool_surface: MCP-local
  audit_mode: READ_ONLY
  audited_head: c38fe53d157309e3cbe9f5b9b2e889a433a0d136
  files_modified_by_audit: 0
  commit_created_by_audit: false
  push_performed_by_audit: false
stage_1:
  status: ACTIVE
  cluster_001:
    id: STAGE1_CLUSTER_001_COMMON_NORMALIZATION_ROUTER
    status: CLOSED_IN_MAIN
    branch: work/service1-stage1-dead-cluster-001
    integrated_commit: f3c10fd8fe826a97d158bda2477989720e727597
    integration_command: git merge --ff-only work/service1-stage1-dead-cluster-001
    merge_result: FAST_FORWARD_PASS
    deleted_files:
      - pymia/smartpyme/service_1_common_normalization_router_v1.py
      - tests/smartpyme/test_service_1_common_normalization_router_v1.py
    caller_audit: ZERO_REAL_CALLERS
    dynamic_loading_audit: PASS
    focal_and_neighbor_tests:
      command: python -m pytest tests/smartpyme/test_service_1_product_completion_gate_v1.py tests/smartpyme/test_service_1_module_disposition_registry_v1.py tests/smartpyme/test_service_1_csv_to_normalized_table_v1.py tests/smartpyme/test_service_1_normalized_table_v1.py tests/smartpyme/test_service_1_xlsx_to_normalized_table_v1.py -q
      result: 50 passed in 14.23s
    full_regression:
      command: python -m pytest -q
      result: 1861 passed in 354.64s (0:05:54)
      passed: 1861
      skipped: 0
      failed: 0
      duration_seconds: 354.64
    module_counts:
      total_modules: 57
      total_modules_before: 58
      productive: 27
      productive_changed: false
      support_necessary: 30
      support_necessary_before: 31
    product_capability_impact: NONE
    independent_audit: PASS_STAGE1_CLUSTER_001_AUDIT
    push_performed: false
  cluster_002:
    id: STAGE1_CLUSTER_002_RUNTIME_CATALOG_PIPELINE_COMPOSITION
    status: CLOSED_IN_MAIN
    branch: work/service1-stage1-dead-cluster-002
    integrated_commit: a40107c95fcbe2ffb23cf6c2f71ada5d375cb303
    integration_command: git merge --ff-only work/service1-stage1-dead-cluster-002
    merge_result: FAST_FORWARD_PASS
    deleted_files:
      - pymia/smartpyme/service_1_runtime_catalog_pipeline_composition_v1.py
      - tests/smartpyme/test_service_1_runtime_catalog_pipeline_composition_v1.py
    caller_audit: ZERO_REAL_CALLERS
    dynamic_loading_audit: PASS
    focal_and_neighbor_tests:
      command: python -m pytest tests/smartpyme/test_service_1_product_completion_gate_v1.py tests/smartpyme/test_service_1_module_disposition_registry_v1.py tests/smartpyme/test_service_1_pipeline_readiness_gate_v1.py tests/smartpyme/test_service_1_runtime_catalog_binding_adapter_v1.py tests/smartpyme/test_service_1_runtime_catalog_to_semantic_binding_handoff_v1.py tests/smartpyme/test_service_1_owner_confirmation_boundary_v1.py -q
      result: 67 passed in 6.84s
    full_regression:
      command: python -m pytest -q
      result: 1844 passed in 173.38s (0:02:53)
      passed: 1844
      skipped: 0
      failed: 0
      duration_seconds: 173.38
    module_counts:
      total_modules: 56
      total_modules_before: 57
      productive: 27
      productive_changed: false
      support_necessary: 29
      support_necessary_before: 30
    product_capability_impact: NONE
    push_performed: false
  cluster_003:
    id: STAGE1_CLUSTER_003_RUNTIME_CATALOG_CHAIN
    status: CLOSED_IN_MAIN
    branch: work/service1-stage1-dead-cluster-003
    integrated_commit: a5608219cd86317295e6a1e5c3b29781c499d9dd
    integration_command: git merge --ff-only work/service1-stage1-dead-cluster-003
    merge_result: FAST_FORWARD_PASS
    deleted_files:
      - pymia/smartpyme/service_1_owner_confirmation_boundary_v1.py
      - pymia/smartpyme/service_1_pipeline_readiness_gate_v1.py
      - pymia/smartpyme/service_1_runtime_catalog_binding_adapter_v1.py
      - pymia/smartpyme/service_1_runtime_catalog_binding_contract_v1.py
      - pymia/smartpyme/service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
      - tests/smartpyme/test_service_1_owner_confirmation_boundary_v1.py
      - tests/smartpyme/test_service_1_pipeline_readiness_gate_v1.py
      - tests/smartpyme/test_service_1_runtime_catalog_binding_adapter_v1.py
      - tests/smartpyme/test_service_1_runtime_catalog_binding_contract_v1.py
      - tests/smartpyme/test_service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
    caller_audit: ZERO_REAL_CALLERS
    dynamic_loading_audit: PASS
    focal_and_neighbor_tests:
      command: python -m pytest tests/smartpyme/test_service_1_module_disposition_registry_v1.py tests/smartpyme/test_service_1_product_completion_gate_v1.py tests/smartpyme/test_service_1_deterministic_semantic_pipeline_v1.py tests/smartpyme/test_service_1_product_pipeline_v1.py tests/smartpyme/test_service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py tests/smartpyme/test_service_1_semantic_bridge_to_controlled_execution_gate_v1.py tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py tests/smartpyme/test_service_1_assisted_web_http_v1.py -q
      result: 77 passed in 34.27s
    full_regression:
      command: python .tmp/run_pytest_partition.py 0..3 4
      result: 1761 passed across 4 exhaustive partitions; 180 test files; 0 failed
      passed: 1761
      skipped: 0
      failed: 0
      execution_mode: exhaustive_partitioned_due_to_tool_timeout_boundary
    module_counts:
      total_modules: 51
      total_modules_before: 56
      productive: 27
      productive_changed: false
      support_necessary: 24
      support_necessary_before: 29
    product_capability_impact: NONE
    independent_audit: PASS_STAGE1_CLUSTER_003_COMMIT_AUDIT
    push_performed: true
  cluster_004:
    id: STAGE1_CLUSTER_004_CSV_INTAKE
    status: CLOSED_IN_MAIN
    branch: main
    integrated_commit: 33cca19c06b842b19e71b7bd0d35f226440bb6e5
    integration_command: direct commit on main
    merge_result: NOT_APPLICABLE_DIRECT_MAIN_COMMIT
    deleted_files:
      - pymia/smartpyme/service_1_csv_intake_v1.py
      - tests/smartpyme/test_service_1_csv_intake_v1.py
    caller_audit: ZERO_REAL_CALLERS
    dynamic_loading_audit: PASS
    supersession: service_1_csv_to_normalized_table_v1 -> service_1_normalized_table_v1
    focal_and_neighbor_tests:
      command: python -m pytest tests/smartpyme/test_service_1_csv_to_normalized_table_v1.py tests/smartpyme/test_service_1_normalized_table_v1.py tests/smartpyme/test_service_1_xlsx_to_normalized_table_v1.py tests/smartpyme/test_service_1_module_disposition_registry_v1.py tests/smartpyme/test_service_1_product_completion_gate_v1.py -q
      result: 50 passed in 5.64s
    full_regression:
      command: python -m pytest -q
      result: 1751 passed in 114.98s (0:01:54)
      passed: 1751
      skipped: 0
      failed: 0
      duration_seconds: 114.98
    module_counts:
      total_modules: 50
      total_modules_before: 51
      productive: 27
      productive_changed: false
      support_necessary: 23
      support_necessary_before: 24
    product_capability_impact: NONE
    independent_audit: PASS_STAGE1_CLUSTER_004_CSV_INTAKE_POST_REMOVAL_AUDIT
    push_performed: false
  cluster_005:
    id: STAGE1_CLUSTER_005_QA_DELIVERY_GATE
    status: CLOSED_IN_MAIN
    branch: main
    integrated_commit: 642966f2ba99634109bc18598b41f02b5f538519
    integration_command: direct commit on main
    merge_result: NOT_APPLICABLE_DIRECT_MAIN_COMMIT
    deleted_files:
      - pymia/smartpyme/service_1_qa_delivery_gate_v1.py
      - tests/smartpyme/test_service_1_qa_delivery_gate_v1.py
    caller_audit: ZERO_REAL_CALLERS
    dynamic_loading_audit: PASS
    legacy_dependency: isolated operator flow requiring case_delivery_manifest absent from current product
    focal_and_neighbor_tests:
      command: python -m pytest tests/smartpyme/test_service_1_product_pipeline_v1.py tests/smartpyme/test_service_1_product_completion_gate_v1.py tests/smartpyme/test_service_1_assisted_web_http_v1.py tests/smartpyme/test_service_1_module_disposition_registry_v1.py tests/smartpyme/test_service_1_post_tool_owner_delivery_summary_v1.py -q
      result: 26 passed in 6.68s
    full_regression:
      command: python -m pytest tests/smartpyme -q; python -m pytest tests/application tests/architecture tests/audit_result tests/cli tests/contracts tests/diagnostic_core tests/diagnosticcore tests/docs tests/document_intelligence tests/domain tests/e2e tests/hermes tests/interfaces tests/llm_operator tests/mcp tests/microsaas tests/orchestration tests/pipeline tests/rendering tests/scn tests/scripts tests/services tests/telegram_runtime tests/tools -q
      result: 1740 passed across 2 exhaustive partitions; 0 failed
      passed: 1740
      skipped: 0
      failed: 0
      execution_mode: exhaustive_partitioned_due_to_connector_timeout_boundary
    module_counts:
      total_modules: 49
      total_modules_before: 50
      productive: 27
      productive_changed: false
      support_necessary: 22
      support_necessary_before: 23
    product_capability_impact: NONE
    independent_audit: PASS_STAGE1_CLUSTER_005_QA_DELIVERY_GATE_POST_REMOVAL_AUDIT
    push_performed: false
next_authorized_action: CERTIFY_NEXT_STAGE1_DEAD_CLUSTER_OR_CLOSE_STAGE1
```

---

## 3. Certified repository facts

```text
MAIN_BRANCH = main
MAIN_HEAD = SELF (resolve with git rev-parse HEAD)
MAIN_WORKTREE_CLEAN = true
MAIN_DIRTY_PATHS = 0
GIT_OPERATION_IN_PROGRESS = none reported
PUSH_PERFORMED_DURING_STABILIZATION = false
DOCUMENTATION_INTEGRATION = COMPLETED
DOCUMENTATION_INTEGRATION_COMMIT = 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
```

The clean `main` state was reached by preserving four unfinished work packages outside `main`, restoring shared documents and registries from `HEAD`, and verifying the safety commits independently.

The existing `SERVICE_1_STATUS.md` and architecture locks describe the product baseline at `394e302`. They do not certify enterprise readiness, the preserved branches, semantic precision or the future architecture migration.

Current enterprise stage:

```text
STAGE_1 — REMOVE CERTIFIED DEAD CLUSTERS
```

Stage 0 closed with all required gates satisfied:

- method/state package passed cold recovery;
- documentation package was integrated as one focal commit;
- full regression passed on the controlled integrated base;
- semantic precision baseline was measured and recorded without hiding the 0.5789 exact-match gap;
- independent Stage 0 audit emitted `PASS_STAGE0_INDEPENDENT_AUDIT`.

Stage 1 is active. Its first audited dead-cluster removal is closed in `main`:

```text
CLUSTER = STAGE1_CLUSTER_001_COMMON_NORMALIZATION_ROUTER
INTEGRATED_COMMIT = f3c10fd8fe826a97d158bda2477989720e727597
AUDIT = PASS_STAGE1_CLUSTER_001_AUDIT
PRODUCT_CAPABILITY_IMPACT = none
```

Its second audited dead-cluster removal is also closed in `main`:

```text
CLUSTER = STAGE1_CLUSTER_002_RUNTIME_CATALOG_PIPELINE_COMPOSITION
INTEGRATED_COMMIT = a40107c95fcbe2ffb23cf6c2f71ada5d375cb303
AUDIT = PASS_STAGE1_CLUSTER_002_INTEGRATION
PRODUCT_CAPABILITY_IMPACT = none
```

Its third audited dead-cluster removal is also closed in `main`:

```text
CLUSTER = STAGE1_CLUSTER_003_RUNTIME_CATALOG_CHAIN
INTEGRATED_COMMIT = a5608219cd86317295e6a1e5c3b29781c499d9dd
AUDIT = PASS_STAGE1_CLUSTER_003_COMMIT_AUDIT
PRODUCT_CAPABILITY_IMPACT = none
```

Its fourth audited dead-cluster removal is also closed in `main`:

```text
CLUSTER = STAGE1_CLUSTER_004_CSV_INTAKE
INTEGRATED_COMMIT = 33cca19c06b842b19e71b7bd0d35f226440bb6e5
AUDIT = PASS_STAGE1_CLUSTER_004_CSV_INTAKE_POST_REMOVAL_AUDIT
FULL_REGRESSION = 1751 passed in 114.98s
PRODUCT_CAPABILITY_IMPACT = none
```

Its fifth audited dead-cluster removal is also closed in `main`:

```text
CLUSTER = STAGE1_CLUSTER_005_QA_DELIVERY_GATE
INTEGRATED_COMMIT = 642966f2ba99634109bc18598b41f02b5f538519
AUDIT = PASS_STAGE1_CLUSTER_005_QA_DELIVERY_GATE_POST_REMOVAL_AUDIT
FULL_REGRESSION = 1740 passed across 2 exhaustive partitions; 0 failed
PRODUCT_CAPABILITY_IMPACT = none
```

The next permitted action remains to certify another Stage 1 dead cluster independently, or close Stage 1 if none remains certifiable.

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
FINAL_AUDITOR = ChatGPT using MCP-local read-only audit tools
DOCUMENTATION_COMMIT = 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
COMMIT_CREATED = true
COMMIT_AUTHORIZED = true
INTEGRATION_AUTHORIZED = true
DOCUMENTATION_INTEGRATED_INTO_MAIN = true
PUSH_AUTHORIZED = true
```

The documentation commit was integrated into `main` by the exact fast-forward command recorded in the machine-readable snapshot. The current `main` HEAD is intentionally `SELF`, resolved by Git after this evidence closure commit.

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

Documentation integration completed:

```text
COMMAND = git merge --ff-only work/service1-enterprise-governance-20260723
INTEGRATED_COMMIT = 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
MAIN_HEAD_AFTER_INTEGRATION = 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
RESULT = FAST_FORWARD_PASS
```

Full regression observed on the integrated documentation commit:

```text
COMMAND = python -m pytest -q
RESULT = 1869 passed in 338.25s (0:05:38)
PASSED = 1869
SKIPPED = 0
FAILED = 0
DURATION_SECONDS = 338.25
```

Semantic baseline observed exclusively through the existing corpus-report evaluator:

```text
CASES_COUNT = 6
COLUMNS_COUNT = 38
EXACT_MATCHES = 22
SAFE_QUESTIONS = 16
SAFE_UNKNOWNS = 0
FALSE_CONFIDENT = 0
MISSED_QUESTIONS = 0
DANGEROUS_ERRORS = 0
EXACT_MATCH_RATE = 0.5789
SAFE_RESOLUTION_RATE = 1.0
EVALUATION_VERDICT = READY_WITH_FIXES
EXACT_MATCH_TARGET_FOR_FRONTEND_READY = 0.8
EXACT_MATCH_TARGET_MET = false
```

The baseline is recorded without concealing its gap: `exact_match_rate` is below the evaluator's 0.8 frontend-readiness threshold. This does not authorize runtime or frontend wiring; the evaluator reports `READY_WITH_FIXES` with zero dangerous errors.

Independent Stage 0 audit result:

```text
AUDIT_TYPE = STAGE_0_INDEPENDENT_CLOSURE_AUDIT
AUDITOR = ChatGPT
TOOL_SURFACE = MCP-local
MODE = READ_ONLY
AUDITED_HEAD = c38fe53d157309e3cbe9f5b9b2e889a433a0d136
MAIN_REF = c38fe53d157309e3cbe9f5b9b2e889a433a0d136
MAIN_WORKTREE = CLEAN
DOCUMENTATION_INTEGRATION = PASS
REGRESSION_EVIDENCE = PASS
SEMANTIC_BASELINE = PASS_RECORDED_WITH_KNOWN_GAP
SAFETY_PACKAGES = PASS_PRESERVED_OUTSIDE_MAIN
DOCUMENT_INDEX = PASS
CONTRADICTIONS = none
FILES_MODIFIED_BY_AUDIT = 0
COMMIT_CREATED_BY_AUDIT = false
PUSH_PERFORMED_BY_AUDIT = false
VERDICT = PASS_STAGE0_INDEPENDENT_AUDIT
```

Audit evidence verified:

- `main` and `HEAD` both resolve to `c38fe53d157309e3cbe9f5b9b2e889a433a0d136` before this state-only closure update;
- the main worktree was clean;
- `94a8b7458ac7788025c3a214b3a5f4ac56bbec7d` is integrated directly before the baseline evidence commit;
- the baseline commit modifies only this execution-state ledger;
- the existing corpus report reproduces 6 cases, 38 columns, 22 exact matches, 16 safe questions, zero dangerous errors, 0.5789 exact-match rate and 1.0 safe-resolution rate;
- WS5, WS234, WS1 and WS6 commits resolve and their safety worktrees are clean;
- README/document references resolve;
- no safety package was integrated and no production or frontend readiness was claimed.

Stage 0 is closed. Current next authorized action:

```text
NEXT_AUTHORIZED_ACTION = CERTIFY_NEXT_STAGE1_DEAD_CLUSTER_OR_CLOSE_STAGE1
```

Stage 1 cluster 001 closure:

```text
CLUSTER = STAGE1_CLUSTER_001_COMMON_NORMALIZATION_ROUTER
STATUS = CLOSED_IN_MAIN
BRANCH = work/service1-stage1-dead-cluster-001
INTEGRATED_COMMIT = f3c10fd8fe826a97d158bda2477989720e727597
INTEGRATION = FAST_FORWARD_PASS
FILES_DELETED = pymia/smartpyme/service_1_common_normalization_router_v1.py; tests/smartpyme/test_service_1_common_normalization_router_v1.py
CALLER_AUDIT = zero real callers
DYNAMIC_LOADING_AUDIT = PASS
FOCAL_AND_NEIGHBOR_TESTS = 50 passed
FULL_REGRESSION = 1861 passed in 354.64s
MODULE_COUNT_CHANGE = total 58 -> 57; SUPPORT_NECESSARY 31 -> 30; PRODUCTIVE 27 unchanged
PRODUCT_CAPABILITY_IMPACT = none
AUDIT = PASS_STAGE1_CLUSTER_001_AUDIT
PUSH_PERFORMED = false
```

Stage 1 cluster 002 closure:

```text
CLUSTER = STAGE1_CLUSTER_002_RUNTIME_CATALOG_PIPELINE_COMPOSITION
STATUS = CLOSED_IN_MAIN
BRANCH = work/service1-stage1-dead-cluster-002
INTEGRATED_COMMIT = a40107c95fcbe2ffb23cf6c2f71ada5d375cb303
INTEGRATION = FAST_FORWARD_PASS
FILES_DELETED = pymia/smartpyme/service_1_runtime_catalog_pipeline_composition_v1.py; tests/smartpyme/test_service_1_runtime_catalog_pipeline_composition_v1.py
CALLER_AUDIT = zero real callers
DYNAMIC_LOADING_AUDIT = PASS
FOCAL_AND_NEIGHBOR_TESTS = 67 passed
FULL_REGRESSION = 1844 passed in 173.38s
MODULE_COUNT_CHANGE = total 57 -> 56; SUPPORT_NECESSARY 30 -> 29; PRODUCTIVE 27 unchanged
PRODUCT_CAPABILITY_impact = none
PUSH_PERFORMED = false
```

Stage 1 cluster 003 closure:

```text
CLUSTER = STAGE1_CLUSTER_003_RUNTIME_CATALOG_CHAIN
STATUS = CLOSED_IN_MAIN
BRANCH = work/service1-stage1-dead-cluster-003
INTEGRATED_COMMIT = a5608219cd86317295e6a1e5c3b29781c499d9dd
INTEGRATION = FAST_FORWARD_PASS
FILES_DELETED = 5 runtime-catalog-chain modules; 5 exclusive tests
CALLER_AUDIT = zero real callers
DYNAMIC_LOADING_AUDIT = PASS
FOCAL_AND_NEIGHBOR_TESTS = 77 passed in 34.27s
FULL_REGRESSION = 1761 passed across 4 exhaustive partitions; 180 test files; 0 failed
MODULE_COUNT_CHANGE = total 56 -> 51; SUPPORT_NECESSARY 29 -> 24; PRODUCTIVE 27 unchanged
PRODUCT_CAPABILITY_IMPACT = none
AUDIT = PASS_STAGE1_CLUSTER_003_COMMIT_AUDIT
PUSH_PERFORMED = true
```

Stage 1 cluster 004 closure:

```text
CLUSTER = STAGE1_CLUSTER_004_CSV_INTAKE
STATUS = CLOSED_IN_MAIN
BRANCH = main
INTEGRATED_COMMIT = 33cca19c06b842b19e71b7bd0d35f226440bb6e5
INTEGRATION = DIRECT_MAIN_COMMIT
FILES_DELETED = pymia/smartpyme/service_1_csv_intake_v1.py; tests/smartpyme/test_service_1_csv_intake_v1.py
CALLER_AUDIT = zero real callers
DYNAMIC_LOADING_AUDIT = PASS
SUPERSESSION = service_1_csv_to_normalized_table_v1 -> service_1_normalized_table_v1
FOCAL_AND_NEIGHBOR_TESTS = 50 passed in 5.64s
FULL_REGRESSION = 1751 passed in 114.98s; 0 failed
MODULE_COUNT_CHANGE = total 51 -> 50; SUPPORT_NECESSARY 24 -> 23; PRODUCTIVE 27 unchanged
PRODUCT_CAPABILITY_IMPACT = none
AUDIT = PASS_STAGE1_CLUSTER_004_CSV_INTAKE_POST_REMOVAL_AUDIT
PUSH_PERFORMED = false
```

Stage 1 cluster 005 closure:

```text
CLUSTER = STAGE1_CLUSTER_005_QA_DELIVERY_GATE
STATUS = CLOSED_IN_MAIN
BRANCH = main
INTEGRATED_COMMIT = 642966f2ba99634109bc18598b41f02b5f538519
INTEGRATION = DIRECT_MAIN_COMMIT
FILES_DELETED = pymia/smartpyme/service_1_qa_delivery_gate_v1.py; tests/smartpyme/test_service_1_qa_delivery_gate_v1.py
CALLER_AUDIT = zero real callers
DYNAMIC_LOADING_AUDIT = PASS
LEGACY_DEPENDENCY = isolated operator flow requiring case_delivery_manifest absent from current product
FOCAL_AND_NEIGHBOR_TESTS = 26 passed in 6.68s
FULL_REGRESSION = 1740 passed across 2 exhaustive partitions; 0 failed
MODULE_COUNT_CHANGE = total 50 -> 49; SUPPORT_NECESSARY 23 -> 22; PRODUCTIVE 27 unchanged
PRODUCT_CAPABILITY_IMPACT = none
AUDIT = PASS_STAGE1_CLUSTER_005_QA_DELIVERY_GATE_POST_REMOVAL_AUDIT
PUSH_PERFORMED = false
```

Stage 1 may continue only by certifying another dead cluster independently, or by closing Stage 1 if no additional dead cluster is certifiable. Preserved safety packages remain out of scope.

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
DO_NOT_DELETE_UNCERTIFIED_OR_REFERENCED_CLUSTERS
DO_NOT_START_STAGE_2
DO_NOT_CREATE_ANOTHER_SEMANTIC_CATALOG
DO_NOT_CREATE_A_SECOND_APPROVAL_CENTER
DO_NOT_PUSH_ANY_SAFETY_BRANCH
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
| S1-DEBT-006 | RESOLVED — semantic precision baseline recorded at 22/38 exact matches, 0.5789 exact-match rate, 1.0 safe-resolution rate and zero dangerous errors | CLOSED | preserve and improve the versioned corpus baseline without concealing the readiness gap | Stage 0 |
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
6. COMPLETE — documentation commit integrated into clean main by fast-forward.
7. COMPLETE — full regression passed on the integrated documentation commit: 1869 passed in 338.25s.
8. COMPLETE — semantic precision baseline recorded: 22/38 exact matches, 1.0 safe-resolution rate, zero dangerous errors.
9. COMPLETE — PASS_STAGE0_INDEPENDENT_AUDIT recorded.
```

Stage 0 is closed. Productive work may begin only through a bounded Stage 1 active specification.

---

## 12. Recovery verification

Expected facts:

```text
main branch = main
main HEAD = SELF (resolve with git rev-parse HEAD)
main working tree = clean
documentation integration commit = 94a8b7458ac7788025c3a214b3a5f4ac56bbec7d
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
ENTERPRISE_STAGE = STAGE_1_REMOVE_CERTIFIED_DEAD_CLUSTERS
STAGE_0_STATUS = PASS
MAIN_CLEAN = true
WS5_PRESERVED = true
WS234_PRESERVED = true
WS1_PRESERVED = true
WS6_PRESERVED = true
SAFE_TO_BEGIN_PRODUCTIVE_REFACTOR = true
CLEAN_BASE_FULL_REGRESSION = PASS (1869 passed in 338.25s)
SEMANTIC_BASELINE_RECORDED = true
SEMANTIC_BASELINE_EXACT_MATCH_RATE = 0.5789 (below 0.8 frontend-readiness target)
SEMANTIC_BASELINE_SAFE_RESOLUTION_RATE = 1.0
SEMANTIC_BASELINE_DANGEROUS_ERRORS = 0
SEMANTIC_BASELINE_EVALUATION_VERDICT = READY_WITH_FIXES
COLD_RECOVERY = PASS_RECOVERABLE_WITHOUT_CHAT
COLD_RECOVERY_AUDITOR = OpenCode
COLD_RECOVERY_AUDIT_MODE = READ_ONLY
DOCUMENTATION_INTEGRATED_INTO_MAIN = true
STAGE_0_INDEPENDENT_AUDIT = PASS_STAGE0_INDEPENDENT_AUDIT
STAGE_0_INDEPENDENT_AUDITOR = ChatGPT_WITH_MCP_LOCAL
STAGE1_CLUSTER_001_COMMON_NORMALIZATION_ROUTER = CLOSED_IN_MAIN
STAGE1_CLUSTER_001_COMMIT = f3c10fd8fe826a97d158bda2477989720e727597
STAGE1_CLUSTER_001_AUDIT = PASS_STAGE1_CLUSTER_001_AUDIT
STAGE1_CLUSTER_001_REGRESSION = PASS (1861 passed in 354.64s)
STAGE1_CLUSTER_001_PRODUCT_CAPABILITY_IMPACT = none
STAGE1_CLUSTER_002_RUNTIME_CATALOG_PIPELINE_COMPOSITION = CLOSED_IN_MAIN
STAGE1_CLUSTER_002_COMMIT = a40107c95fcbe2ffb23cf6c2f71ada5d375cb303
STAGE1_CLUSTER_002_AUDIT = PASS_STAGE1_CLUSTER_002_INTEGRATION
STAGE1_CLUSTER_002_REGRESSION = PASS (1844 passed in 173.38s)
STAGE1_CLUSTER_002_PRODUCT_CAPABILITY_IMPACT = none
STAGE1_CLUSTER_003_RUNTIME_CATALOG_CHAIN = CLOSED_IN_MAIN
STAGE1_CLUSTER_003_COMMIT = a5608219cd86317295e6a1e5c3b29781c499d9dd
STAGE1_CLUSTER_003_AUDIT = PASS_STAGE1_CLUSTER_003_COMMIT_AUDIT
STAGE1_CLUSTER_003_REGRESSION = PASS (1761 passed across 4 exhaustive partitions)
STAGE1_CLUSTER_003_PRODUCT_CAPABILITY_IMPACT = none
STAGE1_CLUSTER_004_CSV_INTAKE = CLOSED_IN_MAIN
STAGE1_CLUSTER_004_COMMIT = 33cca19c06b842b19e71b7bd0d35f226440bb6e5
STAGE1_CLUSTER_004_AUDIT = PASS_STAGE1_CLUSTER_004_CSV_INTAKE_POST_REMOVAL_AUDIT
STAGE1_CLUSTER_004_REGRESSION = PASS (1751 passed in 114.98s)
STAGE1_CLUSTER_004_PRODUCT_CAPABILITY_IMPACT = none
STAGE1_CLUSTER_005_QA_DELIVERY_GATE = CLOSED_IN_MAIN
STAGE1_CLUSTER_005_COMMIT = 642966f2ba99634109bc18598b41f02b5f538519
STAGE1_CLUSTER_005_AUDIT = PASS_STAGE1_CLUSTER_005_QA_DELIVERY_GATE_POST_REMOVAL_AUDIT
STAGE1_CLUSTER_005_REGRESSION = PASS (1740 passed across 2 exhaustive partitions)
STAGE1_CLUSTER_005_PRODUCT_CAPABILITY_IMPACT = none
NEXT_AUTHORIZED_ACTION = CERTIFY_NEXT_STAGE1_DEAD_CLUSTER_OR_CLOSE_STAGE1
COMMIT_CREATED = true
COMMIT_AUTHORIZED = true
INTEGRATION_AUTHORIZED = true
PUSH_AUTHORIZED = true
```
