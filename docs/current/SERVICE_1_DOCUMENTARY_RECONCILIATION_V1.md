# Service 1 Documentary Reconciliation V1

Status: DOCUMENTARY_RECONCILIATION
Date: 2026-07-10
Scope: Servicio 1 XLSX-first closeout, active roadmap, SaaS checkpoint, and semantic runtime candidate lane.

## Verdict

Servicio 1 has multiple valid but differently scoped status documents. This reconciliation normalizes their meaning so future work does not treat a scoped PASS as broader product readiness.

```text
SERVICE_1_OPERATIVE_XLSX_FIRST: CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: NEEDS_EVIDENCE
SAAS_EXECUTION_GATE_CHAIN: SHADOW_COMPOSITION_PASS
REAL_RUNNER: BLOCKED
AUTONOMOUS_DELIVERY: BLOCKED
SEMANTIC_RUNTIME_PLAN_CANDIDATE: CANDIDATE_SHADOW_ONLY
```

The operative XLSX-first lane is closed for controlled real-client use, but this does not mean physical XLSX end-to-end execution through the official entrypoint is certified. The SaaS lane remains shadow/composition-only: no real runner, no SaaS runtime, no API/storage/worker, and no autonomous delivery. The semantic runtime candidate added by `d303608` remains candidate/shadow-only unless a later ADR and CapabilitySpec promote it.

## Normalized states

| State key | Normalized state | Meaning |
|---|---|---|
| `SERVICE_1_OPERATIVE_XLSX_FIRST` | `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS` | Controlled operator use is allowed within the documented closeout limits. |
| `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT` | `NEEDS_EVIDENCE` | A physical XLSX-to-official-entrypoint run remains unproven as a single certified evidence chain. |
| `SAAS_EXECUTION_GATE_CHAIN` | `SHADOW_COMPOSITION_PASS` | Composition through execution gate and runner shadow is tested, but no real runner/runtime/delivery is authorized. |
| `REAL_RUNNER` | `BLOCKED` | Runner invocation remains out of scope until a future authorized phase. |
| `AUTONOMOUS_DELIVERY` | `BLOCKED` | No owner-facing autonomous delivery is authorized. |
| `SEMANTIC_RUNTIME_PLAN_CANDIDATE` | `CANDIDATE_SHADOW_ONLY` | The semantic runtime plan candidate prepares a fail-closed plan candidate only. |

## Source precedence after reconciliation

This document does not erase prior evidence documents. It narrows how each source may be used after reconciliation.

| Source | Still valid for | Not valid for |
|---|---|---|
| `docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` | Scoped normalized-payload bridge evidence and `PASS_WITH_LIMITS` boundary claims. | Current next-front planning or physical XLSX end-to-end certification. |
| `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | Controlled-use closeout of the operative XLSX-first lane, with explicit non-promises. | Claiming SaaS, autonomous delivery, product-ready status, or physical XLSX end-to-end evidence beyond the documented limits. |
| `docs/current/ACTIVE_ROADMAP.md` | Current SaaS shadow/composition roadmap and stop rules. | Claiming real runner invocation, SaaS runtime, API/storage/worker readiness, or autonomous delivery. |
| `docs/current/SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1.md` | Historical checkpoint for the SaaS adapter state before execution-gate and runner-shadow tests closed. | Current next-front planning for execution-gate work already covered by later tests and `ACTIVE_ROADMAP.md`. |
| `d303608` semantic runtime plan candidate | Candidate-only fail-closed planning evidence. | Promoting a semantic runtime capability without ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, evidence, and checkpoint. |

In short:

```text
XLSX_AUDIT remains valid as scoped evidence.
XLSX_AUDIT is superseded only for next-front planning.
OPERATIVE_CLOSEOUT remains valid as controlled-use closeout.
ACTIVE_ROADMAP remains valid for SaaS shadow/composition, not runtime/autonomous delivery.
```

## Claim reconciliation

| Claim | Source | Evidence | Corrected state | Methodological action |
|---|---|---|---|---|
| Service 1 operative XLSX-first is closed for controlled real-client use. | `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | The closeout declares `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE` and lists adapter, real-owner pilot case run, delivery packet adapter, folder smoke, safe case dir, and operator runbook as closed. | `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS` | Preserve the closeout, but always carry the limits in references and planning. |
| The XLSX bridge case-run audit is complete. | `docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` | The audit declares `PASS_WITH_LIMITS`, with normalized-payload bridge coverage and explicit boundaries: no parser, no file IO, no delivery folder. | `PASS_WITH_LIMITS` | Do not expand this PASS into physical XLSX end-to-end evidence. |
| Physical XLSX ingestion through the official entrypoint is certified. | Inferred from the broader operative closeout wording. | The bridge audit states the remaining gap was an actual XLSX file ingestion adapter; the roadmap closeout also listed real file ingestion through official entrypoint and real XLSX fixture audit as not closed at that time. | `NEEDS_EVIDENCE` | Run or document a physical XLSX end-to-end evidence chain before claiming this broader status. |
| Adapter ingestion to runtime bridge is closed. | `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | Closeout lists `SERVICE_1_DOCUMENT_INGESTION_TO_XLSX_RUNTIME_BRIDGE_ADAPTER_V1` as closed at commit `f97ecd0`. | `CLOSED_COMPONENT` | Treat as a closed component, not automatically as a certified physical XLSX end-to-end scenario. |
| Active SaaS checkpoint says execution gate chain is not certified and next. | `docs/current/SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1.md` | The checkpoint states no execution gate chain was certified and names explicit gate to execution gate as next. Current tests now cover that chain. | `STALE_CHECKPOINT_SECTION` | Regenerate or supersede the checkpoint section before using it as current planning authority. |
| Active roadmap says execution gate chain and runner shadow are closed. | `docs/current/ACTIVE_ROADMAP.md` | The roadmap lists closed units 8 and 9 and clarifies runner shadow has no real runner, runtime, delivery, API, storage, or worker. | `SHADOW_COMPOSITION_PASS` | Keep this as the current roadmap status, with the shadow/no-runtime qualifier. |
| SaaS execution chain is product/runtime ready. | Possible over-reading of `Execution gate chain certified`. | Tests certify composition and shadow evidence only; source tests assert no runner/pipeline/runtime/API/storage/worker/LLM imports or calls. | `NOT_PRODUCT_READY` | Do not authorize runner, SaaS runtime, API/storage/worker, or delivery from this evidence. |
| Semantic runtime plan candidate is executable runtime. | Possible over-reading of commit `d303608`. | `service_1_semantic_runtime_plan_candidate_v1.py` states it prepares a plan candidate only and never executes computation, runtime, CLI, delivery, recalculation, reexecution, or Phase 5. Tests assert fail-closed flags. | `CANDIDATE_SHADOW_ONLY` | Freeze promotion until ADR + CapabilitySpec + ModuleContract + TaskSpec exist. |
| More semantic runtime code can continue immediately. | Roadmap momentum after `d303608`. | AGENTS.md requires ADR/CapabilitySpec/ModuleContract/TaskSpec for new capabilities and decisions. | `BLOCKED_METHODOLOGICALLY` | Decide whether the semantic lane is experimental candidate or sanctioned capability before writing more code. |

## Evidence observed in this reconciliation

Local command run by this agent from `PymIA-Live`:

```text
python -m pytest tests/smartpyme/test_service_1_semantic_runtime_plan_candidate_v1.py tests/smartpyme/test_service_1_explicit_gate_to_execution_gate_chain_v1.py tests/smartpyme/test_service_1_execution_gate_to_runner_shadow_smoke_v1.py -q
```

Observed result:

```text
20 passed in 2.32s
```

This evidence supports:

- semantic runtime plan candidate fail-closed behavior;
- SaaS adapter/explicit gate to execution gate composition;
- runner shadow smoke path without real runner, runtime, or delivery authorization.

It does not support:

- physical XLSX end-to-end certification through the official entrypoint;
- real runner invocation;
- SaaS runtime/API/storage/worker readiness;
- autonomous delivery;
- product-ready status.

## Certified facts, hypotheses, and gaps

### Certified facts

- `docs/current/` is the current authority over historical documentation.
- `SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1` declares controlled real-client use closed, with explicit non-promises: no SaaS, frontend, API, worker, autonomous delivery, definitive diagnosis, or replacement of human review.
- `SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1` is `PASS_WITH_LIMITS` for normalized payload bridge behavior.
- `ACTIVE_ROADMAP.md` currently records execution gate and runner shadow units as closed while retaining stop rules before real runner, API/storage/worker, and autonomous delivery.
- `SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1` contains stale next-front language for the execution gate chain.
- `service_1_semantic_runtime_plan_candidate_v1.py` is fail-closed and candidate-only.

### Hypotheses

- The operative closeout may have intentionally broadened the controlled-use status after component closures, but it does not by itself prove a single physical XLSX end-to-end official-entrypoint evidence run.
- The semantic runtime lane may be valuable as a future capability, but its authority must be made explicit before promotion.

### Gaps

- `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT` still needs direct evidence.
- `SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1` needs sync or supersession.
- `SEMANTIC_RUNTIME_PLAN_CANDIDATE` needs ADR/CapabilitySpec/ModuleContract/TaskSpec before it can become more than candidate/shadow.

## Next step

Choose exactly one next methodological step before writing more code:

1. **Promote or freeze the semantic lane**: create an ADR and CapabilitySpec for the bounded/semantic runtime lane, or explicitly mark it experimental candidate-only.
2. **Close physical XLSX evidence**: define and execute `CASE_001` physical XLSX end-to-end through the official entrypoint, producing folder, manifest, and `delivery_policy_guard.json` evidence.

Do not do both in the same cycle.

## Stop conditions

- No new productive code until this reconciliation is accepted.
- No SaaS runner.
- No API/storage/worker.
- No autonomous delivery.
- No second XLSX parser.
- No product-ready claim.
- No promotion of semantic runtime without ADR, CapabilitySpec, ModuleContract, TaskSpec, tests, evidence, and checkpoint.
- No broad PASS statement without naming the exact evidence boundary.
