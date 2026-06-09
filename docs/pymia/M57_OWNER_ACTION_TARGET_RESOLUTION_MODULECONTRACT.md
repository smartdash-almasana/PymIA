# M57 — Owner Action Target Resolution ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M57_OWNER_ACTION_TARGET_RESOLUTION`

---

## 1. Módulos autorizados

- `pymia/contracts/owner_resolved_actions.py`
- `pymia/smartpyme/owner_actions_resolver.py`

---

## 2. Responsabilidad contractual

Estos módulos resuelven referencias de pregunta desde un `OwnerNextActionBundle` hacia textos exactos presentes en `OwnerQuestionsBundle`.

La frontera contractual es:

```text
OwnerNextActionBundle
+ OwnerQuestionsBundle
→ resolve_owner_next_action_targets(...)
→ OwnerResolvedNextActionBundle
```

---

## 3. Reglas obligatorias

- por cada ID en `action.target_questions`, buscar la pregunta correspondiente;
- si existe, usar `question_text` exacto;
- si no existe, fallar con `ValueError`;
- preservar `action_type`;
- preservar orden;
- mantener metadata trazable;
- `keep_as_declared` también resuelve `target_questions` si existen;
- acción sin `target_questions` produce `resolved_questions=[]`.

---

## 4. Prohibiciones

Estos módulos no pueden:

- inventar texto;
- mostrar IDs crudos como salida final;
- tocar `graph.py`, `PymIAState` o `core_delivery_bridge.py`;
- tocar `owner_facing_report.py` o `delivery_markdown.py`;
- promover a evidencia dura;
- abrir render visible.
