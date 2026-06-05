# ADR-M31R — Pilotos reales/prospectos controlados antes de M32

## Estado

ACCEPTED

## Fecha

2026-06-05

## Contexto

M31-P cerró con validación interna realista:

```text
M31-P_OPERATIVO_INTERNO_REALISTA = PASS
M31-P_CLIENTES_REALES = NOT_CERTIFIED
```

M31-C cerró con preparación comercial asistida:

```text
M31-C_PREPARACION_COMERCIAL_ASISTIDA = PASS_DOCUMENTAL_COMERCIAL
M31-C_CLIENTES_REALES = READY_FOR_CONTROLLED_PILOTS
PRODUCTO = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_NEW_ADR
```

Ya existe una oferta asistida mínima, intake comercial-operativo, criterios de aptitud de prospecto y plantilla de entregable mínimo.

El siguiente riesgo metodológico sería abrir M32 o llamar producto a una preparación comercial todavía no probada con prospectos/clientes reales.

## Decisión

Se abre una fase intermedia:

```text
M31-R — Pilotos reales/prospectos controlados
```

M31-R es una fase operativa-comercial controlada.

No es M32.
No es producto.
No autoriza código productivo.
No implementa Guided Evidence Recovery.

## Objetivo

Ejecutar o documentar 3 a 5 pilotos con prospectos o clientes reales usando el paquete M31-C, registrando evidencia, tiempo, costo, bloqueos, entrega y feedback.

## Alcance autorizado

Este ADR autoriza documentación y preparación de M31-R:

- CapabilitySpec M31-R;
- TaskSpec M31-R;
- registro de prospectos/pilotos reales;
- plantilla de piloto real;
- checklist de piloto real;
- checkpoint M31-R;
- issues operativos para capturar prospectos, si corresponde.

## Alcance no autorizado

Este ADR no autoriza:

- código productivo;
- M32;
- producto;
- autonomía end-to-end;
- ERP;
- UI;
- PDF profesional;
- automatización comercial;
- Guided Evidence Recovery;
- LearningMemory automática;
- prometer resultado económico;
- diagnosticar sin evidencia;
- ocultar intervención humana.

## Criterio de piloto real/prospecto válido

Un piloto M31-R sólo es válido si existe:

- prospecto o cliente real identificado de forma segura o anonimizada;
- problema declarado por dueño/operador real;
- evidencia recibida o ausencia explícita documentada;
- sentido operativo aportado o gap registrado;
- aceptación de no-promesas;
- tiempo real medido;
- costo operativo o criterio comercial registrado;
- salida entregada, salida parcial o bloqueo documentado;
- feedback o constancia de ausencia de feedback.

## Criterio PASS de M31-R

M31-R puede cerrar como PASS_OPERATIVO_CLIENTES_REALES sólo si existen:

- 3 a 5 pilotos reales/prospectos controlados;
- registros completos;
- checklist aplicado por piloto;
- tiempos reales medidos;
- costo operativo o modo comercial registrado;
- evidencia recibida/faltante;
- entrega, salida parcial o bloqueo documentado;
- feedback o ausencia de feedback registrada;
- evaluación agregada de repetibilidad comercial;
- checkpoint M31-R.

## Criterio PARTIAL

M31-R queda PARTIAL si:

- hay 1 o 2 pilotos reales/prospectos;
- faltan tiempos;
- falta feedback;
- hay evidencia incompleta;
- no se puede evaluar repetibilidad comercial.

## Criterio BLOCKED

M31-R queda BLOCKED si:

- no hay prospectos reales;
- no se acepta la no-promesa;
- los casos requieren capacidades no implementadas;
- se intenta vender producto;
- se intenta abrir M32;
- se intenta diagnosticar sin evidencia.

## Consecuencias

- M31-R es el puente entre preparación comercial y decisión técnica posterior.
- M32 sigue bloqueado hasta que M31-R cierre o se cree otro ADR explícito.
- El producto sigue no certificado.
- La oferta sigue siendo servicio asistido.
- El dueño PyME sigue siendo proveedor de datos y sentido operativo.

## Próximo paso

Crear:

```text
docs/smartpyme/M31R_CAPABILITY_SPEC.md
docs/smartpyme/M31R_TASK_SPEC.md
docs/smartpyme/M31R_REAL_PILOTS_REGISTRY.md
```

No crear código.
No abrir M32.
