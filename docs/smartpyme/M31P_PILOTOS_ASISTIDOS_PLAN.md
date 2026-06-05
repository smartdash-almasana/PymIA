# M31-P — Pilotos asistidos reales

## Estado

PLAN_METODOLOGICO

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
¿El protocolo M31 puede repetirse en 3 a 5 casos con evidencia, tiempo, bloqueos y salida registrada?
```

## Alcance permitido

- seleccionar 3 a 5 casos piloto;
- registrar intake inicial del dueño PyME;
- registrar evidencia recibida;
- registrar evidencia faltante;
- aplicar el protocolo M31;
- registrar tiempo real de ejecución;
- registrar bloqueos;
- registrar salida entregada;
- registrar aprendizajes candidatos sin promoverlos automáticamente a LearningMemory;
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
→ ejecución / documentación de casos
→ checkpoint M31-P
```

ModuleContract sólo corresponde si se modifica o crea una frontera técnica. En esta fase, por defecto, no corresponde porque no hay código productivo autorizado.

## Evidencia mínima por piloto

Cada piloto debe registrar:

- pilot_id;
- tenant_id o identificador anonimizado;
- tipo de PyME o rubro si aplica;
- dolor declarado por el dueño;
- evidencia aportada;
- evidencia faltante;
- estado final;
- salida entregada o bloqueo;
- tiempo real de ejecución;
- costo operativo si corresponde;
- intervención humana requerida;
- bloqueos encontrados;
- aprendizaje candidato, si corresponde;
- si el caso fue repetible o no repetible.

## Criterio PASS de M31-P

M31-P sólo puede declararse PASS_OPERATIVO si existen:

- 3 a 5 registros de piloto completos;
- evidencia de tiempo real;
- registro de bloqueos;
- salidas o bloqueos documentados;
- evaluación de repetibilidad;
- checkpoint M31-P.

## Criterio PARTIAL

M31-P queda PARTIAL si:

- hay menos de 3 pilotos;
- hay pilotos con registros incompletos;
- faltan tiempos reales;
- faltan bloqueos o aprendizajes;
- no se puede evaluar repetibilidad.

## Criterio BLOCKED

M31-P queda BLOCKED si:

- no hay casos piloto disponibles;
- no hay evidencia suficiente;
- el protocolo M31 no puede aplicarse sin cambiar código;
- se intenta convertir el ciclo en producto;
- se intenta implementar Guided Evidence Recovery sin contrato propio.

## Próximo documento requerido

Crear:

```text
docs/adr/ADR-M31P-PILOTOS-ASISTIDOS.md
```

Luego:

```text
docs/smartpyme/M31P_CAPABILITY_SPEC.md
docs/smartpyme/M31P_TASK_SPEC.md
```

## Regla final

M31-P es una fase de validación operativa asistida.

No es M32.
No es producto.
No es autonomía.
No es implementación técnica.
