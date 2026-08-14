# Active Roadmap — Servicio 1

**Fecha de corte:** 2026-08-14
**Autoridad:** `docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md`

## Estado

```text
LAST_DEPLOYED_PRODUCTION_CUT: SMOKE_PASS
CURRENT_WORKTREE: SEM_1_TO_9 + DERIVED_EVIDENCE
RELEVANT_REGRESSION: 297 PASS
FULL_SUITE_COVERAGE: PASS_BY_EXHAUSTIVE_SHARDS
FULL_SUITE_RESULT: 3614 PASS / 7 SKIPPED / 0 FAILED
COMMIT: NOT_DONE
DEPLOY: NOT_DONE
```

## Frente actual único

```text
REPO_AND_DOCUMENTATION_HYGIENE_V1: CLOSED_PASS
→ RESTORE_FULL_SUITE_EXECUTION: CLOSED_PASS_BY_EXHAUSTIVE_SHARDS
→ THEMATIC_COMMIT_CUT
→ DEPLOY CURRENT SHA
→ PRODUCTION_SMOKE CURRENT SHA
```

No hay un frente productivo paralelo autorizado.

## Hitos cerrados del worktree actual

```text
SEM-0 ADR-029 boundary
SEM-1 WorkbookProfiler
SEM-2 provider-neutral semantic contract
SEM-3 deterministic semantic validator
SEM-4 owner dialogue planner
SEM-5 owner evidence projection
SEM-6 reentry → existing P6
SEM-7 tenant structural compatibility
SEM-8 canonical product-root wiring
SEM-9 assisted web wiring for Cobros and Margen
Derived Evidence REN_001
REN_001 kernel-only formula authority
owner-confirmed discount unit evidence
removal of parallel web margin calculation
```

## Salvedades activas

```text
EXTERNAL_LLM_PROVIDER: NOT_CONNECTED
WORKING_CAPITAL_SEMANTICS: LEGACY_PILOT_RETAINED
MONOLITHIC_MCP_FULL_SUITE: NOT_OBSERVED_DUE_TO_502_TIMEOUT
CURRENT_WORKTREE: NOT_COMMITTED
CURRENT_WORKTREE: NOT_DEPLOYED
```

Estas salvedades no invalidan la cobertura exhaustiva `3614 PASS / 7 skipped / 0 failed`, pero impiden declarar el corte actual released hasta commit/deploy/smoke del nuevo SHA.

## Secuencia inmediata

### 1. REPO_AND_DOCUMENTATION_HYGIENE_V1 — CLOSED_PASS

Objetivo:

```text
canonical docs reconciled
worktree changes classified
historical docs removed from authority index
unrelated landing/UI changes preserved
no commit/push without authorization
```

### 2. RESTORE_FULL_SUITE_EXECUTION — CLOSED_PASS_BY_EXHAUSTIVE_SHARDS

El wrapper monolítico `python -m pytest -q` devuelve HTTP 502 por límite de transporte. La suite se ejecutó mediante shards exhaustivos sin excluir tests ni agregar skips.

```text
3614 passed
7 skipped
0 failed
```

### 3. THEMATIC_COMMIT_CUT

Separar al menos conceptualmente:

```text
A. SEM-1→SEM-9 / tenant / Derived Evidence / kernel
B. documentation authority reconciliation
C. landing / visual work unrelated to Service 1 runtime
```

No mezclar C con A en un commit productivo.

### 4. DEPLOY + PRODUCTION_SMOKE

Sólo después de full-suite y commits autorizados:

```text
new SHA
→ Cloud Run deploy
→ health
→ auth fail-closed
→ Supabase login
→ authenticated upload
→ owner confirmation
→ deterministic execution + persistence
→ delivery download
→ reentry
```

## Después del release

El siguiente frente de producto se decide recién con el nuevo corte desplegado y smokeado.

Candidatos permitidos para evaluación posterior:

```text
1. conectar provider semántico externo real desde infraestructura/bootstrap
2. migrar working_capital desde semantic scoping legacy a SEM-8
3. probar caso real cliente sobre el nuevo journey
```

No ejecutar los tres en paralelo.

## Expansión prohibida antes del release

```text
nueva capability productiva
segundo product root
segundo XLSX parser
segundo semantic pipeline
segundo computability gate
LLM runtime authority
formula authority fuera del kernel
implicit taxes/defaults materiales
refactor amplio sin blocker causal
```

## Regla de método

```text
una tarea
→ una verificación
→ un resultado
→ una decisión
```

Documentar únicamente cuando cambia una verdad rectora. Los closeouts, TaskSpecs y auditorías consumados no vuelven a gobernar el roadmap.
