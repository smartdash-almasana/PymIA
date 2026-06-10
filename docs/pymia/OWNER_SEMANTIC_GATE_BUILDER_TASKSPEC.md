# Owner Semantic Gate Builder TaskSpec

Fecha: 2026-06-10
Estado: VIGENTE
Frente: `OWNER_SEMANTIC_GATE_BUILDER`

---

## 1. Objetivo

Implementar la capacidad pura de construir un gate de confirmación semántica en estado pendiente (`PENDING_OWNER_CONFIRMATION`) a partir de un payload estructurado de traducción conversacional provisto por la IA conversacional externa (Hermes/IA).

```text
structured_semantic_translation_payload
→ OwnerSemanticConfirmationGate(status=PENDING_OWNER_CONFIRMATION)
```

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/pymia/OWNER_SEMANTIC_LOOP_THREE_LAYER_FLOW.md`
- `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_CAPABILITYSPEC.md`
- `docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados para lectura y escritura:

```text
docs/pymia/OWNER_SEMANTIC_GATE_BUILDER_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_semantic_gate_builder.py
tests/smartpyme/test_owner_semantic_gate_builder.py
```

Archivos autorizados solo para lectura:

```text
pymia/contracts/owner_semantic_confirmation.py
tests/smartpyme/test_owner_semantic_confirmation_gate.py
```

---

## 4. Prohibiciones

Queda estrictamente prohibido tocar o modificar:

- `pymia/diagnostic_core/` (DiagnosticCore)
- `pymia/orchestration/graph.py` (graph)
- `pymia/audit_result/core_delivery_bridge.py` (bridge)
- Canales de transporte activos (Telegram, FastAPI)
- Hermes runtime conversacional activo
- PDF / ERP / APIs externas
- Generación de findings o variables de evidencia estructurada
- Mapeos directos de texto libre dentro de PymIA

---

## 5. Lógica Requerida

El módulo `pymia/smartpyme/owner_semantic_gate_builder.py` debe implementar la función:

```python
def build_pending_owner_semantic_confirmation_gate_from_translation(
    translation_payload: dict,
) -> OwnerSemanticConfirmationGate:
    ...
```

Reglas obligatorias de la lógica:
- Generar un identificador de gate estable (por ejemplo, derivado por hashing de sus campos clave, o un UUID determinista).
- Validar que `proposed_interpretation` y `source_ref` no estén vacíos.
- Validar que `target_type` sea un valor válido del tipo `OwnerSemanticConfirmationTargetType`.
- Retornar un `OwnerSemanticConfirmationGate` con `status = PENDING_OWNER_CONFIRMATION`.
- Normalizar las listas candidatas (`related_missing_keys`, `related_pathology_candidates`, `related_formula_candidates`) a fin de eliminar espacios y elementos vacíos.
- No mutar el diccionario `translation_payload` de entrada.
- Lanzar excepciones apropiadas (`ValueError`, `ValidationError`) ante payloads inválidos (fail-closed).

---

## 6. Tests Requeridos

El archivo `tests/smartpyme/test_owner_semantic_gate_builder.py` debe certificar y cubrir los siguientes escenarios:
- **Caso 1:** Creación correcta del gate en estado `PENDING_OWNER_CONFIRMATION` desde un payload mínimo válido.
- **Caso 2:** Falla cerrada (excepción) si falta o está vacío `proposed_interpretation` o `source_ref`.
- **Caso 3:** Falla cerrada si se intenta pasar un `target_type` que no pertenece al contrato.
- **Caso 4:** Forzar un estado terminal en el payload es ignorado o rechazado, resultando siempre en un gate pendiente.
- **Caso 5:** Las listas candidatas son normalizadas correctamente y no contienen elementos nulos o vacíos.
- **Caso 6:** No se muta el diccionario `translation_payload` provisto como entrada.
- **Caso 7:** No se producen variables de evidencia (`evidence_candidate`, `computed_variables`) ni findings.
- **Caso 8:** El gate generado proyecta correctamente su metadata de pregunta mediante `to_owner_question_metadata()`.

---

## 7. Criterios de Aceptación PASS

El trabajo se considerará PASS si:
1. El archivo `owner_semantic_gate_builder.py` implementa la función requerida respetando el ModuleContract.
2. Los tests en `test_owner_semantic_gate_builder.py` pasan exitosamente.
3. No se han tocado archivos prohibidos ni modificado contratos existentes.
4. No se introduce interpretación heurística de texto libre.

---

## 8. Estado

```text
TASK_SPEC_AUTHORIZED = VIGENTE
```

Este TaskSpec autoriza formalmente la implementación del builder de gates en el próximo ciclo.
