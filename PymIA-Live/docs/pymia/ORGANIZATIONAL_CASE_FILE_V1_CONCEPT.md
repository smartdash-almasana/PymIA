# Organizational Case File V1 — Concepto Rector

## Estado

```text
Estado: CONCEPT_READY
Tipo: ARCHITECTURAL_CONCEPT
Runtime impact: NONE
Productive code impact: NONE
Fecha: 2026-06-17
```

## Definición breve

`OrganizationalCaseFile V1` es el artefacto acumulativo donde PymIA reúne, ordena y vuelve inteligible la información de una PyME a lo largo de un caso.

No es una ficha administrativa.
No es un CRM.
No es un reporte final.
No es sólo trazabilidad técnica.

Es el contenedor progresivo donde se pegan las “figuritas” del caso: datos crudos, sentido operativo, taxonomía, variables, hipótesis, fórmulas, resultados, interpretaciones e incógnitas abiertas.

## Metáfora rectora

La ficha funciona como un álbum de figuritas inicialmente vacío.

Cada casillero representa una parte de la empresa que todavía puede estar vacía, parcialmente conocida o confirmada.

A medida que PymIA recibe evidencia, escucha al dueño, interpreta datos y ejecuta fórmulas, va completando el álbum.

```text
álbum vacío
→ datos crudos
→ información con sentido
→ clasificación taxonómica
→ variables organizacionales
→ fórmulas aplicables
→ resultados matemáticos
→ interpretación operativa
→ nuevas preguntas
→ esclarecimiento progresivo
```

## Propósito

El propósito de `OrganizationalCaseFile V1` no es guardar datos por guardar.

Su función es permitir que PymIA avance desde el caos operativo hacia una comprensión matemática e interpretativa de la empresa.

La ficha debe responder progresivamente:

```text
¿Qué empresa tengo delante?
¿Qué familia organizacional representa?
¿Qué datos existen?
¿Qué datos faltan?
¿Qué significan esos datos?
¿Qué variables organizacionales aparecen?
¿Qué fórmulas corresponden?
¿Qué hipótesis se activan?
¿Qué patologías podrían existir?
¿Qué se confirmó?
¿Qué sigue siendo incógnita?
¿Qué pregunta conviene hacer después?
```

## Tesis central

La ficha no es el resultado del diagnóstico.

La ficha es el mapa vivo que permite diagnosticar.

```text
dato → variable
variable → relación
relación → fórmula
fórmula → resultado
resultado → interpretación
interpretación → nueva pregunta
```

Ese ciclo convierte información dispersa en conocimiento organizacional progresivo.

## Diferencia con una ficha pobre

Una ficha pobre registra:

```text
tenant_id
intake_id
evidencias
runs
reportes
estado
```

Eso sirve para trazabilidad, pero no alcanza para PymIA.

Una ficha PymIA debe incluir además:

```text
taxonomía empresarial
familia organizacional
morfología operativa
variables relevantes
hipótesis activas
fórmulas candidatas
patologías candidatas
incógnitas abiertas
datos requeridos
interpretaciones progresivas
```

## Capas de la ficha

### 1. Capa expediente

Registra el caso como unidad operativa.

```text
tenant_id
intake_id
case_id
estado del caso
evidencias recibidas
owner answers
preguntas emitidas
runs ejecutados
reportes generados
hashes / trazabilidad
```

Esta capa responde:

```text
¿Qué pasó en este caso?
```

### 2. Capa taxonómica

Clasifica qué tipo de empresa está siendo observada.

```text
familia de empresa
sector
subsector
tipo operativo
modelo de ingresos
modelo productivo
estructura de costos
estructura comercial
ciclo de caja
intensidad de inventario
intensidad de mano de obra
dependencia de proveedores
dependencia de clientes
grado de formalización
grado de estacionalidad
madurez administrativa
```

Esta capa responde:

```text
¿Qué clase de organismo empresarial tengo delante?
```

La taxonomía no es decoración. La taxonomía gobierna qué fórmulas, patologías, datos e hipótesis tienen sentido.

### 3. Capa de datos crudos

Conserva lo recibido antes de interpretarlo completamente.

```text
Excel
mensajes del dueño
respuestas del dueño
documentos
tablas
ventas
costos
stock
deudas
plazos
sueldos
gastos
observaciones operativas
```

Esta capa responde:

```text
¿Qué material bruto entregó la empresa?
```

### 4. Capa semántica

Convierte datos crudos en información reconocible.

Ejemplos:

```text
esto parece venta
esto parece costo variable
esto parece gasto fijo
esto parece inventario
esto parece plazo de cobro
esto parece deuda operativa
esto parece cuello de botella
esto parece capacidad ociosa
```

Esta capa responde:

```text
¿Qué significan estos datos dentro de una empresa?
```

### 5. Capa de variables organizacionales

Identifica las magnitudes relevantes del caso.

```text
tiempo
producción
dinero
stock
rotación
margen
capacidad
precio
costo
cobro
pago
demanda
personal
desperdicio
productividad
```

Esta capa vuelve computable la empresa.

### 6. Capa matemática

Relaciona variables con fórmulas aplicables.

```text
margen bruto
contribución marginal
punto de equilibrio
rotación de inventario
ciclo de conversión de caja
ticket promedio
productividad por hora
capacidad instalada
concentración de clientes
concentración de SKU
```

Esta capa responde:

```text
¿Qué se puede calcular con lo que sabemos?
¿Qué falta para poder calcular?
```

### 7. Capa investigativa

Registra hipótesis, patologías candidatas e incógnitas abiertas.

```text
hipótesis activas
hipótesis descartadas
patologías candidatas
hallazgos confirmados
incógnitas abiertas
datos requeridos
preguntas siguientes
```

Esta capa responde:

```text
¿Qué estamos investigando y por qué?
```

## Ejemplo conceptual

Entrada del dueño:

```text
"Vendo más pero no me queda plata."
```

La ficha no debe responder directamente con un diagnóstico.

Debe abrir casilleros:

```text
Pregunta emergente:
- rentabilidad percibida vs caja disponible

Hipótesis activas:
- margen erosionado
- descalce de caja
- exceso de stock
- mala mezcla de productos
- costos indirectos invisibles

Taxonomía necesaria:
- comercio, fábrica, distribuidora o servicio
- intensidad de inventario
- modelo de cobro y pago
- estructura de costos

Variables necesarias:
- ventas
- costo de mercadería / producción
- gastos fijos
- stock
- plazo de cobro
- plazo de pago
- margen por producto

Fórmulas candidatas:
- margen bruto
- contribución marginal
- punto de equilibrio
- rotación de inventario
- ciclo de conversión de caja
- concentración de ventas

Incógnitas abiertas:
- no sabemos margen por producto
- no sabemos plazo real de cobro
- no sabemos plazo real de pago
- no sabemos rotación
- no sabemos si el problema es precio, costo, volumen, stock o caja

Siguiente pregunta posible:
- ¿Cuánto tardás en cobrar y cuánto tardás en pagar?
```

## Importancia de las familias empresariales

La misma frase del dueño puede significar cosas distintas según la familia organizacional.

### Comercio con inventario

```text
stock
rotación
margen por SKU
merma
concentración de productos
ciclo de caja
```

### Fábrica

```text
capacidad instalada
costos indirectos
horas máquina
lotes mínimos
desperdicio
cuellos de botella
```

### Servicios profesionales

```text
horas vendibles
utilización
precio por hora
scope creep
costo de personal
retrabajo
```

Misma frase.
Distinto mapa de investigación.
Distintas fórmulas.
Distintas incógnitas.
Distinta interpretación.

## Relación con PymIA-Live actual

PymIA-Live ya posee piezas importantes:

```text
EvidenceRecord
AnamnesisRecord
InvestigationRecord
OwnerAnswerRecord
EvidenceRequestRecord
PipelineRunRecord
Owner/Operator markdown views
Case replay from JSONL
```

Pero esas piezas todavía son registros separados.

`OrganizationalCaseFile V1` debe funcionar como el objeto superior que las organiza dentro de un mapa de caso.

No reemplaza los registros existentes.
Los interpreta y los reúne.

## Relación con replay desde JSONL

`CASE_REPLAY_FROM_JSONL` permite reconstruir qué ocurrió en un caso.

`OrganizationalCaseFile V1` debería permitir entender qué significa ese caso.

```text
Replay:
- reconstruye la traza.

OrganizationalCaseFile:
- organiza la comprensión progresiva.
```

Por eso el replay es una base útil, pero no suficiente.

## Relación con conocimiento enchufable

La ficha no debe hardcodear conocimiento sectorial en el kernel.

Debe estar preparada para recibir conocimiento desde packs:

```text
FormulaPack
PathologyPack
SectorPack
KnowledgePack
CatalogPack
```

El kernel debe conservar el contenedor y las reglas de integridad.

El conocimiento de dominio debe seguir siendo enchufable.

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

## Forma tentativa del artefacto

Nombre recomendado:

```text
OrganizationalCaseFile V1
```

Campos conceptuales:

```text
case_identity
case_status
company_taxonomy
organizational_family
operational_morphology
raw_inputs
semantic_interpretations
organizational_variables
candidate_formulas
candidate_pathologies
active_hypotheses
discarded_hypotheses
available_evidence
missing_evidence
open_unknowns
confirmed_findings
next_questions
calculation_results
interpretive_notes
trace_refs
version
metadata
```

## Invariantes

`OrganizationalCaseFile V1` debe cumplir:

```text
- no reemplaza EvidenceRecord;
- no reemplaza PipelineRunRecord;
- no reemplaza replay;
- no ejecuta diagnóstico por sí misma;
- no recalcula fórmulas por sí misma;
- no inventa datos faltantes;
- no convierte hipótesis en hallazgos;
- no mezcla tenant_id;
- no mezcla intake_id;
- no hardcodea conocimiento sectorial en el kernel;
- no se convierte en CRM;
- no se convierte en ERP;
- conserva diferencia entre dato, interpretación, hipótesis, cálculo y hallazgo.
```

## Estados internos posibles

Cada casillero de la ficha podría estar en uno de estos estados:

```text
EMPTY
OBSERVED
INFERRED
CONFIRMED
REJECTED
NEEDS_EVIDENCE
CALCULATED
INTERPRETED
```

Esto permite representar el avance del esclarecimiento sin fingir certeza.

## Función dentro del ciclo PymIA

```text
1. El dueño expresa una inquietud.
2. PymIA registra el caso.
3. PymIA clasifica preliminarmente la empresa.
4. PymIA detecta datos disponibles.
5. PymIA identifica incógnitas.
6. PymIA activa hipótesis.
7. PymIA selecciona fórmulas candidatas.
8. PymIA pide evidencia faltante.
9. PymIA calcula cuando hay suficiencia.
10. PymIA interpreta resultados.
11. PymIA actualiza la ficha.
12. PymIA formula la siguiente pregunta.
```

## Riesgo si no existe esta ficha

Sin un artefacto de este tipo, PymIA corre el riesgo de quedar como una sucesión de piezas correctas pero fragmentadas:

```text
un Excel leído
un reporte generado
una evidencia registrada
una pregunta emitida
un run guardado
```

Eso produce trazabilidad, pero no necesariamente comprensión acumulativa.

La ficha evita esa fragmentación.

## Veredicto conceptual

```text
OrganizationalCaseFile V1 es una pieza estructural necesaria.
```

Debe ser el álbum progresivo del caso PyME: el lugar donde PymIA ordena datos crudos, les asigna sentido, clasifica la empresa, activa hipótesis, conecta fórmulas, calcula cuando puede e interpreta sin perder las incógnitas abiertas.

No es una ficha pobre.
No es un expediente muerto.
No es un CRM.

Es el mapa vivo de esclarecimiento organizacional.
