# M31-P — Registro maestro de pilotos asistidos

## Estado

READY_FOR_OPERATIVE_CHECKPOINT_LIMITED_INTERNAL

## Propósito

Centralizar el estado de los 3 a 5 pilotos requeridos para evaluar M31-P operativo.

Este registro no declara producto.

Este registro permite evaluar un checkpoint operativo limitado a pilotos internos realistas.

## Estado actual de M31-P

```text
M31-P_DOCUMENTAL = PASS_DOCUMENTAL
M31-P_OPERATIVO_INTERNO_REALISTA = READY_TO_EVALUATE
M31-P_OPERATIVO_CLIENTES_REALES = NOT_CERTIFIED
```

## Reglas

- No inventar pilotos.
- No completar evidencia inexistente.
- No declarar producto.
- No abrir M32 automáticamente.
- No tocar código productivo.
- No implementar Guided Evidence Recovery.
- No convertir aprendizajes candidatos en LearningMemory automática.
- Distinguir pilotos internos realistas de pilotos con clientes reales.

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

| Pilot ID | Estado | Registro | Checklist | Cuenta para PASS_OPERATIVO_INTERNO | Nota |
|---|---|---|---|---|---|
| M31P-001 | BLOCKED | `docs/smartpyme/pilots/M31P-001.md` | Aplicado como bloqueo documental | No | Falta caso real o realista con evidencia mínima |
| M31P-002 | COMPUTABLE_INTERNAL_REALISTIC_CASE | `docs/smartpyme/pilots/M31P-002.md` | Aplicado | Sí | Fixture textil con ejecución local reportada: `12 passed in 29.41s`; costo `not_applicable` |
| M31P-003 | COMPUTABLE_INTERNAL_REALISTIC_CASE | `docs/smartpyme/pilots/M31P-003.md` | Aplicado | Sí | Fixture `pyme_textil_compleja.xlsx`; usa ejecución local reportada de tests existentes |
| M31P-004 | COMPUTABLE_INTERNAL_REALISTIC_CASE | `docs/smartpyme/pilots/M31P-004.md` | Aplicado | Sí | Fixture `simple_bem_test.xlsx`; curación local reportada con `STATUS PARTIAL`, 1 tabla, 3 filas, 2 variables |
| M31P-005 | OPTIONAL | No creado | No aplicado | No | Opcional |

## Registros auxiliares existentes

- `docs/smartpyme/pilots/README.md`
- `docs/smartpyme/pilots/M31P-001_INTAKE.md`
- `docs/smartpyme/pilots/M31P-001_DATA_REQUEST.md`
- `docs/smartpyme/pilots/M31P-001.md`
- `docs/smartpyme/pilots/M31P-002_DATA_REQUEST.md`
- `docs/smartpyme/pilots/M31P-002.md`
- `docs/smartpyme/pilots/M31P-003.md`
- `docs/smartpyme/pilots/M31P-004.md`

## Issues operativos

- Issue #7: resuelto documentalmente como `DATA_REQUEST_PENDING`, luego evolucionado a piloto interno realista computable en `docs/smartpyme/pilots/M31P-002.md`.

## Criterio para contar un piloto hacia PASS_OPERATIVO_INTERNO

Un piloto interno realista cuenta si:

- tiene registro completo;
- tiene checklist aplicado;
- `final_status` no es un bloqueo por ausencia total de caso;
- `execution_time_minutes` está registrado;
- `operational_cost` tiene valor o `not_applicable`;
- `blockers` está registrado;
- `candidate_learnings` está registrado, aunque sea lista vacía;
- `repeatability_assessment` está definido;
- `limitations` está definido.

## Estado agregado

```yaml
total_pilot_records_created: 4
total_data_requests_created: 1
total_pilots_complete: 3
total_pilots_internal_realistic_computable: 3
total_pilots_blocked_before_execution: 1
total_pilots_counting_for_pass_internal: 3
total_real_client_pilots: 0
m31p_operational_internal_status: READY_TO_EVALUATE
m31p_real_client_status: NOT_CERTIFIED
```

## Interpretación

M31-P alcanzó el mínimo de 3 pilotos internos realistas computables.

Esto habilita redactar un checkpoint operativo limitado:

```text
PASS_OPERATIVO_INTERNO_REALISTA
```

No habilita afirmar:

```text
PASS_OPERATIVO_CLIENTES_REALES
producto
servicio comercial validado
M32 automático
```

## Próximo paso

Crear checkpoint operativo limitado:

```text
docs/smartpyme/M31P_OPERATIVE_INTERNAL_CHECKPOINT.md
```
