# M56 — Visible Owner Next Action TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M56_VISIBLE_OWNER_NEXT_ACTION_BOUNDARY_AUDIT`

---

## 1. Objetivo

Cerrar una auditoría documental de frontera para la futura visibilidad de `OwnerNextActionBundle`.

No abrir implementación.

---

## 2. Fuente metodológica

Este TaskSpec deriva de:

- `AGENTS.md`
- `docs/adr/ADR-018-owner-facing-report-boundary.md`
- `docs/adr/ADR-022-owner-action-visibility-boundary.md`
- `docs/pymia/M52_OWNER_ANSWER_EVALUATION_AUTHORIZATION_TASKSPEC.md`
- `docs/pymia/M54_OWNER_ANSWER_EVALUATION_REPLAY_CHECKPOINT.md`
- `docs/pymia/M55_OWNER_NEXT_ACTION_DECISION_TASKSPEC.md`
- `docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_CAPABILITYSPEC.md`
- `docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_MODULECONTRACT.md`

---

## 3. Scope permitido

Archivos autorizados:

```text
docs/adr/ADR-022-owner-action-visibility-boundary.md
docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_CAPABILITYSPEC.md
docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_MODULECONTRACT.md
docs/pymia/M56_VISIBLE_OWNER_NEXT_ACTION_TASKSPEC.md
docs/DOCUMENTATION_INDEX.md
```

---

## 4. Criterios PASS

M56 puede declararse PASS si:

- el problema arquitectónico queda explícito;
- el riesgo de duplicación queda explicitado;
- la frontera owner-facing soberana queda fijada;
- el flujo futuro recomendado queda documentado;
- se prohíbe render paralelo;
- se documentan límites fail-closed;
- el diff es exclusivamente documental.

---

## 5. Archivos prohibidos

No tocar:

- `pymia/orchestration/graph.py`
- `pymia/orchestration/state.py`
- `pymia/audit_result/core_delivery_bridge.py`
- `pymia/smartpyme/owner_facing_report.py`
- `pymia/smartpyme/delivery_markdown.py`
- `pymia/smartpyme/owner_actions_decider.py`
- `pymia/contracts/owner_actions.py`
- `pymia/diagnostic_core/`
- `tests/`
- runtime, Telegram, Hermes, FastAPI, parser Excel, fórmulas, LLM o memoria

---

## 6. Próximos pasos

El próximo frente metodológico, si se autoriza, deberá:

1. definir contrato de resolución `target_question_id -> texto owner-facing`;
2. decidir si la proyección visible entra por `RenderContract`, `OwnerFacingReport` o ambos;
3. tocar `core_delivery_bridge.py` sólo bajo nueva autorización documental y técnica;
4. validar fail-closed cuando no exista resolución trazable.
