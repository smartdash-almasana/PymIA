# SERVICE_1_MATURITY_MAP_POST_INVOICE_COLLECTION_V1

## Status

```text
MATURITY_CONTROL_DOCUMENT
```

## Purpose

Update the Servicio 1 maturity map after the invoice/collection matching sandbox completion slice.

This document is not a new runtime contract, not a new feature, and not a roadmap expansion. It records the current maturity distribution across Servicio 1 microcycles and identifies the next safe development front.

## Current validation point

```text
HEAD:
8094c6a feat(pymia-live): add invoice collection matching sandbox slice

FULL_SUITE:
PASS — 1147 passed in 93.41s

WORKING_TREE_AT_VALIDATION:
CLEAN
```

## Recent cycle window

```text
8094c6a feat(pymia-live): add invoice collection matching sandbox slice
33a859d docs(pymia): add service 1 operator ready packet
573b5e6 docs(pymia): close service 1 post-slices state
70738d4 test(pymia-live): reconcile service 1 test expectations
d8c7e78 feat(pymia-live): add bank reconciliation sandbox completion slice
f0d363b feat(pymia-live): add accounting workpaper completion slice
c54d610 test(pymia-live): add service 1 synthetic real case pilot
51cc37c test(pymia-live): add service 1 microservice chain dry run
d6c2188 feat(pymia-live): add service 1 microservice activation contract
c8a71b0 feat(pymia-live): add service 1 microservice registry contract
```

## Maturity scoring model

Maturity percentages are operational estimates, not mathematical guarantees.

Criteria:

```text
- Code exists and is bounded.
- Tests exist and pass.
- Output artifacts are reviewable.
- Documentation exists.
- Human-review limits are explicit.
- Scope is safe against overclaims.
- Route is close to controlled operator use.
- Route is close to real-client readiness.
```

## Current maturity map

| Microcycle | Previous maturity | Current maturity | Status | Notes |
|---|---:|---:|---|---|
| First Aid tools base | 90% | 90% | HIGH | Five tools, XLSX delivery, owner/operator outputs, full suite green. Needs more real/semi-real cases, not more abstract contracts. |
| XLSX Delivery / files as product | 88% | 88% | HIGH | Core file-output layer remains solid. Used by accounting workpaper, bank sandbox, and invoice/collection sandbox. |
| Operator Harness V1/V2 | 85% | 85% | HIGH | Harness, delivery package, manifest, audit, and decision layers exist. Needs operator rehearsal, not more harness abstraction. |
| Synthetic Real Case Pilot | 82% | 82% | HIGH | End-to-end synthetic rehearsal exists. Still not real-client proof. |
| Accounting Workpaper Draft | 78% | 78% | MEDIUM_HIGH | Produces draft packet. Needs accountant review with realistic expectations. |
| Bank Reconciliation Sandbox | 76% | 76% | MEDIUM_HIGH | Fixture-only review packet exists. No real extract parsing, no final reconciliation, no bank API. |
| Invoice / Collection Matching | 48% | 70% | MEDIUM_HIGH | Moved from contract-only to sandbox review packet after 8094c6a. Still lacks real anonymized fixture and policies for partial payments/duplicates. |
| Excel Treatment Lab | 68% | 68% | MEDIUM | Strong conceptual/code base, but no completion slice yet. Best next functional target. |
| File Intake / TaskSpec boundary | 72% | 72% | MEDIUM_HIGH | Safe boundaries exist. Needs more integration into operator flow. |
| Owner Output / Owner Message | 75% | 75% | MEDIUM_HIGH | Renderers and formatters exist. Needs cross-route consistency review. |
| Delivery Manifest / Audit / Case Folder | 83% | 83% | HIGH | Enough governance exists. Do not expand unless a concrete delivery gap appears. |
| Microservice Registry / Activation | 70% | 70% | MEDIUM | Useful as map/blocking layer. Do not deepen now. |
| Supplier / Purchase Review | 50% | 50% | MEDIUM_LOW | Contract exists, no completion slice. Candidate after Excel Treatment Lab or real-client rehearsal. |
| Mercado Pago Reconciliation | 30% | 30% | LOW_DEFERRED | Contract only. Blocked until domain evidence exists. Do not implement now. |
| Real-client delivery readiness | 35% | 38% | LOW_MEDIUM | Slightly improved due operator packet and stronger sandbox slices, but still not validated with a controlled real/anonymized case. |
| Operator Ready Packet | 80% | 82% | HIGH_DOCUMENTAL | Exists and is commit-validated. Needs actual operator rehearsal. |
| Servicio 1 as assisted sellable product | 65% | 70% | MEDIUM_HIGH | Stronger after invoice/collection sandbox, but still lacks first controlled real-client execution and commercial SOP. |

## Maturity movement after 8094c6a

Primary change:

```text
Invoice / Collection Matching:
48% → 70%
```

Reason:

```text
Moved from contract-only representation to implemented sandbox completion slice with:
- synthetic fixture,
- deterministic conservative matching,
- XLSX review packet,
- owner summary,
- operator notes,
- output hashes,
- tests,
- product documentation,
- full-suite validation.
```

Global effect:

```text
Servicio 1 technical maturity increased moderately.
Accounting-adjacent maturity increased materially.
Real-client readiness increased only slightly.
```

## Current maturity by dimension

| Dimension | Maturity | Status | Comment |
|---|---:|---|---|
| Code + tests | 90% | HIGH | Full suite passes: 1147 tests. Several deterministic slices are implemented. |
| Reviewable file outputs | 82% | HIGH | XLSX, owner summaries, operator notes, hashes exist across key slices. |
| Accounting-adjacent sandbox capability | 76% | MEDIUM_HIGH | Accounting workpaper, bank sandbox, and invoice/collection sandbox are now covered. |
| Operator guidance | 82% | HIGH_DOCUMENTAL | Operator Ready Packet exists. Needs human rehearsal. |
| Product documentation | 84% | HIGH | Closeouts, contract docs, operator packet, and slice docs exist. |
| Real-client readiness | 38% | LOW_MEDIUM | No controlled real/anonymized client case has been executed through the current operator packet. |
| Commercial packaging | 55% | MEDIUM_LOW | Product claim boundaries are clearer, but pricing/SOP/onboarding are still not closed. |
| External integrations | 20% | LOW_BLOCKED | APIs, OCR, Mercado Pago, and live ingestion are intentionally blocked. |

Estimated global maturity:

```text
SERVICE_1_GLOBAL_MATURITY_POST_8094C6A: ~75%
```

Interpretation:

```text
Servicio 1 is technically strong and increasingly operable as an assisted, human-reviewed file/output service.
It is not yet proven as a repeatable real-client delivery service.
```

## Most immature fronts remaining

### 1. Mercado Pago Reconciliation

```text
Maturity: 30%
Status: DEFERRED
```

Reason:

```text
There is not enough domain evidence about real exports, operation dates, settlement dates, fees, retentions, chargebacks, bank settlement relationships, identifiers, and Argentine edge cases.
```

Allowed now:

```text
Contract-level representation only.
```

Blocked now:

```text
Completion slice.
Matching logic.
API.
Settlement claim.
Production claim.
```

### 2. Real-client delivery readiness

```text
Maturity: 38%
Status: NOT_READY_FOR_UNBOUNDED_CLIENT_USE
```

Reason:

```text
The system has synthetic/sandbox proof, but not a controlled real/anonymized case executed through the operator packet.
```

Next safe movement:

```text
Run an internal operator rehearsal.
Then run a controlled anonymized real-like case.
```

### 3. Supplier / Purchase Review

```text
Maturity: 50%
Status: CONTRACT_ONLY_OR_NEAR_CONTRACT
```

Reason:

```text
Contract exists, but no sandbox completion slice exists yet.
```

Safe later movement:

```text
Supplier/purchase sandbox completion slice, after Excel Treatment Lab or real-client rehearsal.
```

## Next recommended functional slice

```text
EXCEL_TREATMENT_LAB_COMPLETION_SLICE_V1
```

Reason:

```text
It strengthens the core commercial value of Servicio 1:
file in,
reviewable file out,
owner summary,
operator notes,
deterministic XLSX artifact,
human review.
```

Why before more accounting-adjacent slices:

```text
Servicio 1 cannot become only an accounting sandbox family.
Its core product thesis is files as product, Excel treatment, and assisted operational data cleanup.
Excel Treatment Lab is central to that thesis.
```

## Required guardrails for Excel Treatment Lab

The next slice must preserve:

```text
No real-client production claim.
No autonomous runtime.
No LLM/chat autonomy.
No API.
No OCR.
No Servicio 2 diagnosis.
No final accounting claim.
No fiscal/tax claim.
Human review remains mandatory.
```

Expected allowed outputs:

```text
excel_treatment_lab_review_packet.xlsx
owner_summary_excel_treatment_lab.txt
operator_notes_excel_treatment_lab.txt
output_hashes
```

Expected allowed scope:

```text
Synthetic or controlled fixture.
Deterministic file-shape/treatment summary.
Reviewable XLSX output.
Operator notes.
Limitations and forbidden claims.
```

## No-go list before next commit cycle

```text
Do not open Mercado Pago.
Do not open real-client production delivery.
Do not open chatbot/autonomous agent runtime.
Do not open API integrations.
Do not open OCR/parser runtime.
Do not open Servicio 2.
Do not add another registry/activation/harness layer.
Do not add broad architecture documents.
```

## Recommended sequence

```text
1. Commit this maturity map.
2. Push.
3. Run docs-only validation or full suite if desired.
4. Open EXCEL_TREATMENT_LAB_COMPLETION_SLICE_V1.
5. Keep the slice small and artifact-centered.
6. Run focal tests and full suite.
```

## Closeout verdict

```text
SERVICE_1_MATURITY_MAP_POST_INVOICE_COLLECTION_V1:
READY_FOR_COMMIT

NEXT_FUNCTIONAL_FRONT:
EXCEL_TREATMENT_LAB_COMPLETION_SLICE_V1

CURRENT_GLOBAL_MATURITY:
~75%

CURRENT_PRIMARY_RISK:
REAL_CLIENT_READINESS_NOT_YET_PROVEN
```
