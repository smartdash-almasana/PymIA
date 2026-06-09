# M59 — Owner Action Pipeline Boundary ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M59_OWNER_ACTION_PIPELINE_BOUNDARY`

---

## 1. Módulo autorizado

`pymia/smartpyme/owner_action_pipeline.py`

---

## 2. Responsabilidad contractual

Este módulo orquesta el pipeline owner-facing ya autorizado, sin agregar lógica nueva fuera de la validación de alineación.

La frontera contractual es:

```text
OwnerAnswersBundle
+ OwnerQuestionsBundle
+ render_contract
→ OwnerActionPipelineResult
```

---

## 3. Resultado requerido

`OwnerActionPipelineResult` debe exponer:

- `projected_render_contract: dict`
- `evaluation_bundle: OwnerAnswerEvaluationBundle`
- `action_bundle: OwnerNextActionBundle`
- `resolved_action_bundle: OwnerResolvedNextActionBundle`

---

## 4. Reglas obligatorias

- cada `answer.question_id` debe existir en `OwnerQuestionsBundle.questions`;
- si falta alguno, el pipeline debe lanzar `ValueError`;
- la orquestación debe invocar los módulos previos en orden:
  1. evaluación
  2. decisión
  3. resolución
  4. proyección
- el `render_contract` proyectado debe ser el retornado por el proyector, no una mutación adicional del pipeline.

---

## 5. Prohibiciones

Este módulo no puede:

- tocar `graph.py`;
- tocar `PymIAState`;
- tocar `core_delivery_bridge.py`;
- tocar `DiagnosticCore`;
- tocar fórmulas, parser, runtime, Telegram, Hermes, FastAPI, LLM o memoria.
