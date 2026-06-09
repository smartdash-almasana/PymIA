# M56 — Visible Owner Next Action ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M56_VISIBLE_OWNER_NEXT_ACTION_BOUNDARY_AUDIT`

---

## 1. Frontera contractual auditada

La futura frontera visible correcta es:

```text
OwnerNextActionBundle
→ resolución target_questions IDs/textos
→ RenderContract / OwnerFacingReport
→ respuesta visible existente
```

---

## 2. Fuente owner-facing soberana

El artefacto owner-facing soberano sigue siendo:

`OwnerFacingReport`

Ningún módulo paralelo debe adquirir autoridad equivalente.

---

## 3. Módulos fuera de alcance visible

En esta frontera:

- `delivery_markdown.py` no adquiere lógica conversacional;
- `graph.py` no adquiere conocimiento de `OwnerNextActionBundle`;
- `core_delivery_bridge.py` queda reservado como candidato futuro de integración visible;
- `OwnerNextActionBundle` permanece interno hasta que exista resolución contractual de IDs a texto.

---

## 4. Dependencia contractual faltante

Antes de cualquier implementación visible, debe existir un contrato explícito que resuelva:

- `target_questions: list[str]`
- textos owner-facing correspondientes
- trazabilidad entre ID, pregunta y acción visible

Sin esa dependencia, el sistema debe fallar en cerrado.

---

## 5. Prohibiciones

Queda prohibido:

- render visible de IDs crudos;
- duplicación de `OwnerFacingReport`;
- render paralelo de acciones owner-facing;
- promoción a evidencia dura;
- diagnóstico nuevo;
- findings nuevos.
