# ADR-M31C — Preparación comercial asistida antes de M32

## Estado

ACCEPTED

## Fecha

2026-06-05

## Contexto

M31-P cerró una validación operativa limitada:

```text
M31-P_OPERATIVO_INTERNO_REALISTA = PASS
M31-P_CLIENTES_REALES = NOT_CERTIFIED
M32 = BLOCKED_UNTIL_EXPLICIT_DECISION
PRODUCTO = NOT_CERTIFIED
```

La evidencia disponible permite afirmar que el protocolo puede ejecutarse con pilotos internos realistas basados en fixtures del repositorio.

No permite afirmar todavía validación comercial, producto, autonomía ni repetibilidad con clientes reales.

## Decisión

Se elige abrir una fase intermedia:

```text
M31-C — Preparación comercial asistida
```

M31-C no es M32.
M31-C no es producto.
M31-C no toca código productivo.
M31-C no implementa Guided Evidence Recovery.

Su objetivo es convertir el aprendizaje operativo interno en un paquete de servicio asistido listo para pilotos con prospectos o clientes reales.

## Por qué se elige esta ruta

Se descartan, por ahora, las otras rutas inmediatas:

### Ruta A — Pilotos con clientes reales directamente

No se elige como paso inmediato.

Motivo: aunque M31-P interno pasó, todavía falta empaquetar intake, promesa, límites, precio/costo operativo, criterios de bloqueo y salida entregable para evitar improvisar frente a clientes reales.

### Ruta B — Fase técnica posterior limitada

No se elige como paso inmediato.

Motivo: abrir una fase técnica antes de preparar el servicio asistido podría convertir evidencia interna en backlog técnico prematuro.

### Ruta C — Preparación comercial asistida

Aceptada.

Motivo: es el puente más seguro entre validación interna y pilotos reales. Preserva el carácter asistido, evita declarar producto y obliga a definir contrato comercial-operativo antes de exponer el flujo a prospectos.

## Alcance autorizado

M31-C autoriza documentación y preparación operativa/comercial:

- oferta asistida mínima;
- intake comercial-operativo;
- criterio de cliente/prospecto apto;
- promesa y no-promesa;
- precio o rango experimental, si corresponde;
- costo operativo estimado;
- criterios de bloqueo;
- formato de salida mínima;
- guion de conversación con dueño PyME;
- checklist de piloto real;
- registro de riesgos antes de cliente real.

## Alcance no autorizado

M31-C no autoriza:

- código productivo;
- M32;
- producto;
- autonomía end-to-end;
- Guided Evidence Recovery;
- ERP;
- UI;
- PDF profesional;
- automatización comercial;
- LearningMemory automática;
- promesas de diagnóstico sin evidencia;
- pilotos reales sin contrato de intake y salida.

## Relación con M31-P

M31-P demostró capacidad interna realista.

M31-C prepara la transición a pilotos reales.

La secuencia correcta queda:

```text
M31-P interno realista
→ M31-C preparación comercial asistida
→ pilotos con prospectos/clientes reales, si M31-C cierra
→ sólo después, decidir M32 o fase técnica posterior
```

## Criterio de cierre de M31-C

M31-C podrá cerrar como PASS_DOCUMENTAL_COMERCIAL si existen:

- oferta asistida mínima;
- intake comercial-operativo;
- criterio de aptitud de caso;
- lista de no-promesas;
- checklist de bloqueo;
- plantilla de salida mínima;
- criterio de costo/tiempo operativo;
- plan de 3 a 5 pilotos reales/prospectos;
- checkpoint M31-C.

## Consecuencias

- M32 sigue bloqueado.
- Producto sigue no certificado.
- Clientes reales no se abordan sin contrato comercial-operativo.
- El dueño PyME sigue siendo proveedor de datos y sentido, no sólo uploader.
- El sistema debe bloquear o pedir evidencia cuando falte base suficiente.

## Próximo paso

Crear:

```text
docs/smartpyme/M31C_PREPARACION_COMERCIAL_PLAN.md
docs/smartpyme/M31C_ASSISTED_SERVICE_OFFER.md
docs/smartpyme/M31C_COMMERCIAL_INTAKE.md
```

No crear código.
No abrir M32.
