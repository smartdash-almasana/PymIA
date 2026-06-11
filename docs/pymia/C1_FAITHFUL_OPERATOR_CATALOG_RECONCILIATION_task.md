# C1 — Faithful Operator Catalog Reconciliation — task

Estado: `READY_FOR_IMPLEMENTATION`

Origen:

```text
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md
```

Auditoría externa:

```text
VEREDICTO: PASS_WITH_NOTES
Actor: Codex / Auditor
```

## Objetivo operativo

Implementar el cambio mínimo aprobado para que el flujo local del Faithful Operator transporte o exponga reconciliación canónica de catálogos a partir de `StructuredEvidence`.

Circuito aprobado:

```text
Faithful Operator
→ build_pipeline(...)
→ StructuredEvidence
→ match_evidence_requirements(...)
→ formula_catalog.v1.json + pathology_catalog.v1.json
→ catalog_reconciliation
```

## Archivos permitidos

```text
pymia/cli/vertical_slice.py
pymia/faithful_operator.py
tests/test_faithful_operator_catalog_reconciliation.py
```

## Archivos prohibidos

```text
pymia/audit_result/evidence_requirement_matcher.py
pymia/contracts/catalogs_v1.py
pymia/services/catalog_loader_v1.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
pymia/cafeteria_margin_focus.py
pymia/margin_evidence_request.py
scripts/demo_cafeteria_margin_focus.py
```

## Condiciones de implementación

1. No modificar firmas existentes del matcher.
2. No crear fórmulas nuevas.
3. No crear patologías nuevas.
4. No abrir M36.
5. No crear Guided Evidence Recovery.
6. No introducir lógica específica de Cafetería ABC.
7. No tocar parser Excel, Telegram, DB, PDF, Hermes ni runtime externo.
8. No cambiar contratos de catálogos.

## Nota de auditoría a respetar

La implementación debe evitar que `catalog_reconciliation` ignore filtros solicitados por `formula_ids` cuando el llamador los use.

Si no hay filtro, puede devolver reconciliación del catálogo completo.
Si hay filtro, debe reducirse a los `formula_id` solicitados.

## Acceptance tests mínimos

Crear:

```text
tests/test_faithful_operator_catalog_reconciliation.py
```

Casos:

1. `build_pipeline(...)` incluye `catalog_reconciliation` cuando `StructuredEvidence` está disponible.
2. Cada entrada de `catalog_reconciliation` contiene:
   - `formula_id`
   - `pathology_code`
   - `status`
   - `available_evidence`
   - `missing_evidence`
   - `next_audit_questions`
3. Si `formula_ids` se pasa a `build_pipeline(...)`, la reconciliación se limita a esos `formula_id`.
4. `Faithful Operator` preserva la reconciliación recibida o la refleja en su estado/salida sin diagnosticar.
5. No se importa ni referencia `cafeteria_margin_focus` ni `margin_evidence_request`.

## Validación focal esperada

```bash
python -m pytest tests/test_faithful_operator_catalog_reconciliation.py tests/test_evidence_requirement_matcher.py -q
```

No correr full suite salvo autorización posterior.

## Salida esperada del ejecutor

```text
VEREDICTO: PASS | BLOCKED
FILES_CHANGED:
- ...
PYTEST:
- ...
CATALOG_RECONCILIATION_SAMPLE:
- formula_id:
- pathology_code:
- status:
- missing_evidence:
- next_audit_questions:
DRIFT_CHECK:
- no cafeteria_margin_focus
- no margin_evidence_request
- no new formulas
- no new pathologies
```
