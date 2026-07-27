# SERVICE_1_COLD_WORKTREE_CLASSIFICATION_AND_CLEANUP_AUDIT_V1

**Front:** COLD_WORKTREE_CLASSIFICATION_AND_CLEANUP_AUDIT_V1
**Date:** 2026-07-27
**Auditor:** opencode/deepseek-v4-flash-free (local)
**Ruleset:** AGENTS.md startup contract + explicit front rules
**Verdict:** COLD_AUDIT_PASS — 1 GENERATED_IGNORE pattern restored, 0 files deleted, 0 committed

---

## 1. Sources read

- AGENTS.md
- ARCHITECTURE_GUARDRAILS.md
- docs/current/README.md
- docs/current/ACTIVE_ROADMAP.md
- docs/current/SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md
- .gitignore
- .graphifyignore

## 2. Initial baseline

| Property | Value |
|---|---|
| HEAD | `52246ec2acf7cc5d4f62c83cae4086b6337ded86` |
| Branch | `main` |
| Recent commit | `refactor(service1): align execution on governed computation input` |
| Tracked modified (M) | 111 files |
| Untracked (??) | ~400+ files across pymia/, tests/, docs/, tools/, scripts/, etc. |
| Initial dirty paths | 111 M + many ?? |
| .gitignore patterns removed | `*$py.class`, `.ipynb_checkpoints`, `vertical_slice_storage/`, `ENV/`, `build/`, `dist/`, `*.egg-info/`, `!prueba_excels/...` |

## 3. Classification table

### KEEP_TRACKED_CHANGE (111 files)

All 111 modified tracked files are valid in-progress changes from the ongoing Stage 2 / Stage 3 development. These include:

- `.gitignore` — governance restructuring (removed stale patterns, added temp pytest patterns)
- `pymia/*.py` — core engine evolution (column understanding, semantic pipeline, product pipeline, controlled execution, variable family bindings, storage, etc.)
- `tests/*.py` — test updates matching code changes
- `docs/current/*.md` — current architecture docs updated
- `docs/producto/*.md` — product contracts updated
- `tools/*.py` — tool updates

No action taken. These are the active work-in-progress.

### KEEP_UNTRACKED (~200+ files/dirs)

Valid new untracked content that must be preserved for future integration:

| Area | Content | Rationale |
|---|---|---|
| `pymia/` new modules | audit_result, contracts, diagnostic_core, document_intelligence, domain, faithful_operator, hermes, interfaces, llm_operator, mcp_server, microsaas, narrative, operational_harness, orchestration, pipeline, pipeline_radiography, smartpyme new files | New source code — belongs to active development fronts (Service 1 expansion, Hermes, domain layer, etc.) |
| `tests/` new modules | architecture/, contracts/, diagnosticcore/, docs/, document_intelligence/, domain/, e2e/, fixtures/, golden_findings/, hermes/, interfaces/, llm_operator/, mcp/, microsaas/, orchestration/, pipeline/, scn/, scripts/, services/, smartpyme/ e2e/, telegram_runtime/, utils/ | Tests for new capabilities — must stay with their code |
| `scripts/` | demo, hashline, hermes_sync, conversa local, smoke tests | Operational scripts for running/demoing |
| `tools/` new files | document_context_classifier, excel_evidence, memory/, service_1_*_v1.py | New diagnostic/governance tools |
| `.github/workflows/` | m31p-textil-pilot, smartpyme-radiography | CI workflow definitions |
| `.skills/pymia-xlsx-quality/` | XLSX quality skill | Explicitly protected by front rules |
| `conversa-engine/` | Conversa engine | Working engine, not temp |
| `_docs_inbox/` | Working docs inbox | Active working directory |
| `src/App.tsx` | Web frontend source | Valid source file |
| `pytest.ini` | Pytest config | Valid (untracked by design) |
| `task.md` | Active task file | Working artifact |
| `docs/current/*.md` (new) | ~35 current docs | Active docs per docs/current/README.md authority |
| `docs/pathology_catalog.enriched.v2.json` | Pathology catalog data | Canonical data |
| `docs/service_1_formula_pathology_evidence_matrix.v2.json` | Evidence matrix data | Canonical data |
| `docs/conversa-engine/` | Engine docs | Documentation |

### GENERATED_IGNORE (1 pattern)

| Path | Reason | Action |
|---|---|---|
| `pymia.egg-info/` (5 files) | Python build artifact — `*.egg-info/` was incorrectly removed from .gitignore in the current change set | Added `*.egg-info/` back to `.gitignore` (line 41). Also restored `build/` and `dist/` for completeness. |

### SAFE_DELETE (0 files)

No unambiguous temp/trash files found outside .gitignore coverage. All typical candidates (`__pycache__/`, `*.pyc`, `.pytest_cache/`, `.tmp/`, `.tmp_pytest_*`, `.coverage`) are already properly ignored by `.gitignore`.

### DOCUMENTATION_REVIEW_REQUIRED (~250+ files)

All untracked files under `docs/` that are NOT in `docs/current/` qualify as historical/legacy/museum documentation that requires a separate documentary audit. These include:

| Directory | File count (approx) | Notes |
|---|---|---|
| `docs/adr/` | ~18 | Untracked ADRs — some superseded, some ADR-007 governed |
| `docs/arquitectura/` | ~18 | Historical architecture docs |
| `docs/auditoria/` | ~35 | Historical audit artifacts — may include quarantine dirs |
| `docs/contracts/` | ~2 | Untracked contract specs |
| `docs/producto/` | ~120+ | Historical product docs — some superseded by docs/current/ |
| `docs/pymia/` | ~80+ | Historical pymia docs — M-series specs, checkpoints |
| `docs/smartpyme/` | ~40 | Historical smartpyme docs |
| `docs/` root | ~8 | Top-level docs (DEPRECATED_DOCS, MUSEUM_CATALOG, etc.) |
| `docs/hermes/`, `docs/microsaas/`, `docs/ops/`, `docs/prompts/`, `docs/refactor/`, `docs/roadmap/`, `docs/transient-design/`, `docs/vision/` | various | Sub-area historical docs |
| `docs/ingenieria_conversacional.*.md` | ~9 | Conversational engineering docs |
| `docs/migrado_desde_smartpyme_*.md` | ~8 | Migrated docs from SmartPyme |

**Action:** NO_TOUCH per front rules. Requires `DOCUMENTARY_PURGE_AUDIT_V2` or equivalent.

### CONCURRENT_DO_NOT_TOUCH (0 files)

All modified and untracked files appear to belong to the same active development front (Service 1 Stage 2/3 convergence). No evidence of concurrent work from another branch or operator was found.

## 4. Execution summary

### What was deleted

Nothing. Zero files deleted. All SAFE_DELETE candidates were already covered by `.gitignore`.

### What was added to .gitignore

```
*.egg-info/
build/
dist/
```

These patterns were in the committed `.gitignore` but were removed in the current change set. `pymia.egg-info/` was actively generating untracked files (`git ls-files --others` listed 5 files). The other two (`build/`, `dist/`) are standard Python build artifacts restored for completeness.

### What was left untouched

- All 111 modified tracked files (KEEP_TRACKED_CHANGE)
- All ~400 untracked source/test/config/data files (KEEP_UNTRACKED)
- All ~250 untracked historical docs (DOCUMENTATION_REVIEW_REQUIRED)
- All already-ignored temp artifacts (`.tmp/`, `.tmp_pytest_*`, `__pycache__/`, etc.)
- `.gitignore` was only modified to add `*.egg-info/`, `build/`, `dist/` — no existing patterns were altered

## 5. Validation

| Check | Result |
|---|---|
| `git status --short` | 111 M + many ?? — only change is `.gitignore` showing additional M (our edit) |
| `git diff --check` | No whitespace errors (CRLF warnings only, pre-existing) |
| `pymia.egg-info/` now ignored | Confirmed by `git check-ignore -v` at `.gitignore:41:*.egg-info/` |
| No temp files unignored | Zero `.pyc`, `.tmp`, `.log` files in `git ls-files --others --exclude-standard` |
| Branch unchanged | `main` (no checkout, no branch creation) |
| HEAD unchanged | `52246ec2acf7cc5d4f62c83cae4086b6337ded86` |
| Commit created | false |
| Push performed | false |

## 6. Remaining risks

1. **Docs/ tree bloat**: ~250 untracked historical docs consume worktree space and cognitive load. They may contain superseded, conflicting, or incorrect information. `docs/current/README.md` already subordinates them, but they remain visible and searchable.
2. **Modified .gitignore**: The current change set removed several standard Python ignore patterns (`*$py.class`, `.ipynb_checkpoints`, `vertical_slice_storage/`, `ENV/`). These were NOT restored because they don't currently produce untracked files. If any of those directories or files appear in the future, they will show as untracked.
3. **Stale state document**: `SERVICE_1_ENTERPRISE_EXECUTION_STATE_V1.md` records `working_tree: CLEAN / dirty_paths: 0` which is no longer accurate. This is expected for an active worktree but could cause confusion during cold recovery.
4. **`pytest.ini` vs `pyproject.toml`**: `pytest.ini` is untracked while `pyproject.toml` (modified tracked) may also contain pytest config. This could cause duplicate or conflicting config.

## 7. Next recommended action

```text
EXECUTE_DOCUMENTARY_PURGE_AUDIT_V2
```

Run a separate, read-only audit of all untracked files under `docs/` (excluding `docs/current/`) to classify as SUPERSEDED, KEEP_REFERENCE, or CANDIDATE_DELETION. This audit must:

1. Cross-reference each doc against `docs/current/` authority
2. Check the ADR trail for supersession evidence
3. Check git log for last meaningful update
4. Classify each doc as KEEP, SUPERSEDED, or DELETE
5. Only delete after explicit authorization and documentation gate

---

## VERDICT

```
HEAD: 52246ec2acf7cc5d4f62c83cae4086b6337ded86
BRANCH: main
INITIAL_DIRTY_PATHS: 111 M + ~400 ??
SAFE_DELETE_COUNT: 0
GENERATED_IGNORE_COUNT: 3 patterns added (*.egg-info/, build/, dist/)
KEEP_TRACKED_CHANGE_COUNT: 111
KEEP_UNTRACKED_COUNT: ~200 (files) + ~200 (dir entries)
DOCUMENTATION_REVIEW_REQUIRED_COUNT: ~250
CONCURRENT_DO_NOT_TOUCH_COUNT: 0
DELETED_PATHS: (none)
GITIGNORE_CHANGES: +*.egg-info/, +build/, +dist/
FINAL_GIT_STATUS: 111 M + many ?? — identical except .gitignore now has 3 additional patterns
DIFF_CHECK: PASS (no whitespace errors)
COMMIT_CREATED: false
PUSH_PERFORMED: false
NEXT_ACTION: EXECUTE_DOCUMENTARY_PURGE_AUDIT_V2
```
