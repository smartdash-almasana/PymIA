# M45 — Guided Evidence Recovery Authorization ModuleContract

Fecha: 2026-06-09
Estado: VIGENTE
Frente: `M45_GUIDED_EVIDENCE_RECOVERY_AUTHORIZATION`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
artefactos soberanos con faltantes trazados
↔ proyección controlada de pedido de evidencia o sentido operativo
```

La frontera M45 no resuelve el faltante.

Sólo autoriza una futura proyección gobernada del faltante ya detectado.

---

## 2. Responsabilidades permitidas

La frontera M45 puede, en una implementación futura:

- leer artefactos soberanos existentes;
- identificar faltantes ya registrados;
- clasificar el faltante como evidencia o sentido operativo;
- proyectar preguntas o pedidos concretos hacia el dueño;
- conservar trazabilidad al artefacto de origen;
- mantener el estado fail-closed del caso.

---

## 3. Responsabilidades prohibidas

La frontera M45 no puede:

- recalcular diagnóstico;
- cambiar findings;
- cambiar gates;
- crear evidencia sintética;
- completar columnas, períodos o valores;
- usar Telegram, Hermes, FastAPI o runtime externo;
- esconder bloqueos;
- reemplazar artefactos soberanos;
- convertir un pedido de aclaración en una conclusión.

---

## 4. Invariantes

- Si el caso fuente está `BLOCKED`, la proyección de recovery no puede marcarlo como resuelto.
- Toda pregunta debe poder trazarse a un faltante ya registrado.
- Un faltante de evidencia no puede presentarse como hallazgo confirmado.
- Un faltante de sentido operativo no puede resolverse inventando contexto.
- La recuperación guiada no puede introducir nueva autoridad diagnóstica.

---

## 5. Dependencias permitidas

- `OperationalAuditResult`
- `RenderContract`
- `OwnerFacingReport`
- `DeliveryPackage`
- `EvidenceGateDecision`
- `FormulaInputGateResult`
- intake/evidence persistidos

No se autorizan dependencias a canales externos, narrativa libre ni fuentes no auditadas.

---

## 6. Side effects

Este contrato no autoriza side effects productivos.

Toda implementación futura deberá definir explícitamente si sólo proyecta texto/estado o si crea un artefacto documental adicional.

---

## 7. Determinismo

Para los mismos artefactos fuente, la clasificación del faltante y el pedido resultante deben preservar el mismo contenido semántico.

---

## 8. Estado

```text
M45 ModuleContract = AUTHORIZED_DOCUMENTARY
```

Este contrato autoriza la frontera futura.

No certifica implementación ni validación.
