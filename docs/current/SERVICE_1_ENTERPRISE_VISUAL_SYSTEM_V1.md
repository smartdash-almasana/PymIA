# SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1

## STATUS

```text
VISUAL_SYSTEM: DEFINED
SCOPE: PRESENTATION_ONLY
PRODUCT_ROOT_AUTHORITY: UNCHANGED
BUSINESS_LOGIC_AUTHORITY: UNCHANGED
PARSER_AUTHORITY: UNCHANGED
P0_P10_AUTHORITY: UNCHANGED
```

## PURPOSE

Definir el lenguaje visual enterprise propio de PymIA para Servicio 1 sin alterar comportamiento, reglas de negocio, autoridad, parser, persistencia ni capacidades.

La interfaz debe ser reconocible como PymIA incluso sin logo.

## DESIGN_CONCEPT

```text
PYMIA — MESA DE OPERACIONES
```

PymIA no se presenta como chatbot, dashboard, tienda de servicios ni planilla decorada.

Se presenta como una mesa digital de control, evidencia y decisión para una PyME.

La dirección visual combina:

```text
libro mayor
+ papel de trabajo de auditoría
+ expediente operativo
+ mesa de operaciones
+ software financiero serio
+ documentación técnica precisa
```

La traducción contemporánea de esos referentes se expresa con reglas, numeración, metadatos, estados explícitos, superficies documentales, jerarquía editorial y alta legibilidad de datos.

## VISUAL DNA

Elementos distintivos obligatorios:

1. **Regla PymIA** — líneas horizontales fuertes que separan hecho, evidencia y decisión.
2. **Registro de caso** — IDs, referencias y fechas en lenguaje monoespaciado, nunca como texto decorativo.
3. **Marca de expediente** — borde lateral o marca de registro en verde PymIA para indicar superficie operativa activa.
4. **Estado estampado** — estados rectangulares, compactos, tipográficos; no pills redondeadas tipo SaaS.
5. **Columnas de metadata** — información contextual en pequeñas columnas alineadas, no dispersa en cards.
6. **Bloque de evidencia** — superficie documental con cabecera, provenance y separación del hallazgo.
7. **Numeración de instrumento** — servicios presentados como instrumentos `S1-01`, `S1-02`, `S1-03`, preparados para crecer.
8. **Marcas de registro** — pequeños ticks, dobles líneas o referencias `REF / CASE / EVIDENCE` como firma visual.
9. **Tablas de revisión** — primera clase visual para conciliación; nunca degradadas a mosaicos de cards.
10. **Hecho / Evidencia / Decisión** — tres niveles semánticos visualmente distintos y recurrentes.

## ANTI-PATTERNS

No usar:

```text
glassmorphism
gradients decorativos
fondo gris + cards blancas + azul primario
cards flotantes masivas
radius excesivo
sombras de tarjeta como estructura principal
blobs
AI glow
cyberpunk
pasteles startup
emoji como sistema de iconografía
hero marketing dentro del producto
saludos personales de consumo
una métrica por pantalla
sidebar genérico de dashboard
```

## TYPOGRAPHY

La tipografía es funcional y jerárquica.

No depende de una fuente remota para ser legible. Se priorizan stacks disponibles en sistemas enterprise.

### DISPLAY

```text
font-family: Charter, "Iowan Old Style", "Palatino Linotype", Georgia, serif
weight: 600–700
use: títulos principales de caso y resultado
```

Editorial, sobria, no monumental.

### SECTION

```text
font-family: "Aptos", "Segoe UI", system-ui, sans-serif
weight: 700
tracking: -0.01em
```

### BODY

```text
font-family: "Aptos", "Segoe UI", system-ui, sans-serif
weight: 400–500
line-height: 1.5–1.6
```

### DATA

```text
font-family: "Cascadia Mono", "IBM Plex Mono", Consolas, ui-monospace, monospace
font-variant-numeric: tabular-nums lining-nums
```

Usar para magnitudes financieras, porcentajes y conteos importantes.

### METADATA

```text
sans / mono según el contenido
11–12 px
uppercase sólo en etiquetas cortas
tracking moderado
```

### STATUS

```text
sans
11–12 px
weight: 800
uppercase
tracking: 0.08em
```

### CODE / REFERENCE

```text
mono
11–13 px
font-variant-numeric: tabular-nums
```

IDs, hashes, fechas ISO, provenance, referencias de archivo y columnas.

## COLOR_SYSTEM

La paleta deriva del verde PymIA, madurado a un uso institucional.

### BASE

```text
PAPER              #F3F0E8
PAPER_RAISED       #FBFAF6
INK                #17201C
INK_SOFT           #47524B
RULE               #C9C5B9
RULE_STRONG        #817F76
LEDGER_DARK        #16231D
```

Las superficies evocan documento, expediente y mesa de trabajo; no una app de consumo.

### PYMIA GREEN

```text
PYMIA_GREEN        #185B43
PYMIA_GREEN_DARK   #103B2D
PYMIA_GREEN_SOFT   #DDE9E2
```

Uso disciplinado:

- marca activa;
- foco;
- controles primarios;
- indicadores de completitud;
- reglas de registro.

No pintar grandes áreas de verde sin función.

### SEMANTIC

```text
READY              #1F6A4A
MISSING            #9A6B13
REVIEW              #A24C1D
BLOCKED             #8A2D2D
COMPLETED           #355C4B
TECHNICAL_NEUTRAL   #5D655F
```

Los colores semánticos nunca sustituyen el texto del estado.

## SPACING

Escala base de 4 px.

```text
4   micro separación
8   metadata / controles
12  filas densas
16  bloques internos
24  separación de secciones
32  separación estructural
48  cambio de capítulo visual
```

No usar padding de 40–64 px dentro de cada bloque salvo superficies excepcionales.

## GRID

Desktop primario:

```text
max-width: 1280 px
12 columnas conceptuales
24 px gutter
```

Patrones:

```text
3 cols metadata + 9 cols contenido
4 cols contexto + 8 cols control
5 cols evidencia + 7 cols decisión
```

Las tablas pueden usar todo el ancho útil.

## SURFACES

Tres superficies:

### DESK

Fondo general `PAPER`.

### WORKPAPER

Bloque principal `PAPER_RAISED` con bordes rectos, regla superior y marca lateral.

### EVIDENCE INSET

Área de evidencia con fondo ligeramente más frío o tramado lineal muy sutil.

No usar sombras como método principal de separación. La profundidad se construye con reglas, contraste y jerarquía.

## BORDERS

```text
radius estándar: 0–4 px
radius excepcional: 6 px
border: 1 px RULE
section rule: 2 px INK / PYMIA_GREEN según semántica
```

El rectángulo es la forma primaria.

## STATUS_SYSTEM

Estados de producto visibles:

```text
LISTO
FALTA INFORMACIÓN
REQUIERE REVISIÓN
BLOQUEADO
COMPLETADO
```

Tratamiento:

- mayúsculas;
- borde 1 px;
- bloque compacto;
- marcador lateral o superior;
- texto siempre presente;
- sin depender sólo del color.

Estados técnicos discretos:

```text
archivo recibido
estructura detectada
significado confirmado
requisitos verificados
ejecución realizada
entrega verificada
```

Se representan como timeline de proceso, sin exponer P6/P7/P8/P9/P10 al cliente.

## DATA_PRESENTATION

Números financieros:

- alineación tabular;
- separadores locales legibles;
- signo y unidad explícitos;
- jerarquía por magnitud, no por tamaño gigante;
- diferencia y ratio adyacentes al universo que describen.

Ejemplo:

```text
VENDIDO      $ 3.000.000,00
COBRADO      $ 2.300.000,00
DIFERENCIA     $ 700.000,00
COBRADO              76,7 %
```

## TABLES

Las tablas son una superficie central, no secundaria.

Reglas:

- headers compactos;
- zebra sólo si mejora lectura;
- filas de 40–48 px desktop;
- números alineados a la derecha;
- referencias en mono;
- estado como texto estampado;
- hover sutil para orientación;
- acciones en la última columna;
- sticky header sólo cuando la tabla larga lo requiera;
- sin transformar cada fila en card en desktop.

## FORMS

Forms con estructura de expediente:

```text
label
control
nota / restricción
```

Inputs:

- fondo claro;
- borde definido;
- radius mínimo;
- foco verde PymIA visible;
- altura 42–46 px;
- file inputs tratados como evidencia recibida, no como upload decorativo.

Botón primario: verde PymIA sólido.

Botón secundario: papel + borde oscuro.

Acciones destructivas o de rechazo: semánticas, sin convertir toda la UI en rojo.

## EVIDENCE_BLOCKS

Un bloque de evidencia debe expresar:

```text
EVIDENCIA
archivo / fuente
hoja
columna
período
provenance
limitaciones
```

La evidencia nunca se mezcla tipográficamente con una conclusión.

## CASE_HEADER

El caso es el objeto visual central.

Formato objetivo:

```text
CASO / S1-2026-00128
CONTROL DE COBROS
ACME SA · JULIO 2026
REQUIERE REVISIÓN
```

Debajo:

```text
EMPRESA
SERVICIO
PERÍODO
RESPONSABLE
EVIDENCIA
ÚLTIMA ACTIVIDAD
```

El `case_id` usa mono y tabular numbers.

### LIMITACIÓN V1

El shell GET actual no expone tenant, usuario y rol verificados a la función de render. Este sistema reserva su posición visual, pero la implementación de esta fase no debe modificar autenticación ni Supabase para completarlos. Cuando el contexto no esté disponible, se muestra explícitamente como no disponible; nunca se inventa identidad.

## SERVICE_NAVIGATION

Servicios se presentan como instrumentos operativos.

Estados:

```text
DISPONIBLE
PILOTO
PRÓXIMAMENTE
NO HABILITADO
```

`DISPONIBLE` controla ejecución según el producto existente. Los otros estados son visuales sólo cuando ya existe una fuente de verdad de disponibilidad; la UI no crea capacidades.

Numeración visual:

```text
S1-01  Control de Cobros y Conciliación
S1-02  Conciliación Bancaria
S1-03  Margen Real
```

El patrón admite futuros `S2-*`, `S3-*` y nuevas familias sin rediseñar el shell.

## SEMANTIC_CONFIRMATION

La confirmación semántica es una firma visual de PymIA.

Debe distinguir cuatro capas:

```text
01 / LO DETECTADO
02 / PYMIA PROPONE
03 / MEMORIA PREVIA
04 / OWNER CONFIRMA
```

Reglas:

- memoria previa es evidencia de contexto, no decisión;
- nunca seleccionar automáticamente por memoria;
- la opción confirmada por owner debe ser la única que habilita continuidad;
- `No estoy seguro` conserva visibilidad como salida legítima;
- cada pregunta se trata como fila de workpaper, no card de chatbot.

## RESULT_PRESENTATION

Toda salida comercial usa esta jerarquía:

```text
CONTROL
PERÍODO
ESTADO
MAGNITUDES
HALLAZGO
EVIDENCIA UTILIZADA
LÍMITES
ACCIONES
```

No usar “AI insights”.

El hallazgo es un bloque editorial fuerte pero acotado.

Las limitaciones tienen presencia visible equivalente a la evidencia.

## RECONCILIATION_REVIEW

La conciliación se diseña como mesa de revisión:

```text
BANCO
↔
REGISTRO INTERNO
→
ESTADO
→
DECISIÓN HUMANA
```

Características:

- resumen numérico compacto;
- lista/tablas densas para casos;
- `CONFIRMAR / RECHAZAR / PENDIENTE` como acciones de revisión;
- nombre del revisor y observación adyacentes a la decisión;
- última decisión registrada visible;
- workpaper descargable como evidencia de cierre de revisión;
- mensaje permanente de que PymIA no concilia automáticamente.

## HOME

Home es el registro de instrumentos, no una landing.

Orden:

```text
cabecera institucional
contexto operativo
instrumentos disponibles
inicio de caso / carga de evidencia
conciliación
casos recientes / continuidad
```

No hero, no marketing, no slogans grandes.

## RECENT_CASES

Casos recientes se presentan como libro de casos:

```text
CASE ID
SERVICIO
ESTADO
ACTUALIZADO
ACCIÓN
```

El case ID debe ser visible en mono.

## RESPONSIVE_BEHAVIOR

### 1440

Mesa completa, 12 columnas, metadata lateral, tablas densas y acciones alineadas.

### 1280

Mismo modelo con gutters reducidos; no cambia la jerarquía.

### 1024

Metadata pasa a banda superior; tablas conservan scroll horizontal cuando sea necesario.

### 768

Navegación compacta; bloques de evidencia y decisión se apilan; tablas largas usan contenedor desplazable.

### 390

No se reproduce una workstation completa.

Prioridad:

```text
estado
caso
magnitud principal
hallazgo
acción
```

Metadata secundaria se agrupa; tablas pueden convertirse en filas apiladas sólo mediante CSS si la semántica sigue siendo legible.

## ACCESSIBILITY

- contraste WCAG AA como mínimo;
- focus visible verde oscuro / tinta;
- no depender del color para estados;
- `prefers-reduced-motion` respetado;
- jerarquía HTML semántica conservada;
- targets táctiles mínimos de 44 px en mobile.

## IMPLEMENTATION_TASKSPEC

### OBJECTIVE

Aplicar `PYMIA — MESA DE OPERACIONES` a la web asistida existente con mínima superficie y sin alterar comportamiento.

### ALLOWED_FILES

```text
docs/current/SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1.md
docs/current/README.md
pymia/smartpyme/templates/service_1_assisted_web_v1.html
pymia/smartpyme/static/service_1_assisted_web_v1.css
pymia/smartpyme/service_1_assisted_web_v1.py  # sólo render HTML / shell / clases de presentación
```

### FORBIDDEN_FILES

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
parser XLSX
gates P0→P10
Supabase adapters / resolver
capability registry
reconciliation computation
business rules
```

### ACCEPTANCE

```text
shell propio de PymIA
home como registro de instrumentos
case ID visible en listado de casos
semantic confirmation visualmente diferenciada
results con hecho/evidencia/límites/acción
reconciliation como mesa de revisión
responsive 1440/1280/1024/768/390 por CSS
journeys HTTP focales permanecen PASS
```

### STOP CONDITIONS

Detener si un cambio visual exige:

```text
nueva capability
nuevo endpoint funcional
cambio de identidad/autenticación
cambio de Supabase
cambio de parser
cambio de autoridad
cambio de cálculo
cambio de delivery gate
```

## VALIDATION_SCOPE

Sólo tests focales presentation/web:

```text
tests/smartpyme/test_service_1_assisted_web_http_v1.py
tests/smartpyme/test_service_1_assisted_web_reconciliation_http_v1.py
```

No full suite para este corte visual.
