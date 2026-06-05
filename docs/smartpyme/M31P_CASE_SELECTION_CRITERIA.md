# M31-P — Criterio de selección de casos piloto

## Estado

READY_FOR_CASE_SELECTION

## Propósito

Definir cuándo un caso puede convertirse en piloto M31-P computable y cuándo debe quedar como intake, solicitud de datos o bloqueo.

Este documento evita crear pilotos vacíos, ficticios o no comparables.

## Relación con M31-P

M31-P necesita 3 a 5 pilotos computables para aspirar a PASS_OPERATIVO.

Un caso computable no significa caso exitoso.

Un caso computable significa que puede registrarse bajo el contrato canónico con evidencia suficiente para evaluar repetibilidad, tiempo, costo, salida o bloqueo.

## Contrato canónico requerido

Todo caso computable debe poder completar estos campos:

```yaml
pilot_id:
tenant_ref:
case_date:
business_type:
case_origin:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
missing_evidence:
protocol_steps_applied:
output_delivered:
final_status:
execution_time_minutes:
operational_cost:
human_intervention:
operator_notes:
blockers:
candidate_learnings:
repeatability_assessment:
limitations:
```

## Criterio de entrada mínimo

Un caso puede abrirse como piloto computable si tiene:

1. Problema declarado por dueño PyME.
2. Tenant o referencia de caso anonimizada.
3. Evidencia recibida o ausencia explícita suficientemente documentada.
4. Evidencia faltante identificable.
5. Sentido operativo mínimo o gap de sentido operativo registrable.
6. Posibilidad de medir tiempo real.
7. Criterio para registrar costo operativo o `not_applicable`.
8. Posibilidad de cerrar como DELIVERED, PARTIAL, BLOCKED o UNSUPPORTED bajo contrato.

## Casos aptos

Son aptos para M31-P casos como:

- dueño dice “no sé si gano plata” y aporta ventas/costos o declara qué falta;
- dueño dice “vendo mucho pero no queda plata” y aporta Excel de ventas, precios o compras;
- dueño dice “no me cierra caja/banco” y aporta extracto, reporte o describe faltantes;
- dueño dice “no entiendo este Excel” y aporta el archivo;
- dueño dice “creo que los costos están desactualizados” y aporta lista de precios/costos o facturas;
- caso realista interno con archivos controlados y problema declarado explícitamente.

## Casos no aptos todavía

No son aptos para piloto computable si:

- no hay problema declarado;
- no hay tenant o referencia anonimizada;
- no hay evidencia ni ausencia explícita de evidencia;
- no puede medirse tiempo real;
- no puede registrarse costo operativo o `not_applicable`;
- no puede aplicarse el protocolo M31 sin código nuevo;
- requiere Guided Evidence Recovery no implementado;
- exige UI, PDF profesional, ERP, dispatcher o runtime nuevo.

## Clasificación previa

Antes de crear `M31P-00X.md`, clasificar el caso como uno de:

```text
READY_FOR_PILOT
INTAKE_PENDING
DATA_REQUEST_PENDING
BLOCKED_NO_CASE
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
UNSUPPORTED
```

## Decisión por estado

### READY_FOR_PILOT

Crear registro individual computable:

```text
docs/smartpyme/pilots/M31P-00X.md
```

### INTAKE_PENDING

Crear o mantener intake:

```text
docs/smartpyme/pilots/M31P-00X_INTAKE.md
```

### DATA_REQUEST_PENDING

Crear o mantener solicitud de datos:

```text
docs/smartpyme/pilots/M31P-00X_DATA_REQUEST.md
```

### BLOCKED_NO_CASE

Documentar bloqueo si ya se intentó abrir piloto sin caso.

### BLOCKED_NEEDS_EVIDENCE

Documentar qué evidencia falta.

### BLOCKED_OUT_OF_SCOPE

Documentar por qué el caso exige capacidades fuera de M31-P.

### UNSUPPORTED

Registrar que el caso no pertenece a M31-P.

## Matriz de decisión rápida

| Condición | Acción |
|---|---|
| Hay problema + evidencia + tiempo medible + costo registrable | Crear piloto computable |
| Hay problema pero falta evidencia concreta | Crear data request |
| Hay intención de piloto pero no hay caso | Crear intake bloqueado |
| Requiere código nuevo | BLOCKED_OUT_OF_SCOPE |
| Requiere Guided Evidence Recovery | BLOCKED_OUT_OF_SCOPE |
| Requiere producto/UI/ERP | BLOCKED_OUT_OF_SCOPE |

## Regla de bloqueo sano

Un bloqueo bien documentado es evidencia operativa.

Pero no cuenta como piloto completo para PASS_OPERATIVO si no cumple contrato canónico y no permite evaluar repetibilidad con tiempo y costo reales.

## Regla de no invención

No completar:

- problema declarado;
- evidencia recibida;
- sentido operativo;
- tiempo real;
- costo operativo;
- salida entregada;

si no existen datos para sostenerlos.

## Próximo paso

Seleccionar el próximo caso candidato y clasificarlo con este criterio antes de crear `M31P-002.md`.
