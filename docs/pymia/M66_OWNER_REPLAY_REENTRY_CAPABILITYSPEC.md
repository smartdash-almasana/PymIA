# M66 — Owner Replay Reentry CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M66_OWNER_REPLAY_REENTRY_SPEC`

---

## 1. Propósito

Definir la futura capacidad de reentrada del flujo owner-answer hacia `core_delivery_bridge.py`.

M66 no implementa esa reentrada.

M66 sólo fija la especificación documental mínima para abrir un hito posterior de integración.

---

## 2. Contrato conceptual

La tesis aprobada para la futura integración es:

```text
CoreAuditDeliveryBundle
+ OwnerAnswerToActionCompositionResult
→ projected CoreAuditDeliveryBundle
```

La proyección futura deberá operar sobre artefactos estructurados ya trazables.

No autoriza atajos desde texto libre.

---

## 3. Frontera visible

`OwnerFacingReport` sigue siendo la única salida visible soberana.

La futura reentrada:

- no podrá reemplazar `OwnerFacingReport`;
- no podrá crear una salida owner-facing paralela;
- sólo podrá reconstruir o reproyectar la frontera visible existente de forma controlada.

---

## 4. Regla sobre formatter sandbox

`owner_answer_replay_formatter.py` no puede usarse como salida productiva.

Ese formatter permanece en condición de:

- sandbox;
- debug;
- revisión humana controlada.

No constituye frontera visible soberana.

---

## 5. Reglas de seguridad

La futura implementación deberá:

- no mutar el bundle original;
- fallar en cerrado ante `question_id` inválido o desalineado;
- no diagnosticar;
- no promover `OwnerAnswer` a evidencia dura;
- no crear renderer paralelo;
- no tocar `graph.py`, runtime ni Telegram.

Además deberá:

- preservar bloqueos;
- preservar trazabilidad;
- preservar findings y diagnóstico existentes sin cambios;
- rechazar cualquier proyección que necesite completar datos con LLM o memoria conversacional.

---

## 6. Próximo test futuro

El test futuro mínimo esperado es:

```text
test_bridge_reentry_contract_projection
```

Ese test deberá certificar:

- entrada estructurada;
- no mutación;
- fail-closed;
- preservación de `OwnerFacingReport` como frontera visible;
- ausencia de renderer paralelo.
