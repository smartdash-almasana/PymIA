# Service 1 — F1 Mathematical Authority Specification V1

**Status:** FROZEN  
**Baseline:** `1412dbad51e66d559808acdc92d6a1b162c6bdeb`  
**Scope:** freeze the F1 authority boundary without changing runtime behavior.  
**Explicit non-goals:** F8 aggregation convergence, AnalysisPlan, P7/P8 changes, vertical logic, and unrelated refactoring.

## Decision

The productive mathematical authority for Service 1 is one facade:

```text
FormulaEngineService
```

The facade owns both registered business-formula execution and the governed
`FormulaNodeV1` AST runtime. Adapters and evidence builders may validate,
resolve, classify, prepare, and package results, but they do not become a
second mathematical authority.

## Frozen authority map

| Contract | Frozen decision |
|---|---|
| `BUSINESS_FORMULA_AUTHORITY` | `FormulaEngineService.calculate` / `calculate_formula` |
| `AST_EXECUTION_AUTHORITY` | `FormulaEngineService.evaluate_ast` |
| `AGGREGATION_AUTHORITY_TARGET` | `FormulaEngineService` |
| `AGGREGATION_CURRENT_DEBT` | `GenericCapabilityEngine` SUM during input resolution |
| `DEBT_CONVERGENCE_PHASE` | F8 |

`AGGREGATION_CURRENT_DEBT` is explicit and accepted for F1 closure. It is not
silently promoted to a second authority and must not be moved as part of F1.

## Component contracts

### FormulaEngineService

Owns:

- registered `BUSINESS_FORMULA` execution;
- `FormulaNodeV1` AST execution (`VALUE`, `VARIABLE`, `ADD`, `SUBTRACT`,
  `MULTIPLY`, `DIVIDE`);
- formula blocking semantics and mathematical results.

No caller may reproduce these operations in a productive adapter.

### GenericCapabilityEngine

Retains:

- capability and governed-input resolution;
- evidence and domain validation;
- classification;
- bounded result and outcome assembly.

It **does not execute AST**. Its current `SUM` in
`_resolve_atomic_inputs` is input preparation and is classified as:

```text
AGGREGATION_EXISTING_DEBT
```

That SUM remains in place for F1. Its convergence to the target aggregation
authority is an F8 task and is not implemented here.

### LIQ_001

`sold_vs_collected_gap` delegates to the existing
`LIQ_001_vendido_cobrado` formula through `FormulaEngineService`. LIQ_001
continues to own input validation, classification, packet shape, and outcome
projection.

### REN_001

REN_001 already delegates through the formula contract. This is the required
adapter pattern and remains unchanged.

### Derived Evidence

`_apply_discount` is classified as:

```text
GOVERNED_EVIDENCE_TRANSFORMATION
```

It applies an owner-confirmed discount unit while preparing row-level evidence
for derived totals. It does not own final business-formula execution and is not
an alternative to `FormulaEngineService`.

### LIQ_002 and PYME_011 legacy evaluators

The direct arithmetic in:

- `service_1_liq_002_evaluator_v1.py`;
- `service_1_pyme_011_evaluator_v1.py`;

is classified as:

```text
NON_PRODUCT_ROOT_LEGACY_MATH
```

The canonical product root uses `GenericCapabilityEngine` for these capabilities;
these legacy evaluators are not modified in F1. Their future convergence is a
separate governed task and is not executed by this spec.

## F1 invariants

```text
ONE_MATH_AUTHORITY_SPEC = FROZEN
ALL_CURRENT_MATH_CLASSIFIED = YES
NO_BEHAVIOR_CHANGE = YES
BUSINESS_FORMULA_DUPLICATE_AUTHORITY = 0
KNOWN_AGGREGATION_DEBT = EXPLICITLY_DEFERRED_TO_F8
```

The F1 acceptance evidence must demonstrate:

1. GenericCapabilityEngine delegates AST evaluation.
2. LIQ_001 delegates `sold_vs_collected_gap`.
3. REN_001 remains delegated.
4. Existing representative outputs remain equivalent before/after the F1
   authority move.
5. No second productive math authority is introduced.

## Deferred work

F8 owns the future aggregation convergence. That phase may define the governed
aggregation runtime under `FormulaEngineService`; it must not be implemented or
anticipated by F1.

This document freezes the boundary. It does not authorize F2, F3, F4, F5, F6,
F7, F8, AnalysisPlan, or any new vertical capability.
