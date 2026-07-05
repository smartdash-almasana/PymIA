# PYMIA_DOCUMENTARY_AXIS_PURGE_AND_CANONICAL_INDEX_AUDIT_V1

## VERDICT

```text
AUDIT_CREATED
DOCUMENTARY_CURATION_STATUS: PARTIAL_NOT_CLOSED
PURGE_READY: PARTIAL
DELETE_READY_BATCH: LIMITED_ONLY
```

## SCOPE

```text
Type: DOCUMENTARY_AXIS_AUDIT
Repo impact: DOC ONLY
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
Deletion impact: NONE
```

## QUESTION

```text
Did we already curate the PymIA documentary axis?
```

## ANSWER

```text
YES, partially.
NO, not as a closed global purge.
```

## EVIDENCE_READ

```text
docs/DOCUMENTATION_INDEX.md
docs/current/ACTIVE_ROADMAP.md
docs/current/SERVICE_1_STATUS.md
```

## CERTIFIED_FACTS

From `docs/DOCUMENTATION_INDEX.md`:

```text
- It declares itself the unified sovereign index of the PymIA documentary library.
- It classifies many documents by status: VIGENTE, CANDIDATO, ARCHIVO, SUPERADO, BORRAR_PROPUESTO, CLOSED, IMPLEMENTED, etc.
- It states that no new document should be created without immediate incorporation into the index.
- It prohibits duplicated normative implementation rules.
- It prohibits using SUPERADO, ARCHIVO or BORRAR_PROPUESTO documents to guide coding.
```

From `docs/current/ACTIVE_ROADMAP.md`:

```text
SERVICE_1_XLSX_BRIDGE_MILESTONE_CLOSED
STOP_AND_DECIDE
FOURTH_UNIT_ALLOWED: FALSE
```

From `docs/current/SERVICE_1_STATUS.md`:

```text
Servicio 1 Full Assisted V1 está cerrado con límites.
Next main product objective: S1_AUTONOMOUS_GUARDED_SAAS_V1.
```

## AUDIT_FINDING

```text
The repository already has a documentary governance index.
However, the index is not equivalent to physical purge.
```

Reason:

```text
Many obsolete, archival, candidate, and historical documents remain physically present and indexed.
That is valid as archival governance, but it is not the stronger purge policy recently requested by the owner.
```

## CURRENT_DOCUMENTARY_AXIS_STATE

### 1. Canonical governance exists

```text
PASS
```

Evidence:

```text
docs/DOCUMENTATION_INDEX.md exists and acts as sovereign index.
```

### 2. Lifecycle taxonomy exists

```text
PASS
```

Evidence:

```text
The index classifies documents as VIGENTE, CANDIDATO, ARCHIVO, SUPERADO, BORRAR_PROPUESTO and other states.
```

### 3. Physical purge completed

```text
FAIL / NOT_CERTIFIED
```

Evidence:

```text
The index still contains many ARCHIVO and historical migrated documents.
Only one explicit BORRAR_PROPUESTO was observed in the read range:
docs/ingenieria_conversacional.README.md
```

### 4. Service 1 axis curated

```text
PARTIAL_HIGH
```

Evidence:

```text
SERVICE_1_STATUS closes Full Assisted V1 with limits.
ACTIVE_ROADMAP closes XLSX bridge milestone and stops further units.
Recent audits selected autonomy path and then stopped implementation due to integration risk.
```

### 5. PymIA / SmartPyme / Hermes / Factory / Product separation

```text
PARTIAL
```

Evidence:

```text
DOCUMENTATION_INDEX has many sections and owners, but old conceptual, product, architecture, Hermes, SCN, migrated and Service 1 docs coexist in one large table.
```

## AXIS_CLASSIFICATION

### SERVICE_1_CANONICAL_AXIS

Current governing docs include:

```text
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
docs/producto/SERVICE_1_INTEGRALITY_AND_MATURITY_AUDIT_V1.md
docs/producto/S1_AUTONOMOUS_GUARDED_SAAS_V1_ACTIVE_FRONT_DECISION.md
docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_TRACE_AUDIT_V1.md
docs/producto/S1_AUTONOMOUS_OWNER_EVIDENCE_GATE_CHAIN_REUSE_MAPPING_V1.md
```

Status:

```text
CANONICAL_BUT_NEEDS_INDEX_REFRESH
```

### PYMIA_CORE_AXIS

Current governing docs include:

```text
docs/DOCUMENTATION_INDEX.md
docs/adr/ADR-007-documentation-governance.md
docs/adr/ADR-024-pack-system-foundation.md
docs/contratos/primary-case-file-v1.md
```

Status:

```text
CANONICAL_BUT_LARGE
```

### SMARTPYME_PRODUCT_AXIS

Current issue:

```text
Vision, product, laboratory, First Aid, MVP and pilot docs coexist.
Some are useful product memory; not all should govern implementation.
```

Status:

```text
NEEDS_CANONICAL_SPLIT
```

Recommended split:

```text
CANONICAL_PRODUCT
PRODUCT_ARCHIVE
COMMERCIAL_COPY
PILOT_LEARNING
```

### HERMES_AXIS

Current issue:

```text
Hermes docs are numerous and include architecture, VM audits, sandbox results, MCP, SCN, local runtime and historical protocols.
```

Status:

```text
NEEDS_SEPARATE_HERMES_INDEX_OR_SUBINDEX
```

### FACTORY_AXIS

Current issue:

```text
Factory / LearningMemory / ArchitecturalDNA material exists conceptually but is not clearly separated from PymIA runtime/product governance in this audit pass.
```

Status:

```text
NEEDS_AXIS_DECISION
```

## OBSOLETE_OR_NON_GOVERNING_CLASSES

Do not use for implementation:

```text
SUPERADO
ARCHIVO
BORRAR_PROPUESTO
historical migrated docs
commercial landing docs
conceptual vision docs unless promoted by explicit canonical decision
```

Explicit delete candidate observed:

```text
docs/ingenieria_conversacional.README.md
```

## PROPOSED_PURGE_POLICY

The owner's stronger policy is:

```text
obsolete documentation is deleted, not kept alive as museum/archive, if it can still contaminate development.
```

This requires a stricter policy than current DOCUMENTATION_INDEX.

Current index policy permits archival preservation.
Owner policy prefers deletion for obsolete docs that remain dangerous.

## GAP

```text
No global physical deletion audit has been certified yet.
No batch delete list has been approved yet.
Recent Servicio 1 docs may not be incorporated into DOCUMENTATION_INDEX.
No separate canonical subindex exists for Service 1 autonomy path.
No separate canonical subindex exists for SmartPyme product/lab docs.
No separate canonical subindex exists for Factory/ADN docs.
```

## RECOMMENDED NEXT STEP

```text
PYMIA_DOCUMENTARY_PURGE_BATCH_001_AUDIT_ONLY
```

Scope:

```text
AUDIT ONLY
No deletion
No code
No tests
No commit until owner approves delete list
```

Output required:

```text
DELETE_CANDIDATES_SAFE:
DELETE_CANDIDATES_NEEDS_OWNER_CONFIRMATION:
KEEP_CANONICAL:
KEEP_ARCHIVE_BUT_QUARANTINE:
MOVE_TO_SUBINDEX:
INDEX_REFRESH_REQUIRED:
```

## SAFE_RULE_FOR_NEXT_CYCLE

```text
Do not delete by status alone.
Delete only when:
1. DOCUMENTATION_INDEX marks BORRAR_PROPUESTO; or
2. document is duplicate and replacement is explicit; or
3. document contradicts active roadmap/status; or
4. owner approves deletion after audit list.
```

## FINAL_STATUS

```text
PYMIA_DOCUMENTARY_AXIS_PURGE_AND_CANONICAL_INDEX_AUDIT_V1: CREATED
CURATION_DONE: PARTIAL
GLOBAL_PURGE_DONE: NO
NEXT_STEP: PURGE_BATCH_001_AUDIT_ONLY
```
