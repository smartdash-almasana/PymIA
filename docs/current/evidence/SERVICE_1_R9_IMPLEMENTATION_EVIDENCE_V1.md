# Servicio 1 — R9 ResultReadBoundary Evidence V1

**Scope:** R9 only. Persisted F13 result reading is separated from the
execution root.

## Verification

```text
R9_F13_FOCAL = 17 passed / 0 failed
RESULT_READ_SEPARATE_FROM_EXECUTION = PASS
F13_READ_NO_RECALCULATION = PASS
```

Executed:

```text
python -m pytest -q tests/smartpyme/test_service_1_result_memory_f13_v1.py
```

The focal covers:

```text
same tenant + case + result + integrity digest -> READY
different tenant -> BLOCKED
different case -> BLOCKED
wrong integrity digest -> BLOCKED
unknown result -> BLOCKED
tampered F13 ResultSet -> BLOCKED
reentry does not invoke XLSX, SEM, Product Root, P7, P8, F7, F8, F9, or LLM
```

## Runtime boundary

`Service1ResultQueryV1` carries tenant identity, case identity, result ID, and
the expected ResultSet integrity digest. `ResultReadBoundary` validates the
query and the immutable F13 record, then returns a read-only projection with
all authority flags false. The web reentry path uses this boundary and does
not call the Product Root or any analysis stage.

The boundary module imports only the F13 result-memory contract and has no
XLSX, semantic, P7/P8, F7/F8/F9, LLM, or FormulaEngine dependency.

No R10 cleanup was implemented. No full suite, commit, push, or deploy was
performed.
