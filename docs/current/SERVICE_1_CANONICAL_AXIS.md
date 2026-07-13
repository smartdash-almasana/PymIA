# Servicio 1 — eje canónico

## Propósito

Este documento define una sola orientación para Servicio 1. Sustituye las hojas de ruta, checkpoints y cadenas documentales anteriores que presentaban recorridos paralelos o estados ya superados.

## Definición

Servicio 1 es el laboratorio operacional de PymIA para datos y archivos de una PyME. El dueño aporta datos y significado operativo; PymIA comprende, valida, calcula y produce archivos.

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

La confirmación del dueño no es una revisión posterior a la entrega. Es evidencia de entrada dentro del proceso de comprensión.

## Única raíz productiva

```text
PymIA-Live/pymia/smartpyme/service_1_product_pipeline_v1.py
PymIA-Live/pymia/cli/service_1_product.py
```

## Recorrido autorizado

```text
XLSX real
→ ingesta canónica
→ perfil estructural y muestras
→ comprensión semántica de columnas
→ confirmación del dueño, solo si existe duda
→ reentrada semántica validada
→ vínculo de evidencia
→ gate de seguridad y computabilidad
→ tool determinística explícita
→ QA y archivo XLSX de entrega
```

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector/normalizador XLSX canónico.
- Ninguna respuesta libre puede desbloquear un rol semántico desconocido.
- `unknown` permanece bloqueado hasta recibir una opción canónica o ser marcado `IGNORED_NOT_RELEVANT`.
- La capa conversacional no selecciona tools, no diagnostica y no altera gates.
- No se infiere ejecución por entusiasmo, nombre de archivo o texto del dueño.
- No se crean nuevas cadenas soberanas alrededor de piezas ya existentes.
- Los documentos antiguos no autorizan código.

## Evidencia vigente

```text
COMMIT: 5c920c6
REGRESIÓN: 2454 passed, 1 skipped
REAL XLSX E2E: cafeteria_abc.xlsx
FIRST PASS: NEEDS_OWNER_CONFIRMATION / tools_executed=false
CANONICAL REENTRY: PASS
EXPLICIT TOOL EXECUTION: PASS
PHYSICAL XLSX OUTPUT: PASS
FREE-TEXT SEMANTIC REENTRY: BLOCKED
```

## Estado de capacidades

### Certificado

- lectura XLSX real;
- comprensión de columnas integrada;
- preguntas semánticas limitadas;
- reentrada segura;
- gate fail-closed;
- ejecución explícita de tools permitidas;
- generación física de XLSX;
- serialización CLI y compatibilidad con JSON de PowerShell con BOM.

### Pendiente

- conectar el universo completo de patologías, fórmulas y capacidades a esta raíz;
- derivar planes de análisis desde evidencia confirmada sin hardcode ni cadenas paralelas;
- completar la experiencia conversacional sobre esta misma raíz;
- terminar la purga documental.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/service_1_module_disposition.v1.json
```

Cualquier documento no citado por `docs/current/README.md` carece de autoridad sobre Servicio 1.
