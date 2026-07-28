# SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1

Status: Proposed
Type: Classification ADR
Scope: Service 1 semantic runtime candidate lane introduced around commit `d303608`
Runtime impact: None
Code impact: None
Tests impact: None

## 1. Decision

The Service 1 semantic runtime lane introduced around commit `d303608` is classified as:

```text
EXPERIMENTAL_CANDIDATE_ONLY
```

This lane may prepare fail-closed candidate artifacts for future reasoning about semantic runtime planning, but it is not a sanctioned runtime capability, not product-ready, and not authorized to execute computation, call a runner, mutate case state, recalculate, reexecute, deliver, or promote Phase 5.

The current allowed classification is narrower than a sanctioned future capability:

```text
CANDIDATE_SHADOW_ONLY
-> EXPERIMENTAL_CANDIDATE_ONLY
```

A later promotion to sanctioned capability requires the full method chain:

```text
ADR update or successor ADR
-> CapabilitySpec promotion
-> ModuleContract
-> TaskSpec
-> acceptance tests
-> code or code reconciliation
-> evidence
-> checkpoint
```

## 2. Problem

`docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md` established that `d303608` and the semantic runtime plan candidate are candidate/shadow-only unless later architectural work promotes them.

The repository already contains semantic-lane code such as:

```text
PymIA-Live/pymia/smartpyme/service_1_bounded_semantic_engine_contract_v1.py
PymIA-Live/pymia/smartpyme/service_1_bounded_semantic_engine_implementation_v1.py
PymIA-Live/pymia/smartpyme/service_1_bounded_engine_to_allowed_computation_adapter_v1.py
PymIA-Live/pymia/smartpyme/service_1_semantic_runtime_plan_candidate_v1.py
```

Those modules are intentionally fail-closed and candidate-oriented, but without explicit ADR classification they can be misread as runtime authority.

That would create methodological drift:

- treating a candidate as execution authority;
- treating a semantic plan as a runtime plan;
- using semantic artifacts to bypass XLSX-first evidence requirements;
- promoting SaaS/autonomy without runner/runtime/delivery authorization;
- confusing shadow evidence with product readiness.

## 3. Context and source authority

This ADR is subordinate to `docs/current/`.

Current authority:

```text
docs/current/README.md
docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md
```

The reconciliation document normalizes the semantic runtime candidate as:

```text
SEMANTIC_RUNTIME_PLAN_CANDIDATE: CANDIDATE_SHADOW_ONLY
```

This ADR gives that state an architectural classification:

```text
SERVICE_1_SEMANTIC_RUNTIME_LANE: EXPERIMENTAL_CANDIDATE_ONLY
```

## 4. Scope

This ADR classifies the lane made of candidate-only components that connect:

```text
bounded semantic engine invocation/contract/implementation candidate
-> bounded engine to allowed computation adapter
-> semantic runtime plan candidate
```

The lane may be used to reason about whether a semantic interpretation could eventually prepare a deterministic allowed-computation candidate.

## 5. Non-scope

This ADR does not authorize:

```text
runtime execution
real runner invocation
pipeline call
CLI execution
file IO
XLSX parsing
case mutation
case truth patching
column binding mutation
recalculation
reexecution
Phase 5
owner delivery
autonomous delivery
SaaS runtime
API/storage/worker
LLM decision authority
product-ready claims
```

This ADR does not change the status of:

```text
SERVICE_1_OPERATIVE_XLSX_FIRST
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT
SAAS_EXECUTION_GATE_CHAIN
REAL_RUNNER
AUTONOMOUS_DELIVERY
```

Those states remain governed by `docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md`.

## 6. Required invariants

The lane must remain fail-closed.

Required invariants:

| Invariant | Required value |
|---|---:|
| `runtime_authorized` | `False` |
| `reexecution_authorized` | `False` |
| `recalculation_authorized` | `False` |
| `delivery_authorized` | `False` |
| `phase_5_allowed` | `False` |
| `product_ready` | `False` |
| real runner call | forbidden |
| pipeline call | forbidden |
| LLM decision authority | forbidden |

If any upstream object opens execution, runtime, delivery, product-ready, or Phase 5 guards, the semantic lane must block instead of preparing a ready candidate.

## 7. Relationship to PymIA authority

The lane must preserve the Service 1 rule:

```text
PymIA decides.
The LLM communicates.
```

For this ADR, the lane is not an LLM authority and not an autonomous semantic decider. It can only prepare candidate artifacts inside deterministic guardrails.

If a future LLM-mediated interpretation feeds this lane, that future integration requires a separate ADR/CapabilitySpec/ModuleContract/TaskSpec and must prove that the LLM does not decide case state, evidence requirements, tool selection, diagnosis, treatment, or delivery scope.

## 8. Relationship to XLSX-first and SaaS lanes

This lane is not the operative XLSX-first closeout and does not certify physical XLSX end-to-end execution.

This lane is not the SaaS runner and does not certify SaaS runtime.

Allowed relationship:

```text
semantic candidate artifact
-> possible future input to deterministic allowed-computation planning
```

Forbidden relationship:

```text
semantic candidate artifact
-> runtime execution
-> delivery
-> product-ready claim
```

## 9. Consequences

Positive consequences:

- existing semantic candidate code is classified without pretending it is product runtime;
- future work has a safe promotion path;
- candidate/shadow evidence remains usable without expanding its authority;
- Service 1 avoids another undocumented lane.

Tradeoff:

- this blocks fast continuation of semantic runtime code until the full method chain exists.

That tradeoff is intentional. Architectural clarity wins over speed here.

## 10. Next methodological step

The paired CapabilitySpec is:

```text
docs/pymia/SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_V1_CAPABILITYSPEC.md
```

After this ADR and CapabilitySpec, the next valid choices are:

1. keep the semantic lane frozen as `EXPERIMENTAL_CANDIDATE_ONLY`; or
2. create ModuleContract + TaskSpec to promote one narrow future slice.

No productive code is authorized by this ADR alone.
