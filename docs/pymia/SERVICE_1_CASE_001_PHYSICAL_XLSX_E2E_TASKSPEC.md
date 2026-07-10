# SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_TASKSPEC

Status: Proposed
Scope: Physical XLSX evidence plan for Servicio 1 CASE_001
Code authorized: No
Runtime authorized by this document: No

## 1. Task

Define the documentary execution plan required to close:

```text
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: NEEDS_EVIDENCE
```

The future execution must prove a physical XLSX or explicit ingestion output can flow through the controlled Servicio 1 XLSX-first chain and produce a governed case folder or an honest blocked/needs-owner-input state.

This TaskSpec does not implement code. It defines the evidence contract for the next execution cycle.

## 2. Governing sources

This TaskSpec is governed by:

```text
AGENTS.md
docs/current/README.md
docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md
docs/current/SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md
docs/current/SERVICE_1_REAL_CLIENT_OPERATOR_RUNBOOK_FINAL_V1.md
docs/current/SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md
docs/current/SERVICE_1_XLSX_FIRST_ROADMAP_CLOSEOUT_AUDIT_V1.md
docs/adr/SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1.md
```

Current normalized state:

```text
SERVICE_1_OPERATIVE_XLSX_FIRST: CLOSED_FOR_CONTROLLED_REAL_CLIENT_USE_WITH_LIMITS
XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: NEEDS_EVIDENCE
SEMANTIC_RUNTIME_PLAN_CANDIDATE: CANDIDATE_SHADOW_ONLY
SERVICE_1_SEMANTIC_RUNTIME_LANE: EXPERIMENTAL_CANDIDATE_ONLY
```

## 3. Objective

The CASE_001 physical XLSX evidence cycle must validate this chain:

```text
physical XLSX or documented ingestion output
-> document ingestion adapter
-> runtime bridge
-> official XLSX-first entrypoint
-> real owner pilot case run
-> delivery packet adapter
-> controlled case folder
-> manifest.json
-> delivery_policy_guard.json
```

The goal is not autonomous delivery. The goal is evidence that the official controlled path can produce a reviewable operator case packet or a correct blocked state from a physical XLSX-backed input.

## 4. Authorized inputs

CASE_001 must define these inputs before execution:

| Input | Required | Notes |
|---|---:|---|
| `tenant_id` | Yes | Stable tenant reference for the controlled case. |
| `case_id` | Yes | Stable case reference, recommended: `case:s1:case_001`. |
| `run_id` | Yes | Stable run reference for traceability. |
| `owner_ref` | Yes | Owner reference; may be anonymized. |
| physical XLSX reference | Yes | The XLSX must be referenced, not copied into the final delivery folder. |
| `source_file_ref` | Yes | Stable reference to the source XLSX. |
| `raw_owner_narrative` | Yes | Owner pain, period, and desired decision/support. |
| `business_period_reference` | Yes | Required for this evidence cycle, even if previously only recommended. |
| `column_meaning_confirmations` | Yes | Minimum confirmations for fields used by the selected pathology. |
| `ingestion_output` | Yes | Must include `available_data_fields`, `input_values`, and `source_file_ref`. |
| operator metadata | Yes | Operator, timestamp, repo commit, and notes. |

## 5. Evidence to produce

The future CASE_001 run must produce an evidence bundle with:

```text
command transcript
repo commit hash
input fixture reference or anonymized physical XLSX reference
ingestion_output snapshot or path
source_file_ref
generated case folder path
manifest.json
delivery_policy_guard.json
product_gate.json
final_qa_delivery_gate.json
owner_message.md or next_owner_question.md
evidence_loop_status.json
final operator status
blocked_reason, if applicable
```

The evidence bundle must explicitly state who ran each command:

```text
Codex local shell
operator manual command
CI
other tool
```

Do not write "I ran tests" or "I ran CASE_001" unless the acting agent directly observed the command output.

## 6. Valid final states

The future CASE_001 execution may end in any of these valid states:

| State | Meaning | PASS condition |
|---|---|---|
| `READY_FOR_DELIVERY_POLICY_GUARD` | Folder, manifest, QA, and policy guard are present for operator review. | PASS if no runtime/delivery/autonomous flags are open. |
| `NEEDS_OWNER_INPUT` | Evidence or meaning is incomplete but the next owner question is generated. | PASS if `next_owner_question.md` or equivalent owner question evidence exists. |
| `BLOCKED_BY_EVIDENCE` | The XLSX/ingestion evidence is insufficient or malformed. | PASS if `blocked_reason` and missing evidence are explicit. |
| `BLOCKED_BY_POLICY` | A policy guard blocks unsafe claims or invalid delivery state. | PASS if the guard evidence identifies the violation. |
| `REWORK_REQUIRED` | QA or manifest/folder verification failed. | PASS only as a truthful result, not as completion of the physical E2E objective. |

A blocked or needs-owner-input result can be valid evidence if it is honest, reproducible, and traceable.

## 7. What does not count as PASS

The following do not close `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT`:

```text
only normalized payload bridge test
only unit test
only smoke without controlled case folder
only pilot pack candidate
only document closeout without command transcript
only source code inspection
missing physical XLSX or source_file_ref
missing manifest.json
missing delivery_policy_guard.json
delivery_authorized=True
runtime_authorized=True
autonomous delivery
SaaS/API/worker execution
semantic runtime lane promotion
```

## 8. Acceptance test plan for the future execution cycle

The future execution cycle must define one command or scriptable transcript that performs the run from the repository root or `PymIA-Live` root.

Minimum command evidence:

```text
# repo state
git status --short
git branch --show-current
git log -1 --oneline

# CASE_001 execution command placeholder
COMMAND_PLACEHOLDER: run CASE_001 physical XLSX evidence flow

# artifact verification command placeholder
COMMAND_PLACEHOLDER: verify generated case folder artifacts
```

The future command may be a Python snippet following `SERVICE_1_REAL_CLIENT_OPERATOR_RUNBOOK_FINAL_V1.md` if no formal CLI exists yet. If a snippet is used, the transcript must be preserved as evidence.

## 9. Required artifact checks

The artifact verification step must check:

| Artifact | Required check |
|---|---|
| case folder | Exists and path is recorded. |
| `manifest.json` | Exists, includes file inventory and hashes. |
| `delivery_policy_guard.json` | Exists and does not authorize delivery. |
| `product_gate.json` | Exists; `runtime_authorized` and `delivery_authorized` are false. |
| `final_qa_delivery_gate.json` | Exists and contains evaluated checks or blockers. |
| `owner_message.md` | Exists when a packet is ready; contains no prohibited claims. |
| `next_owner_question.md` | Exists when final state is `NEEDS_OWNER_INPUT`. |
| `evidence_loop_status.json` | Exists and records evidence loop state. |
| source XLSX | Not copied into the final delivery folder. |

## 10. Required JSON key checks

The verification must inspect JSON artifacts for at least these keys or equivalent documented fields:

```text
case_id
run_id
owner_ref
source_file_ref
status
delivery_status
runtime_authorized
delivery_authorized
autonomous_delivery_authorized
blocked_reason
warnings
files_written
hashes
```

If a field is absent because the current artifact schema uses a different name, the CASE_001 evidence report must map the actual schema key to the required meaning.

## 11. Claim guard

The future execution must block or flag owner-facing text containing claims such as:

```text
diagnóstico definitivo
auditoría
certificación
conciliación definitiva
rentabilidad real confirmada
reemplaza al contador
entrega automática
autonomous delivery
```

Allowed owner-facing language remains limited to preliminary, evidence-bound operational findings and owner questions.

## 12. Stop conditions

Stop immediately if any of these occurs:

```text
working tree dirty with unrelated files
second XLSX parser is required
SaaS runner is required
API/storage/worker is required
autonomous delivery is required
semantic runtime promotion is required
productive code modification is required
runtime_authorized=True appears unexpectedly
delivery_authorized=True appears unexpectedly
source XLSX is copied into final delivery folder
manifest.json cannot be produced
policy guard cannot be produced
owner-facing text contains prohibited claims
```

If a stop condition occurs, the result must be recorded as `BLOCKED_BY_EVIDENCE`, `BLOCKED_BY_POLICY`, or `REWORK_REQUIRED`, not hidden.

## 13. Relationship to existing documents

| Document | Relationship |
|---|---|
| `SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md` | Defines the current gap this TaskSpec targets: `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT: NEEDS_EVIDENCE`. |
| `SERVICE_1_OPERATIVE_XLSX_FIRST_CLOSEOUT_V1.md` | Defines the controlled-use closeout and final allowed operator states. |
| `SERVICE_1_REAL_CLIENT_OPERATOR_RUNBOOK_FINAL_V1.md` | Provides the operational flow and expected folder artifacts. |
| `SERVICE_1_XLSX_RUNTIME_BRIDGE_CASE_RUN_AUDIT_V1.md` | Remains scoped normalized-payload evidence; this TaskSpec targets the broader physical XLSX evidence gap. |
| `SERVICE_1_XLSX_FIRST_ROADMAP_CLOSEOUT_AUDIT_V1.md` | Identifies historical not-closed items: real file ingestion, physical delivery folder integration, real XLSX fixture audit. |
| `SERVICE_1_SEMANTIC_RUNTIME_LANE_CLASSIFICATION_ADR_V1.md` | Keeps semantic runtime candidate work frozen as `EXPERIMENTAL_CANDIDATE_ONLY`; not part of CASE_001 physical evidence closure. |

## 14. Files authorized in the future execution cycle

This TaskSpec itself authorizes no code changes.

A later execution cycle may create only evidence artifacts unless a separate TaskSpec authorizes code changes.

Expected future evidence locations may include:

```text
.tmp/service_1_cases/<case_dir>/
docs/current/<future CASE_001 evidence checkpoint>.md
```

The original physical XLSX must not be committed unless explicitly anonymized and authorized by a separate data-handling decision.

## 15. PASS criteria for this TaskSpec

This TaskSpec is complete when:

```text
- it defines the CASE_001 physical XLSX E2E objective
- it defines required inputs
- it defines required evidence artifacts
- it defines valid final states
- it defines what does not count as PASS
- it defines artifact and JSON verification requirements
- it defines stop conditions
- it preserves semantic lane freeze and SaaS/runtime/delivery boundaries
```

## 16. Status

```text
SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_TASKSPEC: PROPOSED
CODE_CHANGE_AUTHORIZED_BY_THIS_TASKSPEC: NO
NEXT_REQUIRED_STEP: review and accept this TaskSpec before running CASE_001
```
