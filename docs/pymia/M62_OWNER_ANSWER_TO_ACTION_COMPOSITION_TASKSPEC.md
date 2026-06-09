# M62 — Owner Answer To Action Composition TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M62_OWNER_ANSWER_TO_ACTION_COMPOSITION`

---

## 1. Objetivo

Implementar la composición pura entre captura estructurada (M61) y pipeline owner-facing (M59).

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `Pymia-memoria/ANTI_DERIVA_OPERATIVA_POST_M61_20260609.md`
- `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_CAPABILITYSPEC.md`
- `docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_CAPABILITYSPEC.md
docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_MODULECONTRACT.md
docs/pymia/M62_OWNER_ANSWER_TO_ACTION_COMPOSITION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/smartpyme/owner_answers_composer.py
tests/smartpyme/test_owner_answers_composer.py
```

---

## 4. Tests mínimos

La suite focal debe validar:

- happy path completo
- devolución de `owner_answers_bundle`
- devolución de `evaluation_bundle`
- devolución de `action_bundle`
- devolución de `resolved_action_bundle`
- devolución de `projected_render_contract`
- no mutación de `answers_payload`
- no mutación de `render_contract`
- falla por `question_id` inexistente en M61
- falla por falta de contenido en M61
- falla por desalineación detectada por M59
- ausencia de imports prohibidos

---

## 5. Criterios PASS

M62 puede declararse PASS si:

- la composición existe;
- la suite focal pasa;
- la suite ampliada M61 + M59 + M62 pasa;
- no se tocó ningún archivo prohibido;
- no se abrió integración con runtime, bridge ni graph.
