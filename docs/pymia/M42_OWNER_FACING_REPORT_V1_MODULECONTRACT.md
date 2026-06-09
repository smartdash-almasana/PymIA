# M42 — Owner-Facing Report V1 ModuleContract

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M42_DOCUMENTARY_REGULARIZATION_AND_OWNER_REPORT_AUTHORIZATION`

---

## 1. Frontera

Este contrato regula la frontera entre:

```text
artefactos operacionales soberanos
↔ traducción controlada owner-facing
```

La frontera de owner-facing queda subordinada a la salida soberana existente.

---

## 2. Responsabilidades permitidas

La frontera M42 puede:

- leer `OperationalAuditResult`, `RenderContract` y `DeliveryPackage`;
- proyectar estado, evidencia usada, evidencia faltante, preguntas y pasos siguientes;
- traducir bloqueo de forma legible sin alterar su significado.

---

## 3. Responsabilidades prohibidas

La frontera M42 no puede:

- recalcular diagnóstico;
- cambiar findings;
- introducir semántica no presente en artefactos fuente;
- ocultar estados de bloqueo;
- degradar trazabilidad;
- reemplazar artefactos soberanos.

---

## 4. Invariantes

- si el estado fuente es `BLOCKED`, el reporte debe permanecer bloqueado;
- si un finding está en estado candidato, no puede elevarse a confirmado;
- toda afirmación del reporte debe poder trazarse a un artefacto fuente.

---

## 5. Dependencias permitidas

- `pymia.audit_result.models`
- `pymia.contracts.scn_render_contract`
- `pymia.smartpyme.delivery_package`

No se autorizan dependencias directas a fuentes no auditadas o a narrativa libre.
