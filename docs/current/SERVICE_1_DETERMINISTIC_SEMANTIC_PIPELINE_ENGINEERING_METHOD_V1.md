# SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1

**Status:** CANONICAL_METHOD_FOR_SERVICE_1_COMPLETION  
**Scope:** XLSX ingestion, semantic understanding, owner confirmation, governed computation and delivery  
**Supersedes as design authority:** isolated semantic micro-slices, repeated local readiness gates and chat-level redesigns  
**Does not delete historical evidence:** prior documents remain evidence only unless explicitly listed as canonical below.

---

## 1. Audit verdict

```text
VERDICT: PARTIAL_ARCHITECTURAL_CONVERGENCE_WITH_EXCESSIVE_SLICE_DUPLICATION
```

Servicio 1 does not lack engineering work. It has too many partially overlapping boundaries around the same business loop:

```text
read Excel
→ understand columns
→ identify ambiguity
→ ask the owner
→ reinject the answer
→ bind evidence
→ decide computability
→ execute deterministic tools
→ produce files
```

The repository already contains most of these responsibilities, but they were implemented repeatedly through contracts, candidates, adapters, handoffs, activation gates, harnesses, audits and checkpoints. Many artifacts prove local safety while no single document governed the productive end-to-end pipeline.

The principal pathology is therefore not absence of functionality. It is:

```text
boundary proliferation
+ duplicated semantic vocabularies
+ repeated fail-closed wrappers
+ documentary closure without one productive composition root
```

The correction is not another redesign. The correction is to freeze one deterministic pipeline, assign each responsibility once, absorb existing artifacts into that pipeline, and prohibit new semantic micro-slices unless a measured corpus gap requires them.

---

## 2. Name of the engineering method

The appropriate term is:

```text
Deterministic, contract-driven, evidence-gated pipeline engineering
```

For PymIA, the compact name is:

```text
PymIA Deterministic Evidence Pipeline Method
```

Its defining properties are:

- deterministic core;
- explicit typed contracts between stages;
- immutable evidence packets;
- fail-closed state transitions;
- owner confirmation as an evidence event;
- no LLM decision authority inside computation;
- measurable corpus performance;
- one composition root;
- files as final product artifacts.

---

## 3. Governing product invariant

```text
The owner supplies operational meaning.
The conversational layer asks and explains.
The deterministic pipeline validates, binds and computes.
Tools generate the files.
```

Operationally:

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

Owner confirmation is not a post-delivery human review. It is an input evidence event inside the semantic pipeline.

---

## 4. Canonical productive pipeline

Only the following pipeline is authorized as the target architecture for Servicio 1:

```text
P0  FILE INTAKE
    ↓
P1  CANONICAL XLSX INGESTION
    ↓
P2  STRUCTURAL AND DATA PROFILING
    ↓
P3  SEMANTIC CANDIDATE GENERATION
    ↓
P4  CONTEXTUAL EVIDENCE SCORING
    ↓
P5  OWNER CONFIRMATION LOOP, only when required
    ↓
P6  CONFIRMED SEMANTIC BINDING
    ↓
P7  PATHOLOGY / FORMULA / CAPABILITY MATCHING
    ↓
P8  COMPUTABILITY AND SAFETY GATE
    ↓
P9  DETERMINISTIC TOOL EXECUTION
    ↓
P10 QA, DELIVERY POLICY AND FILE PACKAGE
```

No parallel semantic lane may bypass this sequence.

---

## 5. Stage contracts

### P0 — File intake

**Responsibility**

- identify file and case;
- validate accepted type and basic metadata;
- create stable case/file references.

**Must not**

- infer business meaning;
- select formulas;
- diagnose;
- authorize delivery.

### P1 — Canonical XLSX ingestion

**Responsibility**

- read the real workbook through the canonical ingestion implementation;
- preserve sheet names, headers, rows and provenance;
- normalize only structural representation.

**Canonical direction**

Use the existing ingestion path and the canonical-ingestion-to-semantic bridge. Do not create another XLSX parser.

### P2 — Structural and data profiling

**Responsibility**

Produce deterministic evidence for each column:

- normalized header;
- inferred physical data type;
- null ratio;
- uniqueness/cardinality;
- numeric range and sign profile;
- date/text/category patterns;
- sample values;
- sheet context;
- neighboring columns;
- row-level arithmetic relationships when testable.

This stage observes data. It does not assign final semantic truth.

### P3 — Semantic candidate generation

**Responsibility**

Generate ranked candidate roles from governed catalogs and aliases.

Candidate output must contain:

```text
column_ref
candidate_role
candidate_concept
supporting_evidence
contradicting_evidence
confidence
risk_if_wrong
owner_confirmation_required
```

A header match alone is never sufficient evidence for a high-risk binding.

### P4 — Contextual evidence scoring

**Responsibility**

Contrast candidates against:

```text
header evidence
+ content profile
+ sheet name
+ co-column graph
+ row identities
+ business exclusions
+ canonical concept catalog
+ formula requirements
```

The resolver evaluates the whole sheet, not isolated headers.

Examples of deterministic identities:

```text
quantity × unit_price ≈ line_total
subtotal + taxes - discount ≈ final_amount
collected_amount + accounts_receivable ≈ invoiced_amount
opening_stock + inbound - outbound + adjustments ≈ closing_stock
```

Identities require minimum row coverage and tolerance. One matching row cannot confirm a role.

### P5 — Owner confirmation loop

**Responsibility**

When evidence remains ambiguous or risk is high:

1. emit one owner-facing question;
2. present bounded alternatives plus `Otra cosa`;
3. receive explicit answer;
4. store answer with file, sheet and column scope;
5. reinject it as immutable evidence;
6. rerun semantic evaluation.

Canonical owner-confirmation event:

```text
case_id
file_ref
sheet_ref
column_ref
proposed_role
owner_answer
confirmed_role or corrected_meaning
confirmation_scope
confirmed_by_owner = true
timestamp/provenance
```

Owner text must not merely clear a boolean. It must either confirm an existing role or produce a structured correction that can be rebound through the governed semantic vocabulary.

### P6 — Confirmed semantic binding

**Responsibility**

Create the final binding only when:

- evidence is sufficient, or
- the owner has explicitly confirmed/corrected meaning;
- contradictions are resolved;
- required type/unit constraints hold.

Allowed states:

```text
CONFIRMED
PROVISIONAL
NEEDS_OWNER_CONFIRMATION
CONFLICTING_EVIDENCE
BLOCKED
```

Only `CONFIRMED` may satisfy a required formula variable.

### P7 — Pathology / formula / capability matching

**Responsibility**

Use confirmed bindings to determine:

- candidate pathology or business problem;
- applicable deterministic formulas;
- governed non-formula capabilities;
- evidence still missing.

Semantic concepts and formulas are separate:

```text
concepts may exist without formulas;
formulas consume compatible confirmed concepts.
```

Identifiers, dimensions, classifications and temporal concepts must not be forced into artificial formulas.

### P8 — Computability and safety gate

**Responsibility**

Decide one of:

```text
READY_FOR_COMPUTATION
NEEDS_OWNER_CONFIRMATION
NEEDS_EVIDENCE
CONFLICTING_EVIDENCE
BLOCKED_BY_POLICY
UNSUPPORTED_CAPABILITY
```

This stage may authorize a specific deterministic computation, not generic runtime autonomy.

### P9 — Deterministic tool execution

**Responsibility**

Execute only explicitly selected and allowed tools with confirmed inputs.

Constraints:

- no semantic reinterpretation;
- no new owner claims;
- no hidden fallback mappings;
- no LLM calculation authority;
- no execution outside the allowed tool contract.

### P10 — QA, delivery policy and file package

**Responsibility**

- validate outputs;
- preserve provenance;
- expose limitations and unresolved gaps;
- apply `delivery_policy_guard`;
- generate XLSX/report/manifest artifacts.

The delivery layer does not retroactively repair semantic uncertainty.

---

## 6. Canonical repository responsibilities

The following existing families are retained and absorbed into the canonical pipeline.

| Existing family | Canonical role | Decision |
|---|---|---|
| canonical ingestion output → semantic bridge | P1/P3 boundary | RETAIN |
| column understanding engine | P2–P4 implementation base | RETAIN AND CONSOLIDATE |
| column understanding corpus evaluation/report | engineering measurement | RETAIN |
| owner question adapter | P5 owner-facing projection | RETAIN |
| owner confirmation boundary and reinjection gate | P5/P6 | RETAIN, FIX SEMANTIC REBINDING |
| semantic evidence binding contracts/engine | P6 | RETAIN AS SINGLE BINDING AUTHORITY |
| runtime catalog binding contract/adapter/handoff | P7 catalog lookup | ABSORB; no new wrapper layers |
| pipeline readiness / controlled execution gates | P8 | CONSOLIDATE INTO ONE COMPUTABILITY GATE |
| semantic binding activation/harness/bounded invocation | pre-runtime safety evidence | FREEZE; do not extend as another chain |
| semantic concept catalog contract/candidate/readiness | concept-model recovery | ABSORB INTO ONE VERSIONED CONCEPT CATALOG |
| stock semantic contract/evidence packet | family evidence specification | RETAIN AS DOMAIN PLUGIN, NOT PIPELINE CENTER |
| historical owner semantic request/gate documents | architectural provenance | EVIDENCE ONLY; not productive authority |

---

## 7. Duplications found and disposition

### 7.1 Repeated contract → candidate → readiness gate pattern

This pattern was created repeatedly around catalogs and semantic stages.

**Problem**

It proves each local object is fail-closed but adds no new business capability.

**Decision**

```text
STOP creating generic candidate/readiness wrappers.
```

A new wrapper is allowed only when it represents a real external boundary, persistence boundary or side-effect boundary.

### 7.2 Multiple semantic authorities

Existing code/docs refer to:

- column semantic mapper;
- column understanding engine;
- semantic evidence binding engine;
- semantic concept catalog candidate;
- runtime catalog binding handoff;
- owner semantic confirmation flow.

**Decision**

There will be only three semantic responsibilities:

```text
Candidate Resolver
Confirmed Binding Authority
Catalog/Capability Matcher
```

Everything else is adapter, evidence, UI projection or historical artifact.

### 7.3 Owner confirmation as boolean clearance

The current reinjection path can mark `owner_confirmation_required=False` while preserving an already existing role, and explicitly states that it does not change roles unless they already existed.

**Risk**

An owner correction can clear the gate without producing a properly governed corrected binding.

**Decision**

P5/P6 must distinguish:

```text
CONFIRM_EXISTING_ROLE
CORRECT_TO_CANONICAL_ROLE
DECLARE_UNCATALOGED_MEANING
REJECT_COLUMN_FOR_CURRENT_CAPABILITY
```

An unrecognized free-text answer must not silently become a confirmed semantic role.

### 7.4 Formula catalog used as universal ontology

This constrained identifiers, classifications and dimensions.

**Decision**

Retain formula catalog for computation. Establish one semantic concept catalog for all concept kinds. Formulas reference concepts; they do not define the entire ontology.

### 7.5 Corpus threshold treated as frontend authorization

A 90% exact-match target is useful engineering evidence but cannot alone authorize production.

**Decision**

Production semantic gate requires:

```text
blind exact match rate >= 0.90
false confident rate = 0
dangerous error rate = 0
safe resolution rate = 1.00
owner correction round-trip pass = true
binding provenance pass = true
unsupported Excel fail-closed pass = true
```

---

## 8. Engineering workflow from now on

Every semantic change must follow this fixed loop:

```text
1. Measure a failure on the corpus or a real workbook fixture.
2. Classify the failure by pipeline stage.
3. Change only the responsible stage.
4. Add positive, ambiguous and negative cases.
5. Run focal tests.
6. Run semantic pipeline regression.
7. Run blind holdout evaluation.
8. Record metric delta.
9. Integrate only if safety metrics do not regress.
```

Forbidden:

- creating a concept because a chat mentioned it;
- adding aliases directly to code without catalog provenance;
- opening another contract chain for the same stage;
- optimizing solely against the development corpus;
- declaring progress from test count without metric improvement;
- redesigning pipeline boundaries in each chat.

---

## 9. Corpus and measurement method

The current 38-column corpus is a development fixture, not production certification.

Required evaluation sets:

```text
Development corpus: 200+ columns
Validation corpus: 100+ columns
Blind holdout corpus: 100+ columns
Adversarial ambiguity corpus: 50+ columns
```

Coverage must include:

- sales;
- purchases;
- collections;
- payments;
- prices and discounts;
- costs and margins;
- inventory movements;
- bank/MP reconciliation;
- accounting workpapers;
- generic administrative sheets;
- malformed and unsupported sheets.

Metrics:

```text
exact_role_accuracy
concept_family_accuracy
owner_question_precision
owner_confirmation_resolution_rate
false_confident_rate
dangerous_error_rate
safe_block_rate
computation_input_completeness
end_to_end_file_success_rate
```

A blocked ambiguous column is a safe outcome, not an accuracy failure. The principal production invariant remains zero dangerous confident errors.

---

## 10. Production Definition of Done for the semantic pipeline

The semantic subsystem is production-ready only when all gates below pass.

### Architecture

- one composition root;
- one confirmed binding authority;
- one computability gate;
- no duplicate productive semantic lanes;
- catalog versions recorded in every run.

### Functional

- real XLSX ingestion;
- multi-sheet preservation;
- deterministic profiling;
- contextual candidate ranking;
- owner confirmation and correction round-trip;
- confirmed binding persistence/replay;
- governed formula/capability selection;
- deterministic execution;
- file delivery with provenance.

### Safety

- zero false-confident errors on blind corpus;
- unknown columns remain blocked or owner-confirmed;
- owner correction cannot bypass catalog governance;
- no computation on provisional bindings;
- no hidden fallback role;
- no runtime/product/delivery flags opened upstream.

### Reliability

- deterministic replay yields identical bindings and computations;
- immutable input/output packets;
- tests for corrupted files, duplicate headers, missing sheets, mixed types and contradictory owner answers;
- full audit trail from source cell/column to output finding.

### Product

- owner can upload a workbook, answer bounded questions and receive files without developer intervention for supported capabilities;
- unsupported workbooks receive a precise actionable limitation, not a fabricated result;
- delivery package states evidence, assumptions, unresolved gaps and computation provenance.

---

## 11. Single integration target

No new domain contract should be opened now.

The next implementation target is one composition module:

```text
SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1
```

It must compose existing productive capabilities rather than duplicate them.

Required public behavior:

```text
run_initial_pass(canonical_ingestion_output)
    -> CONFIRMED_BINDINGS
     | OWNER_QUESTIONS
     | BLOCKED

run_owner_reentry(previous_run, owner_answers)
    -> CONFIRMED_BINDINGS
     | OWNER_QUESTIONS
     | BLOCKED

build_computation_plan(confirmed_bindings, requested_capability)
    -> READY_FOR_COMPUTATION
     | NEEDS_EVIDENCE
     | UNSUPPORTED_CAPABILITY
     | BLOCKED
```

This composition root must call existing components; it must not create another parser, mapper, confirmation model, catalog loader or execution harness.

---

## 12. Immediate implementation sequence

```text
I1. Inventory exact productive modules and select one implementation per stage.
I2. Write an integration contract for SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1.
I3. Add end-to-end tests for initial pass → owner question → reentry → confirmed binding.
I4. Fix owner correction so it produces governed semantic rebinding, not boolean clearance.
I5. Connect confirmed bindings to the existing formula/capability matcher.
I6. Connect one supported deterministic tool family end-to-end.
I7. Produce the real XLSX/report/manifest package.
I8. Expand corpus based only on measured residual failures.
I9. Run blind holdout and production gates.
```

No frontend work is required before I3–I7 work through a stable application boundary. Frontend can be connected after the pipeline API is stable; it must not contain semantic logic.

---

## 13. Documentation governance

From this document onward:

- this file is the canonical semantic-pipeline method;
- prior plans, checkpoints and audits are evidence, not competing authority;
- a new document may not redefine stages P0–P10 without an ADR explicitly superseding this method;
- every continuation prompt must name the current integration item from section 12;
- progress is reported by closed pipeline behavior and metric delta, not number of slices or tests alone.

---

## 14. Final decision

```text
STOP_MICROSLICE_PROLIFERATION = true
FREEZE_PARALLEL_SEMANTIC_CHAINS = true
OWNER_CONFIRMATION_IS_PIPELINE_EVIDENCE = true
ONE_COMPOSITION_ROOT_REQUIRED = true
PRODUCTION_TARGET = SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_V1
```

Servicio 1 should now be completed by integration, corpus validation and production hardening—not by redesigning its semantic architecture in each chat.
