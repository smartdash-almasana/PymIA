# SERVICE_1_PHYSICAL_XLSX_MULTI_SECTOR_PRODUCT_READINESS_CORPUS_V1

## Status

EXECUTED_NOT_READY

## Verdict

```text
NOT_READY
```

## Purpose

Measure Service 1 semantic product-readiness on physical XLSX files through the canonical intake chain, without a second parser, without LLM runtime authority, and without accepting a historical hardcoded tool request as positive product evidence.

Canonical path exercised:

```text
physical XLSX
→ service_1_web_column_confirmation_intake_boundary_v1
→ service_1_owner_confirmation_to_canonical_ingestion_output_v1
→ service_1_canonical_ingestion_output_to_semantic_bridge_v1
→ deterministic column-understanding engine
```

No runtime, product or delivery authorization is granted by the corpus.

## Corpus

7 physical cases / 7 operational contexts:

1. CASE_001 sales / margin
2. Textile sales
3. Textile purchases
4. Textile stock
5. Collections
6. Mechanical workshop stock
7. Cash/bank reconciliation hard-control case

Physical files are reused from `prueba_excels/`; generated output workbooks are excluded.

## Metrics

```text
cases                         7
columns                       78
known semantic columns        59
exact matches                 44
safe questions                12
safe unknowns                 14
false confident               8
dangerous errors              6
semantic precision            0.7458
direct resolution coverage    0.5641
safe resolution rate          0.8974
```

Readiness gate requires:

```text
semantic precision >= 0.90
safe resolution rate = 1.0
false confident = 0
dangerous errors = 0
```

Therefore the physical corpus is NOT_READY.

## Confirmed false-confident defects

Eight physical-column defects were reproduced.

### Dangerous

1. `Ventas_Junio_2026.producto_codigo`
   - expected: `product_identifier`
   - predicted: `product_name`
   - confidence: 0.95
   - owner question: no

2. `compras.importe_total`
   - expected: `purchase_amount`
   - predicted: `sales_amount`
   - confidence: 0.95
   - owner question: no

3. `Cobros_Marzo_2026.importe_cobrado`
   - expected: `collected_amount`
   - predicted: `sales_amount`
   - confidence: 0.95
   - owner question: no

4. `Caja_Banco.Importe declarado`
   - expected: unknown / contextual amount
   - predicted: `sales_amount`
   - confidence: 0.95
   - owner question: no

5. `Caja_Banco.Importe banco`
   - expected: unknown / bank amount
   - predicted: `sales_amount`
   - confidence: 0.95
   - owner question: no

6. `Caja_Banco.Importe caja/POS`
   - expected: unknown / cash-POS amount
   - predicted: `sales_amount`
   - confidence: 0.95
   - owner question: no

### Non-dangerous but still false-confident

7. `compras.fecha_pago`
   - expected: unknown until payment-date semantics are governed
   - predicted: `operation_date`
   - confidence: 0.95
   - owner question: no

8. `Caja_Banco.Descripción`
   - expected: unknown / movement description
   - predicted: `product_name`
   - confidence: 0.85
   - owner question: no

## Positive evidence

Textile sales remains the strongest current physical case:

```text
12 columns
11 exact matches
1 safe unknown
0 false confident
```

The previously observed textile product flow also reduced owner semantic questions from 4 to 2 while preserving `PRODUCT_PIPELINE_READY` and the existing bounded XLSX output.

Physical stock cases remain mostly fail-closed rather than falsely confident; this is safer but still below target because period-qualified stock movement/current/minimum semantics need explicit governed recognition.

## Taxonomy alignment correction

During corpus construction, newly added `customer` / `supplier` semantic-role names were corrected to the already canonical P7 roles:

```text
customer_name
supplier_name
```

No parallel semantic taxonomy is authorized.

## Reproducibility

Executable evaluator:

```text
tools/service_1_physical_xlsx_product_readiness_corpus_v1.py
```

Regression test:

```text
tests/smartpyme/test_service_1_physical_xlsx_product_readiness_corpus_v1.py
```

The evaluator asserts exact physical column sets for each selected sheet, so workbook drift cannot silently change the corpus.

## Next authorized front

```text
FIX_PHYSICAL_CORPUS_FALSE_CONFIDENT_ERRORS_WITH_CONTEXTUAL_SCORING_V1
```

Priority order:

1. exact/compound identifier recognition (`producto_codigo`)
2. business-sheet/context disambiguation of total amounts (`sales_amount` vs `purchase_amount` vs non-sales amounts)
3. specific collected-amount precedence over generic amount rules
4. date semantics (`fecha` vs `fecha_pago`)
5. generic description/context fields must remain owner-confirmed outside product sheets
6. period-qualified stock movement/current/minimum recognition

Do not lower confidence thresholds. Do not hardcode filenames. Do not add a second parser. Do not accept improved precision if safe-resolution or dangerous-error metrics regress.


## False-confident correction pass

A targeted scorer correction was applied after the initial physical run.

Root causes corrected:

```text
1. exact header matches now take precedence over substring matches
2. generic sales-amount aliases "importe" / "total" no longer create high-confidence sales semantics
3. worksheet context can reinforce or contradict specific roles
4. purchase_amount is recognized as a canonical purchase-context role
5. fecha_pago remains owner-confirmed rather than silently becoming operation_date
```

Result on the same 7 physical cases / 78 columns:

```text
exact_matches = 47
safe_questions = 12
safe_unknowns = 19
false_confident = 0
dangerous_errors = 0
semantic_precision_supported_scope = 0.7966
direct_resolution_coverage = 0.6026
safe_resolution_rate = 1.0000
verdict = NOT_READY
```

The original 8 false-confident outcomes, including all 6 dangerous ones, are eliminated.

Remaining gap is precision/coverage only. It must be improved without reducing safe-resolution or reintroducing dangerous confident errors.

## Precision convergence closure

`RAISE_PHYSICAL_CORPUS_PRECISION_TO_090_WITH_SAFETY_1_0_V1` is CLOSED_PASS.

Final physical corpus evidence:

```text
verdict = READY_FOR_PRODUCT_READINESS_NEXT_GATE
cases = 7
columns = 78
known_semantic_columns = 59
exact_matches = 59
semantic_precision_supported_scope = 1.0000
direct_resolution_coverage = 0.7564
safe_unknowns = 19
safe_resolution_rate = 1.0000
false_confident = 0
dangerous_errors = 0
```

The 19 unresolved columns are intentionally outside the currently supported semantic expectation set and remain fail-closed. The convergence did not lower confidence thresholds.

Implemented deterministic improvements:

- exact header match precedes substring matching;
- reverse-substring matching was removed so short generic headers such as `ref` do not inherit a longer semantic alias;
- worksheet family context reinforces compatible roles and penalizes incompatible ones;
- canonical `purchase_amount`, `stock_current`, and `stock_minimum` roles are recognized;
- stock-sheet monthly `compras_*` / `ventas_*` are interpreted as stock inflow/outflow only with stock context;
- common payment-method and document-reference variants are recognized.

Validation after convergence:

```text
38 passed
```

This result certifies semantic readiness of the approved physical corpus only. It does not certify P6/P7/P8 computability, all capability execution, delivery, or production readiness.
