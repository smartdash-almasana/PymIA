# Servicio 1 — R8 Specialized Convergence Evidence V1

**Scope:** R8 only. Consorcios and reconciliation retain their specialized
workflows while using the common mathematical and policy authorities.

## Verification

```text
R8_FOCAL_TESTS = 19 passed / 0 failed
SPECIALIZED_ANTI_DUMP_TESTS = 6 passed / 0 failed
SPECIALIZED_ANTI_DUMP = PASS
```

Executed:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_consorcios_expense_variance_v1.py \
  tests/smartpyme/test_service_1_consorcios_collection_aging_v1.py \
  tests/smartpyme/test_service_1_reconciliation_product_wiring_v1.py \
  tests/smartpyme/test_service_1_reconciliation_governed_flow_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py
```

## Convergence gates

```text
SPECIALIZED_INLINE_BUSINESS_MATH = 0
SPECIALIZED_INLINE_CLASSIFICATION = 0
```

Consorcios expense variance now delegates grouped SUM, named budget and
historical variance formulas, and MAX deviation to `FormulaEngineService`.
Consorcios collection aging delegates the named period-ratio formula and
declarative bucket policy to the shared formula/classification contracts.
Reconciliation keeps its matcher and assisted-review workflow; summary
normalization uses the common MAX primitive and retains human-review and
fail-closed safety boundaries. No confidence is promoted to authority and no
ambiguity is resolved automatically.

The explicit specialized subtype registry remains bounded to the contracted
collection-aging, expense-variance, and reconciliation subtypes; an unknown
subtype is rejected by the Product Root.

## Changed R8 surface

```text
pymia/contracts/formula_rules_v1.json
pymia/services/formula_engine_service.py
pymia/smartpyme/service_1_consorcios_expense_variance_v1.py
pymia/smartpyme/service_1_consorcios_collection_aging_v1.py
pymia/smartpyme/service_1_reconciliation_candidate_to_assisted_review_v1.py
pymia/smartpyme/service_1_reconciliation_request_gate_v1.py
tests/smartpyme/test_service_1_consorcios_expense_variance_v1.py
tests/smartpyme/test_service_1_consorcios_collection_aging_v1.py
tests/smartpyme/test_service_1_reconciliation_product_wiring_v1.py
```

No R9 capability was implemented. No commit, push, deploy, or full-suite run
was performed.
