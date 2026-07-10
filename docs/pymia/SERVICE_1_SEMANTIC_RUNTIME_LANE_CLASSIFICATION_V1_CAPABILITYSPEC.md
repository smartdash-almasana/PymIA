# SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_V1 — CapabilitySpec

Status: Proposed
Authority: `docs/adr/SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1.md`
Scope: Classify the Service 1 semantic runtime lane as `EXPERIMENTAL_CANDIDATE_ONLY`
Code authorized: No
Runtime authorized: No

## 1. Capability

This CapabilitySpec authorizes a documentary classification capability for the Service 1 semantic runtime lane:

```text
SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_V1
```

The capability classifies the lane as:

```text
EXPERIMENTAL_CANDIDATE_ONLY
```

It does not promote the lane to sanctioned runtime capability.

## 2. Problem

The repository contains fail-closed candidate modules around the semantic runtime lane, including the `d303608` semantic runtime plan candidate.

Without a CapabilitySpec, future agents may mistake those modules for:

```text
runtime authority
execution authority
SaaS readiness
product readiness
delivery authority
LLM decision authority
```

This capability exists to prevent that mistake.

## 3. Inputs authorized

The classification may read and reference:

```text
docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md
docs/adr/SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1.md
PymIA-Live/pymia/smartpyme/service_1_bounded_semantic_engine_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_bounded_semantic_engine_implementation_v1.py
PymIA-Live/pymia/smartpyme/service_1_bounded_engine_to_allowed_computation_adapter_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_runtime_plan_candidate_v1.py
PymIA-Live/tests/smartpyme/test_service_1_semantic_runtime_plan_candidate_v1.py
```

## 4. Output authorized

The only authorized output of this capability is a classification record in documentation:

```text
SERVICE_1_SEMANTIC_RUNTIME_LANE: EXPERIMENTAL_CANDIDATE_ONLY
SEMANTIC_RUNTIME_PLAN_CANDIDATE: CANDIDATE_SHADOW_ONLY
PROMOTION_REQUIRED: ADR + CapabilitySpec + ModuleContract + TaskSpec + tests + evidence + checkpoint
```

## 5. What it can do

This capability may:

```text
- classify existing semantic-lane code as experimental candidate only
- preserve existing fail-closed test evidence as candidate evidence
- define source precedence for future agents
- define stop conditions before semantic runtime promotion
- document allowed and forbidden relationships to XLSX-first and SaaS lanes
- require a future ModuleContract and TaskSpec before implementation continues
```

## 6. What it cannot do

This capability must not:

```text
NO authorize runtime execution
NO authorize real runner invocation
NO authorize pipeline calls
NO authorize CLI execution
NO authorize file IO
NO authorize XLSX parsing
NO authorize case mutation
NO authorize case truth patching
NO authorize semantic binding mutation
NO authorize recalculation
NO authorize reexecution
NO authorize Phase 5
NO authorize owner delivery
NO authorize autonomous delivery
NO authorize SaaS runtime
NO authorize API/storage/worker
NO authorize LLM decision authority
NO declare product-ready
NO replace XLSX-first physical evidence requirements
NO bypass SERVICE_1_DOCUMENTARY_RECONCILIATION_V1
```

## 7. Authority model

```text
docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md = current status authority
SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1 = architectural classification authority
this CapabilitySpec = capability boundary for classification only
future ModuleContract = required before promotion
future TaskSpec = required before code continuation
```

The lane remains subordinate to:

```text
PymIA decides.
The LLM communicates.
```

## 8. Accepted current evidence

Current evidence may support only candidate/shadow claims:

```text
test_service_1_semantic_runtime_plan_candidate_v1.py -> fail-closed semantic runtime plan candidate behavior
```

The evidence supports:

```text
candidate prepared when adapter and computation candidate are ready
blocked when adapter is not ready
blocked when computation candidate is missing or not ready
blocked on policy violation
blocked when upstream execution/runtime/delivery guards open
all execution/runtime/reexecution/recalculation/delivery/Phase 5/product-ready flags remain false
```

The evidence does not support:

```text
runtime execution
physical XLSX end-to-end execution
real runner invocation
SaaS runtime
owner delivery
autonomous delivery
product-ready status
```

## 9. Promotion criteria

To promote this lane beyond `EXPERIMENTAL_CANDIDATE_ONLY`, a future cycle must create, review, and accept:

```text
ModuleContract
TaskSpec
acceptance tests
evidence checkpoint
```

The future ModuleContract must define:

```text
input contract
output contract
blocking states
guard invariants
relationship to allowed-computation candidates
relationship to existing XLSX-first and SaaS shadow/composition lanes
```

The future TaskSpec must prove:

```text
no runtime execution
no real runner
no delivery
no LLM decision authority
no bypass of deterministic gates
no product-ready claim
```

Any promotion that changes runtime decisions must also define feature flag + shadow mode behavior before integration.

## 10. Stop conditions

Stop before any further semantic runtime code if:

```text
- there is no accepted ModuleContract
- there is no accepted TaskSpec
- acceptance tests are missing
- a change opens runtime_authorized, delivery_authorized, phase_5_allowed, or product_ready
- a change calls runner, pipeline, CLI, API, storage, worker, LLM provider, or file IO
- a change mutates case truth or semantic bindings
- a change claims physical XLSX evidence or product readiness
```

## 11. Status

```text
SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_V1: PROPOSED
SERVICE_1_SEMANTIC_RUNTIME_LANE: EXPERIMENTAL_CANDIDATE_ONLY
CODE_CHANGE_AUTHORIZED_BY_THIS_CAPABILITYSPEC: NO
NEXT_REQUIRED_FOR_PROMOTION: ModuleContract + TaskSpec
```
