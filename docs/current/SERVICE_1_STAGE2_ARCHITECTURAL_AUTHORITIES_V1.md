# SERVICE_1_STAGE2_ARCHITECTURAL_AUTHORITIES_V1

**Status:** `PROPOSED_CANONICAL_AUTHORITIES_FOR_INDEPENDENT_AUDIT`  
**Stage:** `STAGE_2_CONSOLIDATE_ARCHITECTURE_AND_CONTRACTS`  
**Implementation changes authorized:** `false`

## Purpose

This document resolves the seven architectural authorities left ambiguous by the Stage 2 read-only audit. It freezes target responsibilities and migration rules before implementation changes. It does not claim that every target contract already exists in code.

```text
physical evidence is observed
semantic hypotheses are proposed
owner confirmation is evidence
P6 approves semantic bindings
requirements govern computability
computation consumes only approved governed input
```

## Frozen authority matrix

| Concept | Frozen authority | Current source | Decision |
|---|---|---|---|
| Region | `Service1RegionV1` target contract | canonical ingestion output + normalized table provenance | One immutable region identity per bounded workbook area |
| Physical evidence | `Service1PhysicalEvidencePacketV1` target contract | ingestion profiling + column understanding inputs | Separate observation from semantic interpretation |
| Semantic hypothesis | `Service1ColumnUnderstandingHypothesisV1` | column understanding contract | Only initial hypothesis authority |
| Binding candidate | `Service1ColumnSemanticCandidateV1` as adapter-only input | semantic bridge | Lossless projection, not a second semantic authority |
| Owner confirmation | `Service1OwnerConfirmationEventV1` target contract | owner loop + reinjection | Immutable scoped evidence event, never permission |
| P6 approval | `Service1P6ApprovalDecisionV1` target contract | binding + reinjection + controlled gate | Single fail-closed approval authority |
| Grain | `Service1GrainV1` target value object | `required_grain` + evaluator assumptions | Grain survives through computation |
| Requirements | semantic requirement authority with governed computation projection | `Service1FormulaVariableRequirementV1` + `VariableRequirementV1` | No independent duplicate truth |
| Computation input | `Service1GovernedComputationInputV1` target contract | plans, generic inputs, specialized adapters | Primary input; adapters bounded |

## Region

`Service1RegionV1` identifies one bounded analyzable area.

```text
case_id
file_ref
workbook_ref
sheet_ref
region_ref
header_row
first_data_row
last_data_row
column_refs
provenance
grain
```

A sheet is not automatically one region. Every candidate, confirmation, binding and computation input references one immutable region.

## Physical evidence

`Service1PhysicalEvidencePacketV1` contains only observed file evidence:

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
neighbor_columns
row_identity_results
provenance
```

Semantic roles, confidence, owner answers, approved bindings and computed results are prohibited.

## Semantic hypothesis

`Service1ColumnUnderstandingHypothesisV1` remains the initial authority. Projection into `Service1ColumnSemanticCandidateV1` must preserve the explicit `semantic_role ↔ variable_name` pair, score, evidence references, contradictions, risk and confirmation requirement. Separate unpaired role and variable lists are not authoritative.

## Owner confirmation

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

It never authorizes runtime, tools or delivery. Reinjection consumes the event, not a boolean.

## P6 approval

`Service1P6ApprovalDecisionV1` is the single confirmed-binding authority.

```text
APPROVED
NEEDS_OWNER_CONFIRMATION
NEEDS_REQUIREMENTS
AMBIGUOUS
BLOCKED
```

Only `APPROVED` produces governed computation input. Existing gates remain implementation components until migration; none is independently the permanent P6 authority.

## Grain

`Service1GrainV1` governs:

```text
ROW
TRANSACTION
LINE_ITEM
INVOICE
CUSTOMER
SUPPLIER
PRODUCT
ACCOUNT
PERIOD
REGION
SHEET
```

Grain is explicit, preserved into computation, and incompatible grains fail closed.

## Requirements

`Service1FormulaVariableRequirementV1` is the semantic requirement authority. `VariableRequirementV1` is a computation projection, not separate truth. Projection preserves or resolves variable, required flag, semantic roles, data types, grain, unit, owner confirmation, aggregation, numeric domain and source capability references.

## Computation input

`Service1GovernedComputationInputV1` is the target primary input:

```text
case_id
region_ref
capability_ref
pathology_code
formula_ref
p6_approval_ref
approved_bindings
normalized_values
source_grain
result_grain
units
requirement_satisfaction
provenance
```

Raw columns and semantic candidates are prohibited. Generic and specialized engines consume it directly or through bounded adapters. No fourth computation model may be created.

## Current module roles

```text
service_1_column_understanding_engine_contract_v1 = initial hypothesis authority
service_1_semantic_evidence_binding_contracts_v1 = retained binding contracts, not final P6
service_1_canonical_ingestion_output_to_semantic_bridge_v1 = adapter-only projection
service_1_owner_confirmation_reinjection_to_semantic_gate_v1 = P6 implementation component
service_1_semantic_bridge_to_controlled_execution_gate_v1 = current fail-closed component, not permanent approval authority
service_1_capability_contracts_v1 = computation projection contracts
service_1_capability_registry_v1 = governed capability definitions
service_1_generic_capability_engine_v1 = productive root-reachable engine
service_1_product_pipeline_v1 = only productive composition root
```

## Registry reconciliation

These modules are operationally reachable and must later be reconciled in disposition metadata:

```text
service_1_generic_capability_engine_v1
service_1_capability_registry_v1
service_1_capability_contracts_v1
service_1_owner_confirmation_to_canonical_ingestion_output_v1
```

No registry change is authorized before independent audit.

## Prohibitions

```text
DO_NOT_CHANGE_IMPLEMENTATION_BEFORE_INDEPENDENT_AUDIT
DO_NOT_CREATE_PARALLEL_REGION_OR_EVIDENCE_TYPES
DO_NOT_CREATE_A_SECOND_P6_AUTHORITY
DO_NOT_TREAT_OWNER_CONFIRMATION_AS_PERMISSION
DO_NOT_DROP_GRAIN_BEFORE_COMPUTATION
DO_NOT_LET_COMPUTATION_CONSUME_CANDIDATES
DO_NOT_INTEGRATE_SAFETY_BRANCHES
DO_NOT_TOUCH_FRONTEND
```

```text
DOCUMENT_STATUS = PROPOSED_FOR_INDEPENDENT_AUDIT
IMPLEMENTATION_CHANGES_AUTHORIZED = false
NEXT_ACTION = AUDIT_STAGE2_ARCHITECTURAL_AUTHORITIES_DOCUMENT
```
