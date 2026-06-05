# M31-R — CapabilitySpec Pilotos reales/prospectos controlados

## Estado

READY_FOR_TASK_SPEC

## Capability ID

```text
smartpyme.m31r.controlled_real_pilot_validation
```

## Propósito

Validar la oferta asistida SmartPyme con 3 a 5 prospectos o clientes reales, sin declarar producto, autonomía ni servicio comercial validado antes de evidencia suficiente.

M31-R debe probar si lo preparado en M31-C puede operar frente a casos reales con límites claros.

## Fuente arquitectónica

- `docs/adr/ADR-M31R-PILOTOS-REALES-CONTROLADOS.md`
- `docs/smartpyme/M31C_CHECKPOINT.md`
- `docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md`
- `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md`
- `docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md`
- `docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md`
- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`

## Qué puede hacer esta capacidad

M31-R puede:

- registrar prospectos o clientes reales de forma segura o anonimizada;
- aplicar intake comercial-operativo;
- clasificar FIT, PARTIAL_FIT, NEEDS_MORE_INFO o NOT_FIT;
- registrar aceptación de no-promesas;
- registrar evidencia recibida y faltante;
- registrar sentido operativo aportado por dueño u operador real;
- ejecutar un servicio asistido limitado;
- entregar lectura mínima, salida parcial o bloqueo documentado;
- medir tiempo real;
- registrar costo operativo o modo comercial;
- registrar feedback o ausencia de feedback;
- evaluar repetibilidad comercial limitada.

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

## Estados permitidos

### FIT

Caso apto para piloto real/prospecto controlado.

### PARTIAL_FIT

Caso aceptable con alcance limitado o alta probabilidad de salida parcial/bloqueo.

### NEEDS_MORE_INFO

No iniciar piloto hasta obtener más datos.

### NOT_FIT

Caso fuera de alcance.

## Estados finales permitidos

```text
DELIVERED
PARTIAL
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
UNSUPPORTED
```

## Evidencia requerida por piloto

Cada piloto real/prospecto debe registrar:

- problema declarado por dueño u operador real;
- evidencia recibida;
- evidencia faltante;
- sentido operativo aportado o gap registrado;
- aceptación de no-promesas;
- tiempo real medido;
- costo operativo o modo comercial;
- salida o bloqueo;
- feedback o ausencia explícita de feedback;
- limitaciones.

## Criterio PASS de la capacidad

La capacidad puede cerrar como PASS_OPERATIVO_CLIENTES_REALES sólo si existen:

- 3 a 5 pilotos reales/prospectos controlados;
- registros completos bajo contrato canónico;
- checklist aplicado por piloto;
- tiempos reales medidos;
- costo operativo o modo comercial registrado;
- evidencia recibida/faltante documentada;
- entrega, salida parcial o bloqueo documentado;
- feedback o ausencia explícita de feedback;
- evaluación agregada de repetibilidad comercial;
- checkpoint M31-R.

## Criterio PARTIAL

La capacidad queda PARTIAL si:

- hay 1 o 2 pilotos reales/prospectos;
- hay registros incompletos;
- faltan tiempos reales;
- falta feedback;
- falta evaluación agregada;
- la evidencia no permite evaluar repetibilidad comercial.

## Criterio BLOCKED

La capacidad queda BLOCKED si:

- no hay prospectos reales;
- los prospectos no aceptan no-promesas;
- los casos requieren producto, ERP, UI, automatización o capacidades no implementadas;
- se intenta diagnosticar sin evidencia;
- se intenta abrir M32;
- se intenta tocar código productivo.

## Fuera de alcance

- código productivo;
- M32;
- producto;
- autonomía end-to-end;
- ERP;
- UI;
- PDF profesional;
- Guided Evidence Recovery;
- automatización comercial;
- LearningMemory automática;
- diagnóstico sin evidencia;
- promesa de resultado económico.

## Riesgos

- confundir prospecto con cliente validado;
- prometer más de lo que la evidencia permite;
- ocultar intervención humana;
- aceptar casos fuera de alcance por ansiedad comercial;
- declarar producto a partir de pilotos asistidos;
- convertir feedback aislado en arquitectura.

## Próximo paso

Crear `docs/smartpyme/M31R_TASK_SPEC.md` y `docs/smartpyme/M31R_REAL_PILOTS_REGISTRY.md`.
