# Service 1 Documentary Reconciliation V1

Status: DOCUMENTARY_RECONCILIATION
Date: 2026-07-10
Scope: Servicio 1 XLSX-first closeout, active roadmap, SaaS checkpoint, and semantic runtime candidate lane.

## Verdict

Servicio 1 has multiple valid but differently scoped status documents. This reconciliation normalizes their meaning so future work does not treat a scoped PASS as broader product readiness.

```text
SERVICE_1_OPERATIVE_XLSX_FIRST: CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: PASS_WITH_LIMITS
SAAS_EXECUTION_GATE_CHAIN: SHADOW_COMPOSITION_PASS
REAL_RUNNER: BLOCKED
AUTONOMOUS_DELIVERY: BLOCKED
SEMANTIC_RUNTIME_PLAN_CANDIDATE: EXPERIMENTAL_CANDIDATE_ONLY
```

The operative XLSX-first lane is closed for controlled real-client use with limits. Physical XLSX end-to-end execution through the official entrypoint is now evidenced as `PASS_WITH_LIMITS` by CASE_001: XLSX intake reached governed folder creation and policy-gate artifacts, but the case remains at owner column-confirmation stage. The SaaS lane remains shadow/composition-only: no real runner, no SaaS runtime, no API/storage/worker, and no autonomous delivery. The semantic runtime candidate added by `d303608` is now classified as `EXPERIMENTAL_CANDIDATE_ONLY` by ADR + CapabilitySpec; promotion beyond that still requires ModuleContract, TaskSpec, tests, evidence, and checkpoint.

## Normalized states

| State key | Normalized state | Meaning |
|---|---|---|
| `SERVICE_1_OPERATIVE_XLSX_FIRST` | `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS` | Controlled operator use is allowed within the documented closeout limits. |
| `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT` | `PASS_WITH_LIMITS` | CASE_001 proves physical XLSX intake through the official operator entrypoint into a governed folder with manifest, policy guard, product gate, QA gate, and owner-question evidence; computation/dry-run remains pending owner column confirmations. |
| `SAAS_EXECUTION_GATE_CHAIN` | `SHADOW_COMPOSITION_PASS` | Composition through execution gate and runner shadow is tested, but no real runner/runtime/delivery is authorized. |
| `REAL_RUNNER` | `BLOCKED` | Runner invocation remains out of scope until a future authorized phase. |
| `AUTONOMOUS_DELIVERY` | `BLOCKED` | No owner-facing autonomous delivery is authorized. |
| `SEMANTIC_RUNTIME_PLAN_CANDIDATE` | `EXPERIMENTAL_CANDIDATE_ONLY` | ADR + CapabilitySpec classify the semantic lane as experimental candidate only; it remains fail-closed and non-runtime. |

## Source precedence after reconciliation

This document does not erase prior evidence documents. It narrows how each source may be used after reconciliation.

| Source | Still valid for | Not valid for |
|---|---|---|
| `docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` | Scoped normalized-payload bridge evidence and `PASS_WITH_LIMITS` boundary claims. | Superseding CASE_001 physical XLSX evidence or claiming computation/dry-run/delivery readiness. |
| `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | Controlled-use closeout of the operative XLSX-first lane, with explicit non-promises. | Claiming SaaS, autonomous delivery, product-ready status, or physical XLSX end-to-end evidence beyond the documented limits. |
| `docs/current/ACTIVE_ROADMAP.md` | Current SaaS shadow/composition roadmap and stop rules. | Claiming real runner invocation, SaaS runtime, API/storage/worker readiness, or autonomous delivery. |
| `docs/current/SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1.md` | Historical checkpoint for the SaaS adapter state before execution-gate and runner-shadow tests closed. | Current next-front planning for execution-gate work already covered by later tests and `ACTIVE_ROADMAP.md`. |
| `d303608` semantic runtime plan candidate | Candidate-only fail-closed planning evidence, now governed by semantic runtime ADR + CapabilitySpec. | Promoting a semantic runtime capability beyond `EXPERIMENTAL_CANDIDATE_ONLY` without ModuleContract, TaskSpec, tests, evidence, and checkpoint. |

In short:

```text
XLSX_AUDIT remains valid as scoped evidence.
XLSX_AUDIT is superseded only for next-front planning.
OPERATIVE_CLOSEOUT remains valid as controlled-use closeout.
ACTIVE_ROADMAP remains valid for SaaS shadow/composition, not runtime/autonomous delivery.
CASE_001_EVIDENCE supersedes the prior XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT gap only up to PASS_WITH_LIMITS.
```

## Claim reconciliation

| Claim | Source | Evidence | Corrected state | Methodological action |
|---|---|---|---|---|
| Service 1 operative XLSX-first is closed for controlled real-client use. | `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | The closeout declares `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE` and lists adapter, real-owner pilot case run, delivery packet adapter, folder smoke, safe case dir, and operator runbook as closed. | `CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS` | Preserve the closeout, but always carry the limits in references and planning. |
| The XLSX bridge case-run audit is complete. | `docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` | The audit declares `PASS_WITH_LIMITS`, with normalized-payload bridge coverage and explicit boundaries: no parser, no file IO, no delivery folder. | `PASS_WITH_LIMITS` | Do not expand this PASS into physical XLSX end-to-end evidence. |
| Physical XLSX ingestion through the official entrypoint is certified. | `SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_V1.md` | CASE_001 used a physical XLSX through the existing operator CLI and produced a governed folder with `manifest.json`, `delivery_policy_guard.json`, `product_gate.json`, `final_qa_delivery_gate.json` (`10/10` checks), and `column_confirmation_packet.json`. | `PASS_WITH_LIMITS` | Treat as physical XLSX E2E evidence through intake/folder governance only; owner column confirmations are still required before computation/dry-run. |
| Adapter ingestion to runtime bridge is closed. | `docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | Closeout lists `SERVICE_1_DOCUMENT_INGESTION_TO_XLSX_RUNTIME_BRIDGE_ADAPTER_V1` as closed at commit `f97ecd0`. | `CLOSED_COMPONENT` | Treat as a closed component, not automatically as a certified physical XLSX end-to-end scenario. |
| Active SaaS checkpoint says execution gate chain is not certified and next. | `docs/current/SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1.md` | The checkpoint states no execution gate chain was certified and names explicit gate to execution gate as next. Current tests now cover that chain. | `STALE_CHECKPOINT_SECTION` | Regenerate or supersede the checkpoint section before using it as current planning authority. |
| Active roadmap says execution gate chain and runner shadow are closed. | `docs/current/ACTIVE_ROADMAP.md` | The roadmap lists closed units 8 and 9 and clarifies runner shadow has no real runner, runtime, delivery, API, storage, or worker. | `SHADOW_COMPOSITION_PASS` | Keep this as the current roadmap status, with the shadow/no-runtime qualifier. |
| SaaS execution chain is product/runtime ready. | Possible over-reading of `Execution gate chain certified`. | Tests certify composition and shadow evidence only; source tests assert no runner/pipeline/runtime/API/storage/worker/LLM imports or calls. | `NOT_PRODUCT_READY` | Do not authorize runner, SaaS runtime, API/storage/worker, or delivery from this evidence. |
| Semantic runtime plan candidate is executable runtime. | Possible over-reading of commit `d303608`. | `service_1_semantic_runtime_plan_candidate_v1.py` states it prepares a plan candidate only and never executes computation, runtime, CLI, delivery, recalculation, reexecution, or Phase 5. ADR + CapabilitySpec classify the lane as `EXPERIMENTAL_CANDIDATE_ONLY`. Tests assert fail-closed flags. | `EXPERIMENTAL_CANDIDATE_ONLY` | Freeze promotion beyond candidate-only until ModuleContract + TaskSpec + tests + evidence checkpoint exist. |
| More semantic runtime code can continue immediately. | Roadmap momentum after `d303608`. | ADR + CapabilitySpec already classify the lane as `EXPERIMENTAL_CANDIDATE_ONLY`; AGENTS.md still requires ModuleContract, TaskSpec, tests, and evidence before promotion. | `BLOCKED_METHODOLOGICALLY_BEYOND_EXPERIMENTAL_CANDIDATE` | Do not write promotion/runtime code until the remaining contract chain exists. |

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

- full CASE_001 computation/dry-run after owner column confirmations;
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
- `SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_V1.md` closes physical XLSX E2E evidence as `PASS_WITH_LIMITS` through intake/folder governance.
- Semantic runtime ADR + CapabilitySpec classify the lane as `EXPERIMENTAL_CANDIDATE_ONLY`.

### Hypotheses

- The next CASE_001 run may proceed to computation/dry-run only after owner column confirmations are supplied.
- The semantic runtime lane may be valuable as a future capability, but its authority beyond `EXPERIMENTAL_CANDIDATE_ONLY` must be made explicit before promotion.

### Gaps

- CASE_001 still needs owner column confirmations before computation/dry-run.
- `SERVICE_1_AUTONOMOUS_SAAS_CURRENT_CHECKPOINT_V1` needs sync or supersession.
- `SEMANTIC_RUNTIME_PLAN_CANDIDATE` already has ADR + CapabilitySpec; it still needs ModuleContract, TaskSpec, tests, evidence, and checkpoint before it can become more than `EXPERIMENTAL_CANDIDATE_ONLY`.

## Next step

Proceed with one narrow methodological front:

```text
owner column confirmations -> re-run CASE_001 -> optional dry-run candidate
```

This is not authorization for runner, SaaS runtime, API/storage/worker, autonomous delivery, final diagnosis, or semantic runtime promotion. It is only the next evidence step after the CASE_001 intake/folder-governance `PASS_WITH_LIMITS`.

## Stop conditions

- No new productive code until this reconciliation is accepted.
- No SaaS runner.
- No API/storage/worker.
- No autonomous delivery.
- No second XLSX parser.
- No product-ready claim.
- No promotion of semantic runtime beyond `EXPERIMENTAL_CANDIDATE_ONLY` without ModuleContract, TaskSpec, tests, evidence, and checkpoint.
- No broad PASS statement without naming the exact evidence boundary.
