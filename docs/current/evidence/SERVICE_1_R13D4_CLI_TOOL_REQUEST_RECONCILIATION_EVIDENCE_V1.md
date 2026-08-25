# Service 1 — R13D4 CLI `tool_requests` reconciliation evidence

Date: 2026-08-25

## Scope

Only the six R13D4 CLI callers identified in the R13C diagnosis were migrated:

- `tests/smartpyme/test_service_1_first_operatorless_case_v1.py::test_operatorless_case_replays_from_cli_without_internal_runtime`
- `tests/smartpyme/test_service_1_liq_001_product_wiring_v1.py::test_official_entrypoint_executes_liq_001_from_all_normalized_rows`
- `tests/smartpyme/test_service_1_operability_packet_v1.py::test_operability_packet_real_cafeteria_example_runs_to_xlsx_output`
- `tests/smartpyme/test_service_1_operability_packet_v1.py::test_operability_packet_blocks_free_text_semantic_answers`
- `tests/smartpyme/test_service_1_product_completion_gate_v1.py::test_product_completion_gate_real_cafeteria_acceptance`
- `tests/smartpyme/test_service_1_product_completion_gate_v1.py::test_product_completion_gate_plan_only_liq_001_acceptance`

## Reconciliation

The stale `tool_requests` keyword and its physical-tool expectations were removed
from these callers. They now use the current CLI surface, which constructs typed
`WorkbookSemanticStartRequestV1` / `WorkbookSemanticContinueRequestV1` commands,
passes explicit owner actor identity, and uses SEM-8 `decision_id` action
responses. LIQ-001 keeps its deterministic computation-plan assertions. The
cafeteria `sales_total` cases now assert the canonical fail-closed
`CAPABILITY_NOT_GOVERNED` result because `sales_total` is a discovery analysis,
not a P8-governed capability in the current registry. The invalid semantic case
uses an unsupported canonical action and asserts SEM-8 fail-closed behavior.

No runtime module, Product Root, math engine, semantic provider, wrapper, alias,
fallback, or compatibility shim was added or changed by R13D4.

## Verification

Command executed exactly for the six affected tests:

```text
python -m pytest -q \
tests/smartpyme/test_service_1_first_operatorless_case_v1.py::test_operatorless_case_replays_from_cli_without_internal_runtime \
tests/smartpyme/test_service_1_liq_001_product_wiring_v1.py::test_official_entrypoint_executes_liq_001_from_all_normalized_rows \
tests/smartpyme/test_service_1_operability_packet_v1.py::test_operability_packet_real_cafeteria_example_runs_to_xlsx_output \
tests/smartpyme/test_service_1_operability_packet_v1.py::test_operability_packet_blocks_free_text_semantic_answers \
tests/smartpyme/test_service_1_product_completion_gate_v1.py::test_product_completion_gate_real_cafeteria_acceptance \
tests/smartpyme/test_service_1_product_completion_gate_v1.py::test_product_completion_gate_plan_only_liq_001_acceptance
```

Observed result: **6 passed / 0 failed** in **207.72s**.

Full suite, R14+, commit, push, and deploy were not executed.
