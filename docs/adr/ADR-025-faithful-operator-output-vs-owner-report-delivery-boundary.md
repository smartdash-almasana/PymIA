# ADR-025 — Faithful Operator Output vs Owner-Facing Report and Controlled Delivery Boundary

## Status

ACCEPTED

## Fecha

2026-06-11

## Dueño conceptual

Faithful Operator / Owner-Facing Boundary / Delivery Governance

## Context

Después de C1, C2 y C3, el flujo local del `Faithful Operator` quedó fortalecido:

```text
C1: Faithful Operator → StructuredEvidence → evidence_requirement_matcher → catalog_reconciliation
C2: catalog_reconciliation → síntesis owner-facing no diagnóstica
C3: síntesis owner-facing → confirmación/corrección/incertidumbre del dueño
```

Los checkpoints C1, C2 y C3 certifican capacidades locales y trazables, pero también declaran explícitamente lo que no certifican:

```text
- diagnóstico final;
- recomendaciones operativas definitivas;
- Guided Evidence Recovery;
- M36;
- Telegram;
- DB;
- PDF;
- Hermes;
- runtime externo;
- productización;
- delivery controlado;
- nuevos puertos o gates formales.
```

Además, `ADR-018 — Owner-Facing Report Boundary` ya autoriza `Owner-Facing Report V1` como renderización controlada de artefactos existentes del pipeline soberano, no como diagnóstico nuevo ni como expansión interpretativa.

El contrato `owner-decision-v1` establece una regla central:

```text
SmartPyme no decide; solo propone.
```

La confirmación del dueño sobre una síntesis no equivale automáticamente a autorización para ejecutar acciones, emitir un reporte productivo, iniciar delivery o activar un canal externo.

## Problem

Después de C3 aparece una ambigüedad documental:

```text
si el dueño confirma la síntesis owner-facing local,
¿qué está autorizado a hacer PymIA después?
```

Sin una frontera explícita, existe riesgo de deriva:

```text
catalog_summary_confirmed
→ cierre operativo fuerte
→ next actions definitivas
→ delivery
→ producto
```

Ese salto no está autorizado por C1, C2 ni C3.

También existe riesgo de duplicar o saltear frentes ya documentados como M42, M44 y M58, que regulan owner-facing report, salida visible y proyección de próximos pasos en otros contextos del pipeline.

## Decision

Se define una frontera documental entre cuatro conceptos distintos:

```text
1. Faithful Operator local output
2. Catalog summary confirmed by owner
3. Owner-Facing Report V1
4. Controlled Delivery
```

Esta ADR no autoriza implementación nueva.
Esta ADR no abre C4.
Esta ADR no registra puertos ni gates nuevos.
Esta ADR no habilita delivery.

Su función es impedir que la salida local confirmada del `Faithful Operator` sea confundida con reporte productivo, diagnóstico final, recomendación definitiva o entrega controlada.

## Boundary definitions

### 1. Faithful Operator local output

Es una salida local, asistida, trazable y no productiva del `Faithful Operator`.

Puede contener:

```text
- tenant_id;
- intake_id;
- evidence_id;
- evidence_hash;
- run_id;
- output_hash;
- catalog_reconciliation;
- síntesis owner-facing;
- owner_confirmation_status;
- límites explícitos.
```

No puede ser tratado como:

```text
- diagnóstico final;
- reporte productivo;
- delivery;
- PDF;
- canal externo;
- autorización para ejecutar acciones;
- producto terminado.
```

### 2. Catalog summary confirmed by owner

Es el estado en el que el dueño confirma que la síntesis owner-facing representa razonablemente el contexto operativo revisado.

Puede significar:

```text
- la síntesis no fue rechazada por el dueño;
- el dueño reconoce que el resumen representa su situación;
- el sistema puede registrar esa confirmación como hito local.
```

No significa:

```text
- diagnóstico final;
- aprobación de acción;
- autorización de delivery;
- recomendación definitiva;
- decisión operativa ejecutable;
- cierre comercial;
- transición automática a reporte productivo.
```

### 3. Owner-Facing Report V1

Es la renderización controlada regulada por ADR-018 y los documentos de capability/task correspondientes.

Debe derivar de artefactos existentes y trazables.

No puede inventar evidencia, cambiar estados, crear findings nuevos ni ocultar bloqueos.

La existencia de una síntesis confirmada por el dueño puede ser una entrada contextual, pero no reemplaza los artefactos soberanos requeridos por ADR-018.

### 4. Controlled Delivery

Es cualquier entrega formal al dueño o a un canal externo con expectativa de consumo operativo.

Incluye, por ejemplo:

```text
- reporte final;
- PDF;
- publicación en canal;
- salida visible persistente;
- envío a tercero;
- paquete entregable;
- recomendación formal;
- acción posterior basada en el reporte.
```

Controlled Delivery requiere contrato o TaskSpec propio.

No queda autorizado por C1, C2, C3 ni por esta ADR.

## Allowed after C3

Después de C3, si existe `catalog_summary_confirmed`, queda permitido únicamente:

```text
- conservar la confirmación en el estado local;
- conservar la traza de evidencia y reconciliación;
- declarar que la síntesis fue confirmada por el dueño;
- mantener el límite explícito de no diagnóstico final;
- bloquear acciones posteriores si no existe DecisionRecord o TaskSpec habilitante.
```

## Not allowed after C3

Queda prohibido inferir automáticamente desde `catalog_summary_confirmed`:

```text
- diagnóstico final;
- recomendación operativa definitiva;
- plan de acción;
- delivery;
- PDF;
- canal externo;
- ejecución de job;
- Guided Evidence Recovery;
- M36;
- creación de reporte productivo;
- cierre operativo fuerte;
- autorización para cambiar estado de negocio.
```

## Relationship with owner-decision-v1

La confirmación de una síntesis owner-facing no es necesariamente un `DecisionRecord`.

Para autorizar acciones posteriores debe existir un registro compatible con `owner-decision-v1`, por ejemplo:

```text
APPROVE
AUTHORIZE_ACTION
REQUEST_CLARIFICATION
STOP
DEFER
```

La evidencia y la síntesis pueden informar una decisión, pero no la sustituyen.

## Relationship with ADR-018

ADR-018 sigue gobernando `Owner-Facing Report V1`.

Esta ADR agrega una frontera previa:

```text
Faithful Operator local output ≠ Owner-Facing Report V1
Catalog summary confirmed ≠ Owner-Facing Report V1
Owner-Facing Report V1 ≠ Controlled Delivery automático
```

Cualquier puente entre `Faithful Operator local output` y `Owner-Facing Report V1` requiere TaskSpec explícito y debe respetar ADR-018.

## Consequences

Desde esta ADR:

```text
- no se puede abrir un ciclo de delivery sólo porque C3 está cerrado;
- no se puede abrir un ciclo de cierre operativo fuerte sólo porque el dueño confirmó la síntesis;
- cualquier próximo ciclo debe declarar si trabaja sobre output local, reporte owner-facing o delivery;
- si trabaja sobre delivery, requiere contrato explícito;
- si trabaja sobre owner-facing report, debe subordinarse a ADR-018;
- si trabaja sobre DecisionRecord, debe subordinarse a owner-decision-v1;
- si trabaja sobre Faithful Operator local output, debe conservar su carácter local, asistido y no productivo.
```

## Authorized next documentary move

El próximo movimiento metodológico permitido no es implementación.

Queda autorizado crear un TaskSpec documental de reconciliación si y sólo si su objetivo es clasificar el próximo frente bajo una de estas categorías:

```text
A. Local Faithful Operator output continuation
B. Bridge to Owner-Facing Report V1 under ADR-018
C. OwnerDecision/DecisionRecord capture under owner-decision-v1
D. Controlled Delivery — not authorized without additional contract
```

Ese TaskSpec debe ser auditado antes de cualquier código.

## Explicit non-authorization

Esta ADR no autoriza:

```text
- C4 funcional;
- delivery;
- PDF;
- Telegram;
- DB;
- Hermes;
- runtime externo;
- diagnóstico final;
- recomendaciones definitivas;
- nuevos puertos o gates;
- M36;
- productización.
```

## Status note

Estado inicial `PROPOSED`. Cambiado a `ACCEPTED` mediante auditoría documental externa (2026-06-11).

No debe usarse como base de implementación fuera de los lentes autorizados por OD1.
