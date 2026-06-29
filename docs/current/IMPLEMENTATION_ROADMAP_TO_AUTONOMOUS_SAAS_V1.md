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
| Conversational owner layer | In progress | `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1` implemented; `S1_LLM_GUARDED_RESPONSE_GATE_V1` and `S1_OWNER_QUESTION_ROUTER_V1` pending |
| Human review / release boundary | Partial | Human review gate, final QA gate, and signoff flow exist; final SaaS/runtime release integration is still pending |
| Real SaaS runtime boundary | Not started | No real endpoint/API, auth, DB/storage, upload, worker, or UI as the canonical autonomous path |

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

### Phase E — Conversational AI Under Harness

**Objective:**
Connect conversational AI as a governed interaction layer. The LLM may explain, ask, summarize, and transform owner responses into structured payloads, but it cannot decide truth, bypass gates, invent results, or authorize execution.

**Likely slices:**

- `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1`
- `S1_LLM_GUARDED_RESPONSE_GATE_V1`
- `S1_OWNER_QUESTION_ROUTER_V1`

**Closure criterion:**
The LLM can interact with the PyME owner only through approved contracts and guarded responses, while all truth and execution decisions remain in PymIA runtime.

### Phase F — SaaS Hardening

**Objective:**
Make the autonomous SaaS safe, observable, tenant-isolated, recoverable, and cost-controlled.

**Likely slices:**

- `S1_AUDIT_LOG_V1`
- `S1_TENANT_ISOLATION_GUARD_V1`
- `S1_FAILURE_RECOVERY_V1`
- `S1_COST_AND_RATE_LIMIT_GUARD_V1`

**Closure criterion:**
The system has enough operational safety to run as a real SaaS: audit trail, tenant boundaries, failure recovery, and cost/rate controls.

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

## Dependencies and Blockers

- Phase A must close before autonomous delivery can be claimed.
- Phase B must close before owner-facing autonomous release can be claimed.
- Phase C can begin after the core gates are stable, but must support both pre-execution clarification and post-delivery feedback.
- Phase D should not lead the work. SaaS shell comes after the core autonomous runtime has stable contracts.
- Phase E is active. Its preconditions are already satisfied by the implemented owner reentry, rerun, delivery-candidate, and SaaS-shell contracts.
- The immediate open work inside Phase E is the guarded LLM response gate first, then the owner question router.
- Phase F still depends on the final shape of the conversational layer and the eventual real SaaS runtime boundary.

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
S1_LLM_GUARDED_RESPONSE_GATE_V1
```

This is the immediate front after closing `S1_CONVERSATIONAL_OWNER_BRIDGE_CONTRACT_V1`.

It must consume the conversational bridge candidate and strictly constrain what an LLM-generated response candidate may do:

- explain or summarize existing verified state;
- ask for missing evidence or clarification;
- preserve forbidden scopes such as runtime authorization, case mutation, delivery publication, or fabricated certainty.

It must not replace the bridge, bypass the deterministic contracts, or turn the conversational layer into a truth/authorization engine.
