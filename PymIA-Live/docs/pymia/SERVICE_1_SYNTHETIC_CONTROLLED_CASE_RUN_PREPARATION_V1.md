# SERVICE 1 — SYNTHETIC CONTROLLED CASE RUN PREPARATION V1

## VERDICT

```text
SYNTHETIC_CONTROLLED_CASE_RUN_PREPARATION_DEFINED
```

## Mode

```text
DOC_PREPARATION_ONLY
SYNTHETIC_ONLY
NO_EXTERNAL_CLIENT
NO_BUSINESS_FILES
NO_CLI_EXECUTION
NO_RUNTIME
NO_DATA_PROCESSING
NO_DELIVERY
NO_PUBLISH
NO_NOTIFICATION
NO_PHASE_J
NO_SAAS_API_UI
NO_WORKER_STORAGE_QUEUE
NO_SERVICE_2
```

## Boundary rule

```text
Run preparation ≠ run execution.
Prepared inputs ≠ processed data.
Prepared command plan ≠ executed command.
Expected artifacts ≠ produced artifacts.
Review plan ≠ owner delivery.
```

This document prepares a possible future supervised synthetic run over the canonical synthetic controlled case.

It does not execute anything.
It does not create output artifacts.
It does not invoke CLI.
It does not invoke runtime.
It does not deliver anything.

## Dependency

```text
SERVICE_1_SYNTHETIC_CONTROLLED_CASE_INSTANCE_V1.md
SERVICE_1_SYNTHETIC_OPERATOR_PACKET_REHEARSAL_V1.md
SERVICE_1_OPERATOR_PACKET_TEMPLATE_ACCEPTANCE_AUDIT_V1.md
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1.md
SERVICE_1_REAL_CONTROLLED_CASE_PRECHECK_GATE_V1.md
SERVICE_1_PHASE_I_CLOSEOUT_V1.md
docs/current/ACTIVE_ROADMAP.md
```

## Case prepared

```text
case_ref: S1_SYNTHETIC_CONTROLLED_CASE_001
case_name: PyME Mayorista Alfa — Excel readiness and margin first-aid triage
case_type: SYNTHETIC_CONTROLLED_CASE
operator_ref: synthetic_operator_ref_001
packet_ref: synthetic_packet_wholesale_alfa_001
```

## Preparation objective

Prepare the minimum safe run plan needed to later decide whether a supervised synthetic run could be requested.

The preparation covers:

```text
- input readiness
- evidence category readiness
- column expectation readiness
- gap awareness
- operator checklist readiness
- abort policy readiness
- expected artifact plan
- forbidden action confirmation
```

## Prepared synthetic inputs

```text
input_set_ref: synthetic_run_input_set_wholesale_alfa_001
input_mode: synthetic_descriptions_only
business_files_used: false
external_client_required: false
```

Synthetic input groups:

```text
1. sales spreadsheet description
2. product/cost spreadsheet description
3. inventory spreadsheet description
4. owner business question
5. declared column list
6. known gap list
7. operator observations
```

No spreadsheet file is created or processed by this document.

## Prepared column expectations

```text
sales_columns_expected:
  - sale_date
  - sku
  - quantity
  - unit_price
  - discount
  - customer_segment

cost_columns_expected:
  - sku
  - supplier_ref
  - unit_cost
  - last_cost_update
  - purchase_batch

inventory_columns_expected:
  - sku
  - stock_units
  - warehouse_ref
  - minimum_stock
  - last_movement_date
```

## Prepared known gaps

```text
- product names are not normalized across spreadsheets
- discount policy is not fully declared
- some cost updates may be stale
- customer segment may be incomplete
- inventory dates may not align with sales period
```

These gaps are part of the synthetic preparation. They are not resolved here.

## Pre-run checklist

```text
case_ref_exists: YES
case_is_synthetic: YES
operator_ref_exists: YES
packet_ref_exists: YES
scope_is_service_1_only: YES
evidence_categories_defined: YES
column_expectations_defined: YES
known_gaps_defined: YES
abort_policy_defined: YES
expected_artifact_plan_defined: YES
business_files_used: FALSE
cli_execution_requested: FALSE
runtime_requested: FALSE
data_processing_requested: FALSE
delivery_requested: FALSE
publish_requested: FALSE
notification_requested: FALSE
service_2_requested: FALSE
phase_j_requested: FALSE
```

Pre-run checklist verdict:

```text
PRE_RUN_PREPARATION_CHECKLIST_PASS
```

## Command boundary

Allowed at this stage:

```text
- describe possible future command intent
- list required synthetic inputs
- list expected artifact names
- define abort checks
- define review questions
```

Forbidden at this stage:

```text
- execute CLI
- run scripts
- generate files from pipeline
- process spreadsheet data
- invoke runtime
- create delivery packet
- publish or notify
```

No concrete executable command is authorized by this document.

## Expected artifact plan

If a future supervised synthetic run is explicitly approved, expected artifacts may include:

```text
- synthetic readiness report
- synthetic evidence sufficiency notes
- synthetic missing evidence questions
- synthetic operator observation note
- synthetic manifest
```

Forbidden expected artifacts:

```text
- final owner delivery
- final accounting report
- final reconciliation
- tax conclusion
- production runtime result
- Servicio 2 result
```

## Abort policy for run preparation

Abort preparation if:

```text
- scope expands beyond Service 1
- business files are introduced
- CLI execution is requested
- runtime execution is requested
- data processing is requested
- delivery/publish/notification is requested
- final accounting/tax conclusion is requested
- Servicio 2 appears
- Phase J appears
- SaaS/API/UI/worker/storage/queue appears
```

## Review questions before any future run request

```text
1. Is the case still synthetic?
2. Is scope still Service 1 only?
3. Are all inputs descriptions rather than business files?
4. Are expected columns clear enough?
5. Are known gaps useful for testing evidence sufficiency?
6. Is there any hidden request to execute CLI?
7. Is there any hidden delivery expectation?
8. Is Servicio 2 absent?
9. Is Phase J absent?
10. Should the future front be blocked instead of opened?
```

## Preparation manifest

```text
manifest_version: service_1_synthetic_controlled_case_run_preparation_v1
case_ref: S1_SYNTHETIC_CONTROLLED_CASE_001
packet_ref: synthetic_packet_wholesale_alfa_001
operator_ref: synthetic_operator_ref_001
input_set_ref: synthetic_run_input_set_wholesale_alfa_001
synthetic_only: true
business_files_used: false
cli_executed: false
runtime_executed: false
data_processed: false
delivery_executed: false
publish_executed: false
notification_executed: false
service_2_opened: false
phase_j_opened: false
status: SYNTHETIC_RUN_PREPARATION_READY
```

## Final declaration

```text
SERVICE_1_SYNTHETIC_CONTROLLED_CASE_RUN_PREPARATION_V1: PASS
SYNTHETIC_RUN_PREPARATION: READY
SYNTHETIC_CONTROLLED_CASE: READY
BUSINESS_FILES_USED: FALSE
CLI_EXECUTED: FALSE
RUNTIME_EXECUTED: FALSE
DATA_PROCESSED: FALSE
DELIVERY_EXECUTED: FALSE
SERVICE_2_OPENED: FALSE
PHASE_J_OPENED: FALSE
```

## Next allowed fronts

Choose explicitly:

```text
A. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_SUPERVISED_RUN_REQUEST_V1
   - request model only
   - still no CLI execution

B. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_NEGATIVE_VARIANTS_V1
   - blocked variants
   - still synthetic only

C. STOP_AND_DECIDE
```
