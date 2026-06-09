# M66 — Owner Replay Reentry TaskSpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M66_OWNER_REPLAY_REENTRY_SPEC`

---

## 1. Naturaleza del hito

Este hito M66 sólo documenta.

No implementa código.
No modifica Python.
No modifica tests.
No toca `core_delivery_bridge.py`.

---

## 2. Implementación futura

La implementación futura de bridge reentry deberá abrirse como otro hito independiente.

Ese hito posterior deberá traer:

- CapabilitySpec propio de implementación;
- ModuleContract propio;
- TaskSpec propio;
- tests focales;
- evidencia local de no mutación y fail-closed.

---

## 3. Archivos candidatos futuros

Los candidatos futuros autorizables son:

- `pymia/audit_result/core_delivery_bridge.py`
- un test específico de bridge reentry

M66 no los modifica.

---

## 4. Criterio de implementación futura

La futura implementación deberá cumplir esta secuencia:

1. entrada: `CoreAuditDeliveryBundle` + respuestas estructuradas;
2. composición owner-answer;
3. proyección sobre `render_contract`;
4. reconstrucción controlada de `OwnerFacingReport` usando la frontera existente;
5. output: nuevo `CoreAuditDeliveryBundle` proyectado.

Además deberá cumplir:

- no mutación;
- fail-closed;
- no diagnóstico nuevo;
- no promoción a evidencia dura;
- no renderer paralelo.

---

## 5. Criterio PASS documental de M66

M66 puede declararse PASS si:

- los docs de especificación existen;
- `docs/DOCUMENTATION_INDEX.md` los indexa;
- no se tocó ningún archivo Python;
- no se tocó ningún test;
- no se abrió implementación prematura de bridge reentry.
