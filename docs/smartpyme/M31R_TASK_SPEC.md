# M31-R — TaskSpec Pilotos reales/prospectos controlados

## Estado

READY_FOR_REGISTRY_AND_INTAKE

## Task ID

```text
smartpyme.m31r.prepare_controlled_real_pilots
```

## Objetivo

Preparar 3 a 5 pilotos reales/prospectos controlados usando la oferta asistida M31-C.

No abrir M32. No tocar código productivo. No declarar producto.

## Fuente

- `docs/adr/ADR-M31R-PILOTOS-REALES-CONTROLADOS.md`
- `docs/smartpyme/M31R_CAPABILITY_SPEC.md`
- `docs/smartpyme/M31C_CHECKPOINT.md`
- `docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md`
- `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md`
- `docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md`
- `docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md`

## Archivos permitidos

```text
docs/smartpyme/M31R_REAL_PILOTS_REGISTRY.md
docs/smartpyme/real_pilots/M31R-001.md
docs/smartpyme/real_pilots/M31R-002.md
docs/smartpyme/real_pilots/M31R-003.md
docs/smartpyme/real_pilots/M31R-004.md
docs/smartpyme/real_pilots/M31R-005.md
docs/smartpyme/M31R_CHECKPOINT.md
```

## Archivos prohibidos

```text
pymia/**
conversa-engine/**
src/**
scripts/**
tests/**
landing/**
tools/**
pyproject.toml
pytest.ini
README.md
```

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

## Permitido

- Crear registro maestro M31-R.
- Crear registros individuales sólo con prospecto/caso real suficiente.
- Crear solicitudes de datos si falta evidencia.
- Registrar bloqueos si el caso no es apto.
- Crear checkpoint M31-R cuando haya evidencia suficiente.

## Prohibido

- Crear código.
- Abrir M32.
- Declarar producto.
- Prometer resultado económico.
- Diagnosticar sin evidencia.
- Ocultar intervención humana.
- Implementar Guided Evidence Recovery.
- Convertir feedback en LearningMemory automática.

## Criterio para piloto real computable

Crear `M31R-00X.md` como piloto computable sólo si existe:

- prospecto o cliente real, anonimizado si corresponde;
- problema declarado por dueño u operador real;
- evidencia recibida o ausencia explícita;
- sentido operativo o gap registrado;
- aceptación de no-promesas;
- modo comercial;
- medición de tiempo;
- costo operativo o criterio comercial;
- salida, salida parcial o bloqueo documentado;
- feedback o ausencia explícita.

## PASS_DOCUMENTAL

Esta TaskSpec puede cerrar como PASS_DOCUMENTAL si existen:

- CapabilitySpec M31-R;
- TaskSpec M31-R;
- registro maestro M31-R;
- contrato canónico;
- criterios PASS/PARTIAL/BLOCKED;
- distinción explícita entre servicio asistido y producto.

## PASS_OPERATIVO_CLIENTES_REALES

Sólo puede declararse en checkpoint futuro si existen:

- 3 a 5 pilotos reales/prospectos;
- registros completos;
- tiempos medidos;
- costo/modo comercial registrado;
- evidencia recibida/faltante;
- feedback;
- evaluación agregada;
- checkpoint M31-R.

## Próximo paso

Crear:

```text
docs/smartpyme/M31R_REAL_PILOTS_REGISTRY.md
```
