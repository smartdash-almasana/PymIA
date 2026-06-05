# M31-P — Pilotos asistidos reales

## Estado

PLAN_METODOLOGICO_ALINEADO

## Motivo

M31 quedó aclarado en dos niveles:

```text
M31_DOCUMENTAL = PASS_DOCUMENTAL
M31_OPERATIVO_PILOTOS = PENDING_PILOTS
```

Por lo tanto, el próximo paso no es abrir M32.

El próximo paso es ejecutar una fase M31-P para validar si el protocolo M31 funciona con 3 a 5 casos piloto asistidos.

## Objetivo

Validar repetibilidad operativa asistida con casos reales o realistas, sin declarar producto, autonomía end-to-end ni capacidad comercial validada.

## Qué debe certificar M31-P

M31-P debe responder:

```text
¿El protocolo M31 puede repetirse en 3 a 5 casos con evidencia, tiempo real, bloqueos y salida registrada bajo un contrato único de piloto?
```

## Contrato canónico de registro

Todos los documentos M31-P deben usar estos nombres de campo:

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

No usar variantes incompatibles como:

```text
status
evidence_received
evidence_missing
business_context
```

## Alcance permitido

- seleccionar 3 a 5 casos piloto;
- registrar intake inicial del dueño PyME;
- registrar sentido operativo aportado por el dueño PyME;
- registrar evidencia recibida;
- registrar evidencia faltante;
- aplicar el protocolo M31;
- registrar tiempo real de ejecución;
- registrar costo operativo o `not_applicable`;
- registrar intervención humana;
- registrar notas del operador;
- registrar bloqueos;
- registrar salida entregada;
- registrar aprendizajes candidatos cuando existan, usando lista vacía cuando no existan;
- evaluar repetibilidad o no repetibilidad.

## Fuera de alcance

- abrir M32 como feature;
- tocar código productivo;
- implementar Guided Evidence Recovery;
- declarar producto;
- declarar servicio comercial validado;
- automatizar onboarding;
- integrar ERP;
- crear UI;
- crear PDF profesional;
- modificar dispatcher, registry o runtime;
- convertir pilotos en LearningMemory automática.

## Cadena metodológica mínima

Antes de ejecutar pilotos, M31-P debe tener:

```text
ADR
→ CapabilitySpec
→ TaskSpec
→ plantilla de evidencia piloto
→ checklist de validación
→ ejecución / documentación de casos
→ checkpoint M31-P
```

ModuleContract sólo corresponde si se modifica o crea una frontera técnica. En esta fase, por defecto, no corresponde porque no hay código productivo autorizado.

## Evidencia mínima por piloto

Cada piloto debe registrar:

- `pilot_id`;
- `tenant_ref` o identificador anonimizado;
- `case_date`;
- `business_type`, si se conoce;
- `case_origin`, si se conoce;
- `owner_problem_statement`;
- `owner_operational_meaning`, si existe;
- `received_evidence`;
- `missing_evidence`;
- `protocol_steps_applied`;
- `output_delivered` o bloqueo;
- `final_status`;
- `execution_time_minutes`;
- `operational_cost` con valor o `not_applicable`;
- `human_intervention`, si existió;
- `operator_notes`, si corresponde;
- `blockers`, aunque sea lista vacía;
- `candidate_learnings`, aunque sea lista vacía;
- `repeatability_assessment`;
- `limitations`.

## Regla de tiempo real

Para PASS_OPERATIVO, `execution_time_minutes` debe estar medido en todos los pilotos incluidos.

La ausencia de medición de tiempo puede documentarse, pero impide PASS_OPERATIVO y lleva la fase a PARTIAL o BLOCKED según el resto de la evidencia.

## Regla de costo operativo

`operational_cost` debe existir en todos los registros.

Valores válidos:

- monto o estimación explícita cuando corresponda;
- `not_applicable` cuando no corresponde;
- `not_measured` sólo si se justifica en `limitations`.

## Regla de aprendizajes candidatos

`candidate_learnings` es un campo obligatorio como contenedor.

Puede estar vacío.

La ausencia de aprendizajes candidatos no vuelve PARTIAL al piloto si el resto del registro está completo.

Ningún aprendizaje candidato se convierte automáticamente en LearningMemory.

## Criterio PASS de M31-P

M31-P sólo puede declararse PASS_OPERATIVO si existen:

- 3 a 5 registros de piloto completos;
- `execution_time_minutes` medido en todos los pilotos;
- `operational_cost` registrado con valor o `not_applicable`;
- `blockers` registrado en todos los pilotos, aunque sea lista vacía;
- salidas o bloqueos documentados;
- evaluación de repetibilidad por piloto;
- evaluación agregada de repetibilidad;
- checkpoint M31-P.

## Criterio PARTIAL

M31-P queda PARTIAL si:

- hay menos de 3 pilotos;
- hay pilotos con registros incompletos;
- faltan tiempos reales medidos;
- falta `operational_cost` o su justificación;
- faltan bloqueos como campo explícito;
- no se puede evaluar repetibilidad;
- el protocolo funcionó sólo parcialmente.

La ausencia de aprendizajes candidatos no implica PARTIAL si el campo existe y está explícitamente vacío.

## Criterio BLOCKED

M31-P queda BLOCKED si:

- no hay casos piloto disponibles;
- no hay evidencia suficiente;
- el protocolo M31 no puede aplicarse sin cambiar código;
- se intenta convertir el ciclo en producto;
- se intenta implementar Guided Evidence Recovery sin contrato propio;
- se intenta declarar PASS_OPERATIVO sin contrato de registro completo.

## Regla final

M31-P es una fase de validación operativa asistida.

No es M32.
No es producto.
No es autonomía.
No es implementación técnica.
