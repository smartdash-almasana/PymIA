# SERVICE_1_CONTROLLED_PRODUCT_READINESS_CORPUS_V1

## Status

EXECUTED_NOT_READY

## Purpose

Measure current Service 1 product readiness after Stage 2 without changing runtime architecture.

## Corpus lanes

### Lane A — semantic understanding corpus

Canonical source:

`service_1_column_understanding_corpus_evaluation_v1`

Coverage:

- 6 PyME-like cases
- 38 columns
- sales
- discounts/taxes
- stock
- collections
- purchases/costs
- deliberately ambiguous columns

Acceptance target:

```text
exact_match_rate >= 0.90
safe_resolution_rate = 1.00
dangerous_errors = 0
false_confident = 0
missed_questions = 0
```

Observed run:

```text
cases = 6
columns = 38
exact_matches = 22
safe_questions = 16
safe_unknowns = 0
false_confident = 0
missed_questions = 0
dangerous_errors = 0
exact_match_rate = 0.5789
safe_resolution_rate = 1.0
verdict = READY_WITH_FIXES
```

Interpretation: safety is correct; precision is insufficient for product readiness.

### Lane B — physical XLSX canonical product-path positive case

Case:

```text
S1-PRC-PHYSICAL-001
fixture = prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
sheet = ventas
runner = scripts/run_service_1_pilot_008_textil_completa.py
```

Observed current run:

```text
first_pass.status = NEEDS_OWNER_CONFIRMATION
owner_questions_count = 4
tools_executed_before_confirmation = false
final_pass.status = PRODUCT_PIPELINE_READY
semantic_bindings_confirmed = true
executed_tool_refs = [precio_margen_basico]
xlsx_outputs = [first_aid_001_precio_margen_basico.xlsx]
```

This is admitted as a positive controlled case because sales data and requested margin computation are directionally coherent.

### Lane C — historical negative-control artifact

Case:

```text
S1-PRC-NEGATIVE-001
fixture = prueba_excels/fabrica_industrial_compleja.xlsx
sheet = PRODUCCION
runner = scripts/run_service_1_pilot_005_fabrica_industrial.py
```

Observed current run:

```text
first_pass.status = NEEDS_OWNER_CONFIRMATION
owner_questions_count = 7
final_pass.status = PRODUCT_PIPELINE_READY
executed_tool_refs = [precio_margen_basico]
```

The runner itself hardcodes `precio_margen_basico` with literal price/cost inputs. Therefore this case MUST NOT be used as positive product-readiness evidence for production semantics. It is retained as negative control proving that historical pilot success cannot be equated with current product relevance.

## Current verdict

```text
PRODUCT_READINESS = NOT_READY
ARCHITECTURE_BLOCKER = false
SAFETY_BLOCKER = false
SEMANTIC_PRECISION_BLOCKER = true
PHYSICAL_POSITIVE_CASES = 1
NEGATIVE_CONTROL_CASES = 1
```

Reasons:

1. exact semantic precision is 0.5789 versus required >=0.90;
2. only one current physical XLSX case is admissible as positive product-readiness evidence;
3. historical pilots that execute explicit unrelated tool requests cannot certify product relevance;
4. safe-resolution remains 1.0 and dangerous confident errors remain zero, so precision can be improved without weakening fail-closed behavior.

## Required next corpus expansion

Add physical XLSX cases with explicit business intent and capability alignment for at least:

- sales/margin;
- collections/liquidity;
- stock;
- purchases/cost;
- one deliberately unsupported/ambiguous case that must block safely.

Each positive physical case must record:

```text
business_intent
fixture
sheet
requested_capability
required_variables
owner_questions_count
owner_answer_source
P6 status
P7 requirement status
P8 computability status
execution status
bounded outcome
delivery status
```

A case is not product evidence merely because the pipeline returns READY.

## Next authorized action

```text
EXPAND_SEMANTIC_CATALOG_AND_CORPUS_TO_090_WITHOUT_REDUCING_SAFETY
```

No SaaS/API/autonomy work is authorized by this corpus run.


## Semantic expansion checkpoint — 2026-07-27

The deterministic column-understanding catalog was expanded for high-value, bounded meanings already supported by the Service 1 domain vocabulary:

- list price;
- discount/bonification candidate;
- subtotal;
- customer;
- supplier;
- payment method;
- opening stock;
- stock inflow;
- stock outflow;
- closing stock.

Dangerous/ambiguous commercial fields such as list price, subtotal and discount remain eligible for owner confirmation even when the semantic hypothesis is correct. Generic headers `x1`, `monto`, `valor`, `ref`, `concepto`, and `obs` remain fail-closed.

Current controlled corpus result:

```text
cases = 6
columns = 38
exact semantic hypotheses = 32
intentional unknown negatives = 6
supported-scope semantic precision = 32/32 = 1.0000
direct-resolution coverage = 32/38 = 0.8421
safe-resolution rate = 1.0000
false confident = 0
missed questions = 0
dangerous errors = 0
```

The historical `exact_match_rate` across all 38 columns is retained as direct-resolution coverage. It must not be used as semantic precision because the denominator includes deliberate unknown negative controls.

Physical XLSX control (`la_textil_cosida_srl_mar_abr_may_2026.xlsx`, sheet `ventas`) improved from 4 owner questions to 2 while preserving fail-closed execution:

```text
before: cliente, descuento_pct, medio_cobro, plazo_cobro_dias
now:    descuento_pct, plazo_cobro_dias
final status: PRODUCT_PIPELINE_READY
executed tool: precio_margen_basico
```

Validation after expansion:

```text
34 passed
```

Next evidence front:

```text
BUILD_PHYSICAL_XLSX_MULTI_SECTOR_PRODUCT_READINESS_CORPUS_V1
```
