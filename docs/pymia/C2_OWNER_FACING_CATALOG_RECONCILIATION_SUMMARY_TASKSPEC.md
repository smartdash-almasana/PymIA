# C2 — Owner-facing Catalog Reconciliation Summary TaskSpec

Estado: `DRAFT_TASKSPEC`

Fecha: 2026-06-11

## 1. Enunciado del ciclo

C1 certificó que el flujo local del `Faithful Operator` puede transportar reconciliación canónica entre `StructuredEvidence`, `formula_catalog.v1.json` y `pathology_catalog.v1.json` mediante `evidence_requirement_matcher`.

C2 no debe crear lógica diagnóstica nueva.
C2 debe convertir esa reconciliación interna en una salida sobria y útil para operador asistido / dueño PyME, sin exponer jerga cruda ni afirmar diagnósticos.

El ciclo C2 existe para reducir la distancia entre evidencia canónica interna y comunicación operacional honesta.

## 2. Objetivo

Construir una síntesis owner-facing de `catalog_reconciliation` que comunique:

```text
qué se puede evaluar;
qué falta;
qué no se puede afirmar;
cuál es la próxima pregunta mínima al dueño.
```

La síntesis debe preservar la honestidad epistemológica:

```text
pending_data ≠ diagnóstico
candidate ≠ diagnóstico
calculable ≠ diagnóstico final
blocked = freno explícito
```

## 3. Puerto y gate

```yaml
puerto_afectado: CHANNEL_OUTPUT_PORT
gate_afectado: OWNER_LANGUAGE_GATE
fuente_de_entrada:
  - catalog_reconciliation producido en C1
fuente_canónica:
  - pymia/audit_result/evidence_requirement_matcher.py
  - docs/formula_catalog.v1.json
  - docs/pathology_catalog.v1.json
consumidor:
  - Faithful Operator local assisted flow
```

## 4. Fuentes obligatorias antes de implementación

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
docs/pymia/M35_EVIDENCE_TO_CORE_CHECKPOINT.md
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_CHECKPOINT.md
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_TASKSPEC.md
pymia/faithful_operator.py
pymia/cli/vertical_slice.py
pymia/audit_result/evidence_requirement_matcher.py
tests/test_faithful_operator_catalog_reconciliation.py
```

## 5. Hechos certificados heredados de C1

```text
- build_pipeline(...) expone catalog_reconciliation;
- catalog_reconciliation deriva de evidence_requirement_matcher;
- no hay fórmulas nuevas;
- no hay patologías nuevas;
- Faithful Operator puede transportar la reconciliación sin diagnosticar.
```

## 6. Gap

C1 deja disponible la reconciliación, pero todavía no define una forma owner-facing sobria para comunicarla.

Riesgo si no se corrige:

```text
- salida demasiado técnica para dueño;
- exposición de formula_id/pathology_code sin traducción;
- preguntas genéricas aunque existan next_audit_questions canónicas;
- tentación de convertir pending_data en diagnóstico.
```

## 7. Alcance permitido

Archivos permitidos para implementación posterior:

```text
pymia/faithful_operator.py
tests/test_owner_facing_catalog_reconciliation_summary.py
```

Archivos permitidos sólo para lectura:

```text
pymia/cli/vertical_slice.py
pymia/audit_result/evidence_requirement_matcher.py
tests/test_faithful_operator_catalog_reconciliation.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
```

Archivos prohibidos:

```text
pymia/audit_result/evidence_requirement_matcher.py
pymia/services/catalog_loader_v1.py
pymia/contracts/catalogs_v1.py
docs/formula_catalog.v1.json
docs/pathology_catalog.v1.json
pymia/cafeteria_margin_focus.py
pymia/margin_evidence_request.py
scripts/demo_cafeteria_margin_focus.py
pymia/telegram_bot_runtime.py
pymia/telegram_runtime.py
```

## 8. Comportamiento esperado

Agregar una función determinística, sin LLM, que reciba una lista de entradas de `catalog_reconciliation` y devuelva texto owner-facing.

Nombre sugerido:

```text
build_owner_facing_catalog_reconciliation_summary
```

Integración obligatoria:

```text
receive_excel_and_build_candidate(...)
→ pipeline["catalog_reconciliation"]
→ build_owner_facing_catalog_reconciliation_summary(...)
→ OperatorState.next_question
```

El resumen owner-facing debe integrarse en `next_question` de `OperatorState` durante `receive_excel_and_build_candidate`.

La traza técnica heredada de C1 debe conservarse para no romper tests existentes:

```text
candidate_response debe seguir conteniendo:
- "Reconciliación de catálogos:"
- referencia a "fórmulas"
```

La salida owner-facing principal debe incluir como máximo:

```text
1. estado general;
2. hasta 3 temas evaluables o pendientes;
3. evidencia faltante prioritaria;
4. una pregunta concreta al dueño;
5. límite explícito: no es diagnóstico final.
```

## 9. Reglas de traducción owner-facing

No exponer por defecto:

```text
formula_id
pathology_code
required_variables crudos
missing_evidence crudos
matched_sources crudos
nombres técnicos de variables sin humanización
referencias internas de hojas/tablas como texto principal al dueño
```

Permitido para operador interno si ya existe traza en estado, pero no como texto visible principal al dueño.

Las listas técnicas deben humanizarse antes de llegar al texto owner-facing principal.

Ejemplo:

```text
['impuestos_y_comisiones'] → "impuestos y comisiones"
['ventas_por_sku'] → "ventas por producto/SKU"
```

La traza técnica puede conservarse en `OperatorState.catalog_reconciliation` o en `candidate_response`, pero el resumen owner-facing principal debe ser lenguaje operacional claro.

Mapeo de estados:

```text
calculable:
  texto: Hay datos suficientes para calcular un indicador candidato, pero requiere confirmación del dueño.

pending_data:
  texto: Hay señales parciales, pero falta evidencia para evaluar bien.

candidate:
  texto: Hay una hipótesis posible, todavía no calculable.

blocked:
  texto: No conviene avanzar sin resolver un bloqueo de evidencia.

not_applicable:
  texto: No mostrar salvo que no haya otras entradas.
```

## 10. Reglas de selección

La síntesis debe priorizar:

```text
1. blocked
2. pending_data
3. candidate
4. calculable
5. not_applicable
```

Debe limitar la salida para no saturar al dueño:

```text
máximo 3 entradas visibles
máximo 1 pregunta final
```

La pregunta final debe preferir `next_audit_questions` del matcher cuando existan.

## 11. Non-goals

No hacer:

```text
- Guided Evidence Recovery;
- diagnóstico final;
- recomendaciones operativas definitivas;
- nuevas fórmulas;
- nuevas patologías;
- cambio de catálogos;
- cambio del matcher;
- parser Excel;
- Telegram;
- DB;
- PDF;
- Hermes;
- runtime externo;
- productización.
```

## 12. Acceptance tests requeridos

Crear test focal:

```text
tests/test_owner_facing_catalog_reconciliation_summary.py
```

Casos mínimos:

1. Para `pending_data`, la salida dice que falta evidencia y no diagnostica.
2. Para `candidate`, la salida mantiene hipótesis sin cálculo.
3. Para `calculable`, la salida exige confirmación del dueño antes de cierre.
4. La salida no expone `formula_id` ni `pathology_code` en el texto principal.
5. La pregunta final usa `next_audit_questions` si existen.
6. La salida limita a 3 entradas visibles.
7. No hay imports ni referencias a módulos de Cafetería ABC.

## 13. Stop conditions

Bloquear C2 si:

```text
- se necesita modificar evidence_requirement_matcher;
- se necesita modificar catálogos;
- se intenta diagnosticar;
- se intenta crear flujo autónomo de recuperación de evidencia;
- se requiere tocar Telegram o runtime;
- se reintroduce lógica específica de Cafetería ABC;
- la salida owner-facing no puede ocultar jerga técnica;
- no existe catalog_reconciliation en el estado recibido.
```

## 14. Validación esperada

Validación focal por Codex/local:

```bash
python -m pytest tests/test_owner_facing_catalog_reconciliation_summary.py tests/test_faithful_operator_catalog_reconciliation.py -q
```

No correr full suite salvo autorización posterior.

## 15. Salida requerida de la implementación

```text
VEREDICTO: PASS | BLOCKED
FILES_CHANGED:
- ...
PYTEST:
- ...
OWNER_FACING_SAMPLE:
- ...
DRIFT_CHECK:
- no diagnosis
- no new formulas
- no new pathologies
- no cafeteria modules
- no Guided Evidence Recovery
```

## 16. Criterio de cierre C2

C2 cierra sólo si:

```text
Faithful Operator puede convertir catalog_reconciliation en una síntesis owner-facing sobria, limitada, no diagnóstica y basada en preguntas/faltantes canónicos.
```
