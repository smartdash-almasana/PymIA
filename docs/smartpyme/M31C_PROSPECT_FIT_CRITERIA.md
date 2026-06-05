# M31-C — Criterios de aptitud de prospecto

## Estado

READY_FOR_COMMERCIAL_SCREENING

## Propósito

Definir cuándo una PyME/prospecto puede entrar a un piloto comercial asistido SmartPyme sin convertir la oferta en producto, consultoría integral ni promesa de resultado económico.

## Fuente

- `docs/adr/ADR-M31C-PREPARACION-COMERCIAL-ASISTIDA.md`
- `docs/smartpyme/M31C_PREPARACION_COMERCIAL_PLAN.md`
- `docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md`
- `docs/smartpyme/M31C_COMMERCIAL_INTAKE.md`

## Clasificación

Todo prospecto debe clasificarse como uno de:

```text
FIT
PARTIAL_FIT
NEEDS_MORE_INFO
NOT_FIT
```

## FIT

El prospecto es apto para piloto asistido si cumple:

- dolor operativo/económico concreto;
- evidencia mínima disponible;
- sentido operativo mínimo;
- aceptación de límites/no-promesas;
- alcance compatible con servicio asistido;
- posibilidad de registrar tiempo/costo operativo;
- salida esperable como lectura, hallazgo, evidencia faltante, bloqueo o próximo paso.

Ejemplos:

- “No sé si gano plata” + Excel de ventas/costos.
- “Vendo mucho pero no queda plata” + ventas/compras/lista de precios.
- “No me cierra caja” + extractos o reportes.
- “No entiendo este Excel” + archivo y explicación mínima.

## PARTIAL_FIT

Puede aceptarse con alcance limitado si:

- el dolor está claro pero la evidencia es parcial;
- el dueño puede explicar contexto;
- la salida probable será pedido de evidencia o bloqueo documentado;
- el prospecto acepta que puede no haber diagnóstico.

## NEEDS_MORE_INFO

No avanzar todavía si falta:

- problema declarado;
- período;
- significado de columnas;
- evidencia mínima;
- confirmación de no-promesas;
- decisión que necesita tomar el dueño.

Salida correcta:

```text
REQUEST_MORE_EVIDENCE
```

## NOT_FIT

No aceptar si:

- exige producto autónomo;
- exige integración ERP;
- pide auditoría legal/contable formal;
- no aportará evidencia;
- exige resultado garantizado;
- requiere diagnóstico sin datos;
- necesita una capacidad no implementada;
- quiere delegar toda la gestión sin intervención humana.

## Matriz rápida

| Señal | Clasificación probable |
|---|---|
| Dolor claro + Excel + dueño explica contexto | FIT |
| Dolor claro + evidencia parcial | PARTIAL_FIT |
| Dolor difuso + no hay archivos todavía | NEEDS_MORE_INFO |
| Quiere SaaS autónomo/ERP/producto | NOT_FIT |
| Quiere auditoría contable/legal | NOT_FIT |
| Quiere saber qué evidencia falta | PARTIAL_FIT |

## No-promesas obligatorias

Antes de aceptar un piloto, el prospecto debe entender:

- no hay diagnóstico total sin evidencia;
- no es auditoría contable/legal;
- no es ERP;
- no es producto autónomo;
- no hay garantía de ganancia;
- puede terminar en bloqueo documentado.

## Criterio de aceptación

Aceptar sólo si:

```yaml
fit_status: FIT | PARTIAL_FIT
accepted_no_promises: true
minimum_evidence_available: true
owner_operational_meaning_available_or_gap_registered: true
```

## Criterio de rechazo

Rechazar o pausar si:

```yaml
fit_status: NOT_FIT | NEEDS_MORE_INFO
```

## Próximo paso

Si el prospecto es FIT o PARTIAL_FIT, usar:

```text
docs/smartpyme/M31C_COMMERCIAL_INTAKE.md
```

Luego preparar piloto real/prospecto con contrato M31-P adaptado a caso real.
