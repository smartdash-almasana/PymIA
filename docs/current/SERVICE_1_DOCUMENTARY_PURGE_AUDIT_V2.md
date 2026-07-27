# SERVICE 1 — DOCUMENTARY PURGE AUDIT V2

Status: `AUDIT_COMPLETE_PURGE_NOT_EXECUTED`

## Scope

Read-only classification of the current `docs/` tree for repository cleanup. No document was moved or deleted in this audit.

Authoritative rule used:

```text
docs/current/ wins over all historical documentation.
Everything outside docs/current/ is museum/legacy unless explicitly promoted or retained as reference.
```

Sources:

- `docs/current/README.md`
- `docs/MUSEUM_CATALOG.md`
- `docs/DEPRECATED_DOCS.md`
- `docs/producto/PYMIA_DOCUMENTARY_PURGE_BATCH_001_AUDIT_ONLY.md`
- `docs/current/SERVICE_1_COLD_WORKTREE_CLASSIFICATION_AND_CLEANUP_AUDIT_V1.md`

## Inventory

Physical files under `docs/` observed during this audit:

```text
TOTAL_FILES = 873
KEEP_CURRENT = 99
KEEP_REFERENCE = 97
MOVE_TO_MUSEUM = 677
DELETE_PROVEN_REDUNDANT = 0
```

The counts are structural classification counts, not claims that every historical document was semantically revalidated line by line.

## Classification policy

### KEEP_CURRENT

Contains current authority or artifacts intentionally retained adjacent to current authority:

```text
docs/current/**
docs/DOCUMENTATION_INDEX.md
docs/README.md
docs/DEPRECATED_DOCS.md
docs/MUSEUM_CATALOG.md
docs/INVENTARIO_CANONICO.md
docs/pathology_catalog.enriched.v2.json
docs/service_1_formula_pathology_evidence_matrix.v2.json
docs/adr/ADR-007-documentation-governance.md
docs/adr/ADR-024-pack-system-foundation.md
```

This class is not a statement that every file in `docs/current/` is mutually consistent. `docs/current/README.md` remains the authority rule and contradictory current docs still require reconciliation rather than museum classification.

### KEEP_REFERENCE

Retain as explicit reference material without allowing it to govern current implementation automatically.

Main classes:

```text
docs/adr/**
docs/contracts/**
docs/contratos/**
root formula/pathology/catalog JSON V1 artifacts
doctrinal/foundational/epistemological reference documents
SCN schemas/contracts
```

These are reference surfaces because they may preserve contracts, provenance, ADR rationale, schemas, or domain theory. They are subordinate to `docs/current/` unless explicitly promoted.

### MOVE_TO_MUSEUM

Historical material that should be physically separated from the active documentation surface.

Main classes:

```text
docs/producto/** historical product lifecycle material
docs/pymia/** historical M-series/checkpoints/taskspecs
docs/smartpyme/** historical milestones/checkpoints/pilots
docs/auditoria/** completed audits and quarantine evidence
docs/arquitectura/** historical architecture/design notes
docs/hermes/** historical Hermes integration material
docs/roadmap/** superseded roadmaps
docs/microsaas/** legacy context
docs/ops/** historical operational material except any explicitly promoted live runbook
docs/prompts/** historical agent prompts
docs/refactor/** historical refactor briefs
docs/transient-design/** transient designs
docs/vision/** vision/provenance material
docs/conversa-engine/** frozen/historical surface
docs/migrado_desde_smartpyme_*.md
docs/ingenieria_conversacional.*
```

Current count under this structural rule:

```text
677 files
```

`MOVE_TO_MUSEUM` means preserve history while removing it from the active documentation surface. It does not mean delete.

### DELETE_PROVEN_REDUNDANT

Current verified count:

```text
0
```

Previous audits named:

```text
docs/ingenieria_conversacional.README.md
```

as the sole safe delete candidate, but that path is not present in the current physical tree. Therefore no deletion is currently authorized or required from that prior decision.

## Important corrections to prior cleanup assumptions

1. The documentation problem is larger than the earlier estimate of ~250 untracked docs. The physical `docs/` tree currently contains 873 files total.
2. The bulk of the problem is not disposable trash; it is historical material mixed into the same namespace as current documentation.
3. Deleting historical documents is not required to clean the active documentation surface. Physical museum relocation is sufficient for most of the 677-file historical class.
4. ADRs/contracts/catalog schemas should not be swept into the museum by directory alone because some are still useful reference authorities.

## Recommended physical target

Create a single museum root, for example:

```text
docs/museum/
```

and migrate historical classes into it while preserving relative structure, e.g.:

```text
docs/producto/...  -> docs/museum/producto/...
docs/pymia/...     -> docs/museum/pymia/...
docs/smartpyme/... -> docs/museum/smartpyme/...
```

Do not duplicate files. Use move/rename, not copy.

## Migration invariants

```text
CURRENT_DOCS_STAY_IN_PLACE
REFERENCE_CONTRACTS_STAY_IN_PLACE
NO_RUNTIME_FILE_MOVES
NO_CODE_IMPORT_CHANGES
NO_DELETION_WITHOUT_EXPLICIT_PROOF
PRESERVE_RELATIVE_HISTORY
MUSEUM_NEVER_GOVERNS_CURRENT
```

Before moving a batch, check incoming references from `docs/current/`, code, tests and root README. A referenced historical path must either remain in place or have references migrated atomically.

## Safe first physical batch

The safest first batch is material already explicitly classified as historical/archive by current governance documents:

```text
docs/migrado_desde_smartpyme_*.md
docs/ingenieria_conversacional.*
docs/vision/**
docs/roadmap/**
docs/transient-design/**
docs/conversa-engine/**
```

This batch should still perform reference checks before moves.

## What this audit did not do

```text
NO_FILES_DELETED
NO_FILES_MOVED
NO_COMMIT
NO_PUSH
NO_RUNTIME_CHANGES
```

## Verdict

```text
VERDICT = PASS_DOCUMENTARY_PURGE_AUDIT_V2
TOTAL_DOC_FILES = 873
KEEP_CURRENT = 99
KEEP_REFERENCE = 97
MOVE_TO_MUSEUM = 677
DELETE_PROVEN_REDUNDANT = 0
PURGE_EXECUTED = false
```

## Next action

```text
EXECUTE_DOCUMENTARY_MUSEUM_RELOCATION_BATCH_001_V1
```

Scope Batch 001 only to the safest historical classes above, verify incoming references, move rather than delete, update museum/index references, then run `git diff --check` and documentation tests. Do not touch the 111 tracked code changes as part of that batch.
