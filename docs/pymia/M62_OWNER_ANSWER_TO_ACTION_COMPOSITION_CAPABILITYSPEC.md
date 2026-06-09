# M62 — Owner Answer To Action Composition CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M62_OWNER_ANSWER_TO_ACTION_COMPOSITION`

---

## 1. Objetivo

Autorizar una composición pura entre M61 y M59:

```text
OwnerQuestionsBundle
+ answers_payload estructurado
+ source_ref
+ tenant_id opcional
+ render_contract base
→ capture_owner_answers_from_structured_payload(...)
→ build_owner_action_projection_pipeline(...)
→ OwnerAnswerToActionCompositionResult
```

Sin integración runtime.

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `Pymia-memoria/ANTI_DERIVA_OPERATIVA_POST_M61_20260609.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/adr/ADR-023-owner-answer-entrypoint-rules.md`
- `docs/pymia/M59_OWNER_ACTION_PIPELINE_BOUNDARY_MODULECONTRACT.md`
- `docs/pymia/M60_OWNER_ANSWER_ENTRYPOINT_AUDIT_MODULECONTRACT.md`
- `docs/pymia/M61_OWNER_ANSWER_STRUCTURED_CAPTURE_MODULECONTRACT.md`

---

## 3. Capacidad autorizada

M62 autoriza una composición lógica pura que:

- captura `OwnerAnswersBundle` desde payload estructurado;
- ejecuta el pipeline owner-facing ya autorizado;
- devuelve los artefactos intermedios relevantes sin esconderlos;
- propaga errores contractuales de captura o pipeline sin envolverlos.

---

## 4. Invariantes

- no mutar `questions_bundle`
- no mutar `answers_payload`
- no mutar `render_contract`
- no escribir archivos
- no tocar estado runtime
- no crear evidencia
- no diagnosticar
- no tocar bridge ni graph

---

## 5. Artefacto esperado

Implementación en:

`pymia/smartpyme/owner_answers_composer.py`

Con:

- `OwnerAnswerToActionCompositionResult`
- `compose_owner_answers_to_actions(...)`

---

## 6. Criterios PASS

M62 puede declararse PASS si:

- la composición existe;
- la suite focal pasa;
- la suite ampliada de M61 + M59 + M62 pasa;
- no se tocó ningún archivo prohibido;
- no se abrió integración falsa con runtime.
