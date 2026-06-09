# M62 — Owner Answer To Action Composition ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M62_OWNER_ANSWER_TO_ACTION_COMPOSITION`

---

## 1. Módulo autorizado

`pymia/smartpyme/owner_answers_composer.py`

---

## 2. Responsabilidad contractual

Este módulo compone M61 y M59 sin agregar lógica nueva fuera de la coordinación explícita entre ambos.

La frontera contractual es:

```text
OwnerQuestionsBundle
+ answers_payload estructurado
+ source_ref
+ tenant_id opcional
+ render_contract base
→ OwnerAnswerToActionCompositionResult
```

---

## 3. Resultado requerido

`OwnerAnswerToActionCompositionResult` debe exponer:

- `owner_answers_bundle: OwnerAnswersBundle`
- `evaluation_bundle: OwnerAnswerEvaluationBundle`
- `action_bundle: OwnerNextActionBundle`
- `resolved_action_bundle: OwnerResolvedNextActionBundle`
- `projected_render_contract: dict`

---

## 4. Orden obligatorio

La composición debe:

1. invocar `capture_owner_answers_from_structured_payload(...)`
2. invocar `build_owner_action_projection_pipeline(...)`
3. devolver los artefactos intermedios resultantes

No debe:

- reimplementar reglas internas de M61;
- reimplementar reglas internas de M59;
- ocultar `ValueError` provenientes de cualquiera de los dos módulos.

---

## 5. Prohibiciones

Este módulo no puede:

- tocar `graph.py`
- tocar `state.py`
- tocar `conversation_adapter.py`
- tocar `core_delivery_bridge.py`
- tocar `telegram_bot_runtime.py`
- tocar `DiagnosticCore`
- importar runtime, FastAPI, Hermes, Telegram, parser, LLM o memoria
- persistir artefactos
