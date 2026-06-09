# M63C — Owner Action Bridge Reentry Contract CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63C_OWNER_ACTION_BRIDGE_REENTRY_CONTRACT`

---

## 1. Propósito

Autorizar únicamente el contrato documental para una futura integración bridge-adjacent entre la composición owner-answer de M62 y la frontera de delivery owner-facing existente.

M63C no implementa código.

M63C no autoriza modificar `core_delivery_bridge.py` todavía.

M63C define las condiciones mínimas que deberá cumplir un futuro hito implementativo si se decide conectar `OwnerAnswerToActionCompositionResult` con la cadena de delivery owner-facing.

---

## 2. Contexto certificado

La cadena vigente es:

```text
M59 = pipeline owner-action puro
M60 = regla legal de nacimiento de OwnerAnswer
M61 = captura estructurada pura
M62 = composición pura M61 + M59
M63 = frontera visible soberana de reentrada
M63B = preauditoría bridge reentry
```

M63B verificó que `core_delivery_bridge.py` ya concentra:

- `OperationalAuditResult`
- `RenderContract`
- `OwnerQuestionsBundle`
- `OwnerFacingReport`
- `ExecutionResult`
- `DeliveryPackage`
- `output_refs`

Por eso, `core_delivery_bridge.py` es candidato futuro correcto para integración bridge-adjacent.

Pero ese mismo bridge también toca `DiagnosticCore`, escritura de archivos, delivery package y estado de orquestación. Por lo tanto, no debe tocarse sin contrato y tests propios.

---

## 3. Capacidad autorizada en M63C

M63C autoriza sólo documentación contractual para una futura función bridge-adjacent.

La frontera futura candidata sería:

```text
CoreAuditDeliveryBundle existente
+ OwnerAnswerToActionCompositionResult existente
→ CoreAuditDeliveryBundle derivado o estructura equivalente trazable
```

M63C no autoriza crear esa función todavía.

---

## 4. Principio de diseño futuro

La integración futura, si se aprueba, debe ser:

- explícita;
- pura en lo posible;
- fail-closed;
- sin runtime;
- sin LLM;
- sin inferencia de `question_id`;
- sin diagnóstico nuevo;
- sin promoción de declaraciones a evidencia dura;
- sin renderer paralelo;
- preservando `OwnerFacingReport` como frontera visible soberana.

---

## 5. Fuentes permitidas para un futuro hito implementativo

Un futuro hito implementativo sólo podrá consumir:

- `CoreAuditDeliveryBundle`
- `OwnerAnswerToActionCompositionResult`
- `projected_render_contract`
- `owner_answers_bundle`
- `evaluation_bundle`
- `action_bundle`
- `resolved_action_bundle`
- `owner_facing_report`
- `owner_questions_bundle`
- `delivery_package`
- `output_refs`

Siempre como artefactos ya estructurados.

---

## 6. Fuentes prohibidas

Queda prohibido usar como fuente:

- texto libre del último mensaje;
- Telegram;
- runtime;
- memoria conversacional;
- LLM;
- heurísticas conversacionales antiguas;
- parser Excel;
- diagnóstico nuevo;
- IDs crudos como salida visible final.

---

## 7. Comportamiento futuro esperado

Una futura integración deberá:

1. recibir bundles ya construidos;
2. verificar que existe `OwnerFacingReport`;
3. verificar que las acciones resueltas tienen textos owner-facing;
4. proyectar la acción dentro de una frontera visible autorizada;
5. preservar `output_refs`;
6. preservar bloqueos;
7. no alterar el resultado soberano del core;
8. no crear findings;
9. no recalcular fórmulas;
10. no escribir archivos salvo que el hito futuro lo autorice explícitamente.

---

## 8. Prohibiciones activas

M63C no puede modificar:

- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `conversa-engine/`
- `tests/`

---

## 9. Relación con M64

M64_GLOBAL_TEST_STABILIZATION sigue siendo un frente separado.

M63C no repara fallas globales.

M63C no debe absorber deuda de adapters, CLI, Hermes ni forbidden terms.

---

## 10. Criterio PASS

M63C pasa si:

- crea CapabilitySpec, ModuleContract y TaskSpec;
- actualiza `docs/DOCUMENTATION_INDEX.md`;
- no modifica código;
- no modifica tests;
- no autoriza implementación directa;
- deja explícito el contrato mínimo para un futuro hito bridge-adjacent;
- mantiene M64 separado.
