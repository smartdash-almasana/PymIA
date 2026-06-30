# IMPLEMENTATION_ROADMAP_TO_AUTONOMOUS_SAAS_V1

## Purpose

This document is the implementation roadmap for taking PymIA from the current certified Servicio 1 runtime chain to an autonomous SaaS with conversational AI and guardrails.

Its purpose is to prevent future agents, models, or contributors from redefining PymIA as a demo, an operator-led assistant, a marketing artifact, or an uncontrolled LLM product.

This document is versioned and authoritative under `docs/current/`. It is not immutable: it may change only when implementation evidence changes the certified baseline or the owner of PymIA explicitly changes direction.

## Final Objective

PymIA must become an autonomous SaaS with conversational AI and guardrails.

The main product flow must not depend on a human operator. The PyME owner interacts directly with PymIA, while the system remains governed by deterministic rules, gates, tools, evidence, and explicit state transitions.

## Operational Source of Truth

The operational source of truth for a PymIA case is:

```text
PYMIA + DATA + PYME OWNER
```

- **PymIA**: logic, rules, gates, tools, contracts, deterministic execution.
- **Data**: documentary evidence, files, normalized tables, confirmed fields.
- **PyME Owner**: operational meaning, confirmation, correction, context, missing evidence.

Conversational AI is not a source of truth. It translates, asks, summarizes, requests evidence, and helps the PyME owner interact with PymIA.

The operator is not the main product flow. The operator is fallback, support, audit, or exception handling only.

## Certified Baseline

Current certified baseline:

- `bee3f5e` — `S1_CASE_TRUTH_INTEGRATION_MODEL_V1`
- `9f366bf` — `S1_AUTO_TOOL_PLAN_CANDIDATE_MODEL_V1`
- `42a9d2d` — `S1_TOOL_PLAN_TO_EXPLICIT_REQUESTS_GATE_V1`
- `e0075cc` — `S1_EXPLICIT_REQUEST_TO_PIPELINE_REQUEST_GATE_V1`

Certified chain:

```text
normalized data / evidence
→ case truth integration
→ auto tool plan candidate
→ explicit request candidate gate
→ pipeline request candidate gate
```

This was the original certified baseline. The repository has since advanced beyond this point, so this section should be read as the historical base of the autonomous SaaS roadmap, not as the current frontier.

## Verified Repo State (June 29, 2026)

Verified against the current `main` branch and committed implementation files:

| Area | Status | Verified slices |
|-------|--------|-----------------|
| Autonomous core pipeline | Implemented | `S1_PIPELINE_REQUEST_EXECUTION_GATE_V1`, `S1_AUTONOMOUS_PIPELINE_RUNNER_V1` |
| Autonomous delivery candidate | Implemented | `S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1`, `S1_OWNER_DELIVERY_PACKET_FOR_SAAS_V1` |
| Owner reentry / autonomous rerun | Implemented | `S1_OWNER_FEEDBACK_TO_CASE_TRUTH_PATCH_V1`, `S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1` |
| SaaS shell candidates | Implemented as pure contracts | `S1_SAAS_CASE_SESSION_MODEL_V1`, `S1_SAAS_FILE_INTAKE_API_V1`, `S1_SAAS_JOB_ORCHESTRATION_V1` |
| Conversational owner layer | Implemented | `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1`, `S1_LLM_GUARDED_RESPONSE_GATE_V1`, `S1_OWNER_QUESTION_ROUTER_V1` |
| SaaS hardening — audit log | Implemented | `S1_AUDIT_LOG_V1` — commit `7319e1f` |
| SaaS hardening — tenant isolation | Implemented | `S1_TENANT_ISOLATION_GUARD_V1` — commit `fea2d5b` |
| SaaS hardening — failure recovery | Implemented | `S1_FAILURE_RECOVERY_V1` — commit `9f1aa8b` |
| SaaS hardening — cost/rate limit | Implemented | `S1_COST_AND_RATE_LIMIT_GUARD_V1` — commit `c434b67` |
| Human review / final release integration | Implemented as pure gated release chain | `S1_HUMAN_REVIEW_RELEASE_INTEGRATION_GATE_V1`, `S1_FINAL_OWNER_RELEASE_DECISION_GATE_V1`, `S1_FINAL_RELEASE_TO_OWNER_HANDOFF_CONTRACT_V1`, `S1_PHASE_H_RELEASE_CHAIN_COMPOSITION_TEST_V1` |
| Real SaaS runtime boundary contracts | Implemented as pure contracts | `S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1`, `S1_REAL_AUTH_BOUNDARY_CONTRACT_V1`, `S1_REAL_STORAGE_UPLOAD_BOUNDARY_CONTRACT_V1`, `S1_REAL_WORKER_RUNTIME_BOUNDARY_CONTRACT_V1` |
| Real SaaS runtime infrastructure | Not implemented | No real HTTP API, auth provider, DB/storage, upload pipeline, worker, queue, scheduler, or UI as the canonical autonomous path |

## Implementation Principles

1. **Autonomous core before LLM**  
   Do not connect conversational AI until the core engine can plan, pause, execute, deliver, and reenter through gates.

2. **Gates before execution**  
   No tool or pipeline runs without a pure authorization gate before it.

3. **References before raw values**  
   Planning and request gates should map evidence by references, not uncontrolled raw values.

4. **PyME owner as active user**  
   The PyME owner supplies meaning, confirmation, corrections, and missing evidence directly.

5. **Operator only as fallback**  
   Do not create new core flows that require a human operator as the normal path.

6. **No Hermes as active architecture**  
   Hermes terminology is historical/museum unless explicitly cited as legacy.

7. **No demo as substitute for runtime**  
   A demo cannot close a product gap. Runtime, tests, evidence, and commits close gaps.

8. **Strangler pattern over destructive replacement**  
   Keep the current CLI/operator path until the autonomous path is certified enough to replace it safely.

## Remaining Phases

### Phase A — Close Servicio 1 Autonomous Core Pipeline

**Objective:**
Move from `pipeline_request_candidate` to governed pipeline execution and autonomous `pipeline_result`, without routing through the CLI/operator flow.

**Likely slices:**

- `S1_PIPELINE_REQUEST_EXECUTION_GATE_V1`
- `S1_AUTONOMOUS_PIPELINE_RUNNER_V1`

**Closure criterion:**
A pipeline request candidate can be authorized by a pure gate and executed by an autonomous runner without invoking `service_1_operator.py` as the core path.

### Phase B — Governed Autonomous Delivery

**Objective:**
Transform `pipeline_result` into an owner-facing delivery candidate that can be released through explicit guardrails.

**Likely slices:**

- `S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1`
- `S1_OWNER_DELIVERY_PACKET_FOR_SAAS_V1`

**Closure criterion:**
The system can create a SaaS-ready owner delivery packet and decide whether it is releasable, blocked, or needs owner input without mandatory human review as the normal path.

### Phase C — PyME Owner Reentry and Autonomous Rerun

**Objective:**
Allow PymIA to pause when owner meaning or evidence is missing, ask the PyME owner, ingest structured feedback, patch case truth, and rerun the governed chain.

This phase applies both before execution and after delivery. Reentry is not only a post-delivery feature.

**Likely slices:**

- `S1_OWNER_FEEDBACK_TO_CASE_TRUTH_PATCH_V1`
- `S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1`

**Closure criterion:**
PymIA can ask the PyME owner for missing meaning/evidence, receive a structured answer, update case truth, and replan/rerun without an operator as the normal path.

### Phase D — Minimal SaaS Shell

**Objective:**
Provide the runtime container around the autonomous Servicio 1 core: case session, file intake, persistence boundaries, job orchestration, and tenant-aware state.

**Likely slices:**

- `S1_SAAS_CASE_SESSION_MODEL_V1`
- `S1_SAAS_FILE_INTAKE_API_V1`
- `S1_SAAS_JOB_ORCHESTRATION_V1`

**Closure criterion:**
A PyME owner can create a case, submit files, let PymIA process asynchronously, and inspect state through SaaS-ready interfaces.

### Phase E — Conversational AI Under Harness (CLOSED)

**Objective:**
Connect conversational AI as a governed interaction layer. The LLM may explain, ask, summarize, and transform owner responses into structured payloads, but it cannot decide truth, bypass gates, invent results, or authorize execution.

**Likely slices:**

- `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1` — implemented
- `S1_LLM_GUARDED_RESPONSE_GATE_V1` — implemented
- `S1_OWNER_QUESTION_ROUTER_V1` — implemented

**Closure criterion:**
The LLM can interact with the PyME owner only through approved contracts and guarded responses, while all truth and execution decisions remain in PymIA runtime.

**Status:** CLOSED — all three slices implemented and committed.

### Phase F — SaaS Hardening (CLOSED)

**Objective:**
Make the autonomous SaaS safe, observable, tenant-isolated, recoverable, and cost-controlled.

**Likely slices:**

- `S1_AUDIT_LOG_V1` — CLOSED + PUSHED (`7319e1f`)
- `S1_TENANT_ISOLATION_GUARD_V1` — CLOSED + PUSHED (`fea2d5b`)
- `S1_FAILURE_RECOVERY_V1` — CLOSED + PUSHED (`9f1aa8b`)
- `S1_COST_AND_RATE_LIMIT_GUARD_V1` — CLOSED + PUSHED (`c434b67`)

**Closure criterion:**
The system has enough operational safety to run as a real SaaS: audit trail, tenant boundaries, failure recovery, and cost/rate controls.

**Status:** CLOSED — all four hardening slices are implemented, committed, and pushed.

### Phase G — Real SaaS Runtime Boundary Contracts (CLOSED)

**Objective:**
Define and implement the pure boundary contracts required before real SaaS runtime infrastructure can be introduced.

**Implemented slices:**

- `S1_SAAS_RUNTIME_BOUNDARY_CONTRACTS_V1` — CLOSED + PUSHED (`b681f27`)
- `S1_REAL_ENDPOINT_API_BOUNDARY_CONTRACT_V1` — CLOSED + PUSHED (`bf1d0dc`)
- `S1_REAL_AUTH_BOUNDARY_CONTRACT_V1` — CLOSED + PUSHED (`f7f2813`)
- `S1_REAL_STORAGE_UPLOAD_BOUNDARY_CONTRACT_V1` — CLOSED + PUSHED (`08bcb82`)
- `S1_REAL_WORKER_RUNTIME_BOUNDARY_CONTRACT_V1` — CLOSED + PUSHED (`9e077a1`)

**Closure criterion:**
All four real runtime boundary contracts exist as pure deterministic contracts with focal tests and minimal regression evidence.

**Status:** CLOSED — Phase G closed boundary contracts only. It did not implement real API, real auth, real storage/upload, real worker/queue/scheduler, DB, or UI.

### Phase H — Human Review + Final Release Integration (CLOSED)

**Objective:**
Integrate the SaaS-ready release chain with human review, signoff, QA, final release decision, and owner handoff as pure gated candidates.

**Implemented slices:**

- `S1_HUMAN_REVIEW_RELEASE_INTEGRATION_GATE_V1` — CLOSED + PUSHED (`ba50c81`)
- `S1_FINAL_OWNER_RELEASE_DECISION_GATE_V1` — CLOSED + PUSHED (`f7cca45`)
- `S1_FINAL_RELEASE_TO_OWNER_HANDOFF_CONTRACT_V1` — CLOSED + PUSHED
- `S1_PHASE_H_RELEASE_CHAIN_COMPOSITION_TEST_V1` — CLOSED + PUSHED (`6f54f6c`)

**Status:** CLOSED — Phase H closed the pure human review and final release integration chain.

## Critical Path

Strict implementation path from baseline `e0075cc`:

1. `S1_PIPELINE_REQUEST_EXECUTION_GATE_V1`
2. `S1_AUTONOMOUS_PIPELINE_RUNNER_V1`
3. `S1_AUTONOMOUS_DELIVERY_RELEASE_GATE_V1`
4. `S1_OWNER_DELIVERY_PACKET_FOR_SAAS_V1`
5. `S1_OWNER_FEEDBACK_TO_CASE_TRUTH_PATCH_V1`
6. `S1_OWNER_REENTRY_TO_AUTONOMOUS_RERUN_V1`
7. `S1_SAAS_CASE_SESSION_MODEL_V1`
8. `S1_SAAS_FILE_INTAKE_API_V1`
9. `S1_SAAS_JOB_ORCHESTRATION_V1`
10. `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1`
11. `S1_LLM_GUARDED_RESPONSE_GATE_V1`
12. `S1_OWNER_QUESTION_ROUTER_V1`

This critical path from Phase A through Phase H is now COMPLETE.

## Dependencies and Blockers

- Phase A must close before autonomous delivery can be claimed.
- Phase B must close before owner-facing autonomous release can be claimed.
- Phase C can begin after the core gates are stable, but must support both pre-execution clarification and post-delivery feedback.
- Phase D should not lead the work. SaaS shell comes after the core autonomous runtime has stable contracts.
- Phase E is CLOSED. All three conversational slices are implemented and committed.
- Phase F is CLOSED. Audit log, tenant isolation, failure recovery, and cost/rate limit guards are implemented and pushed.
- Phase G is CLOSED. Real SaaS runtime boundary contracts are implemented and pushed as pure contracts only.
- Phase H is CLOSED. Human review, signoff, QA, final release decision, owner handoff, and composition test are implemented and pushed as pure contracts/tests only.
- Real runtime infrastructure remains NOT IMPLEMENTED: no real API, auth provider, DB/storage, upload pipeline, worker, queue, scheduler, publish execution, notification, or UI.
- The next front is Phase I preparation: First Real Controlled Client Flow.

## Not Allowed Yet

- Do not connect LLM/chatbot before the autonomous core pipeline and owner reentry gates exist.
- Do not build a UI that hides missing runtime gaps.
- Do not introduce Supabase or external SaaS infrastructure before defining the case/session model.
- Do not remove the old CLI/operator flow until the autonomous path is certified.
- Do not reopen Hermes as an active architecture.
- Do not open Servicio 2 as a substitute for closing Servicio 1 autonomous SaaS.
- Do not use commercial claims to close runtime gaps.
- Do not let conversational AI mutate truth, authorize runtime, or invent delivery results.

## Definition of Closed

A slice is closed only when:

- Runtime/model file exists.
- Focal tests exist and pass.
- Minimal relevant regression passes.
- The repo has no unrelated dirty state.
- A focal commit records the change.
- `docs/current/` is updated only when the certified roadmap/canon changes.

A phase is closed only when all its required slices meet the same criteria and the resulting chain can be demonstrated through tests or controlled runtime evidence.

## Next Unique Front

```text
Phase I preparation
```

This is the immediate front after closing Phase G boundary contracts.

It should prepare First Real Controlled Client Flow:

- audit requirements for a first controlled case;
- preserve CLI/operator fallback until the autonomous path is certified;
- define evidence, owner consent, oversight, and rollback boundaries;
- preserve the distinction between pure candidates and real execution.

It must not implement real API, auth, storage/upload, worker, queue, scheduler, DB, or UI.
