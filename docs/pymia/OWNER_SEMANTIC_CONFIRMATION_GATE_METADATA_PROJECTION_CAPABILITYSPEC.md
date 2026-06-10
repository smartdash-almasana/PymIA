# Owner Semantic Confirmation Gate Metadata Projection CapabilitySpec

Fecha: 2026-06-10
Estado: VIGENTE
Frente: `OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION`

---

## 1. Objetivo

Autorizar formalmente una proyección pura y contractual:

```text
OwnerSemanticConfirmationGate pendiente
→ OwnerQuestion.metadata

OwnerSemanticConfirmationGate terminal
→ OwnerAnswer.metadata
```

Sin integración runtime.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/pymia/OWNER_SEMANTIC_LOOP_THREE_LAYER_FLOW.md`
- `docs/pymia/OWNER_SEMANTIC_CONFIRMATION_GATE_METADATA_PROJECTION_CHECKPOINT.md`
- `docs/pymia/SEMANTIC_CONFIRMATION_REENTRY_BLOCK_CLOSURE.md`

---

## 3. Capacidad autorizada

Se autoriza que `OwnerSemanticConfirmationGate` exponga dos proyecciones de metadata:

- `to_owner_question_metadata()`
- `to_owner_answer_metadata()`

La capacidad queda limitada a serializar información ya contenida en el gate. No puede leer otros contratos ni ejecutar lógica externa.

---

## 4. Reglas obligatorias

### 4.1 Gate pendiente → OwnerQuestion.metadata

`to_owner_question_metadata()` debe:

- declarar `expects_semantic_confirmation = True`;
- transportar `semantic_confirmation_gate_id`;
- transportar `semantic_confirmation_target_type`;
- transportar `proposed_interpretation`;
- transportar candidatos relacionados como listas;
- transportar `semantic_confirmation_source_ref`;
- no transportar `semantic_confirmation_status`.

### 4.2 Gate terminal → OwnerAnswer.metadata

`to_owner_answer_metadata()` debe:

- exigir que el gate sea terminal;
- transportar `semantic_confirmation_status` explícito;
- transportar `owner_response_text`;
- transportar `corrected_interpretation` sólo cuando aplique;
- preservar trazabilidad al gate y al `source_ref` original.

---

## 5. Invariantes

La proyección debe ser:

- pura;
- determinística;
- sin IO;
- sin mutación del gate;
- sin imports de `OwnerQuestion`, `OwnerAnswer`, bridge, graph, runtime, Telegram, Hermes, PDF o ERP;
- sin LLM;
- sin inferencia desde texto libre;
- sin promover semántica a evidencia estructural;
- sin `evidence_candidate`;
- sin `computed_variables`;
- sin findings;
- sin diagnóstico.

---

## 6. Artefacto esperado

Implementación autorizada en:

`pymia/contracts/owner_semantic_confirmation.py`

Tests autorizados en:

`tests/smartpyme/test_owner_semantic_confirmation_gate.py`

---

## 7. Criterios de aceptación

Debe existir cobertura para:

- metadata de pregunta con `expects_semantic_confirmation = True`;
- ausencia de `semantic_confirmation_status` en metadata de pregunta pendiente;
- metadata de respuesta con `semantic_confirmation_status` terminal explícito;
- preservación de corrección del dueño cuando el gate está corregido;
- fallo cerrado si se intenta proyectar metadata de respuesta desde un gate pendiente;
- ausencia de campos de evidencia o diagnóstico.

---

## 8. Prohibiciones explícitas

Este CapabilitySpec no autoriza:

- cambios en `graph.py`;
- cambios en `core_delivery_bridge.py`;
- cambios en DiagnosticCore;
- cambios en runtime;
- Telegram productivo;
- Hermes runtime;
- PDF productivo;
- ERP;
- nuevas fórmulas;
- generación de findings;
- inferir confirmación desde texto libre.

---

## 9. Veredicto

`CAPABILITY_AUTHORIZED`

La capacidad queda autorizada sólo como proyección contractual pura del gate hacia metadata transportable.
