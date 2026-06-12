# C3 — Owner Confirmation Boundary for Catalog Summary TaskSpec

Estado: `DRAFT_TASKSPEC`

Fecha: 2026-06-11

## 1. Enunciado del ciclo

C1 conectó `Faithful Operator` con `catalog_reconciliation` canónica.

C2 convirtió esa reconciliación en una síntesis owner-facing sobria y no diagnóstica.

C3 debe agregar una frontera explícita de confirmación/corrección del dueño sobre esa síntesis antes de permitir cualquier avance posterior.

C3 no debe diagnosticar.
C3 no debe recomendar acciones operativas definitivas.
C3 no debe implementar Guided Evidence Recovery.
C3 no debe abrir M36.

## 2. Objetivo

Hacer que el `Faithful Operator` capture la respuesta del dueño frente a la síntesis C2 y la clasifique en una decisión operacional mínima:

```text
confirmed
correction_requested
new_evidence_needed
owner_uncertain
unclear
```

La salida debe mantener el sistema en estado seguro:

```text
confirmación ≠ diagnóstico final
corrección ≠ reprocesamiento automático
incertidumbre ≠ avance
ambigüedad = bloqueo visible
```

## 3. Puerto y gate

```yaml
puerto_afectado: OWNER_INPUT_PORT
control_operacional_interno: OWNER_CONFIRMATION_GATE
fuente_de_entrada:
  - OperatorState.next_question con síntesis C2
  - owner_reply
fuente_canónica:
  - owner-decision-v1 contract, si aplica
  - faithful_operator.py estado local
consumidor:
  - Faithful Operator local assisted flow
```

Nota de auditoría:

```text
OWNER_DECISION_PORT / OWNER_CONFIRMATION_GATE no están registrados como par formal independiente en PORTS_AND_GATES_CONTRACT_REGISTRY.md al momento de C3.
Para C3, el puerto se asimila a OWNER_INPUT_PORT y OWNER_CONFIRMATION_GATE queda definido sólo como control operacional interno de transición del Faithful Operator.
C3 no registra puerto nuevo ni gate nuevo.
```

## 4. Fuentes obligatorias antes de implementación

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
docs/pymia/C1_FAITHFUL_OPERATOR_CATALOG_RECONCILIATION_CHECKPOINT.md
docs/pymia/C2_OWNER_FACING_CATALOG_RECONCILIATION_SUMMARY_CHECKPOINT.md
docs/pymia/C2_OWNER_FACING_CATALOG_RECONCILIATION_SUMMARY_TASKSPEC.md
pymia/faithful_operator.py
tests/test_owner_facing_catalog_reconciliation_summary.py
tests/test_faithful_operator_catalog_reconciliation.py
```

## 5. Hechos certificados heredados

```text
- catalog_reconciliation existe y deriva del matcher canónico;
- la síntesis C2 no diagnostica;
- la síntesis C2 humaniza variables técnicas;
- OperatorState.next_question puede contener una síntesis owner-facing;
- C2 no certifica Guided Evidence Recovery ni diagnóstico final.
```

## 6. Gap

Después de C2, el dueño puede responder:

```text
- sí, esto representa mi negocio;
- no, está mal interpretado;
- falta una evidencia;
- no estoy seguro;
- respuesta ambigua.
```

Hoy esa frontera no está formalizada específicamente para la síntesis C2.

## 7. Alcance permitido

Archivos permitidos para implementación posterior:

```text
pymia/faithful_operator.py
tests/test_owner_confirmation_boundary_for_catalog_summary.py
```

Archivos permitidos sólo para lectura:

```text
tests/test_owner_facing_catalog_reconciliation_summary.py
tests/test_faithful_operator_catalog_reconciliation.py
```

Archivos prohibidos:

```text
pymia/cli/vertical_slice.py
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

Agregar una función determinística, sin LLM, que reciba el estado actual y la respuesta del dueño.

Nombre sugerido:

```text
handle_catalog_summary_owner_confirmation
```

Entrada mínima:

```text
state: OperatorState
owner_reply: str
```

Salida:

```text
OperatorState actualizado
```

La función debe clasificar la respuesta del dueño y actualizar:

```text
owner_confirmation_status
owner_confirmation_message
current_state
next_question
blocked_reason, si corresponde
```

## 9. Clasificación mínima

C3 usa estatus con prefijo `catalog_summary_` únicamente cuando `state.catalog_reconciliation` existe y no está vacío.

Si `state.catalog_reconciliation` no existe o está vacío, debe preservarse el comportamiento estándar existente de `handle_owner_confirmation`, incluyendo estatus heredados como `candidate_confirmed`.

### confirmed

Marcadores posibles:

```text
sí
si
correcto
representa
confirmo
está bien
ok
```

Resultado:

```text
current_state = CLOSED o OWNER_CONFIRMATION_PENDING según semántica existente
owner_confirmation_status = catalog_summary_confirmed
next_question = aclarar que la síntesis fue confirmada, pero no es diagnóstico final
```

### correction_requested

Marcadores posibles:

```text
está mal
no representa
corregir
mezcla
faltan datos
eso no es así
```

Resultado:

```text
current_state = EVIDENCE_REQUESTED o BLOCKED según semántica existente
owner_confirmation_status = catalog_summary_correction_requested
next_question = pedir corrección concreta o nueva evidencia, sin reprocesar automáticamente
```

### new_evidence_needed

C3 no implementa un flujo autónomo separado para `new_evidence_needed`.

Para este ciclo, `new_evidence_needed` se asimila a `correction_requested` cuando la respuesta del dueño indica datos faltantes, evidencia nueva o necesidad de corregir la base.

Marcadores posibles:

```text
faltan datos
faltó
falto
te paso otro archivo
nueva evidencia
hay otra planilla
falta cargar
```

Resultado:

```text
current_state = EVIDENCE_REQUESTED o BLOCKED según semántica existente
owner_confirmation_status = catalog_summary_correction_requested
next_question = pedir corrección concreta o nueva evidencia, sin reprocesar automáticamente
```

### owner_uncertain

Marcadores posibles:

```text
no sé
no estoy seguro
no estoy segura
ni idea
dudo
```

Resultado:

```text
current_state = BLOCKED
owner_confirmation_status = catalog_summary_owner_uncertain
blocked_reason = owner_uncertain_about_catalog_summary
next_question = pedir validación del dueño o evidencia adicional
```

### unclear

Sin marcadores claros.

Resultado:

```text
current_state = BLOCKED
owner_confirmation_status = catalog_summary_unclear_confirmation
blocked_reason = unclear_catalog_summary_confirmation
next_question = pedir confirmación, corrección concreta o nueva evidencia
```

## 10. Reglas de seguridad

```text
- No diagnosticar después de confirmed.
- No construir próximos pasos operativos definitivos.
- No ejecutar reprocesamiento automático.
- No pedir cadenas largas de evidencia.
- No iniciar Guided Evidence Recovery.
- No cambiar catalog_reconciliation.
- No tocar matcher ni catálogos.
```

## 11. Relación con función existente

`faithful_operator.py` ya contiene una función general de confirmación del dueño.

C3 debe preferir:

```text
- reutilizar estructura existente si alcanza;
- agregar función específica sólo si evita ambigüedad con la síntesis C2;
- no romper tests existentes de confirmación.
```

Si la función existente ya cubre el comportamiento, C3 puede ser un adapter explícito o tests que certifiquen la frontera para síntesis C2.

## 12. Non-goals

No hacer:

```text
- diagnóstico final;
- recomendaciones operativas definitivas;
- Guided Evidence Recovery;
- reprocesamiento automático de Excel;
- nuevos puertos;
- nuevos gates;
- nuevas fórmulas;
- nuevas patologías;
- cambios de catálogos;
- Telegram;
- DB;
- PDF;
- Hermes;
- runtime externo;
- productización.
```

## 13. Acceptance tests requeridos

Crear test focal:

```text
tests/test_owner_confirmation_boundary_for_catalog_summary.py
```

Casos mínimos:

1. Confirmación explícita marca `catalog_summary_confirmed` y no diagnostica.
2. Corrección explícita marca `catalog_summary_correction_requested` y pide corrección concreta.
3. Incertidumbre del dueño bloquea el avance.
4. Respuesta ambigua bloquea el avance.
5. Confirmación no ejecuta próximos pasos operativos definitivos.
6. No se modifica `catalog_reconciliation` al procesar la respuesta.
7. No hay imports ni referencias a módulos de Cafetería ABC.
8. Tests C1 y C2 siguen pasando junto con C3.

## 14. Stop conditions

Bloquear C3 si:

```text
- se requiere tocar vertical_slice.py;
- se requiere tocar matcher o catálogos;
- se intenta diagnosticar tras confirmación;
- se intenta activar recuperación guiada;
- se requiere integrar canal externo;
- la función existente de confirmación entra en conflicto semántico grave;
- se rompe C1 o C2.
```

## 15. Validación esperada

Validación focal por Codex/local:

```bash
python -m pytest tests/test_owner_confirmation_boundary_for_catalog_summary.py tests/test_owner_facing_catalog_reconciliation_summary.py tests/test_faithful_operator_catalog_reconciliation.py -q
```

No correr full suite salvo autorización posterior.

## 16. Salida requerida de la implementación

```text
VEREDICTO: PASS | BLOCKED
FILES_CHANGED:
- ...
PYTEST:
- ...
OWNER_CONFIRMATION_SAMPLE:
- ...
DRIFT_CHECK:
- no diagnosis
- no Guided Evidence Recovery
- no new formulas
- no new pathologies
- no cafeteria modules
- no external runtime
```

## 17. Criterio de cierre C3

C3 cierra sólo si:

```text
El Faithful Operator puede procesar confirmación/corrección/incertidumbre/ambigüedad del dueño frente a la síntesis C2 sin diagnosticar ni avanzar automáticamente.
```
