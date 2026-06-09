# M61 — Owner Answer Structured Capture ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M61_OWNER_ANSWER_STRUCTURED_CAPTURE`

---

## 1. Módulo autorizado

`pymia/smartpyme/owner_answers_capture.py`

---

## 2. Responsabilidad contractual

Este módulo captura `OwnerAnswer` y `OwnerAnswersBundle` exclusivamente desde payloads estructurados validados contra preguntas contractuales ya emitidas.

La frontera contractual es:

```text
OwnerQuestionsBundle
+ list[dict]
+ source_ref
→ OwnerAnswersBundle
```

---

## 3. Reglas obligatorias

- cada payload debe declarar `question_id`
- cada `question_id` debe existir en el `OwnerQuestionsBundle`
- `question_text` final debe tomarse desde `OwnerQuestion.question_text`
- si el payload trae `question_text`, sólo se acepta si coincide exactamente
- `source_ref` del parámetro prevalece sobre cualquier `source_ref` del payload
- `answer_type` válido del payload prevalece sobre `expected_answer_type`
- si el payload no trae `answer_type`, se usa `expected_answer_type`
- si ninguno aplica, se usa `"unknown"`

---

## 4. Fail-closed

El módulo debe lanzar `ValueError` si:

- falta `question_id`
- `question_id` no existe
- falta contenido de respuesta
- `source_ref` está vacío
- `question_text` del payload contradice el contractual
- `answer_type` es inválido

---

## 5. Prohibiciones

Este módulo no puede:

- invocar M59 pipeline
- tocar `graph.py`, `state.py` o `core_delivery_bridge.py`
- tocar `owner_facing_report.py`
- importar Telegram, Hermes, FastAPI, runtime, parser, LLM o memoria
- escribir archivos
- crear evidencia o diagnóstico
