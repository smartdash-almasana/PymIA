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
→ confirmación del dueño, sólo si existe duda
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
→ ejecución determinística sólo para una capacidad absorbida por la raíz
→ hallazgo acotado, sin atribución causal
→ delivery sólo ante solicitud explícita

B. TOOL REQUEST EXPLÍCITA
→ tool determinística permitida
→ QA
→ archivo XLSX de entrega
```

## Capacidad absorbida actualmente

La única capacidad formulaica absorbida por la raíz en este corte es:

```text
CAPABILITY: sold_vs_collected_gap
PATHOLOGY: LIQ_001
FORMULA: LIQ_001_vendido_cobrado
```

Su recorrido certificado es:

```text
filas normalizadas completas
→ bindings confirmados
→ agregación vendido/cobrado
→ cálculo determinístico
→ hallazgo acotado
→ tratamiento determinístico
→ XLSX sólo con --deliver-result
```

No produce diagnóstico causal. Todos los flags de autoridad permanecen en falso.

## REN_001

`service_1_ren_001_evaluator_v1.py` es un evaluador aislado clasificado `SUPPORT_NECESSARY`.

No forma parte del recorrido autorizado porque:

- no es alcanzable desde la raíz canónica;
- no está conectado a la CLI oficial;
- no autoriza hallazgo, tratamiento ni delivery;
- requiere un ciclo documental explícito antes de cualquier absorción productiva.

## Reglas obligatorias

- Una sola raíz productiva.
- Un solo lector y normalizador XLSX canónico.
- Ninguna respuesta libre puede desbloquear un rol semántico desconocido.
- `unknown` permanece bloqueado hasta recibir una opción canónica o ser marcado `IGNORED_NOT_RELEVANT`.
- La confirmación explícita del dueño prevalece sobre hipótesis secundarias del matcher.
- Una familia incompleta no puede producir una fórmula lista.
- Una relación de catálogo no autoriza runtime por existir.
- `READY_FOR_COMPUTATION` no significa autoridad general de runtime, tools, delivery ni diagnóstico.
- Sólo una capacidad explícitamente absorbida por la raíz puede ejecutar cálculo gobernado.
- La capa conversacional no selecciona tools, no diagnostica y no altera gates.
- No se infiere ejecución por entusiasmo, nombre de archivo o texto del dueño.
- No se crean nuevas cadenas soberanas alrededor de piezas existentes.
- Los documentos antiguos y la memoria conversacional no autorizan código.

## Evidencia vigente

```text
ÚLTIMA REGRESIÓN OBSERVADA: 1644 passed in 175.30s
REAL XLSX OWNER CONFIRMATION: PASS
CANONICAL REENTRY: PASS
LIQ_001 COMPUTATION: PASS
LIQ_001 BOUNDED FINDING: PASS
LIQ_001 EXPLICIT DELIVERY: PASS
REN_001 ISOLATED EVALUATOR: PASS, SUPPORT ONLY
EXPLICIT TOOL EXECUTION PATH: PASS
FREE-TEXT SEMANTIC REENTRY: BLOCKED
```

## Estado de capacidades

### Certificado

- lectura XLSX real;
- comprensión de columnas integrada;
- preguntas semánticas limitadas;
- reentrada segura;
- confirmación del dueño prioritaria;
- familias de variables integradas;
- loader de catálogos integrado en la raíz;
- motor de evidencia semántica integrado en la raíz;
- ejecución gobernada de `LIQ_001_vendido_cobrado`;
- hallazgo acotado y tratamiento determinístico LIQ_001;
- delivery LIQ_001 explícito;
- ruta explícita de tools y generación física de XLSX;
- serialización CLI y compatibilidad con JSON de PowerShell con BOM.

### Fuera de la raíz

- `REN_001_margen_neto_real`: evaluador aislado de soporte;
- universo restante de patologías, fórmulas y capacidades.

## Próximo paso autorizado

```text
CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA
```

No está autorizada la conexión productiva de REN_001 dentro de ese ciclo.

## Documentación rectora relacionada

```text
docs/current/README.md
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_PRODUCT_COMPLETION_GATE.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/service_1_module_disposition.v1.json
docs/service_1_formula_pathology_evidence_matrix.v1.json
```

Cualquier documento no listado en `docs/current/README.md` ni citado expresamente como evidencia técnica por un documento rector carece de autoridad sobre Servicio 1.
