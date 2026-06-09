# M49 — Visible Owner Questions ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M49_VISIBLE_OWNER_QUESTIONS`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
OwnerQuestionsBundle
↔ render_contract
↔ artefactos visibles ya existentes
```

La frontera M49 no construye preguntas nuevas.

Sólo proyecta preguntas ya construidas por M47/M48.

---

## 2. Responsabilidades permitidas

La frontera M49 puede:

- leer `OwnerQuestionsBundle.questions`;
- extraer `question_text` válidos;
- poblar `render_contract["next_questions"]`;
- asignar la primera pregunta a `render_contract["blocked_message"]`;
- escribir `render_contract.json` después de esa actualización.

---

## 3. Responsabilidades prohibidas

La frontera M49 no puede:

- tocar `graph.py`;
- tocar `PymIAState`;
- mutar el builder de preguntas;
- generar nuevas preguntas por heurística;
- recalcular diagnóstico;
- abrir canales externos;
- reescribir artefactos fuente fuera del bridge.

---

## 4. Invariantes

- el orden de preguntas visibles debe seguir el orden del bundle;
- sólo `question_text` no vacíos pueden proyectarse;
- `blocked_message` visible debe ser la primera pregunta si existe;
- `render_contract.json` debe persistirse después de la proyección;
- el cambio no debe introducir nueva semántica diagnóstica.

---

## 5. Estado

```text
M49 ModuleContract = AUTHORIZED_FOR_IMPLEMENTATION
```

Este contrato autoriza la proyección visible mínima de preguntas owner-facing.
