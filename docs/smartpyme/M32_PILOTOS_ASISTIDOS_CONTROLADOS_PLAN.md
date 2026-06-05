# M32 — Pilotos asistidos controlados

## Estado

PLAN_OPERATIVO

## Fuente documental

Este plan deriva de:

- `AGENTS.md`
- `ARCHITECTURE_GUARDRAILS.md`
- `docs/roadmap/ROADMAP_SERVICIO_ASISTIDO_EXCEL_SEMANTICA_PYME.md`
- `docs/smartpyme/M27_EXCEL_SEMANTICA_DUENO_CHECKPOINT.md`
- `docs/smartpyme/M28_EXPLICABLE_FINDING_CHECKPOINT.md`
- `docs/smartpyme/M29_REPORTE_MINIMO_ENTREGABLE_CHECKPOINT.md`
- `docs/smartpyme/M30_CONTINUIDAD_DEL_CASO_CHECKPOINT.md`
- `docs/smartpyme/M31_SERVICIO_ASISTIDO_REPETIBLE_CHECKPOINT.md`

## Decisión de alcance

M32 no es producto.

M32 no abre nueva arquitectura.

M32 no introduce código productivo.

M32 no implementa UI, PDF profesional, ERP, dispatcher, registry, Telegram, LLM obligatorio, MCP, Hermes duplicado ni automatización comercial.

M32 ejecuta o simula controladamente 3 a 5 casos piloto usando el protocolo M31 para medir repetibilidad real del servicio asistido.

## Objetivo

Validar si el servicio asistido Excel + semántica PyME puede repetirse de forma controlada en varios casos, registrando:

- entrada del dueño;
- evidencia recibida;
- evidencia faltante;
- hallazgos;
- reporte o bloqueo;
- tiempos reales;
- bloqueos;
- aprendizajes;
- decisión de repetibilidad.

## Relación con M31

M31 certificó documentalmente un protocolo operativo para probar repetibilidad asistida.

M32 debe usar ese protocolo, no reemplazarlo.

La secuencia vigente queda:

```text
M27 — entender caso
M28 — explicar hallazgo
M29 — entregar reporte
M30 — recordar continuidad
M31 — protocolo de servicio asistido repetible
M32 — ejecución controlada de pilotos asistidos
```

## Cantidad de casos

M32 requiere:

```text
mínimo: 3 casos piloto
máximo operativo recomendado: 5 casos piloto
```

Los casos pueden ser:

- reales;
- prospectos reales;
- simulados controlados con fixtures realistas, si se declara explícitamente su naturaleza.

No se puede mezclar caso simulado y caso real sin indicarlo en el registro.

## Contrato de registro por piloto

Cada caso debe registrarse con estos campos:

```yaml
pilot_id:
tenant_id:
case_id:
case_type: real | prospect | simulated_controlled
case_date:
business_type:
owner_problem_statement:
owner_operational_meaning:
files_received:
initial_classification:
evidence_status:
received_evidence:
missing_evidence:
findings:
report_ref:
next_step:
final_status:
time_intake_minutes:
time_evidence_preparation_minutes:
time_analysis_minutes:
time_report_minutes:
time_delivery_minutes:
time_total_minutes:
blockers:
learnings:
operator_notes:
repeatability_signal:
limitations:
```

## Estados permitidos

```text
DELIVERED
PARTIAL_DELIVERY
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
SIMULATED_ONLY
REJECTED_NOT_A_FIT
```

## Criterio para contar un caso

Un caso cuenta para M32 sólo si:

- tiene problema declarado;
- tiene evidencia recibida o ausencia explícita documentada;
- tiene sentido operativo del dueño o gap registrado;
- registra evidencia faltante;
- registra reporte o bloqueo;
- mide tiempo total;
- registra bloqueos;
- registra aprendizajes u observa que no hubo aprendizajes;
- declara limitaciones;
- no se presenta como producto.

## Criterio PASS M32

M32 puede cerrar como `PASS_OPERATIVO_CONTROLADO` si existen:

- 3 a 5 registros de piloto completos;
- cada caso clasificado o bloqueado honestamente;
- reporte mínimo generado o bloqueo justificado;
- tiempo total medido por caso;
- bloqueos registrados;
- aprendizajes registrados;
- evaluación agregada de repetibilidad;
- checklist estable o ajuste documentado del checklist M31.

## Criterio PARTIAL

M32 queda `PARTIAL` si:

- hay 1 o 2 casos válidos;
- hay casos completos pero sin suficiente diversidad;
- falta medición parcial de tiempos;
- faltan aprendizajes agregados;
- hay reportes entregados pero baja repetibilidad.

## Criterio BLOCKED

M32 queda `BLOCKED` si:

- no hay casos;
- no hay evidencia mínima;
- no hay sentido operativo suficiente;
- se intenta vender producto;
- se intenta abrir código nuevo sin ADR/CapabilitySpec/ModuleContract/TaskSpec;
- los casos requieren capacidades fuera de M31.

## Archivos permitidos en esta fase

```text
docs/smartpyme/M32_PILOTOS_ASISTIDOS_CONTROLADOS_PLAN.md
docs/smartpyme/pilots/M32-001.md
docs/smartpyme/pilots/M32-002.md
docs/smartpyme/pilots/M32-003.md
docs/smartpyme/pilots/M32-004.md
docs/smartpyme/pilots/M32-005.md
docs/smartpyme/M32_PILOTOS_ASISTIDOS_CONTROLADOS_CHECKPOINT.md
```

## Archivos prohibidos salvo nuevo contrato formal

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

## Procedimiento operativo por piloto

1. Registrar intake inicial.
2. Registrar problema declarado por dueño/operador.
3. Registrar archivos recibidos.
4. Registrar sentido operativo aportado.
5. Clasificar caso.
6. Verificar evidencia suficiente o faltante.
7. Generar hallazgos si corresponde.
8. Generar reporte mínimo o bloqueo justificado.
9. Medir tiempos por etapa.
10. Registrar bloqueos.
11. Registrar aprendizajes.
12. Definir próximo paso.
13. Marcar si el caso aporta señal de repetibilidad.

## Evaluación agregada final

Al cerrar los casos, el checkpoint debe responder:

```text
¿El servicio asistido es repetible?
¿En qué condiciones?
¿Qué bloqueos se repiten?
¿Qué evidencia falta más seguido?
¿Qué parte consume más tiempo?
¿Qué debe mejorar antes de hablar de producto mínimo?
```

## No certificado por M32

Incluso con PASS, M32 no certifica:

- producto final;
- autonomía end-to-end;
- servicio comercial validado;
- pricing validado;
- UI;
- PDF profesional;
- ERP;
- integración con dispatcher;
- integración con registry;
- automatización comercial.

## Próximo paso

Crear el primer registro de piloto sólo cuando exista un caso concreto:

```text
docs/smartpyme/pilots/M32-001.md
```

Si no hay caso suficiente, crear un bloqueo documentado, no un piloto falso.
