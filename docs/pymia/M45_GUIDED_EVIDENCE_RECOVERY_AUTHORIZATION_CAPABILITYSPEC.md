# M45 — Guided Evidence Recovery Authorization CapabilitySpec

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION`

---

## 1. Capacidad

PymIA puede abrir en el futuro una capacidad gobernada de `Guided Evidence Recovery` para pedir al dueño PyME evidencia faltante o sentido operativo faltante, sin inventar datos ni diagnosticar.

La capacidad autorizada es:

```text
OperationalAuditResult / gates / artefactos owner-facing
→ faltante trazado
→ pedido controlado de evidencia o aclaración operativa
```

---

## 2. Qué puede hacer

M45 puede autorizar una capacidad futura que:

- exponga qué evidencia falta;
- exponga qué aclaración operativa falta;
- traduzca bloqueos a pedidos concretos hacia el dueño;
- preserve distinción entre dato faltante y significado faltante;
- mantenga el caso en estado bloqueado o pendiente cuando corresponda.

---

## 3. Qué no puede hacer

M45 no autoriza:

- diagnóstico nuevo;
- findings nuevos;
- completar datos faltantes;
- inferir columnas o valores no entregados;
- reinterpretar el core;
- cambiar veredictos ya calculados;
- abrir Telegram, Hermes, FastAPI o runtime productivo;
- generar producto conversacional.

---

## 4. Inputs requeridos

- `OperationalAuditResult`
- `RenderContract`
- `OwnerFacingReport`, si existe
- `DeliveryPackage`
- `missing_evidence`
- `next_questions`
- `blocked_message`
- `EvidenceGateDecision`
- `FormulaInputGateResult`
- intake/evidence ya registrados

---

## 5. Outputs requeridos

Un artefacto o proyección futura de recuperación guiada que:

- pida evidencia faltante o sentido operativo faltante;
- no cambie el estado operacional subyacente;
- sea trazable al artefacto fuente;
- mantenga un modo fail-closed si falta base suficiente para pedir algo.

---

## 6. Failure states

La capacidad futura debe admitir:

- casos bloqueados por evidencia faltante;
- casos con aclaración operativa insuficiente;
- casos donde no hay base trazable suficiente y por lo tanto debe bloquearse sin preguntar de forma inventada.

---

## 7. Autoridad canónica

```text
ADR-019 — Guided Evidence Recovery Authority
```

---

## 8. Estado

```text
M45 = AUTHORIZED_DOCUMENTARY
```

Este documento autoriza la capacidad futura.

No certifica implementación, tests ni evidencia operativa.
