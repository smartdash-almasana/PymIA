# M31-P — CapabilitySpec Pilotos asistidos reales

## Estado

DRAFT_OPERATIVO

## Capability ID

```text
smartpyme.m31p.assisted_pilot_validation
```

## Propósito

Validar si el protocolo M31 de servicio asistido repetible puede ejecutarse en 3 a 5 casos piloto con evidencia suficiente, tiempos reales, bloqueos documentados y evaluación de repetibilidad.

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
- registrar intervención humana requerida;
- registrar bloqueos reales;
- registrar aprendizajes candidatos;
- evaluar repetibilidad o no repetibilidad.

## Inputs requeridos

Cada piloto debe tener como mínimo:

```yaml
pilot_id: string
tenant_ref: string
case_date: string
owner_problem_statement: string
business_context: string | null
received_evidence: list[string]
missing_evidence: list[string]
operator_notes: string | null
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

Este sentido debe registrarse como evidencia semántica o nota operativa, no como conclusión diagnóstica automática.

## Outputs esperados

Cada piloto debe producir un registro con:

```yaml
pilot_id: string
status: DELIVERED | BLOCKED | PARTIAL | UNSUPPORTED
evidence_received: list[string]
evidence_missing: list[string]
output_delivered: string | null
blockers: list[string]
execution_time_minutes: number | null
human_intervention: string | null
candidate_learnings: list[string]
repeatability_assessment: REPEATABLE | PARTIALLY_REPEATABLE | NOT_REPEATABLE | NOT_ENOUGH_EVIDENCE
limitations: list[string]
```

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
- evidencia recibida;
- evidencia faltante;
- tiempo real o razón de ausencia de medición;
- salida o bloqueo;
- limitaciones;
- evaluación de repetibilidad.

## Criterio PASS de la capacidad

La capacidad `smartpyme.m31p.assisted_pilot_validation` puede declararse PASS_OPERATIVO sólo si existen:

- 3 a 5 registros de pilotos completos;
- tiempos reales registrados o justificación explícita de ausencia;
- bloqueos documentados;
- salidas o estados BLOCKED/PARTIAL documentados;
- evaluación de repetibilidad;
- checkpoint M31-P.

## Criterio PARTIAL

La capacidad queda PARTIAL si:

- hay menos de 3 pilotos;
- los registros están incompletos;
- no se puede medir repetibilidad;
- faltan tiempos reales;
- hay evidencia parcial.

## Criterio BLOCKED

La capacidad queda BLOCKED si:

- no hay pilotos disponibles;
- no hay evidencia suficiente;
- el protocolo M31 no puede aplicarse sin código nuevo;
- se intenta convertir la fase en producto;
- se intenta implementar Guided Evidence Recovery;
- se intenta abrir M32 por inercia.

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
- Plan M31-P.
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

Los aprendizajes derivados de pilotos sólo pueden registrarse como candidatos.

No pueden convertirse automáticamente en LearningMemory, política, ADR ni arquitectura.

## Próximo paso

Ejecutar `docs/smartpyme/M31P_TASK_SPEC.md` para preparar plantilla de registro y validación documental de los pilotos.
