# Servicio 1 — eje canónico

## Propósito

Este documento define una sola orientación para Servicio 1. Sustituye hojas de ruta, checkpoints y cadenas documentales anteriores que presentaban recorridos paralelos o estados superados.

## Definición

Servicio 1 es el laboratorio operacional de PymIA para datos y archivos de una PyME. El dueño aporta datos y significado operativo; PymIA comprende, valida, calcula y produce archivos.

```text
La IA conversa.
La FSM gobierna.
Las tools ejecutan.
Los archivos son el producto.
El dueño confirma significado durante la lectura.
```

La confirmación del dueño no es revisión posterior a la entrega. Es evidencia de entrada dentro del proceso de comprensión.

## Única raíz productiva

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
```

## Recorrido autorizado

```text
XLSX real
→ ingesta canónica
→ perfil estructural y muestras
→ comprensión semántica de columnas
→ confirmación del dueño, solo si existe duda
→ reentrada semántica validada
→ familias de variables
→ gate de seguridad y computabilidad
```

Desde ese punto existen dos salidas gobernadas:

```text
A. CAPACIDAD EXPLÍCITA
→ matriz fórmula–patología–evidencia
→ binding semántico de variables
→ plan READY_FOR_COMPUTATION
→ sin ejecución, sin diagnóstico y sin delivery automático

B. TOOL REQUEST EXPLÍCITA
→ tool determinística permitida
→ QA
→ archivo XLSX de entrega
```

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector y normalizador XLSX canónico.
- Ninguna respuesta libre puede desbloquear un rol semántico desconocido.
- `unknown` permanece bloqueado hasta recibir una opción canónica o ser marcado `IGNORED_NOT_RELEVANT`.
- La confirmación explícita del dueño prevalece sobre hipótesis secundarias del matcher.
- Una familia incompleta no puede producir una fórmula lista.
- Una relación de catálogo no autoriza runtime por existir.
- `READY_FOR_COMPUTATION` no significa `runtime_authorized`, `tool_execution_authorized`, `delivery_authorized` ni `diagnosis_generated`.
- La capa conversacional no selecciona tools, no diagnostica y no altera gates.
- No se infiere ejecución por entusiasmo, nombre de archivo o texto del dueño.
- No se crean nuevas cadenas soberanas alrededor de piezas existentes.
- Los documentos antiguos no autorizan código.

## Evidencia vigente

```text
BASELINE ESTRUCTURAL: c4834a8
REGRESIÓN P7/P8: 2823 passed, 1 skipped
PYTHON LIMPIO: 3.11
REAL XLSX PLAN-ONLY: PASS
FIRST PASS: NEEDS_OWNER_CONFIRMATION
CANONICAL REENTRY: PASS
READY FAMILY: CASH_COLLECTIONS
REQUESTED CAPABILITY: sold_vs_collected_gap
FORMULA: LIQ_001_vendido_cobrado
SOURCE BINDINGS: venta_total + cobrado
COMPUTATION PLAN: READY_FOR_COMPUTATION
COMPUTATION EXECUTED: false
EXPLICIT TOOL EXECUTION PATH: PASS
FREE-TEXT SEMANTIC REENTRY: BLOCKED
```

## Estado de capacidades

### Certificado

- lectura XLSX real;
- comprensión de columnas integrada;
- preguntas semánticas limitadas;
- reentrada segura;
- confirmación del dueño prioritaria en el matcher;
- familias de variables integradas;
- loader de catálogos integrado en la raíz;
- motor de evidencia semántica integrado en la raíz;
- relación gobernada `CASH_COLLECTIONS → LIQ_001_vendido_cobrado`;
- plan computable sin ejecución;
- ruta explícita de tools y generación física de XLSX;
- serialización CLI y compatibilidad con JSON de PowerShell con BOM.

### Pendiente

- ejecutar de forma controlada un plan `READY_FOR_COMPUTATION` mediante el motor determinístico existente;
- ampliar capacidades formulaicas una por una, con vocabulario y política explícitos;
- conectar el universo restante de patologías, fórmulas y capacidades a esta raíz;
- completar la experiencia conversacional sobre la misma raíz;
- conservar CI, build y dependencias reproducibles.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/service_1_module_disposition.v1.json
docs/service_1_formula_pathology_evidence_matrix.v1.json
```

Cualquier documento no listado en `docs/current/README.md` ni citado expresamente como evidencia técnica por un documento rector carece de autoridad sobre Servicio 1.
