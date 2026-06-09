# M49 — Visible Owner Questions TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M49_VISIBLE_OWNER_QUESTIONS`

---

## 1. Objetivo

Después de construir `OwnerQuestionsBundle`, copiar sus `question_text` válidos a:

- `render_contract["next_questions"]`
- `render_contract["blocked_message"] = primera pregunta`

y asegurar que `render_contract.json` se escriba después.

---

## 2. Scope permitido

Archivos autorizados:

```text
docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_CAPABILITYSPEC.md
docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_MODULECONTRACT.md
docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
pymia/audit_result/core_delivery_bridge.py
tests/diagnosticcore/test_core_audit_delivery_bridge.py
tests/orchestration/test_graph.py
```

---

## 3. Prohibiciones

No tocar:

- `graph.py`
- `PymIAState`
- `owner_questions.py`
- `owner_questions_builder.py`
- `DiagnosticCore`
- parser
- Telegram
- Hermes
- FastAPI

---

## 4. Criterios PASS

M49 puede declararse PASS si:

- `render_contract` refleja las preguntas owner-facing;
- `render_contract.json` se escribe después de esa proyección;
- los tests focales del bridge y del replay real pasan;
- no se tocaron archivos prohibidos.

---

## 5. Estado

```text
M49 = AUTHORIZED_FOR_IMPLEMENTATION
```

Este TaskSpec autoriza el slice mínimo de visibilidad de preguntas.
