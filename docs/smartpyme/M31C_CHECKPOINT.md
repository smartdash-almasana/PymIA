# M31-C — Checkpoint de preparación comercial asistida

## Estado

PASS_DOCUMENTAL_COMERCIAL

## Fecha

2026-06-05

## Contexto

M31-C fue elegido por ADR como fase intermedia después de:

```text
M31-P_OPERATIVO_INTERNO_REALISTA = PASS
M31-P_CLIENTES_REALES = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_EXPLICIT_DECISION
PRODUCTO = NOT_CERTIFIED
```

El objetivo fue preparar una oferta asistida honesta antes de exponer el protocolo a prospectos o clientes reales.

## Documentos creados

- `docs/adr/ADR-M31C-PREPARACION-COMERCIAL-ASISTIDA.md`
- `docs/smartpyme/M31C_PREPARACION_COMERCIAL_PLAN.md`
- `docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md`
- `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md`
- `docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md`
- `docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md`

## Certificado

Este checkpoint certifica:

- existe ADR aceptado para M31-C;
- existe plan de preparación comercial asistida;
- existe oferta asistida mínima;
- existe intake comercial-operativo;
- existen criterios de aptitud de prospecto;
- existe plantilla de entregable mínimo;
- la oferta distingue promesa y no-promesa;
- el dueño PyME aporta datos y sentido operativo;
- se preserva la posibilidad de bloqueo por falta de evidencia;
- no se abrió M32;
- no se tocó código productivo;
- no se declaró producto;
- no se implementó Guided Evidence Recovery;
- no se convirtió aprendizaje candidato en LearningMemory automática.

## No certificado

Este checkpoint no certifica:

- pilotos con clientes reales;
- ventas reales;
- precio validado;
- servicio comercial validado;
- producto mínimo;
- autonomía;
- UI;
- PDF profesional;
- ERP;
- diagnóstico automático sin evidencia;
- repetibilidad comercial.

## Oferta resultante

Nombre operativo:

```text
SmartPyme — Diagnóstico operativo asistido
```

Promesa honesta:

```text
Revisamos la evidencia operativa disponible de tu PyME y te devolvemos una lectura clara: qué se ve, qué falta, qué riesgo aparece y cuál sería el próximo paso razonable.
```

## Estados habilitados para prospectos

```text
FIT
PARTIAL_FIT
NEEDS_MORE_INFO
NOT_FIT
```

## Salidas habilitadas

```text
DELIVERED
PARTIAL
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
UNSUPPORTED
```

## Restricciones vigentes

- No vender como producto.
- No prometer resultado económico.
- No aceptar casos sin evidencia mínima.
- No ocultar intervención humana.
- No llamar diagnóstico total a una lectura limitada.
- No abrir M32 por inercia.
- No tocar código productivo.

## Veredicto

```text
M31-C_PREPARACION_COMERCIAL_ASISTIDA = PASS_DOCUMENTAL_COMERCIAL
M31-C_CLIENTES_REALES = READY_FOR_CONTROLLED_PILOTS
PRODUCTO = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_NEW_ADR
```

## Próximo paso metodológico

Abrir una fase de pilotos reales/prospectos controlados, si se decide avanzar:

```text
M31-R — Pilotos reales/prospectos controlados
```

Antes de ejecutarla debe crearse:

```text
ADR-M31R
CapabilitySpec M31-R
TaskSpec M31-R
registro de prospectos/pilotos reales
checkpoint M31-R
```

No es automático.
