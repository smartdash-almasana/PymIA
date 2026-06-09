# M56 — Visible Owner Next Action CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M56_VISIBLE_OWNER_NEXT_ACTION_BOUNDARY_AUDIT`

---

## 1. Objetivo

Documentar la frontera correcta para hacer visible `OwnerNextActionBundle` sin crear renderizador paralelo ni duplicar `OwnerFacingReport`.

Este frente es:

```text
documental / boundary audit
```

---

## 2. Fuente metodológica

Este CapabilitySpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M44_VISIBLE_OWNER_REPORT_OUTPUT_CAPABILITYSPEC.md`
- `docs/pymia/M49_VISIBLE_OWNER_QUESTIONS_CAPABILITYSPEC.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md`

---

## 3. Capacidad auditada

M56 no autoriza implementación visible todavía.

Autoriza únicamente dejar explícito que la futura visibilidad de `OwnerNextActionBundle` debe:

- conservar `OwnerFacingReport` como frontera owner-facing soberana;
- evitar render paralelo;
- evitar que `graph.py` conozca `OwnerNextActionBundle`;
- requerir resolución previa de `target_questions` desde IDs a texto.

---

## 4. Decisiones explícitas

- `OwnerFacingReport` sigue siendo la frontera owner-facing soberana.
- `delivery_markdown.py` queda fuera de lógica conversacional.
- `graph.py` no debe conocer `OwnerNextActionBundle`.
- `core_delivery_bridge.py` es candidato futuro de integración, pero no se modifica en M56.
- `target_questions` hoy contiene IDs; la resolución `ID -> texto` debe definirse antes de cualquier render visible.
- `OwnerAnswer` y `OwnerNextAction` no se promueven a evidencia dura.
- no hay diagnóstico ni findings nuevos.

---

## 5. Criterios PASS

M56 puede declararse PASS si:

- existe un ADR de frontera explícito;
- la frontera owner-facing soberana queda inequívoca;
- queda prohibido el render paralelo;
- quedan documentados los límites fail-closed;
- no se toca código, tests ni runtime.

---

## 6. Archivos prohibidos

M56 no autoriza tocar:

- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/smartpyme/owner_facing_report.py`
- `pymia/smartpyme/delivery_markdown.py`
- `pymia/smartpyme/owner_actions_decider.py`
- `pymia/contracts/owner_actions.py`
- `tests/`
- runtime, Telegram, Hermes, FastAPI, parser, fórmulas, LLM o memoria.

---

## 7. Próximo paso

El próximo frente, si se autoriza, deberá definir:

```text
target_question_id
→ texto owner-facing trazable
→ proyección vía RenderContract / OwnerFacingReport
```
