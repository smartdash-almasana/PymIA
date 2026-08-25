# Servicio 1 — R13C full-suite root-cause diagnosis

## Scope and method

R13C is read-only diagnosis. No runtime or test source was changed and no
failure was repaired.

The 52 previously failing node IDs from
`SERVICE_1_R13_FULL_SUITE_EVIDENCE_V1.md` were replayed as a bounded subset
with `pytest -q --tb=short` (not the full suite). Observed result: **52 failed
in 80.24s**. The three Playwright setup errors from R13 remain a separate
infrastructure prerequisite and were not included in this replay.

## Root-cause matrix

| Count | Tests | Confirmed root cause | Classification |
|---:|---|---|---|
| 1 | `tests/architecture/test_forbidden_terms.py` | The lexical guard flags the word `workflow` in a web-boundary docstring at `service_1_web_column_confirmation_intake_boundary_v1.py:378`. | Guard/token mismatch; not a runtime execution failure. |
| 8 | `test_service_1_assisted_web_radar_http_v1.py` (1), `test_service_1_assisted_web_tenant_persistence_v1.py` (4), `test_service_1_cafeteria_semantic_scope_v1.py` (2), `test_service_1_ren_001_sellable_vertical_closure_v1.py` (1) | Assertions expect the retired owner-facing copy (`Esto entendí de tu Excel`, `Resultado listo`) and old answer controls. Current pages use the workbook-first wording/state and, for some fixtures, reach a completed/blocked review without those controls. | Stale UI/semantic-flow test contract; no repair performed. |
| 1 | `test_service_1_assisted_web_vertical_slice_contract.py` | Source guard still requires the removed top-level `owner_answers` token after R10B2. | Stale legacy-source assertion. |
| 7 | `test_service_1_cafeteria_generalization_f11_v1.py` | Tests call F7 evidence preparation directly with a D7 governed input lacking the required D4 graph/provenance carrier. Current F7 fail-closes with `D4_RELATIONSHIP_PROVENANCE_REQUIRED`. | Direct legacy bypass of the D4→D7→F7 contract; test fixture/orchestration stale. |
| 1 | `test_service_1_consorcios_radar_plug_v1.py` | Radar projection serializes the computed float directly, yielding `30.000000000000004`; the test requires exact text `30.0`. | Numeric presentation/precision contract mismatch. |
| 1 | `test_service_1_cycle_053_global_12_pathology_closure_v1.py` | Test introspects the retired kwargs-shaped `requested_capability` parameter. Product Root now accepts a typed `ProductExecutionRequestV1`. | Stale signature assertion. |
| 2 | `test_service_1_excel_reality_lab_a4_adversarial_matrix_v1.py` | The A4 helper calls the canonical bridge with removed `sheet_name`; cases S1-A4-008/009 crash before fail-closed classification. | Stale non-production helper API call. |
| 6 | `test_service_1_first_operatorless_case_v1.py` (1), `test_service_1_liq_001_product_wiring_v1.py` (1), `test_service_1_operability_packet_v1.py` (2), `test_service_1_product_completion_gate_v1.py` (2) | Tests still pass removed CLI `tool_requests` to `run_service_1_product_entrypoint_v1`. | Stale legacy CLI/tool-launch contract. |
| 2 | `test_service_1_frozen_dependency_evidence_matrix_v1.py` | Registry contains one `EXPERIMENTAL_FROZEN` module (`service_1_pipeline_v1`), while the frozen-dependency matrix is still empty (`frozen_module_count=0`, no entries). | Stale registry/matrix documentation artifact. |
| 17 | `test_service_1_llm_semantic_interpreter_v1.py` (7), `test_service_1_semantic_proposal_validator_v1.py` (9), `test_service_1_semantic_dimensions_relationships_f6_v1.py` (1) | Shared fixtures construct legacy top-level ingestion (`case_id`, `filename`, `source_file_ref`, tables) without canonical `workbook_context` and `provenance`. The current profiler deliberately returns `BLOCK_PROFILE_WORKBOOK_CONTEXT_REQUIRED`/`BLOCK_PROFILE_PROVENANCE_REQUIRED`, so SEM-2/SEM-3 never reach their intended assertions. | Stale pre-canonical-envelope fixtures. |
| 1 | `test_service_1_next_productive_capability_decision_v1.py` | Test expects obsolete token `KERNEL_IS_FORMULA_EXECUTION_AUTHORITY`; current status uses `FORMULA_ENGINE_SERVICE_IS_MATH_KERNEL_AUTHORITY`. | Stale documentation token assertion. |
| 1 | `test_service_1_owner_semantic_answer_projection_v1.py` | Current dialogue plan splits `p-cost` into its own semantic-group decision; accepting the `p-qty+p-price` group therefore projects 2 events, while the test expects 3. | Stale owner-dialogue grouping expectation. |
| 1 | `test_service_1_semantic_bridge_to_controlled_execution_gate_v1.py` | Test passes removed `sheet_name` to the canonical bridge and fails before safe-option assertions execute. | Stale canonical-bridge call. |
| 2 | `test_service_1_physical_xlsx_product_readiness_corpus_v1.py` | Readiness helper passes removed `sheet_name` to the canonical bridge for all corpus cases. | Stale non-production helper API call. |
| 1 | `test_service_1_product_completion_gate_v1.py::test_product_completion_gate_counts_and_legacy_absence` | Current registry counts are 63 `PRODUCTIVE`, 47 `SUPPORT_NECESSARY`, 1 `EXPERIMENTAL_FROZEN`; the historical gate still requires at least 48 support modules and zero frozen modules. | Stale completion-gate baseline versus R11 registry reconciliation. |

Counts sum to **52**. The first 8 UI cases are assertion/state-contract drift;
they are not evidence of a single common runtime exception. The 7 F11 cases
and 17 SEM-2/SEM-3/F6 cases are deterministic fail-closed precondition
mismatches, not uncontrolled crashes.

## Separate infrastructure errors from R13

The three R13 errors remain Playwright fixture startup failures because the
Chromium executable is absent from the local Playwright cache. They are not
included in the 52-test root-cause count.

## State and decision

- Runtime changed by R13C: **NO**
- Tests changed by R13C: **NO**
- Repairs performed: **NO**
- Full suite rerun after R13: **NO**
- Commit/push/deploy: **NO**
- Next action: bounded reconciliation of the stale contracts above, only after
  explicit authorization.
