# M31-P — Runbook operativo para pilotos asistidos

## Estado

READY_FOR_OPERATOR_USE

## Propósito

Guiar la ejecución de pilotos M31-P sin abrir M32, sin tocar código productivo y sin inventar evidencia.

Este runbook traduce la documentación M31-P en un procedimiento operativo para seleccionar, registrar, validar y cerrar casos piloto.

## Fuente obligatoria

Antes de operar, leer:

1. `AGENTS.md`
2. `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
3. `docs/smartpyme/M31P_CASE_SELECTION_CRITERIA.md`
4. `docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md`
5. `docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md`
6. `docs/smartpyme/M31P_PILOTS_REGISTRY.md`
7. `docs/smartpyme/M31P_CHECKPOINT.md`

## Estado inicial conocido

```yaml
M31-P_DOCUMENTAL: PASS_DOCUMENTAL
M31-P_OPERATIVO: PENDING_PILOTS
M31P-001: BLOCKED / no computable
M31P-002: DATA_REQUEST_PENDING / no computable
M32: BLOQUEADO
```

## Procedimiento

### Paso 1 — Recibir candidato

Registrar candidato sólo si existe una fuente concreta:

- cliente real;
- prospecto;
- caso interno realista;
- demo realista con problema declarado explícito.

No crear piloto computable sólo por necesidad de avanzar.

### Paso 2 — Clasificar candidato

Usar `M31P_CASE_SELECTION_CRITERIA.md`.

Estados posibles:

```text
READY_FOR_PILOT
INTAKE_PENDING
DATA_REQUEST_PENDING
BLOCKED_NO_CASE
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
UNSUPPORTED
```

### Paso 3 — Elegir archivo de salida

Según clasificación:

| Clasificación | Archivo |
|---|---|
| READY_FOR_PILOT | `docs/smartpyme/pilots/M31P-00X.md` |
| INTAKE_PENDING | `docs/smartpyme/pilots/M31P-00X_INTAKE.md` |
| DATA_REQUEST_PENDING | `docs/smartpyme/pilots/M31P-00X_DATA_REQUEST.md` |
| BLOCKED_* | `docs/smartpyme/pilots/M31P-00X.md` con `final_status: BLOCKED` |
| UNSUPPORTED | `docs/smartpyme/pilots/M31P-00X.md` con `final_status: UNSUPPORTED` |

### Paso 4 — Completar contrato canónico

Todo piloto computable debe usar exactamente estos campos:

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

No usar:

```text
status
evidence_received
evidence_missing
business_context
```

salvo como nombres prohibidos en documentación.

### Paso 5 — Medir tiempo

Para que un piloto cuente hacia PASS_OPERATIVO:

```yaml
execution_time_minutes: <número medido>
```

Si no se mide tiempo, el caso puede documentarse, pero no cuenta para PASS_OPERATIVO.

### Paso 6 — Registrar costo operativo

Todo piloto debe incluir:

```yaml
operational_cost:
```

Valores válidos:

- monto o estimación explícita;
- `not_applicable`;
- `not_measured`, sólo con justificación en `limitations`.

Para PASS_OPERATIVO debe ser valor o `not_applicable`.

### Paso 7 — Aplicar checklist

Aplicar `M31P_PILOT_VALIDATION_CHECKLIST.md`.

Si falla un punto obligatorio, no contar el piloto hacia PASS_OPERATIVO.

### Paso 8 — Actualizar registry

Actualizar `M31P_PILOTS_REGISTRY.md` con:

- estado del piloto;
- archivo creado;
- checklist aplicado o no;
- si cuenta para PASS_OPERATIVO;
- nota breve.

### Paso 9 — Evaluar cierre de fase

M31-P sólo puede pasar a PASS_OPERATIVO si hay:

- 3 a 5 pilotos completos;
- checklist aplicado por piloto;
- `execution_time_minutes` medido en todos los pilotos que cuentan;
- `operational_cost` registrado con valor o `not_applicable`;
- salidas o bloqueos documentados;
- evaluación de repetibilidad por piloto;
- evaluación agregada;
- checkpoint operativo.

## Prohibiciones

- No abrir M32.
- No tocar código productivo.
- No declarar producto.
- No declarar autonomía.
- No implementar Guided Evidence Recovery.
- No convertir `candidate_learnings` en LearningMemory automática.
- No declarar PASS_OPERATIVO sin 3 pilotos computables.

## Regla de bloqueo sano

Un bloqueo documentado puede ser evidencia operativa.

Pero sólo cuenta para PASS_OPERATIVO si el caso tiene contrato completo, tiempo medido, costo registrado y evaluación de repetibilidad.

Un bloqueo por ausencia total de caso no cuenta.

## Próximo uso esperado

Cuando haya candidato real o realista, aplicar este runbook para crear o actualizar:

```text
docs/smartpyme/pilots/M31P-002.md
```

si el caso cumple `READY_FOR_PILOT`, o mantenerlo como `DATA_REQUEST_PENDING` si no cumple.
