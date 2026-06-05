# M31-P — Registro maestro de pilotos asistidos

## Estado

READY_FOR_PILOTS_WITH_BLOCKED_INTAKE

## Propósito

Centralizar el estado de los 3 a 5 pilotos requeridos para evaluar M31-P operativo.

Este registro no declara PASS_OPERATIVO.

Sólo habilita la carga ordenada de pilotos bajo el contrato canónico definido en:

- `docs/smartpyme/M31P_PILOT_RECORD_TEMPLATE.md`
- `docs/smartpyme/M31P_PILOT_VALIDATION_CHECKLIST.md`
- `docs/smartpyme/M31P_CHECKPOINT.md`

## Estado actual de M31-P

```text
M31-P_DOCUMENTAL = PASS_DOCUMENTAL
M31-P_OPERATIVO = PENDING_PILOTS
```

## Reglas

- No inventar pilotos.
- No completar evidencia inexistente.
- No declarar PASS_OPERATIVO con menos de 3 pilotos completos.
- No contar intentos bloqueados como pilotos completos.
- No abrir M32.
- No tocar código productivo.
- No implementar Guided Evidence Recovery.
- No declarar producto.
- No convertir aprendizajes candidatos en LearningMemory automática.

## Contrato canónico

Cada piloto debe respetar estos campos:

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

## Pilotos requeridos

| Pilot ID | Estado | Registro | Checklist | Cuenta para PASS_OPERATIVO | Nota |
|---|---|---|---|---|---|
| M31P-001 | BLOCKED | `docs/smartpyme/pilots/M31P-001.md` | Aplicado como bloqueo documental | No | Falta caso real o realista con evidencia mínima |
| M31P-002 | PENDING | No creado | No aplicado | No | Pendiente de caso real o realista |
| M31P-003 | PENDING | No creado | No aplicado | No | Pendiente de caso real o realista |
| M31P-004 | OPTIONAL | No creado | No aplicado | No | Opcional |
| M31P-005 | OPTIONAL | No creado | No aplicado | No | Opcional |

## Registros auxiliares existentes

- `docs/smartpyme/pilots/README.md`
- `docs/smartpyme/pilots/M31P-001_INTAKE.md`
- `docs/smartpyme/pilots/M31P-001_DATA_REQUEST.md`
- `docs/smartpyme/pilots/M31P-001.md`

## Ubicación recomendada de registros individuales

Crear registros individuales sólo cuando exista caso real o realista suficiente:

```text
docs/smartpyme/pilots/M31P-002.md
docs/smartpyme/pilots/M31P-003.md
docs/smartpyme/pilots/M31P-004.md
docs/smartpyme/pilots/M31P-005.md
```

`M31P-001.md` ya existe como registro BLOCKED y no computable.

## Criterio para crear un piloto computable

Crear un registro individual computable sólo si existe, como mínimo:

- `pilot_id`;
- referencia de tenant o caso anonimizado;
- problema declarado por dueño PyME;
- evidencia recibida o ausencia explícita;
- evidencia faltante o lista vacía justificada;
- posibilidad de medir tiempo real;
- operador responsable o forma de registrar intervención humana;
- `operational_cost` con valor o `not_applicable`.

## Criterio para contar un piloto hacia PASS_OPERATIVO

Un piloto cuenta hacia PASS_OPERATIVO sólo si:

- tiene registro completo;
- tiene checklist aplicado;
- `final_status` no es un bloqueo por ausencia total de caso;
- `execution_time_minutes` está medido;
- `operational_cost` tiene valor o `not_applicable`;
- `blockers` está registrado;
- `candidate_learnings` está registrado, aunque sea lista vacía;
- `repeatability_assessment` está definido;
- `limitations` está definido.

## Estado agregado

```yaml
total_pilot_records_created: 1
total_pilots_complete: 0
total_pilots_blocked_before_execution: 1
total_pilots_counting_for_pass: 0
m31p_operational_status: PENDING_PILOTS
```

## Próximo paso

Conseguir o seleccionar un caso real o realista suficiente para crear un piloto computable.

Opciones válidas:

```text
M31P-002.md
```

O reemplazar `M31P-001.md` sólo si se aportan datos reales suficientes para dejar de estar BLOCKED.
