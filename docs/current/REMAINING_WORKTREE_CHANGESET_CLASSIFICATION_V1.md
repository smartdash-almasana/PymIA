# REMAINING_WORKTREE_CHANGESET_CLASSIFICATION_V1

> **HISTORICAL SNAPSHOT — SUPERSEDED.** Este documento registra una clasificación pasada del worktree y no autoriza frentes Hermes/Conversa. Toda disposición `HOLD_SEPARATE_FRONT` para Hermes/Conversa quedó superada por `docs/current/ARCHITECTURE_BOUNDARY.md`, que los declara legacy/congelados y fuera de la arquitectura activa.

Status: HISTORICAL_SUPERSEDED_CLASSIFICATION
Baseline commit: 344116fceeac6f28471c0cbd57893771f3212614
Branch: main

## Objective

Convert the remaining dirty worktree into bounded integration fronts without destructive cleanup or cross-front commits.

## Inventory

Total status entries classified: 553.

| Cluster | Count | Disposition |
|---|---:|---|
| A_XLSX_QA_EXTERNAL_TOOLING | 6 | INTEGRATE_BOUNDED |
| B_STAGE2_GOVERNANCE_PHYSICAL_CONTROLS | 14 | INTEGRATE_WITH_SERVICE1_CORE |
| C_STAGE2_CLOSEOUT_DOCS | 10 | INTEGRATE_WITH_SERVICE1_CORE |
| D_SERVICE1_CORE_PENDING | 53 | SPLIT_AND_INTEGRATE |
| E_SERVICE1_DOCS_PENDING | 46 | SPLIT_AND_INTEGRATE |
| F_HERMES | 17 | HOLD_SEPARATE_FRONT |
| G_CONVERSA | 24 | HOLD_SEPARATE_FRONT |
| H_TELEGRAM | 6 | HOLD_SEPARATE_FRONT |
| I_LANDING | 2 | HOLD_SEPARATE_FRONT |
| J_OTHER_DOCS | 108 | DOC_REVIEW / SEPARATE_FRONTS |
| K_OTHER_TESTS | 139 | FOLLOW_OWNING_CODE_FRONT |
| L_OTHER_CODE | 105 | MULTIPLE_SEPARATE_FRONTS |
| M_CI | 2 | FOLLOW_OWNING_FEATURE |
| N_CONFIG_MISC | 21 | REVIEW_BY_OWNER_FRONT |

## Integration order

### Batch 1 — Stage 2 convergence closeout

Include only Stage 2 convergence code/tests/docs already known to belong to Packages 8–10 and closeout.
Do not include physical capability expansion or XLSX QA in this batch.

### Batch 2 — Remaining capability governance + physical controls

Includes:
- bounded governance expansion;
- V2 pathology/evidence matrices;
- six governed capabilities;
- physical positive/negative controls;
- corresponding tests/tools/docs.

### Batch 3 — XLSX P10 quality gate

Includes:
- `.skills/pymia-xlsx-quality/`;
- `service_1_xlsx_quality_gate_v1.py`;
- delivery quality-gate integration;
- QA CLI;
- QA/config tests;
- external Excel tooling audit doc.

### Batch 4+ — separate projects/fronts

Do not mix with Service 1 convergence:
- Hermes;
- Conversa;
- Telegram;
- landing;
- autonomous SaaS experiments;
- broad platform/domain/orchestration work;
- unrelated documentation and CI.

## Safety rule

No `git add -A`.
Each integration batch must be staged by explicit path list, inspected with `git diff --cached`, tested with its focal suite, and pushed only after a clean cached diff is proven.

## Verdict

PASS_WORKTREE_CLASSIFIED_FOR_INCREMENTAL_INTEGRATION

Next action: PREPARE_STAGE2_CONVERGENCE_COMMIT_BATCH_V1
