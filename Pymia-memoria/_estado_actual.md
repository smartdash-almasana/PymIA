# PymIA Memoria — Estado actual

Fecha: 2026-06-15

## Estado operativo actual

Repo principal:

```text
E:\BuenosPasos\smartbridge\PymIA
```

Subcarpeta viva:

```text
PymIA-Live
```

GitHub:

```text
smartdash-almasana/PymIA
```

HEAD validado por MCP:

```text
42d19bc chore(repo): ignore local temp and quarantine artifacts
```

Commits recientes relevantes:

```text
42d19bc chore(repo): ignore local temp and quarantine artifacts
c958ff3 docs(pymia-live): document canonical test command
bc4e1b5 refactor(pymia): reuse qag reconduction copy from contract
5da7f43 refactor(pymia): replace formula engine branches with dispatch table
e4e1844 feat(pymia): wire presentation labels v1
b61cbbb test(pymia-live): cover formula engine calculation results
b29e06b refactor(pymia-live): retire supported formulas contract
10126c8 refactor(pymia-live): replace SUPPORTED_FORMULAS with load_formula_rules in runtime
```

## Estado de saneamiento genético

```text
PASS / CERRADO hasta FORMULA_ENGINE_DISPATCH_TABLE_V1
```

Cierres posteriores al dispatch table:

```text
FORMULA_CATALOG_RECONCILIATION_V1 = CLOSED_BY_AUDITORIA
QAG_RECONDUCTION_COPY_DEDUP_V1 = CLOSED en bc4e1b5
ROOT_TEST_COMMAND_RECONCILIATION_V1 = CLOSED en c958ff3
COMMIT_GITIGNORE_HYGIENE_V1 = CLOSED en 42d19bc
```

## Resultado arquitectónico vigente

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.

JSON/contratos gobiernan conocimiento declarativo.
Python runtime carga, valida, calcula, orquesta, renderiza y falla cerrado.
```

Estado específico de fórmulas:

```text
formula_rules_v1.json gobierna reglas declarativas.
formula_engine_service.py carga reglas, valida inputs, aplica bloqueos y despacha cálculo por registry.
formula_contract.py conserva tipos vivos: FormulaInput, FormulaResult, FormulaStatus.
SUPPORTED_FORMULAS está retirado.
FormulaDefinition está retirado.
calculate_formula está retirado.
```

Estado específico de presentación/QAG:

```text
presentation_labels_v1.json gobierna labels owner-facing.
question_alignment_v1.json gobierna copy de reconducción QAG.
vertical_slice.py consume final_question_text y technical_reference desde QAG.
```

## Worktree restante conocido

```text
M Pymia-memoria/_decisiones_vigentes.md
M Pymia-memoria/_estado_actual.md
M Pymia-memoria/_task_actual.md
?? PymIA-Live/.tmp_smoke_owner_alignment/
?? PymIA-Live/docs/pymia/ROLE_PLAYING_ONBOARDING_FINDINGS.md
?? docs/MUSEUM_CATALOG.md
```

## Ruido local ya saneado

```text
.tmp/ ignorado por .gitignore root.
_local_quarantine/ ignorado por .gitignore root.
```

## Runtime

```text
LIMPIO en status actual.
No tocar PymIA-Live/pymia/ durante higiene de memoria/museo.
```

## Deuda viva inmediata

```text
1. Decidir destino de PymIA-Live/.tmp_smoke_owner_alignment/ como artefacto smoke no versionable.
2. Decidir destino de PymIA-Live/docs/pymia/ROLE_PLAYING_ONBOARDING_FINDINGS.md como hallazgo experimental.
3. Decidir destino de docs/MUSEUM_CATALOG.md como documento de museo.
4. Auditar hardcodes remanentes de conocimiento owner-facing o dominio fuera de JSON/contratos.
```

## Próximo foco recomendado

```text
HARD_CODE_INVENTORY_OUTSIDE_FORMULAS_V1
```

Objetivo:

```text
Sólo lectura/auditoría.
Listar hardcodes vivos remanentes fuera de fórmulas, QAG y presentation labels.
No implementar runtime.
No crear contratos nuevos.
No tocar fórmulas, QAG, pathology, evidence, presentation ni storage.
```

## Regla de avance

```text
No abrir features nuevas hasta listar deuda viva real.
No volver a refactorizar por estética.
Sólo intervenir si la deuda detectada afecta kernel estable, conocimiento enchufable o entrega owner-facing real.
```
