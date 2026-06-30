# SERVICE 1 — SYNTHETIC CONTROLLED CASE INSTANCE V1

## VERDICT

```text
SYNTHETIC_CONTROLLED_CASE_INSTANCE_DEFINED
```

## Methodological correction

For the current post-A→I stage, a controlled case does not require an external live client.

Canonical rule:

```text
controlled case = synthetic, well-enunciated, operationally plausible case
```

This document converts the previous synthetic rehearsal into a formal synthetic controlled case instance.

## Mode

```text
DOC_INSTANCE_ONLY
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

## Purpose

Define one canonical synthetic controlled Service 1 case instance with enough operational density to exercise the operator packet boundary without needing an external client or live files.

This is not a run.
This is not execution.
This is not delivery.

## Dependencies

```text
SERVICE_1_SYNTHETIC_OPERATOR_PACKET_REHEARSAL_V1.md
SERVICE_1_OPERATOR_PACKET_TEMPLATE_ACCEPTANCE_AUDIT_V1.md
SERVICE_1_OPERATOR_PACKET_FOR_REAL_CONTROLLED_CASE_V1.md
SERVICE_1_REAL_CONTROLLED_CASE_PRECHECK_GATE_V1.md
SERVICE_1_DOC_DRIFT_AND_NAMING_CLEANUP_V1.md
SERVICE_1_PHASE_I_CLOSEOUT_V1.md
docs/current/ACTIVE_ROADMAP.md
```

## Case identity

```text
case_ref: S1_SYNTHETIC_CONTROLLED_CASE_001
case_name: PyME Mayorista Alfa — Excel readiness and margin first-aid triage
case_type: SYNTHETIC_CONTROLLED_CASE
operator_ref: synthetic_operator_ref_001
tenant_ref: synthetic_tenant_wholesale_alfa
owner_ref: synthetic_owner_wholesale_alfa
packet_ref: synthetic_packet_wholesale_alfa_001
precheck_ref: synthetic_precheck_wholesale_alfa_001
```

## Synthetic PyME profile

```text
business_type: small wholesale distributor
team_size: 8
monthly_order_volume: medium
main_operational_pain: margin uncertainty and spreadsheet disorder
current_tools: spreadsheets exported from internal sales/admin process
owner_question: Which spreadsheet evidence is sufficient to prepare a first-aid margin/readiness triage without producing a final accounting result?
```

## Controlled scope

```text
service_family: Service 1 / Excel readiness and first-aid triage
allowed_focus:
  - spreadsheet structure review
  - declared column readiness
  - margin-related evidence sufficiency
  - missing evidence questions
  - operator packet completeness
explicitly_excluded:
  - final accounting result
  - final reconciliation
  - tax conclusion
  - automatic accounting entry
  - autonomous delivery
  - SaaS/API/UI
  - runtime execution
  - Servicio 2
  - Phase J
```

## Synthetic evidence inventory

Expected evidence categories:

```text
1. sales spreadsheet description
2. product/cost spreadsheet description
3. inventory spreadsheet description
4. owner business question
5. declared column list
6. missing data notes
7. operator observations
```

No live file is attached or ingested by this document.

## Synthetic columns expected

Sales spreadsheet expected columns:

```text
sale_date
sku
quantity
unit_price
discount
customer_segment
```

Cost spreadsheet expected columns:

```text
sku
supplier_ref
unit_cost
last_cost_update
purchase_batch
```

Inventory spreadsheet expected columns:

```text
sku
stock_units
warehouse_ref
minimum_stock
last_movement_date
```

## Known synthetic gaps

```text
- product names are not normalized across spreadsheets
- discount policy is not fully declared
- some cost updates may be stale
- customer segment may be incomplete
- inventory dates may not align with sales period
```

These gaps are intentional. They exist to exercise evidence sufficiency and operator review boundaries.

## Packet instance fields

```text
packet_ref: synthetic_packet_wholesale_alfa_001
case_ref: S1_SYNTHETIC_CONTROLLED_CASE_001
tenant_ref: synthetic_tenant_wholesale_alfa
owner_ref: synthetic_owner_wholesale_alfa
operator_ref: synthetic_operator_ref_001
precheck_result_ref: synthetic_precheck_wholesale_alfa_001
case_scope_ref: synthetic_scope_wholesale_alfa_001
evidence_plan_ref: synthetic_evidence_plan_wholesale_alfa_001
abort_policy_ref: synthetic_abort_policy_wholesale_alfa_001
review_plan_ref: synthetic_review_plan_wholesale_alfa_001
status: SYNTHETIC_CONTROLLED_CASE_INSTANCE_READY
```

## Operator checklist result

```text
precheck_ref_exists: YES
operator_ref_present: YES
scope_one_service_1_family_only: YES
synthetic_only: YES
evidence_inventory_defined: YES
known_gaps_defined: YES
abort_policy_defined: YES
review_plan_defined: YES
runtime_request_present: NO
cli_execution_request_present: NO
delivery_request_present: NO
publish_request_present: NO
notification_request_present: NO
service_2_scope_present: NO
phase_j_request_present: NO
```

Checklist verdict:

```text
SYNTHETIC_CASE_INSTANCE_CHECKLIST_PASS
```

## Abort policy

Abort if any of the following appears in the next front:

```text
- scope expands beyond Service 1
- live business files are introduced without explicit new approval
- CLI execution is requested
- runtime execution is requested
- owner delivery is requested
- final accounting or tax conclusion is requested
- Servicio 2 is introduced
- Phase J is introduced
- SaaS/API/UI or worker/storage/queue is introduced
```

## Expected outputs at this stage

Allowed outputs:

```text
- synthetic case statement
- synthetic packet instance fields
- expected evidence inventory
- known gaps
- checklist result
- abort policy
- review questions
```

Forbidden outputs:

```text
- computed diagnosis
- final report
- owner delivery packet
- spreadsheet output
- runtime result
- CLI result
- Servicio 2 result
```

## Review questions for next front

```text
1. Is the synthetic case operationally dense enough?
2. Are expected evidence categories clear?
3. Are known gaps useful for testing evidence sufficiency?
4. Does the scope remain Service 1 only?
5. Does the packet avoid execution by implication?
6. Are all execution flags still false?
```

## Final manifest

```text
manifest_version: service_1_synthetic_controlled_case_instance_v1
case_ref: S1_SYNTHETIC_CONTROLLED_CASE_001
packet_ref: synthetic_packet_wholesale_alfa_001
operator_ref: synthetic_operator_ref_001
synthetic_only: true
business_files_used: false
cli_executed: false
runtime_executed: false
delivery_executed: false
publish_executed: false
notification_executed: false
service_2_opened: false
phase_j_opened: false
status: SYNTHETIC_CONTROLLED_CASE_INSTANCE_READY
```

## Final declaration

```text
SERVICE_1_SYNTHETIC_CONTROLLED_CASE_INSTANCE_V1: PASS
SYNTHETIC_CONTROLLED_CASE_INSTANCE: READY
EXTERNAL_CLIENT_REQUIRED: NO
BUSINESS_FILES_USED: FALSE
CLI_EXECUTED: FALSE
RUNTIME_EXECUTED: FALSE
DELIVERY_EXECUTED: FALSE
SERVICE_2_OPENED: FALSE
PHASE_J_OPENED: FALSE
```

## Next allowed fronts

Choose explicitly:

```text
A. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_RUN_PREPARATION_V1
   - preparation only
   - still no CLI execution

B. SERVICE_1_SYNTHETIC_CONTROLLED_CASE_NEGATIVE_VARIANTS_V1
   - add blocked variants
   - still synthetic only

C. STOP_AND_DECIDE
```
