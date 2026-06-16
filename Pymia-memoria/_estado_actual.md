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
629fd85 docs(pymia): catalog museum boundary
```

Commits recientes relevantes:

```text
629fd85 docs(pymia): catalog museum boundary
222e096 refactor(pymia-live): externalize vertical slice owner questions
92d5381 refactor(pymia-live): externalize vertical slice owner copy
731e580 refactor(pymia-live): externalize owner report warnings
c552c27 refactor(pymia-live): externalize evidence requirement owner copy
42d19bc chore(repo): ignore local temp and quarantine artifacts
5da7f43 refactor(pymia): replace formula engine branches with dispatch table
```

## Estado de saneamiento genético

```text
PASS / CERRADO hasta FORMULA_ENGINE_DISPATCH_TABLE_V1
```

Cierres posteriores al dispatch table:

```text
FORMULA_CATALOG_RECONCILIATION_V1 = CLOSED_BY_AUDITORIA
OWNER_FACING_REPORT_WARNINGS_EXTERNALIZATION_V1 = CLOSED en 731e580
VERTICAL_SLICE_MINIMAL_COPY_EXTERNALIZATION_V1 = CLOSED en 92d5381
VERTICAL_SLICE_OWNER_QUESTION_COPY_EXTERNALIZATION_V1 = CLOSED en 222e096
HARD_CODE_RESCAN_AFTER_OWNER_COPY_V1 = CLOSED por auditoría
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
evidence_requirement_copy_v1.json gobierna pregunta owner-facing mínima del matcher.
owner_facing_report_copy_v1.json gobierna warnings owner-facing por status operativo.
vertical_slice_copy_v1.json gobierna copy mínimo y fallback owner-facing de vertical_slice.py.
language_corpus_seed.json sigue gobernando labels dueñas/variables del corpus.
vertical_slice.py consume final_question_text y technical_reference desde QAG.
El copy visible principal owner-facing fue movido a contratos declarativos.
```

## Worktree restante conocido

```text
M Pymia-memoria/_decisiones_vigentes.md
M Pymia-memoria/_estado_actual.md
M Pymia-memoria/_task_actual.md
```

## Ruido local ya saneado

```text
.tmp/ ignorado por .gitignore root.
_local_quarantine/ ignorado por .gitignore root.
```

## Runtime

```text
PymIA-Live mantiene worktree limpio al cierre del saneamiento owner-facing copy.
No tocar PymIA-Live/pymia/ desde memoria documental.
```

## Deuda viva inmediata

```text
No queda deuda owner-facing grande sin externalizar.
operator next step copy = baja prioridad.
headings/render markdown = no tocar ahora.
diagnostic reasoning fallback = otro frente futuro.
pathology engine fallback = técnico, no owner-facing primario.
```

## Próximo foco recomendado

```text
PARAR SANEAMIENTO OWNER-FACING COPY ACÁ
```

Objetivo:

```text
No seguir picando micro-copy owner-facing.
Elegir próximo frente sólo si aporta capacidad operativa real.
```

## Regla de avance

```text
No abrir features nuevas hasta listar deuda viva real.
No volver a refactorizar por estética.
El saneamiento owner-facing copy se considera completo para esta fase.
Sólo intervenir si el próximo slice agrega capacidad operativa real o cierra deuda técnica material.
```
