# SERVICE_1_STAGE2_ARCHITECTURAL_AUTHORITIES_V1

**Status:** `REVISED_PROPOSED_CANONICAL_AUTHORITIES_FOR_INDEPENDENT_AUDIT`
**Stage:** `STAGE_2_CONSOLIDATE_ARCHITECTURE_AND_CONTRACTS`  
**Implementation changes authorized:** `false`

## 1. Purpose

This document freezes target architectural authorities before implementation changes. It resolves the seven findings from the first independent audit without claiming that every target contract already exists in code.

```text
physical evidence is observed
semantic hypotheses are proposed
owner confirmation is evidence
P6 approves meaning only
P7 matches pathology, formula and capability
P8 decides computability and safety
computation consumes only approved governed input
```

No target type authorizes a parallel permanent pipeline. Existing contracts are evolved or projected into the frozen authorities, and replaced routes must be deleted in the same migration closure.

## 2. Frozen authority matrix

| Concept | Frozen authority | Current source | Decision |
|---|---|---|---|
| Region | `Service1RegionV1` target | canonical ingestion + normalized table provenance | Immutable bounded rectangular area in V1 |
| Column physical evidence | `Service1ColumnPhysicalEvidenceV1` target | profiling + column understanding inputs | Column observation only |
| Relational physical evidence | `Service1RegionRelationalEvidenceV1` target | deterministic multi-column identities | Region/column-set evidence only |
| Semantic hypothesis | `Service1ColumnUnderstandingHypothesisV1` | column understanding contract | Initial hypothesis authority |
| Binding candidate | `Service1ColumnSemanticCandidateV1` adapter-only | semantic bridge | Lossless projection, not second truth |
| Owner confirmation | `Service1OwnerConfirmationEventV1` target | owner loop + reinjection | Immutable scoped evidence |
| P6 approval | `Service1P6ApprovalDecisionV1` target | binding + reinjection | Meaning approval only |
| Grain | `Service1GrainV1` multidimensional target | `required_grain` + evaluator assumptions | Preserve all dimensions |
| Requirements | semantic requirement + normative projection | semantic requirements + `VariableRequirementV1` | No duplicate truth |
| Computation value | `Service1GovernedComputationValueV1` target | values + bindings + provenance | Provenance per value |
| Computation input | `Service1GovernedComputationInputV1` target | plans and bounded adapters | Primary governed package |

## 3. Region V1

`Service1RegionV1` identifies one bounded analyzable area:

```text
case_id
file_ref
workbook_ref
sheet_ref
region_ref
header_rows
first_data_row
last_data_row
column_refs
excluded_rows
region_shape
provenance
grain
```

V1 limits are explicit:

```text
V1_REGION_SHAPE = RECTANGULAR_CONTIGUOUS_COLUMNS
V1_DATA_ROWS = CONTIGUOUS_WITH_OPTIONAL_EXCLUDED_ROWS
V1_MULTI_REGION_SHEET = ALLOWED
V1_DISCONTIGUOUS_CELL_AREAS = BLOCKED
V1_MERGED_MULTIROW_HEADERS = ALLOWED_ONLY_WHEN_NORMALIZED_TO_HEADER_ROWS
```

A sheet is not automatically one region. Unsupported shapes fail closed before semantic interpretation.

## 4. Physical evidence

### 4.1 Column evidence

`Service1ColumnPhysicalEvidenceV1` contains only observed column evidence:

```text
region_ref
column_ref
normalized_header
observed_data_type
sample_values
null_ratio
cardinality
numeric_range
sign_profile
date_profile
neighbor_column_refs
provenance
```

### 4.2 Relational evidence

`Service1RegionRelationalEvidenceV1` represents deterministic multi-column or region evidence:

```text
region_ref
evidence_ref
evidence_kind
participating_column_refs
rows_evaluated
rows_matching
coverage_ratio
tolerance
result
contradicting_rows
provenance
```

Examples:

```text
quantity × unit_price ≈ line_total
subtotal + taxes - discount ≈ final_amount
collected_amount + accounts_receivable ≈ invoiced_amount
opening_stock + inbound - outbound + adjustments ≈ closing_stock
```

Semantic roles, confidence, owner answers, bindings and business results are prohibited in physical evidence.

## 5. Semantic hypothesis and candidate projection

`Service1ColumnUnderstandingHypothesisV1` remains the initial authority. Projection into `Service1ColumnSemanticCandidateV1` is adapter-only and must preserve without loss:

```text
semantic_role ↔ variable_name pair
score
supporting evidence references
contradicting evidence references
risk_if_wrong
owner_confirmation_required
region_ref
column_ref
```

Independent unpaired role and variable lists are not authoritative. A projection that cannot preserve pair identity fails closed.

## 6. Owner confirmation

`Service1OwnerConfirmationEventV1` is immutable evidence:

```text
case_id
file_ref
region_ref
sheet_ref
column_ref
question_ref
proposed_role
proposed_variable
owner_answer
confirmed_role or corrected_meaning
confirmation_scope
confirmed_by_owner = true
timestamp
provenance
```

It never authorizes runtime, tools, diagnosis or delivery. Reinjection consumes the event, not a boolean or free text alone.

## 7. P6, P7 and P8 separation

### P6 — Confirmed semantic binding

`Service1P6ApprovalDecisionV1` is the only meaning-approval authority.

```text
APPROVED
NEEDS_OWNER_CONFIRMATION
AMBIGUOUS
BLOCKED
```

P6 answers only whether a region/column-to-concept binding is semantically approved. It does not select formulas, evaluate requirements or authorize execution.

### P7 — Pathology, formula and capability matching

P7 consumes only P6 `APPROVED` bindings and selects governed requirements. Missing variables, unsupported formulas and pathology ambiguity belong here.

### P8 — Computability and safety

P8 verifies requirement satisfaction, unit/grain compatibility, complete provenance and safe execution. Only P8 produces an execution-eligible governed computation input.

Existing binding, reinjection and controlled-execution gates remain implementation components until migrated; none is independently the permanent P6 authority.

## 8. Multidimensional grain

`Service1GrainV1` is composed, not a flat enum:

```text
structural_scope:
  ROW | REGION | SHEET
business_entity_grain:
  TRANSACTION | LINE_ITEM | INVOICE | CUSTOMER | SUPPLIER | PRODUCT | ACCOUNT | NONE
temporal_grain:
  EVENT | DAY | WEEK | MONTH | QUARTER | YEAR | PERIOD | NONE
aggregation_grain:
  ATOMIC | GROUPED | AGGREGATED
```

Compatibility is evaluated dimension by dimension. Physical scope cannot substitute for business entity grain. Missing or incompatible required grain fails closed.

## 9. Normative requirements projection

`Service1FormulaVariableRequirementV1` is the semantic authority. `VariableRequirementV1` is a computation projection.

| Semantic field | Computation field or gate | Normative rule |
|---|---|---|
| `variable_name` | `name` | Exact identity |
| `required` | presence | Preserved |
| `accepted_semantic_roles` | P6 validation | Satisfied before projection |
| `accepted_data_types` | P8 validation | Satisfied before execution |
| `required_grain` | `Service1GrainV1` compatibility | Never discarded |
| `required_unit` | `unit` | Exact or governed conversion with provenance |
| `owner_confirmation_required` | P6 precondition | Resolved before approval |
| aggregation | `aggregation` | Explicit, never silently inferred |
| minimum/maximum | computation requirement | Preserved exactly |
| source capability | `source_capability_ref` | Preserved |
| source result key | `source_result_key` | Preserved |

Projection outcomes:

```text
PROJECTED
BLOCKED_MISSING_SEMANTIC_APPROVAL
BLOCKED_DATA_TYPE
BLOCKED_GRAIN
BLOCKED_UNIT
BLOCKED_UNSUPPORTED_AGGREGATION
```

No field disappears without an explicit prior gate and evidence reference.

## 10. Governed computation values and input

`Service1GovernedComputationValueV1` contains:

```text
variable_name
value
unit
source_grain
result_grain
source_region_ref
source_column_refs
source_row_refs or aggregation_evidence_ref
binding_ref
p6_approval_ref
owner_confirmation_ref, when applicable
transformation_history
provenance
```

Every value is independently traceable. Package provenance alone is insufficient.

`Service1GovernedComputationInputV1` contains:

```text
case_id
region_ref
capability_ref
pathology_code
formula_ref
p6_approval_refs
p7_match_ref
p8_computability_ref
values: tuple[Service1GovernedComputationValueV1, ...]
requirement_satisfaction
package_provenance
```

Raw columns, semantic candidates and unapproved bindings are prohibited. Engines consume this package directly or through temporary bounded adapters. No fourth computation model may be created.

## 11. Current module roles

```text
service_1_column_understanding_engine_contract_v1 = initial hypothesis authority
service_1_semantic_evidence_binding_contracts_v1 = retained binding contracts, not final P6
service_1_canonical_ingestion_output_to_semantic_bridge_v1 = adapter-only projection
service_1_owner_confirmation_reinjection_to_semantic_gate_v1 = current P6 component
service_1_semantic_bridge_to_controlled_execution_gate_v1 = current P8-adjacent component, not P6 authority
service_1_capability_contracts_v1 = current computation projection contracts
service_1_capability_registry_v1 = governed capability definitions
service_1_generic_capability_engine_v1 = productive root-reachable engine
service_1_product_pipeline_v1 = only productive composition root
```

## 12. Registry reconciliation

The following are operationally reachable and must later be reconciled in disposition metadata:

```text
service_1_generic_capability_engine_v1
service_1_capability_registry_v1
service_1_capability_contracts_v1
service_1_owner_confirmation_to_canonical_ingestion_output_v1
```

This is metadata correction, not architecture migration.

## 13. Mandatory migration sequence

### Package 1 — Region and physical evidence

```text
CURRENT = canonical ingestion + normalized table + profiling metadata
TARGET = Region + column and relational evidence
TEMPORARY_ADAPTER = canonical ingestion projection
ACCEPTANCE = real XLSX provenance, multi-region sheet, identity coverage/tolerance, fail-closed shape
DELETION = downstream semantic path consumes target evidence
ROLLBACK = remove targets/adapter; current ingestion unchanged
```

### Package 2 — Owner confirmation event

```text
CURRENT = question packets + answer maps + reinjection payloads
TARGET = OwnerConfirmationEvent
TEMPORARY_ADAPTER = UI/CLI answer to event
ACCEPTANCE = scoped immutable event, correction, replay, no permission flags
DELETION = reinjection consumes event only
ROLLBACK = restore prior projection
```

### Package 3 — P6 approval

```text
CURRENT = binding result + reinjection gate combination
TARGET = P6ApprovalDecision
TEMPORARY_ADAPTER = confirmed binding to P6 decision
ACCEPTANCE = P6-only states, no P7/P8 concerns, no computation bypass
DELETION = all P7 consumers require P6 APPROVED
ROLLBACK = retain current fail-closed gates
```

### Package 4 — Grain and requirements projection

```text
CURRENT = required_grain strings + VariableRequirement assumptions
TARGET = multidimensional Grain + normative projection
TEMPORARY_ADAPTER = semantic to generic requirement projection
ACCEPTANCE = dimension compatibility, unit/type preservation, blocked unsupported projection
DELETION = no productive path drops semantic fields
ROLLBACK = retain existing requirements without new execution
```

### Package 5 — Governed computation input

```text
CURRENT = plans + normalized evidence + generic/direct inputs
TARGET = governed values + governed input
TEMPORARY_ADAPTER = one bounded adapter per existing engine family
ACCEPTANCE = value provenance, P6/P7/P8 refs, deterministic replay
DELETION = selected first pathology consumes governed input
ROLLBACK = selected pathology returns to prior green path
```

### Packages 6 and 7 — First integrated migration and deletion

These form one indivisible closure:

```text
MIGRATE = one real pathology already supported by generic engine
COMPARE = old/new outputs on regression and adversarial evidence
REQUIRE = equal governed result or documented intended correction
DELETE = replaced route and obsolete temporary adapters
ROLLBACK = one commit before migration closure
```

No second pathology starts before one authority, green evidence and deletion of the replaced route.

## 14. Global acceptance gates

```text
exact path audit
git diff --check
focal and neighboring tests
no new productive root
no parallel permanent contract
no frontend changes
no safety branch integration
independent final audit
same-closure deletion when authority replacement completes
```

## 15. Prohibitions

```text
DO_NOT_CHANGE_IMPLEMENTATION_BEFORE_INDEPENDENT_AUDIT
DO_NOT_CREATE_PARALLEL_REGION_OR_EVIDENCE_TYPES
DO_NOT_CREATE_A_SECOND_P6_AUTHORITY
DO_NOT_MIX_P6_WITH_P7_OR_P8
DO_NOT_TREAT_OWNER_CONFIRMATION_AS_PERMISSION
DO_NOT_FLATTEN_GRAIN_DIMENSIONS
DO_NOT_DROP_REQUIREMENT_FIELDS_IN_PROJECTION
DO_NOT_DROP_VALUE_LEVEL_PROVENANCE
DO_NOT_LET_COMPUTATION_CONSUME_CANDIDATES
DO_NOT_OPEN_SECOND_MIGRATION_BEFORE_FIRST_CLOSURE
DO_NOT_INTEGRATE_SAFETY_BRANCHES
DO_NOT_TOUCH_FRONTEND
```

```text
DOCUMENT_STATUS = REVISED_PROPOSED_FOR_INDEPENDENT_AUDIT
IMPLEMENTATION_CHANGES_AUTHORIZED = false
NEXT_ACTION = AUDIT_REVISED_STAGE2_ARCHITECTURAL_AUTHORITIES_DOCUMENT
```
