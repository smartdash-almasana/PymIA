# M42 — Owner-Facing Report V1 CapabilitySpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M42_DOCUMENTARY_REGULARIZATION_AND_OWNER_REPORT_AUTHORIZATION`

---

## 1. Capacidad

PymIA puede producir un `Owner-Facing Report V1` sólo como traducción controlada del estado operacional ya calculado por el sistema.

La capacidad autorizada es:

```text
OperationalAuditResult
+ RenderContract
+ DeliveryPackage
→ Owner-Facing Report V1
```

---

## 2. Qué puede hacer

M42 puede:

- traducir para lectura humana del dueño el estado operacional ya existente;
- exponer evidencia usada y evidencia faltante;
- exponer preguntas siguientes y pasos siguientes;
- exponer mensaje de bloqueo cuando exista;
- preservar distinción entre entregado y bloqueado.

---

## 3. Inputs requeridos

- `RenderContract`
- `DeliveryPackage`
- `OperationalAuditResult`
- `missing_evidence`
- `evidence_used`
- `next_questions`
- `next_steps`
- `blocked_message`

---

## 4. Outputs requeridos

Un artefacto owner-facing controlado que:

- no cambia el estado operacional;
- no agrega findings;
- no recalcula nada;
- refleja el estado real del circuito.

---

## 5. Limitaciones obligatorias

M42 no autoriza:

- inventar evidencia;
- findings nuevos;
- diagnóstico nuevo;
- confirmaciones no trazables;
- narrativa libre sin backing;
- ocultar bloqueos;
- presentar `CANDIDATE` como `CONFIRMED`.

---

## 6. Failure states

La capacidad debe admitir:

- reportes de entrega cuando existan artefactos suficientes;
- reportes bloqueados cuando el circuito esté bloqueado;
- fail-closed si faltan artefactos necesarios para traducir de forma segura.

---

## 7. Autoridad canónica

```text
ADR-018 — Owner-Facing Report Boundary
```
