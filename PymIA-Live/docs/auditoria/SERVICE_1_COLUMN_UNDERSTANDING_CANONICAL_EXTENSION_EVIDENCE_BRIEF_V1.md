# SERVICE_1_COLUMN_UNDERSTANDING_CANONICAL_EXTENSION_EVIDENCE_BRIEF_V1

## Status

Documentary evidence brief. No runtime, no frontend wiring, no catalog mutation.

## Base

- Repository: `PymIA`
- Subproject: `PymIA-Live`
- Base commit: `c90fb53`
- Governing rule: `service_1_semantic_variable_catalog.v1.json` derives from unique `required_variables` in `formula_catalog.v1.json`.

## Problem

The column-understanding corpus still contains eight owner-confirmed concepts that do not have sufficient canonical support:

- `stock_inicial`
- `entradas`
- `salidas`
- `stock_final`
- `cliente`
- `medio_pago`
- `proveedor`
- `bonif`

The current engine correctly keeps them fail-closed. Directly inserting variables or semantic roles would violate the catalog derivation rule and create a second source of truth.

## Decision

No new variable, formula, semantic role, runtime binding, or frontend option may be introduced for these concepts until the corresponding evidence package is complete.

The valid sequence is:

```text
operational concept
→ business definition
→ evidence fields
→ formula or governed non-formula capability
→ required_variables
→ semantic variable catalog regeneration
→ column-understanding role
→ corpus evaluation
→ owner-question audit
→ integration decision
```

A column name alone is not evidence.

## Required evidence package

Every proposed canonical extension must include:

1. **Operational definition**
   - What the concept means in a PyME process.
   - What it explicitly does not mean.
   - Whether it is a stock, flow, identifier, counterparty, classification, rate, or currency amount.

2. **Source evidence**
   - Typical source document or spreadsheet.
   - Minimum fields required.
   - Whether the value is declared, calculated, reconciled, or physically verified.

3. **Temporal semantics**
   - Point-in-time or period flow.
   - Required date or period reference.
   - Whether opening and closing values are comparable.

4. **Unit and data type**
   - Quantity, currency, percentage, text identifier, or categorical value.
   - Required data type.

5. **Formula or capability relationship**
   - Existing formula reference, or
   - proposed formula with inputs and interpretation, or
   - explicit classification as a governed non-formula evidence field.

6. **Risk if wrong**
   - Diagnostic, reconciliation, stock, pricing, cash, or supplier consequence.

7. **Owner confirmation rule**
   - Conditions under which confirmation remains mandatory.
   - Allowed alternatives presented to the owner.

8. **Acceptance evidence**
   - Positive examples.
   - Ambiguous examples.
   - Negative examples.
   - Corpus cases proving fail-closed behavior.

## Concept-specific evidence requirements

### `stock_inicial`

Must prove:

- opening quantity at a defined period boundary;
- distinction from current stock, average stock, safety stock, available stock, and physical count;
- compatible unit by item/SKU;
- formula relationship only when opening stock is a required variable of a governed stock movement or reconciliation formula.

Current status: `PARTIAL_EVIDENCE`.

### `entradas`

Must prove:

- inbound stock movement quantity during a defined period;
- distinction between purchases, returns, production, transfers, and adjustments;
- sign convention and item identity;
- whether separate movement classes are required.

Current status: `BLOCKED_NEEDS_OPERATIONAL_TAXONOMY`.

### `salidas`

Must prove:

- outbound stock movement quantity during a defined period;
- distinction between sales, consumption, transfer, breakage, expiry, and adjustments;
- sign convention and item identity.

Current status: `BLOCKED_NEEDS_OPERATIONAL_TAXONOMY`.

### `stock_final`

Must prove:

- closing quantity at a defined period boundary;
- distinction from current physical stock and computed theoretical stock;
- reconciliation rule such as opening plus entries minus exits plus/minus adjustments;
- treatment of negative stock and missing movements.

Current status: `PARTIAL_EVIDENCE`.

### `cliente`

Must prove:

- counterparty identity rather than free-text description;
- whether a stable identifier is required;
- relationship to receivables, collections, revenue concentration, or document matching;
- privacy and normalization constraints.

Current status: `BLOCKED_NEEDS_COUNTERPARTY_CONTRACT`.

### `medio_pago`

Must prove:

- controlled payment-method classification;
- distinction from sales channel, bank account, collection platform, and settlement method;
- canonical vocabulary or normalization contract;
- relevance to cash reconciliation or collection analysis.

Current status: `BLOCKED_NEEDS_CLASSIFICATION_CONTRACT`.

### `proveedor`

Must prove:

- supplier/counterparty identity rather than product brand or free-text note;
- stable identifier requirements;
- relationship to purchases, payables, supplier concentration, or document matching;
- normalization and duplicate handling.

Current status: `BLOCKED_NEEDS_COUNTERPARTY_CONTRACT`.

### `bonif`

Must prove:

- whether the value is percentage, unit amount, line amount, or total discount;
- whether it applies before or after taxes;
- sign convention;
- relationship to list price, effective sale price, subtotal, and final amount.

Current status: `BLOCKED_NEEDS_PRICING_DISCOUNT_CONTRACT`.

## Prohibited shortcuts

- Do not add these names directly to `service_1_semantic_variable_catalog.v1.json`.
- Do not map them to the nearest existing variable by lexical similarity.
- Do not treat `average_stock` as equivalent to opening or closing stock.
- Do not treat `segment` as equivalent to payment method, customer, or supplier.
- Do not infer discount semantics from `bonif` without unit and tax context.
- Do not wire owner-facing frontend choices before the evidence package and corpus tests exist.

## Acceptance gate for a future extension

A concept may move from blocked/partial to extension candidate only when:

```text
operational_definition_complete = true
evidence_fields_complete = true
temporal_semantics_complete = true
unit_and_type_complete = true
formula_or_capability_contract_exists = true
risk_and_owner_confirmation_defined = true
positive_ambiguous_negative_tests_exist = true
runtime_authorized = false
frontend_wiring_authorized = false
```

Even after acceptance as a catalog candidate, runtime and frontend remain separately gated.

## Current verdict

```text
VERDICT: EVIDENCE_BRIEF_READY
CANONICAL_EXTENSION_AUTHORIZED: false
FORMULA_CATALOG_MUTATION_AUTHORIZED: false
VARIABLE_CATALOG_MUTATION_AUTHORIZED: false
ENGINE_MAPPING_EXTENSION_AUTHORIZED: false
FRONTEND_WIRING_AUTHORIZED: false
```

## Next methodological slice

Create one focused contract family at a time. Recommended first candidate:

```text
SERVICE_1_STOCK_MOVEMENT_SEMANTIC_CONTRACT_V1
```

It should define opening stock, inbound movements, outbound movements, closing stock, adjustments, period semantics, units, reconciliation identity, owner confirmation rules, and acceptance cases before any catalog mutation.