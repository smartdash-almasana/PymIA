# Owner Semantic Gate Builder ModuleContract

Fecha: 2026-06-10
Estado: VIGENTE
Frente: `OWNER_SEMANTIC_GATE_BUILDER`

---

## 1. Frontera

Este contrato regula la frontera y las responsabilidades del módulo:

`pymia/smartpyme/owner_semantic_gate_builder.py`

y su punto de entrada principal:

`build_pending_owner_semantic_confirmation_gate_from_translation(translation_payload: dict) -> OwnerSemanticConfirmationGate`

---

## 2. Responsabilidades permitidas

El módulo futuro puede:
- Recibir un payload estructurado de traducción semántica (`translation_payload`).
- Validar la presencia y formato de los campos obligatorios del payload.
- Construir un objeto `OwnerSemanticConfirmationGate` en estado `PENDING_OWNER_CONFIRMATION`.
- Rellenar los campos del gate (`gate_id`, `target_type`, `proposed_interpretation`, `confirmation_question`, `source_ref`, `related_missing_keys`, `related_pathology_candidates`, `related_formula_candidates`).
- Normalizar las listas de claves, patologías y fórmulas candidatas (quitando espacios y nulos).

---

## 3. Responsabilidades prohibidas

El módulo no debe:
- Conversar directamente con el dueño, ni recibir ni procesar texto libre del dueño para inferir confirmaciones.
- Construir o retornar gates en estados terminales (`CONFIRMED_BY_OWNER`, `REJECTED_BY_OWNER`, `CORRECTED_BY_OWNER`).
- Interactuar con persistencia (DB, files).
- Modificar el payload de entrada.
- Importar o llamar APIs de LLMs, diagnostic core, graph, bridge o runtime.
- Crear o manipular variables de evidencia dura (`evidence_candidate`, `computed_variables`), findings o diagnósticos.

---

## 4. Invariantes y Reglas

- **Pureza y Determinismo:** Para un mismo diccionario de entrada, la función debe producir exactamente el mismo objeto `OwnerSemanticConfirmationGate` sin causar efectos secundarios.
- **Fail-Closed:** Si el payload es nulo, le faltan campos obligatorios (`proposed_interpretation`, `source_ref`), o contiene valores inválidos (por ejemplo, `target_type` no soportado), debe lanzar un `ValueError` o `ValidationError` (fail-closed).
- **Solo Gates Pendientes:** El `status` del gate resultante debe ser incondicionalmente `PENDING_OWNER_CONFIRMATION`.
- **Trazabilidad:** Debe conservar el identificador del gate y el `source_ref` provisto por el traductor conversacional.

---

## 5. Dependencias e Imports Permitidos

- `pymia.contracts.owner_semantic_confirmation` (para `OwnerSemanticConfirmationGate`, `OwnerSemanticConfirmationTargetType`, etc.)
- Módulos estándar de Python (`typing`, `collections`, `uuid`, `hashlib`, etc.)
- `pydantic` (a través del contrato del gate)

---

## 6. Dependencias e Imports Prohibidos

Queda prohibido importar o enlazar componentes de:
- `pymia.diagnostic_core`
- `pymia.audit_result.core_delivery_bridge`
- `pymia.orchestration.graph`
- Hermes runtime / adapters conversacionales activos
- Telegram / PDF / ERP / APIs externas / LLMs / IO

---

## 7. Criterios de Aceptación y Tests Futuros Sugeridos

Cualquier implementación de este módulo debe validar mediante tests unitarios en `tests/smartpyme/`:
- **TC01:** Creación exitosa de un gate pendiente a partir de un payload estructurado mínimo válido.
- **TC02:** Falla cerrada (lanzando excepción) cuando falten `proposed_interpretation` o `source_ref` en el payload.
- **TC03:** Falla cerrada cuando se provea un `target_type` no soportado por el contrato.
- **TC04:** Garantizar que no se permita forzar un estado terminal en el gate resultante.
- **TC05:** Verificación de que las listas candidatas (`related_missing_keys`, etc.) se normalizan correctamente y no contienen elementos nulos o vacíos.
- **TC06:** El diccionario de entrada no es modificado (invariancia de entrada).

---

## 8. Estado del Contrato

```text
MODULE_CONTRACT_AUTHORIZED = VIGENTE
```

Este contrato técnico autoriza el diseño detallado de la compuerta conversacional.
