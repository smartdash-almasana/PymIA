# M31-P — CapabilitySpec Pilotos asistidos reales

## Estado

READY_FOR_DOCUMENTAL_VALIDATION

## Capability ID

```text
smartpyme.m31p.assisted_pilot_validation
```

## Propósito

Validar si el protocolo M31 de servicio asistido repetible puede ejecutarse en 3 a 5 casos piloto con evidencia suficiente, tiempos reales medidos, bloqueos documentados, costo operativo registrado y evaluación de repetibilidad.

Esta capacidad no implementa producto, autonomía ni código productivo.

## Fuente arquitectónica

- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`
- `docs/pymia/START_HERE_FOR_AGENTS.md`
- `docs/smartpyme/M31_CLOSURE_CLARIFICATION.md`
- `docs/smartpyme/M31P_PILOTOS_ASISTIDOS_PLAN.md`
- `docs/adr/ADR-M31P-PILOTOS-ASISTIDOS.md`
- `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md`
- `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md`

## Contrato canónico de piloto

Todos los registros M31-P deben usar estos campos:

```yaml
pilot_id: string
tenant_ref: string
case_date: string
business_type: string | null
case_origin: string | null
owner_problem_statement: string
owner_operational_meaning: string | null
received_evidence: list[string]
missing_evidence: list[string]
protocol_steps_applied: list[string]
output_delivered: string | null
final_status: DELIVERED | BLOCKED | PARTIAL | UNSUPPORTED
execution_time_minutes: number
operational_cost: number | string
human_intervention: string | null
operator_notes: string | null
blockers: list[string]
candidate_learnings: list[string]
repeatability_assessment: REPEATABLE | PARTIALLY_REPEATABLE | NOT_REPEATABLE | NOT_ENOUGH_EVIDENCE
limitations: list[string]
```

No usar nombres alternativos como:

```text
status
evidence_received
evidence_missing
business_context
```

## Qué puede hacer esta capacidad

M31-P puede:

- seleccionar o documentar 3 a 5 casos piloto;
- registrar intake inicial de cada caso;
- registrar datos aportados por el dueño PyME;
- registrar sentido operativo aportado por el dueño PyME;
- registrar evidencia recibida;
- registrar evidencia faltante;
- aplicar el protocolo documental M31;
- registrar salida entregada o bloqueo;
- registrar tiempo real de ejecución;
- registrar costo operativo o `not_applicable`;
- registrar intervención humana requerida;
- registrar notas del operador;
- registrar bloqueos reales;
- registrar aprendizajes candidatos como lista obligatoria, vacía si no existen;
- evaluar repetibilidad o no repetibilidad.

## Inputs requeridos

Cada piloto debe tener como mínimo:

```yaml
pilot_id: string
tenant_ref: string
case_date: string
owner_problem_statement: string
owner_operational_meaning: string | null
received_evidence: list[string]
missing_evidence: list[string]
```

## Input de sentido operativo

El dueño PyME puede aportar sentido operativo además de archivos.

Ejemplos:

- qué le preocupa;
- qué período mirar;
- qué significa una columna;
- qué proceso real generó un dato;
- qué dato falta pero existe en otro lugar;
- qué decisión necesita tomar.

Este sentido debe registrarse en `owner_operational_meaning`, no como conclusión diagnóstica automática.

## Outputs esperados

Cada piloto debe producir un registro completo con el contrato canónico.

Valores permitidos de `final_status`:

- DELIVERED;
- BLOCKED;
- PARTIAL;
- UNSUPPORTED.

Valores permitidos de `repeatability_assessment`:

- REPEATABLE;
- PARTIALLY_REPEATABLE;
- NOT_REPEATABLE;
- NOT_ENOUGH_EVIDENCE.

## Estados válidos

### DELIVERED

El piloto pudo ejecutarse y entregar una salida asistida usando el protocolo M31.

### BLOCKED

El piloto no pudo avanzar por falta de evidencia, falta de sentido operativo, imposibilidad de aplicar el protocolo o restricción metodológica.

### PARTIAL

El piloto produjo una salida incompleta o limitada.

### UNSUPPORTED

El caso queda fuera del alcance de M31-P.

## Evidencia requerida

Para certificar un piloto:

- registro de intake;
- evidencia recibida en `received_evidence`;
- evidencia faltante en `missing_evidence`;
- tiempo real medido en `execution_time_minutes`;
- costo operativo en `operational_cost` con valor, `not_applicable` o `not_measured` justificado;
- salida o bloqueo;
- intervención humana, si existió;
- notas del operador, si corresponde;
- limitaciones;
- evaluación de repetibilidad.

## Criterio PASS de la capacidad

La capacidad `smartpyme.m31p.assisted_pilot_validation` puede declararse PASS_OPERATIVO sólo si existen:

- 3 a 5 registros de pilotos completos;
- `execution_time_minutes` medido en todos los pilotos;
- `operational_cost` registrado en todos los pilotos con valor o `not_applicable`;
- `blockers` registrado en todos los pilotos, aunque sea lista vacía;
- salidas o estados BLOCKED/PARTIAL documentados;
- evaluación de repetibilidad por piloto;
- evaluación agregada de repetibilidad;
- checkpoint M31-P.

## Criterio PARTIAL

La capacidad queda PARTIAL si:

- hay menos de 3 pilotos;
- los registros están incompletos;
- faltan tiempos reales medidos;
- falta `operational_cost` o su justificación;
- no se puede medir repetibilidad;
- hay evidencia parcial.

La ausencia de aprendizajes candidatos no implica PARTIAL si el campo `candidate_learnings` existe y está explícitamente vacío.

## Criterio BLOCKED

La capacidad queda BLOCKED si:

- no hay pilotos disponibles;
- no hay evidencia suficiente;
- el protocolo M31 no puede aplicarse sin código nuevo;
- se intenta convertir la fase en producto;
- se intenta implementar Guided Evidence Recovery;
- se intenta abrir M32 por inercia;
- se intenta declarar PASS_OPERATIVO sin contrato de registro completo.

## Fuera de alcance

Esta CapabilitySpec no autoriza:

- código productivo;
- Guided Evidence Recovery;
- M32;
- producto final;
- autonomía end-to-end;
- UI;
- PDF profesional;
- ERP;
- dispatcher;
- registry;
- runtime;
- LearningMemory automática;
- cambios en contratos técnicos existentes.

## Dependencias

- Protocolo M31 existente.
- Plan M31-P alineado.
- ADR-M31P.
- Disponibilidad de 3 a 5 casos piloto o casos realistas suficientemente documentados.

## Riesgos

- confundir PASS_DOCUMENTAL con PASS_OPERATIVO;
- ejecutar pilotos sin registrar tiempos;
- registrar aprendizajes como política automática;
- diagnosticar sin evidencia;
- tratar la fase como producto comercial;
- abrir M32 antes de completar M31-P.

## Regla de aprendizaje

Los aprendizajes derivados de pilotos sólo pueden registrarse como candidatos en `candidate_learnings`.

No pueden convertirse automáticamente en LearningMemory, política, ADR ni arquitectura.

## Próximo paso

Validar documentalmente que TaskSpec, plantilla y checklist usan este mismo contrato canónico.
