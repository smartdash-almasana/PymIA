# Post ADR-025 — Next Front Classification TaskSpec

Estado: `ACCEPTED`

Fecha: 2026-06-11

## 1. Enunciado

ADR-025 fue aceptado para impedir deriva posterior a C3 y distinguir cuatro fronteras:

```text
A. Faithful Operator local output
B. Bridge to Owner-Facing Report V1 under ADR-018
C. OwnerDecision / DecisionRecord capture under owner-decision-v1
D. Controlled Delivery — not authorized without additional contract
```

Este TaskSpec no implementa código.
No abre C4.
No autoriza delivery.
No autoriza reporte productivo.
No autoriza M36.

Su único objetivo es clasificar el próximo frente metodológico permitido.

## 2. Contexto certificado

Ciclos cerrados:

```text
C1 — Faithful Operator Catalog Reconciliation
C2 — Owner-facing Catalog Reconciliation Summary
C3 — Owner Confirmation Boundary for Catalog Summary
```

ADR aceptado:

```text
docs/adr/ADR-022-faithful-operator-output-vs-owner-report-delivery-boundary.md
```

ADR-025 establece:

```text
Faithful Operator local output ≠ Owner-Facing Report V1
Catalog summary confirmed ≠ diagnóstico final
Owner-Facing Report V1 ≠ Controlled Delivery automático
Controlled Delivery requiere contrato propio
```

## 3. Problema a resolver

Después de C3 existe una síntesis confirmada o corregida por el dueño, pero no existe autorización para convertirla automáticamente en:

```text
- diagnóstico final;
- reporte productivo;
- delivery;
- PDF;
- canal externo;
- plan de acción definitivo;
- productización.
```

Por lo tanto, el próximo frente debe clasificarse antes de diseñarse.

## 4. Categorías posibles según ADR-025

### A — Local Faithful Operator output continuation

Trabaja únicamente sobre salida local, asistida y no productiva del Faithful Operator.

Permitido sólo si mantiene:

```text
- carácter local;
- trazabilidad;
- no diagnóstico final;
- no delivery;
- no canal externo;
- no ejecución de acciones.
```

### B — Bridge to Owner-Facing Report V1 under ADR-018

Trabaja en un puente explícito entre salida local del Faithful Operator y `Owner-Facing Report V1`.

Requiere subordinarse a:

```text
docs/adr/ADR-018-owner-facing-report-boundary.md
M42 / M44 / M58, si aplican
```

No puede inventar artefactos ni duplicar reportes existentes.

### C — OwnerDecision / DecisionRecord capture under owner-decision-v1

Trabaja sobre captura formal de decisión del dueño.

Requiere subordinarse a:

```text
docs/contratos/owner-decision-v1.md
```

Debe distinguir:

```text
confirmación de síntesis ≠ DecisionRecord
DecisionRecord ≠ ejecución automática
```

### D — Controlled Delivery

No autorizado en este momento.

Requiere contrato adicional antes de cualquier TaskSpec funcional.

## 5. Clasificación recomendada

La opción metodológicamente más segura para el próximo frente es:

```text
C — OwnerDecision / DecisionRecord capture under owner-decision-v1
```

Razón:

```text
C3 ya captura confirmación/corrección/incertidumbre del dueño,
pero ADR-025 aclara que esa confirmación no equivale a DecisionRecord.
```

El gap real inmediato no es delivery, sino formalizar cuándo una respuesta del dueño se convierte, o no, en decisión registrable.

## 6. Frente NO recomendado ahora

No abrir todavía:

```text
A — Local Faithful Operator output continuation
```

Motivo:

```text
podría seguir acumulando salida local sin resolver autoridad de decisión.
```

No abrir todavía:

```text
B — Bridge to Owner-Facing Report V1
```

Motivo:

```text
riesgo de duplicar M42/M44/M58 sin reconciliación específica.
```

No abrir:

```text
D — Controlled Delivery
```

Motivo:

```text
ADR-025 lo declara no autorizado sin contrato adicional.
```

## 7. Próximo ciclo documental recomendado

Nombre recomendado:

```text
OD1 — Owner Decision Capture Boundary for Confirmed Catalog Summary
```

Tipo:

```text
Documentary TaskSpec + auditoría previa
```

No es C4.
No es delivery.
No es reporte final.
No es implementación todavía.

## 8. Objetivo de OD1

Definir si una respuesta del dueño posterior a C3 puede producir un `DecisionRecord` o si debe quedar como simple confirmación semántica.

OD1 debe distinguir:

```text
catalog_summary_confirmed
REQUEST_CLARIFICATION
APPROVE
AUTHORIZE_ACTION
STOP
DEFER
```

Y debe declarar explícitamente:

```text
catalog_summary_confirmed ≠ APPROVE
catalog_summary_confirmed ≠ AUTHORIZE_ACTION
```

## 9. Fuentes obligatorias para OD1

```text
AGENTS.md
docs/pymia/START_HERE_FOR_AGENTS.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
docs/adr/ADR-022-faithful-operator-output-vs-owner-report-delivery-boundary.md
docs/contratos/owner-decision-v1.md
docs/pymia/C3_OWNER_CONFIRMATION_BOUNDARY_FOR_CATALOG_SUMMARY_CHECKPOINT.md
pymia/faithful_operator.py
tests/test_owner_confirmation_boundary_for_catalog_summary.py
```

## 10. Prohibiciones para OD1

```text
- no delivery;
- no PDF;
- no Telegram;
- no DB;
- no Hermes;
- no runtime externo;
- no diagnóstico final;
- no recomendaciones definitivas;
- no ejecución de acciones;
- no M36;
- no nuevos puertos o gates formales sin ADR propio;
- no tocar matcher ni catálogos.
```

## 11. Stop conditions

Bloquear OD1 si:

```text
- se intenta convertir confirmación semántica en autorización;
- se intenta ejecutar una acción posterior;
- se requiere canal externo;
- se requiere persistencia productiva;
- se intenta abrir delivery;
- se intenta duplicar M42/M44/M58;
- se confunde DecisionRecord con owner-facing report.
```

## 12. Criterio de cierre de este TaskSpec

Este TaskSpec cierra si una auditoría externa confirma:

```text
- que la clasificación C es correcta;
- que no debe abrirse C4;
- que OD1 es documentalmente válido como próximo frente;
- que no autoriza implementación sin TaskSpec propio auditado.
```
