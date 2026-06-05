# M31-C — Plantilla de entregable mínimo asistido

## Estado

READY_FOR_ASSISTED_DELIVERY

## Propósito

Definir la salida mínima que SmartPyme puede entregar en un piloto asistido con prospecto o cliente real, sin declarar producto ni diagnóstico total.

## Naturaleza

Este entregable es:

```text
servicio asistido
lectura operativa limitada
evidencia + límites + próximo paso
```

No es:

```text
producto autónomo
auditoría contable/legal
ERP
consultoría integral
garantía económica
```

## Estructura mínima

```markdown
# Diagnóstico operativo asistido — [Nombre/Alias PyME]

## 1. Contexto del pedido

- Problema declarado:
- Período analizado:
- Evidencia recibida:
- Sentido operativo aportado:

## 2. Qué se pudo observar

- Observación 1:
- Observación 2:
- Observación 3:

## 3. Hallazgos explicables

| Hallazgo | Evidencia usada | Límite |
|---|---|---|
| | | |

## 4. Evidencia faltante

- Falta 1:
- Falta 2:
- Falta 3:

## 5. Bloqueos o advertencias

- Bloqueo/advertencia 1:
- Bloqueo/advertencia 2:

## 6. Próximo paso recomendado

- Próximo paso:
- Responsable sugerido:
- Evidencia necesaria:

## 7. No-promesas

Este entregable no es auditoría contable/legal, no garantiza resultado económico y no reemplaza sistemas de gestión.
```

## Reglas de redacción

- No diagnosticar más allá de la evidencia.
- No ocultar faltantes.
- No presentar inferencias como hechos.
- No usar lenguaje de producto autónomo.
- No prometer resultado económico.
- No culpar al dueño por falta de datos.
- Registrar si el caso queda bloqueado.

## Estados posibles de salida

```text
DELIVERED
PARTIAL
BLOCKED_NEEDS_EVIDENCE
BLOCKED_OUT_OF_SCOPE
UNSUPPORTED
```

## Criterio DELIVERED

Usar sólo si hay evidencia suficiente para entregar lectura operativa mínima.

## Criterio PARTIAL

Usar si hay lectura útil, pero faltan datos relevantes.

## Criterio BLOCKED_NEEDS_EVIDENCE

Usar si no se puede avanzar sin nueva evidencia.

## Criterio BLOCKED_OUT_OF_SCOPE

Usar si el pedido exige capacidades fuera de M31-C.

## Criterio UNSUPPORTED

Usar si el caso no corresponde al servicio asistido.

## Checklist antes de entregar

- [ ] El problema declarado está escrito.
- [ ] La evidencia recibida está listada.
- [ ] El sentido operativo está registrado o su ausencia está marcada.
- [ ] Los hallazgos citan evidencia.
- [ ] La evidencia faltante está explícita.
- [ ] Las limitaciones están visibles.
- [ ] El próximo paso es accionable.
- [ ] Las no-promesas están incluidas.
- [ ] No se llama producto.
- [ ] No se promete resultado económico.

## Salida bloqueada mínima

Si no hay evidencia suficiente, entregar:

```markdown
# Diagnóstico operativo asistido — Bloqueado por evidencia insuficiente

## Problema declarado

[Texto del dueño]

## Evidencia recibida

[Listado]

## Evidencia faltante

[Listado concreto]

## Por qué no se puede diagnosticar todavía

[Explicación breve]

## Próximo paso

[Qué debe aportar el dueño]
```

## Próximo paso

Usar esta plantilla sólo después de intake comercial-operativo y clasificación FIT/PARTIAL_FIT.
