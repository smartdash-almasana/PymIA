# SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_MODULE_INVENTORY_V1

**Status:** CANONICAL_I1_INVENTORY  
**Method:** `SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1`  
**Base:** `8704aea`  
**Purpose:** select one productive implementation per stage P0–P10 and freeze competing lanes.

---

## 1. Verdict

```text
VERDICT: PARTIAL_BUT_INTEGRABLE
ONE_COMPOSITION_ROOT_EXISTS: false
PRODUCTIVE_COMPONENTS_EXIST: true
DUPLICATE_BOUNDARIES_EXIST: true
NEXT_STEP: I2_COMPOSITION_ROOT_CONTRACT
```

Servicio 1 already contains enough implementation to build one deterministic end-to-end semantic pipeline. The main gap is composition and semantic correction round-trip, not another parser, mapper, gate family or catalog wrapper.

---

## 2. Selection rules

A module is selected only when it:

- performs a real stage responsibility;
- has focal tests or repository evidence;
- can be called deterministically;
- preserves source provenance;
- does not silently authorize generic runtime autonomy;
- does not duplicate a selected responsibility.

Statuses:

```text
SELECTED       = canonical implementation for the stage
SELECTED_PARTIAL = canonical base, but missing behavior must be completed in place
ADAPTER_ONLY   = retained only at a real boundary
ABSORB         = logic may be consumed, but module must not become another pipeline stage
FREEZE         = historical/safety evidence; no further downstream chain
REJECT         = not part of the canonical composition root
```

---

## 3. Canonical module map P0–P10

### P0 — File intake

**Selected**

```text
PymIA-Live/pymia/smartpyme/file_intake_v1.py
```

**Boundary support**

```text
PymIA-Live/pymia/smartpyme/file_intake_taskspec_boundary_v1.py
```

**Decision:** `SELECTED`

**Reason:** stable file/case metadata boundary; does not need to understand workbook semantics.

**Not selected as core**

```text
service_1_saas_file_intake_api_v1.py
```

This is an external/application adapter, not the semantic pipeline core.

---

### P1 — Canonical XLSX ingestion

**Selected ingestion implementation**

```text
PymIA-Live/tools/document_ingestion.py
```

**Selected boundary adapter**

```text
PymIA-Live/pymia/smartpyme/service_1_document_ingestion_to_xlsx_runtime_bridge_adapter_v1.py
```

**Selected semantic handoff**

```text
PymIA-Live/pymia/smartpyme/service_1_canonical_ingestion_output_to_semantic_bridge_v1.py
```

**Decision:** `SELECTED + ADAPTER_ONLY`

**Rule:** no new XLSX parser. `excel_lab_ingestion_v1.py` may remain for its existing domain usage but is not a second canonical ingestion authority.

---

### P2 — Structural and data profiling

**Selected base**

```text
PymIA-Live/pymia/smartpyme/service_1_column_understanding_engine_v1.py
```

**Contract**

```text
service_1_column_understanding_engine_contract_v1.py
```

**Decision:** `SELECTED_PARTIAL`

**Certified existing signals**

- header normalization;
- inferred type;
- sample values;
- sheet and neighboring-column context;
- evidence and counterevidence;
- confidence and owner-confirmation requirement.

**Missing in the selected implementation**

- governed cardinality profile;
- null ratio;
- uniqueness ratio;
- numeric sign/range profile;
- categorical vocabulary profile;
- row-level identity coverage/tolerance;
- explicit profile packet reusable by P3/P4.

**Action:** extend this selected lane or add one tightly scoped profiler consumed by it. Do not create a competing semantic engine.

---

### P3 — Semantic candidate generation

**Selected**

```text
PymIA-Live/pymia/smartpyme/service_1_column_understanding_engine_v1.py
```

**Catalog sources retained**

```text
service_1_semantic_catalog_loader_v1.py
service_1_semantic_concept_catalog_contract_v1.py
```

**Decision:** `SELECTED_PARTIAL`

The column-understanding engine is the only candidate resolver. The older `service_1_column_semantic_mapper_v1.py` may be read for compatibility and regression, but must not remain a parallel semantic authority.

**Disposition of mapper:** `ABSORB/FREEZE`

---

### P4 — Contextual evidence scoring

**Selected base**

```text
service_1_column_understanding_engine_v1.py
```

**Domain evidence plugin retained**

```text
service_1_stock_movement_semantic_contract_v1.py
service_1_stock_movement_evidence_packet_v1.py
```

**Decision:** `SELECTED_PARTIAL`

**Missing behavior**

- whole-sheet candidate consistency;
- co-column graph scoring;
- row-identity validators;
- deterministic contradiction aggregation;
- minimum coverage and numeric tolerance policy.

These must be implemented behind the selected resolver, not through another top-level resolver chain.

---

### P5 — Owner confirmation loop

**Selected owner-facing projection**

```text
service_1_column_understanding_owner_question_adapter_v1.py
```

**Selected loop packet**

```text
service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1.py
```

**Selected reentry connector**

```text
service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py
```

**Decision:** `SELECTED_PARTIAL`

**Critical defect to repair in place**

Current reinjection can clear `owner_confirmation_required` and preserve an existing role. It does not provide a governed correction path for an owner who says the proposed role is wrong.

Required structured answer actions:

```text
CONFIRM_EXISTING_ROLE
CORRECT_TO_CANONICAL_ROLE
DECLARE_UNCATALOGED_MEANING
REJECT_COLUMN_FOR_CURRENT_CAPABILITY
```

Free text alone cannot clear the semantic gate.

**Historical owner-semantic modules outside `PymIA-Live`**

```text
pymia/contracts/owner_semantic_confirmation.py
pymia/smartpyme/owner_confirmed_semantic_request_flow.py
related checkpoints and TaskSpecs
```

Disposition: `EVIDENCE_ONLY`. They inform invariants but are not a second productive loop.

---

### P6 — Confirmed semantic binding

**Selected authority**

```text
service_1_semantic_evidence_binding_contracts_v1.py
service_1_semantic_evidence_binding_engine_v1.py
```

**Decision:** `SELECTED`

This is the only confirmed-binding authority.

**Required integration rule**

The P5 correction result must enter this engine as governed structured evidence. No adapter may mark a role confirmed solely by toggling a boolean.

**States standardized by composition root**

```text
CONFIRMED
PROVISIONAL
NEEDS_OWNER_CONFIRMATION
CONFLICTING_EVIDENCE
BLOCKED
```

---

### P7 — Pathology / formula / capability matching

**Selected catalog loader**

```text
service_1_semantic_catalog_loader_v1.py
```

**Selected governed binding boundary**

```text
service_1_runtime_catalog_binding_contract_v1.py
service_1_runtime_catalog_binding_adapter_v1.py
```

**Selected semantic handoff logic**

```text
service_1_runtime_catalog_to_semantic_binding_handoff_v1.py
```

**Decision:** `ABSORB INTO P7`

These modules are not three additional pipeline stages. The composition root calls them as one catalog/capability-matching responsibility.

**Concept model**

```text
service_1_semantic_concept_catalog_contract_v1.py
```

Retained as the governed distinction between measures, identifiers, dimensions, classifications and temporal concepts.

**Candidate/readiness wrappers**

```text
service_1_semantic_concept_catalog_candidate_v1.py
service_1_semantic_concept_catalog_readiness_gate_v1.py
```

Disposition: `FREEZE`. Evidence useful; no further wrapper chain.

---

### P8 — Computability and safety gate

**Selected base**

```text
service_1_pipeline_readiness_gate_v1.py
```

**Controlled execution checks to absorb**

```text
service_1_semantic_bridge_to_controlled_execution_gate_v1.py
service_1_pipeline_request_execution_gate_v1.py
```

**Decision:** `SELECTED_PARTIAL + ABSORB`

The final architecture has one computability gate. Existing checks may be reused internally, but the composition root exposes one result vocabulary:

```text
READY_FOR_COMPUTATION
NEEDS_OWNER_CONFIRMATION
NEEDS_EVIDENCE
CONFLICTING_EVIDENCE
BLOCKED_BY_POLICY
UNSUPPORTED_CAPABILITY
```

No generic `runtime_authorized` flag is required to describe a specific allowed deterministic computation.

---

### P9 — Deterministic tool execution

**Selected execution pipeline**

```text
service_1_pipeline_v1.py
```

**Decision:** `SELECTED`

It already:

- accepts explicit allowlisted tool requests;
- executes deterministic First Aid tools;
- does not select tools itself;
- delegates delivery.

**Initial supported tool family**

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
gastos_triage
proveedores_precio_variacion_triage
```

**Rejected as canonical core**

```text
service_1_autonomous_pipeline_runner_v1.py
service_1_saas_job_to_pipeline_request_adapter_v1.py
```

They may remain external/infrastructure experiments but do not define the semantic production core.

---

### P10 — QA, delivery policy and file package

**Selected execution-to-delivery flow**

```text
service_1_manual_first_aid_delivery_flow_v1.py
```

**Selected general XLSX writer**

```text
service_1_xlsx_delivery_v1.py
```

**Selected QA gate**

```text
service_1_qa_delivery_gate_v1.py
```

**Selected policy guard**

```text
service_1_pathology_finding_delivery_policy_guard_v1.py
```

**Selected owner package / manifest responsibilities**

```text
service_1_owner_delivery_package_v1.py
service_1_delivery_manifest_audit_contract_v1.py
service_1_case_delivery_folder_v1.py
```

**Decision:** `SELECTED_PARTIAL`

The composition root must expose one delivery result while these remain internal implementation modules. Delivery may not reinterpret uncertain semantics.

---

## 4. Frozen parallel chains

The following family is frozen as safety evidence and must not receive another downstream stage:

```text
service_1_semantic_binding_activation_v1.py
service_1_semantic_binding_execution_harness_v1.py
service_1_semantic_binding_bounded_invocation_v1.py
service_1_bounded_semantic_engine_invocation_port_v1.py
service_1_bounded_semantic_engine_contract_v1.py
service_1_bounded_semantic_engine_implementation_v1.py
```

Reason:

```text
they prove fail-closed boundaries but do not replace the required application composition root
```

They may be used as regression evidence or mined for guards. They are not the productive P0–P10 chain.

---

## 5. Duplicate authority prohibitions

From this inventory onward:

```text
ONE_XLSX_INGESTION_AUTHORITY = true
ONE_SEMANTIC_CANDIDATE_RESOLVER = true
ONE_CONFIRMED_BINDING_AUTHORITY = true
ONE_COMPUTABILITY_GATE = true
ONE_TOOL_EXECUTION_PIPELINE = true
ONE_COMPOSITION_ROOT = required
```

Prohibited:

- new generic semantic mapper;
- new confirmation loop;
- new catalog candidate/readiness wrappers;
- new execution harness between P8 and P9;
- frontend-owned semantic logic;
- a second parser for the same XLSX input.

---

## 6. Exact gaps preventing the composition root from being production-ready

### G1 — No application composition root

There is no module exposing the complete initial pass, owner reentry and computation-plan API.

### G2 — Owner correction is not governed rebinding

The current loop can confirm an existing role but cannot safely correct to another canonical role or preserve an uncataloged meaning without accidental clearance.

### G3 — Profiling/context scoring incomplete

The selected engine lacks the full deterministic profile and whole-sheet consistency layer required for 90% blind exact accuracy.

### G4 — Catalog/capability modules are chained as wrappers

They must be called as one P7 responsibility rather than extended as more handoffs.

### G5 — One computability vocabulary is missing

Existing readiness and controlled-execution gates expose overlapping statuses.

### G6 — End-to-end provenance not yet certified

The final pipeline must trace:

```text
source workbook/sheet/column
→ profile evidence
→ candidate
→ owner answer, when applicable
→ confirmed binding
→ formula/tool input
→ finding
→ delivered file
```

---

## 7. I2 contract boundary

The next and only new boundary is:

```text
PymIA-Live/pymia/smartpyme/service_1_deterministic_semantic_pipeline_v1.py
```

Before productive implementation, define a focused contract/test for these public operations:

```text
run_initial_pass(canonical_ingestion_output)
run_owner_reentry(previous_run, owner_answers)
build_computation_plan(confirmed_bindings, requested_capability)
```

The implementation must import selected P0–P8 components only. P9/P10 integration follows after the semantic round-trip passes end-to-end.

---

## 8. Final I1 decision

```text
I1_STATUS: COMPLETE
SELECTED_STAGE_IMPLEMENTATIONS: P0_P10_RECORDED
PARALLEL_CHAINS: FROZEN
NEXT_ITEM: I2_SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_CONTRACT
NO_NEW_DOMAIN_SLICE: true
NO_FRONTEND_WORK: true
```
