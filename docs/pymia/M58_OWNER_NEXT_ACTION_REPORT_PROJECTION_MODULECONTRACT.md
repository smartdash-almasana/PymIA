# M58 — Owner Next Action Report Projection ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M58_OWNER_NEXT_ACTION_REPORT_PROJECTION`

---

## 1. Módulo autorizado

`pymia/smartpyme/owner_actions_projector.py`

---

## 2. Responsabilidad contractual

Este módulo proyecta una acción owner-facing ya resuelta a texto dentro de un `render_contract` existente sin alterar otras capas.

La frontera contractual es:

```text
render_contract
+ OwnerResolvedNextActionBundle
→ project_resolved_owner_actions_to_render_contract(...)
→ dict proyectado
```

---

## 3. Reglas de proyección

- la entrada `render_contract` no se muta;
- los textos proyectados provienen exclusivamente de `resolved_questions`;
- nunca se muestran IDs;
- la proyección preserva `tenant_id`, `references` y demás campos no relacionados;
- la proyección no crea `evidence_candidate`, diagnóstico ni findings.

---

## 4. Warnings trazables

La proyección debe usar un contenedor compatible con el contrato existente:

- `forbidden_inferences`, si ya existe;
- de lo contrario, `limit_warnings`.

Los warnings deben ser trazables y determinísticos.

---

## 5. Prohibiciones

Este módulo no puede:

- tocar `core_delivery_bridge.py`;
- tocar `graph.py` o `state.py`;
- tocar `owner_facing_report.py`;
- tocar `delivery_markdown.py`;
- inventar preguntas;
- abrir render paralelo.
