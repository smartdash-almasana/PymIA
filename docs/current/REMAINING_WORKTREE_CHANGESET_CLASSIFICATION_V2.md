# REMAINING_WORKTREE_CHANGESET_CLASSIFICATION_V2

> **HISTORICAL SNAPSHOT — SUPERSEDED.** Esta clasificación conserva el estado observado del worktree en su baseline, pero ya no constituye roadmap activo. Los clusters `B_HERMES_MCP` y `C_CONVERSA` no son frentes separados a retener: quedaron supersedidos por `docs/current/ARCHITECTURE_BOUNDARY.md` y sólo pueden conservarse como evidencia histórica/museo, sin reactivación de runtime, wrappers, aliases, shims, fallbacks ni rutas paralelas.

## Baseline

- HEAD/origin baseline: `13813cbe3a2fef9c57febe213048e5baef53aa12`
- Context: Stage 2 convergence/governance and XLSX QA/P10 already integrated.
- Scope of this document: classify only the remaining dirty worktree.
- No staging, deletion, reset, clean, commit or push performed.

## Snapshot

Total worktree entries: `314`

| Cluster | Count | Treatment |
|---|---:|---|
| A_AUTONOMOUS_SAAS_SERVICE1 | 20 | active candidate; audit before integration |
| B_HERMES_MCP | 23 | separate front; do not mix with Service 1 |
| C_CONVERSA | 24 | separate front; do not mix with Service 1 |
| D_TELEGRAM | 6 | separate front |
| E_LANDING | 2 | separate front |
| F_CI_WORKFLOWS | 2 | separate front; validate independently |
| G_SERVICE1_REMAINDER | 47 | mixed docs/tests; reconcile before commit |
| H_PLATFORM_DOCS | 91 | documentary/platform archaeology; not active by default |
| I_PLATFORM_CODE | 24 | broad platform code; independent architecture audit required |
| J_PLATFORM_TESTS | 62 | tests coupled to platform code; not a standalone commit |
| K_CONFIG_MISC | 13 | config/scripts; inspect individually |

## Interpretation

### A — Autonomous SaaS / Service 1

Contains autonomous-SaaS contracts/checkpoints, owner-evidence chain docs, real-client pilot docs, `pymia/microsaas/` and `tests/microsaas/`.

This is the strongest next active product candidate, but it must not be committed merely because it is grouped. It needs a bounded audit against current Service 1 invariants, especially:

- deterministic runtime authority;
- no LLM authority in Service 1 runtime;
- one canonical product root;
- no alternate execution route;
- owner confirmation as evidence, never authorization;
- compatibility with the now-integrated P0–P10 authority chain.

### B — Hermes / MCP

Independent architectural front. Keep isolated from Service 1 integration commits.

### C — Conversa

Independent conversational front, including `conversa-engine`, conversation contracts, scripts and tests. Keep isolated.

### D — Telegram

Runtime/channel front. Keep isolated from Service 1 core and autonomous-SaaS contracts.

### E — Landing

Presentation-only front. Separate commit if retained.

### F — CI workflows

Two workflows. Validate triggers, branches, secrets assumptions and relevance before integration.

### G — Service 1 remainder

This cluster is not homogeneous. It includes:

- modified canonical/current Service 1 docs;
- accounting/workpaper contracts;
- older closeouts and case/task specs;
- pilot evidence;
- one untracked governance-expansion test already related to integrated work.

Do not commit this cluster wholesale. First reconcile which documents are current authority, which are retained evidence, and which are residue superseded by the commits already integrated.

### H — Platform docs

Largest documentary cluster. Treat as documentary archaeology/reference until proven active. Do not infer authority from filename or directory alone.

### I + J — Platform code and tests

These form one broad platform/frontier rather than two integration batches. They include orchestration, document intelligence, LLM operator, narrative, domain, pipeline radiography, adapters and their tests.

Do not integrate piecemeal without an architecture boundary audit. Several of these areas previously caused collection/import failures when mixed with Service 1 work.

### K — Config / misc

Includes `.gitignore`, `.graphifyignore`, root docs, `pyproject.toml`, `pytest.ini`, utility scripts and `task.md`. Inspect individually; never stage as a convenience bundle.

## Recommended order

1. `AUDIT_AUTONOMOUS_SAAS_SERVICE1_BATCH_V1`
2. `RECONCILE_SERVICE1_REMAINDER_V1`
3. Hermes/MCP as its own project front
4. Conversa as its own project front
5. Telegram
6. CI / landing / config individually
7. Platform code+tests only after a dedicated architecture audit
8. Platform docs only after authority/reference reconciliation

## Guardrail

The remaining worktree is not one backlog and must not be reduced with blanket staging or destructive cleanup.

Allowed integration pattern:

```text
classify
→ audit bounded cluster
→ validate dependencies
→ run focal tests
→ inspect staged diff
→ commit one coherent front
```

Forbidden:

```text
git add -A
git clean
git reset --hard
blanket restore
cross-front commit
```

## Verdict

`PASS_REMAINING_WORKTREE_RECLASSIFIED_V2`

The next recommended action is `AUDIT_AUTONOMOUS_SAAS_SERVICE1_BATCH_V1`.
