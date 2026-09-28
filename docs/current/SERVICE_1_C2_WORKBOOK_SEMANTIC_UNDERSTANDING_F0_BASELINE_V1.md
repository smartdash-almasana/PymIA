# SERVICE 1 — C2 Workbook Semantic Understanding — F0 Baseline

STATUS: EVIDENCE / NON_NORMATIVE
CHANGE_SCOPE: F0_FREEZE_AND_BASELINE
ACTIVE_CHANGE_CONTRACT: NOP3-S1-003

## Productive path observed

`service_1_product_pipeline_v1.py`
→ `run_service_1_assisted_semantic_initial_v1(...)`
→ semantic provider
→ semantic proposal validator
→ owner semantic dialogue
→ owner reentry / confirmed bindings

## Frozen perimeter for this refactor

Do not modify in F1–F8 unless a causal blocker is demonstrated:
- canonical XLSX ingestion/parser
- Product Root identity
- deterministic mathematics
- delivery/result adapters
- tenant isolation rules
- owner-confirmation authority
- join/cardinality authority

## Baseline product defect — real workshop workbook

Workbook: `prueba_excels/taller_mecanico_lubricar_srl.xlsx`

Observed incorrect owner-facing interpretations include:
- `orden_id` rendered as `prestación del servicio por evento` instead of preserving identity as an order/work-order identifier.
- `costo_mano_obra` rendered as `costo por unidad` instead of preserving the business object `mano de obra`.
- prior lexical contamination interpreted `horas_mano_obra`, `valor_hora` and `costo_hora_real` as operation-time concepts.
- the owner dialogue can still expose many column-level confirmations instead of first presenting a coherent business model of the workbook.

## Golden business expectations for the workshop case

Before owner dialogue, C2 must be able to form a coherent hypothesis equivalent to:
- `ORDENES_TRABAJO`: work-order/service-delivery table, one business event/order per row unless evidence says otherwise.
- `PRODUCTOS_STOCK`: product/catalog/inventory context with costs, prices and stock levels.
- `CLIENTES`: customer context with commercial/payment conditions.

Minimum column semantics:
- `orden_id`: identifier of work order.
- `horas_mano_obra`: duration of labor.
- `valor_hora`: hourly labor price/rate; not event time.
- `costo_hora_real`: real hourly labor cost; not event time.
- `costo_mano_obra`: cost of labor; not generic unit cost.
- `ingreso_mano_obra`: labor revenue.
- `margen_mano_obra`: labor margin.

## Forbidden regression examples

The following owner-facing meanings are product FAIL:
- `orden_id` → `prestación del servicio por evento`
- `costo_mano_obra` → `costo por unidad`
- `horas_mano_obra` → `hora de la operación`
- `valor_hora` → `hora de la operación`
- `costo_hora_real` → `hora de la operación`

## Existing semantic knowledge discovered during F0

A repository glossary exists at:
- `docs/contracts/scn/GLOSSARY.md`

Its suitability as LLM retrieval context has not yet been evaluated. That belongs to the later knowledge/glossary phase and is not assumed in F0.

## F0 exit condition

PASS requires:
1. productive path identified;
2. workshop defect fixed as durable evidence/oracle;
3. frozen perimeter explicit;
4. no claim that the refactor itself is complete.
