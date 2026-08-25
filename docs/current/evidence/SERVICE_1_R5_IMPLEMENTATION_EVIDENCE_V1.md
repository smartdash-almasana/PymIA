# Servicio 1 — R5 Implementation Evidence

## Scope

R5 retired the productive semantic legacy reentry path and productive
`sheet1` identity fallbacks. R6 and later nodes were not started.

## Preconditions

- Branch: `work/service1-cafeteria-flow-v1`
- HEAD before R5: `8d5708e9becdddaa5aa24387b310972643d1ef86`
- R4.5 integration checkpoint: `docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V2.md`
- Existing worktree changes and `_audit/` were preserved; no reset, checkout,
  commit, push, or deploy was performed.

## Implementation

- Removed `service_1_legacy_semantic_reentry_compat_v1.py` and its productive
  caller from the CLI.
- Removed `service_1_deterministic_semantic_pipeline_v1.py` as a productive
  composition root. The P8 adapter for confirmed SEM-8 bindings now lives in
  `service_1_computability_v1.py`.
- Routed CLI semantic reentry through explicit
  `WorkbookSemanticStartRequestV1` and `WorkbookSemanticContinueRequestV1`
  commands at `run_service_1_product_pipeline_v1`.
- Added explicit CLI owner actor inputs; SEM-8 remains fail-closed when owner
  identity is absent.
- Removed productive `sheet1` fabrication from owner confirmation, SEM-6/P6
  identity paths. Missing physical sheet identity now remains unresolved or
  blocks instead of inventing a worksheet.
- Migrated the focal parity coverage to the single SEM-8 state machine and
  preserved sheet-qualified multi-sheet evidence.

## Exit gates

```text
PRODUCTIVE_LEGACY_SEMANTIC_CALLERS = 0
PARALLEL_SEMANTIC_FSM = 0
PRODUCTIVE_SHEET1_FALLBACK = 0
```

The static search was limited to productive `pymia/` runtime code. The
deterministic proposal provider remains the provider-neutral SEM-8 input and
is not a second semantic state machine.

## Verification

Command executed:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py \
  tests/smartpyme/test_service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py \
  tests/smartpyme/test_service_1_owner_semantic_evidence_reentry_v1.py \
  tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py
```

Result: **52 passed / 0 failed**.

No full suite, Playwright, smoke, Cloud Run, Gemma, R6, commit, push, or
deploy was executed.

## Verdict

```text
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R6
BLOCKERS: NONE
```
