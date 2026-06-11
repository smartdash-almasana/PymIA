# C1 — Faithful Operator Catalog Reconciliation Checkpoint

Estado: `PASS / READY_TO_COMMIT`

Fecha: 2026-06-11

## 1. Alcance

C1 conecta el flujo local del `Faithful Operator` con la reconciliación canónica de catálogos ya existente.

Circuito certificado por el slice:

```text
Faithful Operator
→ build_pipeline(...)
→ StructuredEvidence
→ match_evidence_requirements(...)
→ docs/formula_catalog.v1.json
→ docs/pathology_catalog.v1.json
→ catalog_reconciliation
```

## 2. Fuente metodológica

TaskSpec aprobado:

```text
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md
```

Task de implementación:

```text
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_task.md
```

Puerto:

```text
EVIDENCE_STATUS_PORT
```

Gate:

```text
EVIDENCE_SUFFICIENCY_GATE
```

## 3. Archivos modificados por C1

```text
pymia/cli/vertical_slice.py
pymia/faithful_operator.py
tests/test_faithful_operator_catalog_reconciliation.py
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_task.md
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_CHECKPOINT.md
```

## 4. Evidencia de validación

Validación ejecutada por Codex / local, reportada por el usuario:

```bash
python -m pytest tests/test_faithful_operator_catalog_reconciliation.py tests/test_evidence_requirement_matcher.py -q
```

Resultado reportado:

```text
9 passed in 8.46s
```

## 5. Sample certificado

Ejemplo reportado de `catalog_reconciliation`:

```text
formula_id: REN_001_margen_neto_real
pathology_code: REN_001
status: pending_data
missing_evidence: ['impuestos_y_comisiones']
next_audit_questions:
  - question: Falta evidencia para evaluar REN_001. ¿Podés compartir impuestos_y_comisiones?
    requires_data: ['impuestos_y_comisiones']
    priority: high
```

## 6. Drift check reportado

Codex reportó:

```text
no cafeteria_margin_focus: yes
no margin_evidence_request: yes
no new formulas: yes
no new pathologies: yes
only allowed files changed: yes
```

## 7. Qué queda certificado

C1 certifica que:

```text
- build_pipeline(...) puede exponer catalog_reconciliation;
- la reconciliación usa evidence_requirement_matcher;
- la reconciliación conserva formula_id, pathology_code, status, available_evidence, missing_evidence, matched_sources, required_evidence, required_variables y next_audit_questions;
- si se pasan formula_ids, la salida se filtra a esos IDs;
- Faithful Operator preserva o transporta la reconciliación sin diagnosticar;
- no se reintroduce lógica artesanal de Cafetería ABC;
- no se crean fórmulas ni patologías nuevas.
```

## 8. Qué NO certifica

C1 no certifica:

```text
- Guided Evidence Recovery;
- diagnóstico final;
- owner-facing report final;
- M36;
- Telegram;
- DB;
- PDF;
- Hermes;
- runtime externo;
- parser Excel nuevo;
- productización.
```

## 9. Working tree al cierre lógico

Estado reportado por Codex tras limpieza de `.tmp/`:

```text
 M pymia/cli/vertical_slice.py
 M pymia/faithful_operator.py
?? docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md
?? docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_task.md
?? docs/pymia/infografia_pymia.html
?? "prueba_excels/Cafetería ABC.xlsx"
?? tests/test_faithful_operator_catalog_reconciliation.py
```

Luego de este checkpoint, el commit focal de C1 debe incluir sólo los archivos de C1 y excluir:

```text
docs/pymia/infografia_pymia.html
prueba_excels/Cafetería ABC.xlsx
```

## 10. Estado

```text
C1 = PASS / READY_TO_COMMIT
```
