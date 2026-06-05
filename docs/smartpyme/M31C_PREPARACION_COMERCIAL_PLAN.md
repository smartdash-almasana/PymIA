# M31-C — Plan de preparación comercial asistida

## Estado

PLAN_METODOLOGICO_COMERCIAL

## Fuente

- `docs/adr/ADR-M31C-PREPARACION-COMERCIAL-ASISTIDA.md`
- `docs/smartpyme/M31P_OPERATIVE_INTERNAL_CHECKPOINT.md`
- `docs/smartpyme/M31P_PILOTS_REGISTRY.md`
- `AGENTS.md`
- `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md`

## Contexto

M31-P cerró como:

```text
M31-P_OPERATIVO_INTERNO_REALISTA = PASS
M31-P_CLIENTES_REALES = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_EXPLICIT_DECISION
PRODUCTO = NOT_CERTIFIED
```

M31-C existe para preparar una transición controlada desde pilotos internos realistas hacia pilotos con prospectos o clientes reales, sin declarar producto y sin abrir M32.

## Objetivo

Definir un paquete comercial-operativo mínimo para vender o probar un servicio asistido SmartPyme con límites claros.

M31-C debe responder:

```text
¿Qué se puede ofrecer a una PyME real sin mentir, sin sobrediagnosticar y sin convertir el protocolo asistido en producto?
```

## Alcance permitido

- definir oferta asistida mínima;
- definir intake comercial-operativo;
- definir criterios de cliente apto/no apto;
- definir promesa y no-promesa;
- definir salida mínima entregable;
- definir precio/rango experimental o criterio de costo;
- definir tiempos esperados y condiciones de bloqueo;
- definir guion de conversación con dueño PyME;
- definir checklist antes de piloto real;
- definir registro de riesgos;
- preparar fase futura de 3 a 5 pilotos reales/prospectos.

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
- promesa de resultado económico garantizado.

## Principio comercial central

SmartPyme no vende magia ni software autónomo.

En M31-C vende un servicio asistido de claridad operativa:

```text
Mandame la evidencia y te devuelvo una lectura ordenada, límites claros y próximos pasos accionables.
```

## Rol del dueño PyME

El dueño PyME aporta:

1. Datos:
   - Excel;
   - ventas;
   - costos;
   - compras;
   - stock;
   - facturas;
   - extractos;
   - listas de precios.
2. Sentido operativo:
   - qué le preocupa;
   - qué período mirar;
   - qué significa una columna;
   - qué proceso real produjo el dato;
   - qué decisión necesita tomar;
   - qué dato falta pero existe en otro lado.

El dueño no es sólo uploader de archivos.

## Entregable mínimo esperado

La salida comercial asistida debe poder entregar una de estas opciones:

```text
A) lectura operativa mínima
B) hallazgos explicables
C) pedido concreto de evidencia faltante
D) bloqueo documentado
E) próximo paso recomendado
```

## Criterio de cliente/prospecto apto

Un prospecto es apto para piloto comercial asistido si:

- tiene dolor operativo/económico concreto;
- acepta entregar evidencia;
- puede explicar sentido operativo mínimo;
- acepta que el servicio puede bloquearse por falta de evidencia;
- entiende que no se promete diagnóstico total ni producto autónomo;
- acepta un alcance acotado.

## Criterio de no apto

No apto si:

- exige automatización completa;
- exige integración ERP inmediata;
- exige resultado económico garantizado;
- no puede aportar evidencia ni sentido;
- quiere auditoría contable/legal formal;
- exige diagnóstico sin datos;
- requiere una capacidad no implementada.

## Criterio PASS de M31-C

M31-C puede cerrar como PASS_DOCUMENTAL_COMERCIAL si existen:

- oferta asistida mínima;
- intake comercial-operativo;
- criterio de cliente apto/no apto;
- promesa y no-promesa;
- checklist de bloqueo;
- plantilla de salida mínima;
- criterio de tiempo/costo operativo;
- plan de 3 a 5 pilotos reales/prospectos;
- checkpoint M31-C.

## Criterio PARTIAL

M31-C queda PARTIAL si:

- existe oferta pero no intake;
- existe intake pero no no-promesa;
- no hay criterio de bloqueo;
- no hay criterio de costo/tiempo;
- no queda claro que no es producto.

## Criterio BLOCKED

M31-C queda BLOCKED si:

- se intenta abrir M32;
- se intenta vender producto;
- se intenta prometer diagnóstico sin evidencia;
- se intenta tocar código productivo;
- se intenta implementar Guided Evidence Recovery;
- no se puede formular una oferta honesta.

## Documentos requeridos

Mínimos:

```text
docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md
docs/smartpyme/M31C_COMMERCIAL_INTAKE.md
docs/smartpyme/M31C_CHECKPOINT.md
```

Recomendados:

```text
docs/smartpyme/M31C_PROSPECT_FIT_CRITERIA.md
docs/smartpyme/M31C_MINIMUM_DELIVERABLE_TEMPLATE.md
```

## Próximo paso

Crear o validar:

```text
docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md
docs/smartpyme/M31C_COMMERCIAL_INTAKE.md
```
