# C1 — Faithful Operator Catalog Reconciliation TaskSpec

Estado: `APPROVED_TASKSPEC`

Fecha: 2026-06-11

## 1. Enunciado del ciclo

Después del saneamiento post-deriva C0, el próximo avance válido no es crear lógica específica para un caso PyME.

El ciclo C1 debe conectar el `Faithful Operator` con el circuito canónico de catálogos ya existente:

```text
StructuredEvidence
→ evidence_requirement_matcher.match_evidence_requirements(...)
→ docs/formula_catalog.v1.json
→ docs/pathology_catalog.v1.json
→ hipótesis/fórmulas/faltantes/preguntas canónicas
```

C1 no crea fórmulas nuevas.
C1 no crea patologías nuevas.
C1 no lee Excel por fuera del pipeline existente.
C1 no implementa recuperación guiada de evidencia.
C1 no abre M36.

## 2. Objetivo

Exponer, desde el flujo del Faithful Operator, una reconciliación canónica entre evidencia estructurada y los catálogos de fórmulas/patologías, sin duplicar lógica ni crear caminos artesanales.

## 3. Puerto y gate

```yaml
puerto_afectado: EVIDENCE_STATUS_PORT
gate_afectado: EVIDENCE_SUFFICIENCY_GATE
productor_actual:
  - pymia/cli/vertical_slice.py::build_pipeline
  - pymia/smartpyme/structured_evidence_builder.py
consumidor_nuevo:
  - Faithful Operator local assisted flow
fuente_de_verdad:
  - pymia/audit_result/evidence_requirement_matcher.py
  - docs/formula_catalog.v1.json
  - docs/pathology_catalog.v1.json
```

## 4. Fuentes leídas para este TaskSpec

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
docs/pymia/M35_EVIDENCE_TO_CORE_CHECKPOINT.md
docs/pymia/KERNEL_PIPELINE_INVENTORY.md
pymia/contracts/catalogs_v1.py
pymia/services/catalog_loader_v1.py
pymia/audit_result/evidence_requirement_matcher.py
pymia/faithful_operator.py
pymia/cli/vertical_slice.py
tests/test_evidence_requirement_matcher.py
```

## 5. Hechos certificados

- `pymia/audit_result/evidence_requirement_matcher.py` ya cruza `StructuredEvidence` contra `formula_catalog.v1.json` y `pathology_catalog.v1.json`.
- El matcher devuelve `EvidenceRequirementMatch` con `pathology_code`, `formula_id`, `status`, `available_evidence`, `missing_evidence`, `matched_sources`, `required_evidence`, `required_variables` y `next_audit_questions`.
- `pymia/cli/vertical_slice.py::build_pipeline` ya devuelve `structured_summary`, pero no expone todavía el resultado completo del matcher de catálogos.
- `pymia/faithful_operator.py` usa `build_pipeline(...)` para registrar evidencia y construir una respuesta candidata.
- M35 cerró `StructuredEvidence -> DiagnosticCoreInput -> DiagnosticCoreV1`; C1 no debe modificar ese cierre.

## 6. Gap

El `Faithful Operator` no consume todavía una salida canónica de reconciliación de catálogos.

La consecuencia es que la siguiente pregunta al dueño puede quedar demasiado genérica o depender de lógica manual si no se conecta al matcher existente.

## 7. Alcance permitido

Archivos permitidos para implementación posterior:

```text
pymia/cli/vertical_slice.py
pymia/faithful_operator.py
tests/test_faithful_operator_catalog_reconciliation.py
```

Archivos permitidos sólo para lectura:

```text
pymia/audit_result/evidence_requirement_matcher.py
pymia/contracts/evidence_v1.py
pymia/contracts/catalogs_v1.py
pymia/services/catalog_loader_v1.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
tests/test_evidence_requirement_matcher.py
```

Archivos prohibidos:

```text
pymia/cafeteria_margin_focus.py
pymia/margin_evidence_request.py
scripts/demo_cafeteria_margin_focus.py
docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_COST_EVIDENCE_REQUEST.md
docs/pymia/cases/PYMIA_CASE_CAFETERIA_ABC_MARGIN_REPROCESS_RESULT.md
```

## 8. Comportamiento esperado

Cuando `build_pipeline(...)` logra construir `StructuredEvidence`, debe poder exponer una sección canónica de reconciliación:

```text
catalog_reconciliation:
  - formula_id
  - pathology_code
  - status
  - available_evidence
  - missing_evidence
  - matched_sources
  - next_audit_questions
```

El `Faithful Operator` puede mostrar esa reconciliación como evidencia interna o como base de la próxima pregunta, pero no debe declarar diagnóstico final.

## 9. Estados esperados

Estados admitidos desde el matcher:

```text
calculable
pending_data
candidate
blocked
not_applicable
```

Regla de salida:

```text
calculable       → candidato computable, requiere confirmación del dueño antes de diagnóstico
pending_data     → pedir faltantes canónicos
candidate        → hipótesis candidata, no cálculo suficiente
blocked          → bloqueo visible
not_applicable   → no priorizar en salida owner-facing
```

## 10. Acceptance tests requeridos

Crear test focal:

```text
tests/test_faithful_operator_catalog_reconciliation.py
```

Casos mínimos:

1. `build_pipeline(...)` incluye `catalog_reconciliation` cuando hay structured evidence disponible.
2. La reconciliación contiene al menos un match con `formula_id`, `pathology_code`, `status` y `missing_evidence`.
3. Si una fórmula está `pending_data`, la salida conserva `next_audit_questions` del matcher.
4. `Faithful Operator` no inventa preguntas manuales por patología; usa la reconciliación disponible o mantiene pregunta genérica.
5. No se importa ni referencia ningún módulo artesanal de Cafetería ABC.

## 11. Non-goals

No hacer:

```text
- nuevo parser Excel;
- nueva fórmula;
- nueva patología;
- nuevo catálogo;
- recuperación guiada de evidencia;
- output owner-facing final;
- integración Telegram;
- integración DB;
- runtime externo;
- refactor masivo;
- full suite obligatoria.
```

## 12. Stop conditions

Bloquear C1 si:

```text
- no se puede obtener StructuredEvidence desde el pipeline existente;
- el matcher requiere cambiar su contrato;
- se necesita inventar mapeos por caso;
- aparece lógica específica de Cafetería ABC;
- se intenta diagnosticar desde `candidate` o `pending_data`;
- se requiere modificar catálogos sin TaskSpec propio;
- el working tree contiene deriva relacionada.
```

## 13. Validación esperada

Validación focal por Codex/local:

```bash
python -m pytest tests/test_faithful_operator_catalog_reconciliation.py tests/test_evidence_requirement_matcher.py -q
```

No correr full suite salvo autorización posterior.

## 14. Salida requerida de la implementación

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

## 15. Criterio de cierre C1

C1 cierra sólo si:

```text
Faithful Operator puede exponer o transportar reconciliación canónica de catálogo desde StructuredEvidence sin lógica artesanal.
```
