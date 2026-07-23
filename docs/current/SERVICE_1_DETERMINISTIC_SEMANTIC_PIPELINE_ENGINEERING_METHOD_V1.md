# SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1

**Status:** CANONICAL_METHOD_FOR_SERVICE_1_COMPLETION  
**Scope:** XLSX ingestion, semantic understanding, owner confirmation, governed computation and delivery  
**Supersedes as design authority:** isolated semantic micro-slices, repeated local readiness gates and chat-level redesigns  
**Historical trace:** Git conserva las versiones anteriores; los documentos superados no permanecen en el árbol activo.

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

#### Family-level binding rule

A confirmed column role is an evidence atom, not an executable capability. Servicio 1 must not advance by attaching one isolated variable directly to a tool.

The governed unit is a coherent variable family:

```text
OPERATION_CORE
SALES_MARGIN
CASH_COLLECTIONS
PURCHASES_SUPPLIERS
INVENTORY_CONTROL
```

Each family declares required role groups, optional roles, source columns, coverage and gaps. Equivalent roles may satisfy the same requirement, such as product code or product name. Family states are:

```text
VARIABLE_FAMILY_READY
VARIABLE_FAMILY_NEEDS_OWNER_CONFIRMATION
VARIABLE_FAMILY_MISSING_REQUIRED_ROLES
VARIABLE_FAMILY_NOT_OBSERVED
```

`VARIABLE_FAMILY_READY` means only that the semantic evidence set is coherent. It does not authorize tool selection, execution, diagnosis or delivery. P7 and P8 must still match the ready family against governed formulas/capabilities and case evidence.

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


---

## 15. Enterprise engineering control system

The deterministic pipeline defined in sections 1–14 remains the architectural authority. The controls in this section govern **how changes are proposed, implemented, evidenced, audited and integrated**. They do not create another product architecture.

The method combines:

```text
Spec-Driven Development
+ Contract-Driven Development
+ Artifact-Driven Execution
+ Evidence-Gated Integration
+ Git-Enforced Isolation
+ Deletion-Oriented Closure
```

Meaning:

- the specification defines intent, scope and acceptance;
- contracts define machine-verifiable boundaries;
- artifacts preserve decisions, evidence and recovery state;
- tests and observed runs gate integration;
- Git branches/worktrees isolate unfinished work;
- replaced paths are removed rather than retained indefinitely.

A specification, contract, ADR or TaskSpec is a **logical artifact**. It may be incorporated into an existing governing document when that avoids documentary duplication. This method does not authorize one document per slice.

### 15.1 Truth and closure

A work package is closed only when the following agree:

```text
architecture
method
active specification
contracts
code
acceptance tests
execution evidence
execution state
module disposition
architecture lock
Git state
independent audit
```

Chat messages, confidence statements and local test counts are not closure evidence by themselves.

### 15.2 Single active intervention

Only one productive implementation package may be active against `main` at a time. Other valuable unfinished work must be preserved outside `main` in named safety branches and separate worktrees.

Parallelism is permitted only when responsibilities do not overlap:

```text
many read-only auditors
+ one writer per file surface
+ one final integrator
```

Shared authorities, registries and composition roots must never have multiple concurrent writers.

---

## 16. Active change specification

Before code or governing documents are modified, the active package must record:

```text
CHANGE_ID
TITLE
BASE_BRANCH
BASE_HEAD
ENTERPRISE_STAGE
RISK_CLASS
OBSERVED_PROBLEM
AUTHORIZED_OUTCOME
WRITABLE_PATHS
READ_ONLY_PATHS
PROHIBITED_PATHS
NON_GOALS
ACCEPTANCE_TESTS
NEIGHBOR_TESTS
FULL_REGRESSION_REQUIREMENT
MANUAL_VALIDATION
DEBT_CREATED
DEBT_REMOVED
TEMPORARY_ARTIFACTS
REMOVAL_CONDITION
ROLLBACK
IMPLEMENTER
INDEPENDENT_AUDITOR
PUSH_AUTHORIZED
STOP_CONDITIONS
```

Blank fields are prohibited. `NOT_APPLICABLE` requires a reason.

### 16.1 Scope lock

The writable path set is exact. Touching an undeclared path stops the package until the scope is explicitly amended and re-audited.

### 16.2 New-module and new-document gate

A new module or governing document must state:

- the responsibility that is genuinely absent;
- the existing owner that was inspected;
- why evolving that owner is insufficient;
- its productive caller;
- the authority it replaces or its distinct boundary;
- its deletion condition when temporary.

A new file without this statement is rejected.

### 16.3 No chat-only authorization

A conversational decision becomes actionable only after it is represented in the active change specification or an existing governing authority. Conversation can coordinate work; it cannot silently authorize architecture or code.

---

## 17. Risk classes and mandatory gates

The highest affected class governs the work package.

### CLASS_0 — Documentation/state alignment

No behavior change. Requires:

- source verification;
- exact diff review;
- documentation-index audit;
- cold-recovery consistency when operational state changes.

### CLASS_1 — Internal refactor with unchanged contract

Requires:

- focal tests;
- direct-caller tests;
- neighboring regression;
- proof that public behavior and safety states are unchanged.

### CLASS_2 — Contract, semantic or formula change

Requires:

- acceptance-first tests;
- positive, negative and adversarial cases;
- corpus impact where semantic behavior changes;
- neighboring regression;
- independent audit.

### CLASS_3 — Execution authority or architecture change

Requires:

- explicit architecture decision;
- shadow comparison where practical;
- full regression;
- rollback proof;
- same-closure deletion of the replaced productive path;
- independent audit `PASS`.

### CLASS_4 — Production release

Requires all CLASS_3 gates plus operational, security, resource, recovery, observability and reproducible-release evidence.

---

## 18. Anti-drift controls

### 18.1 No moving goalposts

Acceptance criteria may not be weakened after implementation merely to obtain green tests. A criterion may change only when evidence shows that the prior contract was wrong, and the decision must be documented before the test is changed.

Mechanical expectation changes such as count updates are prohibited until the underlying contract decision is explicit.

### 18.2 No count-based progress

File count, line count and number of tests are secondary indicators. Progress is measured by:

- closed end-to-end behavior;
- fewer productive paths;
- clearer ownership;
- improved precision and safety metrics;
- removed replaced code;
- reduced unresolved debt.

### 18.3 No permanent coexistence

Old and new productive paths may coexist only inside an isolated comparison branch. A merge-ready closure contains one productive authority.

### 18.4 No frontend authority

The web/UI may:

- collect user intent;
- display workbook evidence;
- collect bounded owner selections;
- present results and limitations.

The web/UI must not:

- implement business formulas;
- synthesize economic values;
- assign final semantic truth;
- bypass P6 approval;
- authorize computation or delivery independently.

### 18.5 No speculative abstraction

Do not generalize for hypothetical future services. Extract a reusable abstraction only after real, stable consumers demonstrate the same contract.

### 18.6 Handoff contract

Every agent handoff states:

- verified repository state;
- exact scope;
- allowed and prohibited actions;
- required evidence;
- output schema;
- stop conditions.

---

## 19. Anti-debt controls

### 19.1 Debt is explicit or prohibited

Any accepted temporary compromise must be registered in the execution-state debt register with:

```text
debt_id
source_change
violated_invariant
scope
impact
risk
owner
disposition
removal_condition
latest_removal_stage
removal_test
status
```

Hidden debt is not accepted.

### 19.2 Adapter expiry

A temporary adapter without a deletion condition is prohibited. If its declared removal condition is not satisfied by the assigned stage, that stage fails or requires a new explicit architecture decision.

### 19.3 Same-closure deletion

When replacement equivalence is proven, the old path and any temporary adapter are deleted in the same closure. “Delete later” is not a completed state.

### 19.4 Temporary-artifact expiry

Experimental modules, spikes and transitory contracts must declare:

- productive authority: false;
- permitted use;
- exit test;
- absorption or deletion target;
- latest stage of removal.

Temporary artifacts cannot become productive merely because they pass their own tests.

### 19.5 No test-only product code

Product code must not contain fixture names, expected outputs, predeclared compatibility decisions or branches whose purpose is only satisfying a test.

### 19.6 Production debt budget

Production certification requires:

```text
permanent_adapters = 0
parallel_productive_paths = 0
unknown_owners = 0
unclassified_service_1_modules = 0
open_high_risk_debt = 0
```

---

## 20. Testing and evidence ladder

Tests are selected by risk rather than convenience.

### T0 — Repository integrity

- imports and schema validation;
- module disposition coverage;
- architecture-lock consistency;
- forbidden terms;
- documentation index;
- `git diff --check`.

### T1 — Contract tests

Validate types, states, invariants, ranges, fail-closed behavior and immutable projections.

### T2 — Focal behavior tests

Exercise the smallest responsible implementation.

### T3 — Neighboring integration tests

Exercise direct callers and consumers.

### T4 — End-to-end vertical test

Exercise real workbook → owner interaction when required → approved binding → governed computation → bounded output.

### T5 — Corpus evaluation

Record at least:

```text
corpus_version_or_hash
case_count
column_count
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

A safe block is not a dangerous error.

### T6 — Adversarial and robustness tests

At minimum:

- nulls and blanks;
- mixed physical types;
- misleading and duplicate headers;
- several candidate regions;
- impossible negative values;
- percentages outside valid range;
- grain mismatch;
- stock/flow contradiction;
- partial or contradictory owner assertions;
- formula self-verification;
- corrupted workbook;
- oversized workbook;
- interrupted execution.

### T7 — Full regression

Required for global stability claims, architecture changes, stage exits and release candidates.

### T8 — Manual product run

A human validates the actual owner journey against a fresh process and a real fixture. Cached state and stale servers are not valid evidence.

### 20.1 Evidence record

Each observed command records:

```text
actor
command
date
branch
commit
result
relevant_output
```

An unobserved command must not be reported as `PASS`.

---

## 21. Architecture fitness functions

The following properties must be machine-checked where practical:

```text
one canonical XLSX reader
one productive product root
one P6 binding authority
no productive import from experimental modules
all Service 1 modules classified exactly once
no computation from provisional bindings
no safety flag opened upstream
no unbounded free-text semantic unlock
no duplicate semantic-concept authority
no business formula implemented in the web surface
all temporary adapters registered with expiry
all active-package paths declared
all governing document references resolve
```

Fitness functions are merge gates, not advisory reports.

---

## 22. Separation of duties

### Method and plan owner

- maintains this method and the execution-state ledger;
- defines the active specification;
- prevents scope drift;
- resolves disputed contract changes from evidence.

### Implementer

- executes only the active specification;
- does not broaden scope;
- records exact evidence;
- stops on precondition mismatch.

### Independent auditor

- verifies read-only unless explicitly assigned another role;
- attempts to refute ownership, callers, hardcodes, test quality, deletion and recovery claims;
- emits `PASS`, `PASS_WITH_CORRECTIONS` or `FAIL`;
- does not create a competing strategy during audit.

### Integrator

- verifies branch, commit scope, evidence, audit and rollback;
- authorizes merge/push only when explicitly permitted;
- does not infer readiness from developer confidence.

For critical changes, the implementer cannot be the final auditor.

---

## 23. Git, worktree and preservation protocol

### 23.1 Dirty-tree rule

When unrelated changes exist, productive implementation stops. Every dirty path is classified as:

```text
COMPLETE_AND_CLOSABLE
INCOMPLETE_BUT_RECOVERABLE
UNKNOWN_DO_NOT_TOUCH
DISCARD_CANDIDATE
```

### 23.2 Safety preservation

Recoverable unfinished work is preserved in a named safety branch and separate worktree. Preservation must prove:

- exact path set;
- byte-for-byte hashes;
- exact safety-commit scope;
- source branch and HEAD unchanged;
- non-target paths unchanged;
- no push unless explicitly authorized.

A safety commit preserves evidence; it does not authorize integration.

### 23.3 Commit rules

- one coherent work package per commit;
- exact paths reviewed before staging;
- no unrelated formatting;
- commit message states behavioral intent;
- closure commit removes replaced paths;
- governing documents and execution state converge with the closure.

### 23.4 Push rules

Push only when:

- the user explicitly authorizes it;
- branch and destination are confirmed;
- commit scope is verified;
- required tests and audits pass;
- no known divergence exists;
- rollback remains possible.

---

## 24. Enterprise stages 0–8

The execution-state document records the active stage and exact next authorized action.

### Stage 0 — Stabilize and establish baseline

- map every dirty workstream;
- preserve recoverable work outside `main`;
- restore a clean, controlled `main`;
- establish recoverable method and execution-state documentation;
- run full regression on the clean base;
- record semantic precision baseline;
- pass independent cold-recovery audit.

### Stage 1 — Remove certified dead clusters

Delete only clusters proven to have no productive callers, one small group per closure. Begin with the safest certified cluster. Update disposition and lock files in the same closure.

### Stage 2 — Consolidate architecture and contracts

Freeze the stable decisions for Region, physical evidence, semantic hypotheses, P6 approval, grain, requirements and computation consumption. Evolve existing authorities rather than opening permanent parallel contracts.

### Stages 3 and 4 — First integrated approval-center migration

These stages form one indivisible implementation closure:

- specify the approval center;
- implement computed approval decisions;
- connect one real pathology already supported by the generic engine;
- compare old and new behavior;
- delete the replaced path and temporary adapter in the same closure.

A disconnected second spike is prohibited. If the new authority is not integrated with a real pathology, it is discarded or remains outside the productive tree.

### Stage 5 — Migrate the remaining eleven pathologies

Migrate one pathology at a time with the same frozen checklist. Do not open the next migration before the prior path has one authority, green evidence and deletion of its replaced route.

### Stage 6 — Converge computation engines

Converge generic, transactional and legacy computation forms toward one primary engine or narrowly justified bounded exceptions. Do not create a fourth engine.

### Stage 7 — Enterprise hardening

Prove:

- input and resource limits;
- structured errors;
- deterministic replay and idempotence;
- interruption recovery;
- structured observability;
- provenance to workbook/sheet/region/column/row;
- sensitive-data handling;
- concurrency/session behavior;
- reproducible installation, release and rollback.

### Stage 8 — Production certification

Production readiness requires measured evidence for:

- twelve migrated pathologies;
- one approval authority;
- one product root;
- one XLSX reader;
- no productive experimental artifacts;
- no temporary adapters;
- semantic precision at or above the approved threshold;
- zero dangerous confident errors on the certification corpus;
- adversarial, regression and manual product evidence;
- reproducible release and tested rollback.

Test volume or documentation volume alone cannot certify production.

---

## 25. Cold-recovery protocol

A fresh agent without access to conversation history must:

1. read `AGENTS.md`;
2. read `ARCHITECTURE_GUARDRAILS.md`;
3. read `docs/current/README.md`;
4. read this method;
5. read `SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md`;
6. verify branch, HEAD, working-tree state and recorded safety commits/worktrees;
7. stop on any mismatch and emit `RECOVERY_STATE_MISMATCH`;
8. execute only the recorded `NEXT_AUTHORIZED_ACTION`.

The agent must correctly identify:

- active enterprise stage;
- productive architecture invariants;
- preserved workstreams and commits;
- known debt and failed evidence;
- prohibited actions;
- exact next authorized action.

Failure to recover these facts produces:

```text
FAIL_DOCUMENTATION_RECOVERY
```

After every preserved workstream, closure, rollback, stage transition or change of next action, the execution-state document must be updated.

---

## 26. Enterprise final decisions

```text
SPEC_DRIVEN_BASE = true
CONTRACT_AND_ACCEPTANCE_GATES_REQUIRED = true
ONE_ACTIVE_IMPLEMENTATION_PACKAGE = true
ONE_WRITER_PER_SURFACE = true
INDEPENDENT_FINAL_AUDIT_REQUIRED = true
CHAT_IS_NOT_INSTITUTIONAL_MEMORY = true
SAFETY_BRANCH_IS_NOT_PRODUCTIVE_AUTHORITY = true
NO_PERMANENT_PARALLEL_PATHS = true
SAME_CLOSURE_DELETION_REQUIRED = true
COLD_RECOVERY_IS_A_STAGE_GATE = true
```
