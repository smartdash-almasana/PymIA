# M31-R — Registro maestro de pilotos reales/prospectos controlados

## Estado

READY_FOR_REAL_PROSPECTS

## Propósito

Registrar 3 a 5 pilotos con prospectos o clientes reales bajo el contrato M31-R.

Este registro no declara producto.

Este registro no declara PASS_OPERATIVO_CLIENTES_REALES hasta que existan pilotos reales completos.

## Estado actual

```yaml
m31r_documental_status: READY_FOR_REAL_PROSPECTS
m31r_operational_real_clients_status: PENDING_REAL_PILOTS
product_status: NOT_CERTIFIED
m32_status: BLOCKED
```

## Fuente contractual

- `docs/adr/ADR-M31R-PILOTOS-REALES-CONTROLADOS.md`
- `docs/smartpyme/M31R_CAPABILITY_SPEC.md`
- `docs/smartpyme/M31R_TASK_SPEC.md`
- `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md`
- `docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md`
- `docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md`

## Contrato canónico de piloto real

```yaml
pilot_id:
prospect_ref:
contact_date:
business_type:
case_origin:
owner_or_operator_role:
fit_status:
accepted_no_promises:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
missing_evidence:
commercial_mode:
operational_cost:
execution_time_minutes:
protocol_steps_applied:
output_delivered:
final_status:
human_intervention:
operator_notes:
feedback:
blockers:
candidate_learnings:
repeatability_assessment:
limitations:
```

## Pilotos requeridos

| Pilot ID | Estado | Registro | Cuenta para PASS_OPERATIVO_CLIENTES_REALES | Nota |
|---|---|---|---|---|
| M31R-001 | PENDING | No creado | No | Pendiente de prospecto/cliente real |
| M31R-002 | PENDING | No creado | No | Pendiente de prospecto/cliente real |
| M31R-003 | PENDING | No creado | No | Pendiente de prospecto/cliente real |
| M31R-004 | OPTIONAL | No creado | No | Opcional |
| M31R-005 | OPTIONAL | No creado | No | Opcional |

## Criterio para crear piloto real

Crear `docs/smartpyme/real_pilots/M31R-00X.md` sólo si existe:

- prospecto o cliente real anonimizado;
- problema declarado por dueño u operador real;
- evidencia recibida o ausencia explícita;
- sentido operativo o gap registrado;
- aceptación de no-promesas;
- modo comercial;
- tiempo medido;
- costo operativo o criterio comercial;
- salida o bloqueo documentado;
- feedback o ausencia explícita.

## Criterio para contar hacia PASS

Un piloto cuenta si:

- tiene contrato canónico completo;
- no es ficticio;
- tiene no-promesas aceptadas;
- `execution_time_minutes` está medido;
- `operational_cost` o `commercial_mode` está registrado;
- hay evidencia recibida/faltante;
- hay salida, salida parcial o bloqueo;
- hay feedback o ausencia explícita;
- tiene repeatability_assessment;
- tiene limitations.

## Estado agregado

```yaml
total_real_pilot_records_created: 0
total_real_pilots_complete: 0
total_real_pilots_counting_for_pass: 0
total_real_pilots_blocked: 0
m31r_operational_real_clients_status: PENDING_REAL_PILOTS
```

## Restricciones

- No crear pilotos reales ficticios.
- No declarar producto.
- No abrir M32.
- No tocar código productivo.
- No prometer resultado económico.
- No diagnosticar sin evidencia.
- No ocultar intervención humana.
- No convertir feedback en LearningMemory automática.

## Próximo paso

Conseguir o seleccionar el primer prospecto real para:

```text
docs/smartpyme/real_pilots/M31R-001.md
```

Si faltan datos, crear una solicitud de datos o intake pendiente, no un piloto computable.
