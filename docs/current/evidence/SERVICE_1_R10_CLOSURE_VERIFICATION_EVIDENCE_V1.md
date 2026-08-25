# Service 1 — R10 Closure Verification Evidence

Date: 2026-08-24

## Certifier repair

`tools/service_1_architecture_baseline_v1.py` now treats the R5-retired deterministic semantic composition root as an absent legacy cluster instead of reading a deleted file. Current Product Root, SEM wiring, and P8 sources provide the active checks; no legacy module was recreated and no gate was weakened.

## R10 gates

The five R10 gates from `SERVICE_1_RECONSTRUCTION_PLAN_V1.md` pass against the current worktree:

```text
PRODUCTIVE_COMPATIBILITY_SHIMS = 0
TRANSITIONAL_ALIAS_WITHOUT_EXIT = 0
PROCEDURAL_ROOT_SWITCHES = 0
POST_CONSTRUCTION_ENVELOPE_MUTATIONS = 0
PRODUCTIVE_SHEET1_FALLBACK = 0
```

Evidence includes the R10B1–R10B6D records, current runtime searches, the canonical-envelope alias scan, the repaired architecture certifier, and the passing bounded Product Root/semantic/ingestion tests. Remaining `owner_answers` occurrences are canonical owner-confirmation input/evidence contracts, not the retired top-level alias path. The only `analysis_execution_request` occurrence is a fail-closed reason string, not an informal request dictionary.

## Tests

Architecture certifier:

```text
python tools/service_1_architecture_baseline_v1.py --json
```

Result: `PASS_ARCHITECTURE_BASELINE_V1`; structural checks pass and its behavior suite reports **75 passed / 0 failed**.

Certifier test:

```text
python -m pytest -q tests/smartpyme/test_service_1_architecture_baseline_certifier_v1.py
```

Result: **1 passed / 0 failed**.

R10 closure command:

```text
python -m pytest -q tests/smartpyme/test_service_1_architecture_lock_v1.py tests/smartpyme/test_service_1_architecture_baseline_certifier_v1.py tests/smartpyme/test_service_1_product_pipeline_v1.py tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py tests/smartpyme/test_service_1_owner_confirmation_to_canonical_ingestion_output_v1.py tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py tests/smartpyme/test_service_1_multisheet_parity_guard_v1.py tests/smartpyme/test_service_1_canonical_ingestion_to_region_evidence_adapter_v1.py
```

Result: **92 passed / 0 failed** in 50.34 seconds.

No full suite, R11, commit, push, or deploy was performed. Existing worktree changes and `_audit/` were preserved.

## Verdict

`R10_GATES = PASS`

`R10_CLOSURE = PASS`
