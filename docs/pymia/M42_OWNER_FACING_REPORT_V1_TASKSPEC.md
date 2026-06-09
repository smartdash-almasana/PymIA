# M42 — Owner-Facing Report V1 TaskSpec

Fecha: 2026-06-08
Estado: VIGENTE
Frente: `M42_DOCUMENTARY_REGULARIZATION_AND_OWNER_REPORT_AUTHORIZATION`

---

## 1. Objetivo

Autorizar el próximo frente implementativo para producir un `Owner-Facing Report V1` controlado y trazable, apoyado únicamente en artefactos soberanos ya existentes.

---

## 2. Slices autorizables

La implementación futura de M42 deberá dividirse al menos en:

- `M42-S1` contrato mínimo del reporte owner-facing
- `M42-S2` traducción de estados bloqueados/faltantes
- `M42-S3` traducción de estados entregables sin alterar findings ni diagnóstico

---

## 3. Archivos frontera esperados

La implementación futura podrá tocar sólo fronteras owner-facing específicas y tests focales del reporte.

No autoriza tocar:

- `DiagnosticCoreV1`
- parser Excel
- Telegram
- runtime conversacional
- fórmulas

---

## 4. Criterios PASS futuros

- el reporte se construye exclusivamente desde artefactos existentes;
- bloqueos y faltantes quedan visibles;
- no se inventan findings ni evidencia;
- la salida distingue `CANDIDATE` vs `CONFIRMED`;
- existe trazabilidad entre reporte y artefactos fuente.

---

## 5. Estado de autorización

```text
M42 = AUTHORIZED
```

La autorización es documental y metodológica.

No implica implementación inmediata.
