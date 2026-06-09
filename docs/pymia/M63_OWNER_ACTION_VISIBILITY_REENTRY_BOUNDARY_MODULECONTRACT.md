# M63 — Owner Action Visibility Reentry Boundary ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M63_OWNER_ACTION_VISIBILITY_REENTRY_BOUNDARY`

---

## 1. Naturaleza del contrato

Este ModuleContract es documental.

No autoriza un módulo Python nuevo.

No autoriza cambios en código productivo.

Define la frontera que un futuro módulo de integración deberá respetar si se decide hacer visible el resultado de M62.

---

## 2. Frontera conceptual

La frontera conceptual permitida es:

```text
OwnerAnswerToActionCompositionResult.projected_render_contract
+ artefactos owner-facing trazables
→ OwnerFacingReport o frontera visible equivalente
```

El `projected_render_contract` producido por M62 es artefacto técnico intermedio.

No es una respuesta final al dueño.

---

## 3. Artefacto soberano visible

El único artefacto soberano para visibilidad owner-facing sigue siendo:

```text
OwnerFacingReport
```

o una frontera contractual equivalente explícitamente autorizada por un futuro hito.

M63 no autoriza equivalentes nuevos.

---

## 4. Candidato futuro de integración

El candidato futuro correcto para integrar acciones owner-facing visibles sigue siendo:

```text
pymia/audit_result/core_delivery_bridge.py
```

Pero M63 no lo modifica.

Cualquier modificación futura de ese archivo requiere un hito nuevo con:

- CapabilitySpec propio;
- ModuleContract propio;
- TaskSpec propio;
- tests focales;
- evidencia;
- revisión de ADR-018 y ADR-022.

---

## 5. Reglas obligatorias para una futura implementación

Una futura implementación deberá:

1. preservar `OwnerFacingReport` como frontera visible soberana;
2. consumir sólo artefactos trazables;
3. preservar bloqueos;
4. distinguir acciones owner-facing de evidencia dura;
5. distinguir declaraciones del dueño de evidencia verificable;
6. no mostrar IDs crudos al dueño;
7. fallar en cerrado si faltan textos owner-facing resueltos;
8. mantener `graph.py` fuera de la lógica owner-action;
9. mantener `delivery_markdown.py` fuera de decisiones owner-action;
10. no crear hallazgos ni diagnóstico.

---

## 6. Prohibiciones vigentes

M63 prohíbe modificar:

- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/orchestration/conversation_adapter.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/telegram_bot_runtime.py`
- `pymia/diagnostic_core/`
- `conversa-engine/`

M63 prohíbe crear:

- renderer paralelo de `OwnerNextActionBundle`;
- salida markdown ad-hoc;
- conversión automática de `OwnerAnswer` a evidencia;
- diagnóstico nuevo;
- inferencia de `question_id` desde texto libre;
- integración runtime.

---

## 7. Fail-closed

Una futura reentrada visible deberá fallar en cerrado si:

- no hay `OwnerFacingReport` o frontera visible autorizada;
- el `projected_render_contract` no preserva trazabilidad;
- existen `target_questions` sin texto resuelto;
- la salida intenta mostrar IDs crudos;
- el estado operacional original está bloqueado y la salida lo oculta;
- la implementación necesita leer runtime, Telegram, memoria o LLM para completar la acción.

---

## 8. Relación con M64

Las fallas globales clasificadas por M63A pertenecen a un frente separado:

```text
M64_GLOBAL_TEST_STABILIZATION
```

M63 no repara esas fallas.

M63 no debe absorber estabilización global.
