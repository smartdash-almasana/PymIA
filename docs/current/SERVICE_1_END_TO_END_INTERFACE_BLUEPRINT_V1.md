# SERVICE_1_END_TO_END_INTERFACE_BLUEPRINT_V1

**Fecha:** 2026-08-16  
**Estado:** `IMPLEMENTED_LOCAL_PENDING_RELEASE`  
**Scope:** interfaz y experiencia de Servicio 1 de punta a punta  
**No altera:** parser, pipeline, fórmulas, P6/P7/P8/P10, Supabase, persistencia, autoridad determinística ni delivery

---

# 1. Decisión de diseño

Servicio 1 deja de diseñarse como una sucesión de pantallas técnicas corregidas individualmente.

La interfaz se diseña como **un único recorrido de análisis empresarial**:

```text
SUBIR EL EXCEL
→ VER QUÉ ENTENDIÓ PYMIA
→ CONFIRMAR SÓLO LAS DUDAS MATERIALES
→ OFRECER EL MENÚ DE ANÁLISIS SOBRE ESA EVIDENCIA
→ ELEGIR UNO, VARIOS O TODOS
→ RECIBIR LA DEVOLUCIÓN ANALIZADA
→ AMPLIAR / DESCARGAR / GUARDAR
```

Regla central:

```text
cada pantalla responde una sola pregunta del usuario.
```

El usuario nunca debe comprender la arquitectura de PymIA para poder usar PymIA.

---

# 2. Usuario objetivo

Dueño, responsable administrativo o persona de gestión de una PyME que:

- trabaja con Excel;
- conoce su negocio pero no necesariamente la terminología técnica del software;
- necesita responder una pregunta concreta;
- puede reconocer sus columnas y operaciones cuando se las muestran;
- no debería tener que interpretar conceptos internos como semantic role, evidence, computability, owner confirmation, P6/P7/P8, provenance o capability.

La interfaz usa **títulos empresariales correctos** y los acompaña con una traducción inmediata a lenguaje cotidiano.

Patrón obligatorio:

```text
TÉRMINO EMPRESARIAL
Pregunta que explica para qué sirve
Qué debería contener el Excel
Qué resultado va a recibir
```

---

# 3. Principios UX no negociables

## 3.1 Business-first

Los títulos visibles pertenecen al vocabulario real de empresas y comercios.

No se reemplazan términos empresariales correctos por frases infantiles.

Se explican.

Ejemplo:

```text
Margen real
¿Cuánto te queda realmente después de los costos que aparecen en tu Excel?
```

## 3.2 Evidence-before-question

PymIA nunca pregunta primero y explica después.

Antes de solicitar una confirmación muestra:

```text
qué encontró,
dónde lo encontró,
qué valores vio,
y por qué necesita confirmar algo.
```

## 3.3 Una decisión por vez

Cuando una duda sea material y separable, se muestra una pregunta por bloque/pantalla.

No formularios masivos de columnas.

## 3.4 Progressive disclosure

Primero:

```text
resultado / decisión necesaria
```

Después, bajo demanda:

```text
datos utilizados
hojas y columnas
límites
trazabilidad
```

## 3.5 Result-first

Si PymIA puede responder la pregunta principal, el resultado se considera listo aunque existan análisis adicionales posibles.

No se convierte una ampliación opcional en un error.

## 3.6 No internal jargon

Prohibido en UX primaria:

```text
P6 / P7 / P8 / P10
semantic role
semantic confirmation
computability
evidence candidate
provenance
tenant
owner event
capability
bounded outcome
kernel
```

Traducciones visibles:

```text
evidence        → datos del Excel / datos utilizados
semantic doubt  → quiero confirmar una cosa
blocked         → necesito un dato más
partial         → mostrar sólo si la pregunta principal realmente quedó incompleta
```

## 3.7 Honestidad sin dramatización

Fail-closed sigue intacto por debajo.

Pero la UX diferencia:

```text
RESULTADO LISTO
HAY UNA DIFERENCIA
NECESITO UN DATO MÁS
NECESITA TU REVISIÓN
```

No usar `FALTA INFORMACIÓN` como sello general cuando existe un resultado útil.

---

# 4. Arquitectura de información

Navegación global mínima:

```text
PYMIA                                      Mis análisis
```

No sidebar.
No dashboard genérico.
No menú técnico.
No marketing dentro del producto.

Objetos principales:

```text
Análisis
Archivo
Dato encontrado
Pregunta de confirmación
Resultado
Caso guardado
```

---

# 5. Portfolio visible de Servicio 1

La disponibilidad visible debe provenir del producto real; la UI no habilita capacidades por sí sola.

## 5.1 Ventas y cobranzas

**Título empresarial**

```text
Ventas y cobranzas
```

**Pregunta**

```text
¿Cuánto vendiste, cuánto cobraste y qué quedó pendiente?
```

**Qué debería traer el Excel**

```text
Ventas y cobranzas del mismo período.
Idealmente importes y fechas o referencias que permitan distinguirlas.
```

**Resultado principal**

```text
Total vendido
Total cobrado
Diferencia
Porcentaje cobrado, cuando corresponda
```

---

## 5.2 Margen real

**Título empresarial**

```text
Margen real
```

**Pregunta**

```text
¿Cuánto te queda realmente después de los costos que aparecen en tu Excel?
```

**Qué debería traer el Excel**

```text
Ventas y costos.
Si las ventas están por producto, ayudan cantidad, precio, costo y descuentos cuando existan.
```

**Resultado principal**

```text
Margen calculado con la evidencia disponible y confirmada.
```

La interfaz nunca promete incorporar impuestos, comisiones o retenciones que no estén presentes y gobernadas.

---

## 5.3 Flujo de caja

**Título empresarial**

```text
Flujo de caja
```

**Pregunta**

```text
¿Cuánto dinero te quedaría después de los cobros y pagos previstos?
```

**Qué debería traer el Excel**

```text
Saldo inicial.
Ingresos o cobros previstos.
Egresos o pagos previstos.
Período, si está disponible.
```

**Resultado principal**

```text
Saldo de caja proyectado
```

Análisis adicionales, sólo como ampliación:

```text
Tiempo promedio de cobro
Cobertura de corto plazo
```

Estos análisis nunca hacen que un saldo proyectado válido aparezca como resultado incompleto.

---

## 5.4 Conciliación bancaria

**Título empresarial**

```text
Conciliación bancaria
```

**Pregunta**

```text
¿Qué movimientos del banco coinciden con tus registros y cuáles necesitan revisión?
```

**Qué debería adjuntar**

```text
1. Extracto bancario.
2. Registro interno de cobros/movimientos.
```

**Resultado principal**

```text
Coincidencias
Diferencias
Movimientos pendientes de revisión humana
Workpaper descargable cuando corresponda
```

PymIA nunca comunica una conciliación definitiva automática.

---

# 6. Journey canónico de una fuente

## Pantalla 0 — Login

Objetivo:

```text
entrar
```

Contenido:

```text
PYMIA
Ingresá para revisar tus archivos
Email
Contraseña
[Ingresar]
```

Nada más.

Errores en lenguaje humano:

```text
No pude iniciar sesión con esos datos.
Revisá el email y la contraseña.
```

---

## Pantalla 1 — Subir archivo

Pregunta de la pantalla:

```text
¿Qué información contiene mi Excel?
```

No se obliga al cliente a elegir un análisis antes de que PymIA conozca la evidencia disponible.

Contenido principal:

```text
Subí tu Excel

PymIA primero lee el archivo, después te pide confirmar sólo lo necesario
y recién entonces te muestra qué análisis podés pedir sobre esa misma información.

.xlsx · PymIA no modifica el original
[Seleccionar archivo]
[Leer mi Excel]
```

Secuencia visible:

```text
1. PymIA identifica hojas, columnas y relaciones.
2. El dueño confirma las dudas materiales.
3. PymIA ofrece el menú de devolución.
4. El cliente puede pedir uno, varios o todos los análisis soportados.
```

No se muestra `S1-01`, estados técnicos, PILOTO, capability IDs ni códigos internos como contenido primario.

Contexto opcional se mantiene secundario y colapsado.

Conciliación de dos fuentes permanece como journey secundario explícito.

---

## Pantalla 2 — Lectura / comprensión

Pregunta de la pantalla:

```text
¿Qué entendió PymIA de mi Excel?
```

Título:

```text
Esto encontré en tu Excel
```

Primero se muestra un resumen, no preguntas.

Ejemplo margen:

```text
✓ Ventas
  Encontré importes de venta en la hoja Ventas.

✓ Cantidades
  Encontré cantidades por operación.

✓ Costos
  Encontré costos en la hoja Productos.

? Descuento
  Encontré una columna con valores 0 · 0,10 · 0,20.
  Necesito confirmar cómo están expresados.
```

Estados visuales de un dato:

```text
ENCONTRADO
NECESITO CONFIRMAR
NO ENCONTRADO / OPCIONAL
```

No usar confianza numérica como contenido de dueño.

CTA:

```text
[Continuar]
```

Si no existen dudas materiales, esta pantalla puede continuar directamente al resultado después de mostrar el resumen o usar un CTA único `Calcular resultado`.

---

## Pantalla 3 — Confirmación material

Pregunta de la pantalla:

```text
¿Qué tengo que confirmar?
```

Título:

```text
Quiero confirmar una cosa
```

Ejemplo:

```text
Descuento · hoja Ventas

Encontré estos valores:
0 · 0,10 · 0,20

¿Un valor 0,10 significa 10% de descuento?

○ Sí, significa 10%
○ No, es un importe de dinero
○ Es otra cosa
○ No lo puedo confirmar ahora
```

Siempre mostrar:

- dato real;
- ejemplo real;
- consecuencia de la decisión en lenguaje humano.

Nunca seleccionar automáticamente una respuesta por memoria previa.

Si hay varias dudas, preferir secuencia breve:

```text
Pregunta 1 de 2
```

No tabla masiva salvo que las dudas sean homogéneas y la tabla realmente simplifique.

---

## Pantalla 4 — Menú de devolución

Pregunta de la pantalla:

```text
¿Qué querés que PymIA te devuelva con este Excel ya entendido?
```

El menú aparece **después** de la lectura y de las confirmaciones materiales.

Regla de selección:

```text
UNO
O VARIOS
O TODOS
```

No es un catálogo excluyente. La misma evidencia confirmada puede alimentar más de un análisis sin volver a subir el archivo.

Ejemplo:

```text
¿Qué querés que PymIA te devuelva?

☐ Ventas y cobranzas
  ¿Cuánto vendiste, cuánto cobraste y qué quedó pendiente?

☐ Margen real
  ¿Cuánto te queda después de los costos respaldados por el Excel?

☐ Flujo de caja
  ¿Qué saldo de caja proyecta la evidencia disponible?

[Preparar análisis seleccionados]
```

Si un análisis seleccionado requiere evidencia material ausente, PymIA lo presenta como `Análisis pendiente`; no completa el dato por inferencia ni bloquea los demás análisis seleccionados que sí sean computables.

La selección explícita del cliente sigue siendo la que habilita la solicitud de cada capability. PymIA no ejecuta capacidades silenciosamente para construir el menú.

---

## Pantalla 5 — Resultado

Pregunta de la pantalla:

```text
¿Qué encontré y qué significa?
```

Jerarquía obligatoria:

```text
TÍTULO EMPRESARIAL
ESTADO HUMANO
RESULTADO PRINCIPAL
EXPLICACIÓN BREVE
ACCIONES
AMPLIACIONES OPCIONALES
DATOS UTILIZADOS
LÍMITES
```

### Resultado de Flujo de caja

```text
Flujo de caja                         RESULTADO LISTO

Saldo de caja proyectado
$ 1.700,00

Según el saldo inicial, los cobros previstos y los pagos previstos
informados, este sería el saldo al cierre del período analizado.

[Descargar, si existe entregable]   [Revisar otro Excel]
```

Debajo:

```text
Podés ampliar este análisis

Tiempo promedio de cobro
Para estimarlo necesito cuentas por cobrar, ventas del período y días.

Cobertura de corto plazo
Para estimarla necesito activo corriente y pasivo corriente.
```

No mostrar tarjetas `No disponible` como resultados.

### Resultado de Ventas y cobranzas

```text
Ventas y cobranzas                   HAY UNA DIFERENCIA

Vendido             $ 3.000.000,00
Cobrado             $ 2.300.000,00
Diferencia             $ 700.000,00
Cobrado                       76,7%

Tus registros muestran $700.000 más vendidos que cobrados.
Eso no prueba por sí solo mora ni pérdida: puede haber diferencias
de período, anticipos u otras situaciones que necesitan revisión.
```

### Resultado de Margen real

Resultado principal primero.

Luego:

```text
Qué incluí
Qué no estaba informado
Qué conviene revisar
```

No obligar al usuario a abrir detalles para descubrir qué significa el número principal.

---

# 7. Journey de falta de datos

No usar una página genérica de bloqueo para todos los casos.

La estructura depende de la pregunta elegida.

Ejemplo margen:

```text
Margen real

Necesito un dato más para calcularlo

Encontré ventas, pero no encontré costos suficientes.

Para calcular el margen necesito poder relacionar las ventas
con sus costos.

Podés:
[Subir otro Excel]
[Revisar otro análisis]
```

Ejemplo descuento no confirmado:

```text
Margen real

Lo dejamos pendiente

No pude calcular el margen porque todavía no sabemos si la columna
Descuento representa porcentaje o dinero.

No hice ninguna suposición.

[Volver a intentarlo]
[Ver mis análisis]
```

`FAIL_CLOSED` permanece intacto; sólo cambia la traducción.

---

# 8. Mis análisis / Casos

Nombre visible preferido:

```text
Mis análisis
```

No `Casos recientes` como concepto primario para un dueño.

Vista:

```text
Margen real
cafeteria_julio.xlsx
16 ago 2026 · Resultado listo
[Ver resultado]

Ventas y cobranzas
ventas_agosto.xlsx
16 ago 2026 · Hay una diferencia
[Ver resultado]
```

Metadata técnica como case_id puede existir en detalle secundario, no como objeto principal de navegación.

Estados:

```text
Resultado listo
Necesito un dato más
Necesita tu revisión
En curso
```

---

# 9. Conciliación bancaria — journey propio

No se incrusta como detalle colapsado debajo del upload de otro análisis.

Debe ser un instrumento de primer nivel cuando esté habilitado.

Recorrido:

```text
Conciliación bancaria
→ explicar los dos archivos
→ subir extracto bancario
→ subir registro interno
→ mostrar qué columnas encontró en cada uno
→ confirmar dudas
→ mostrar coincidencias candidatas
→ revisión humana
→ resumen
→ workpaper
```

Pantalla de carga:

```text
Conciliación bancaria
¿Qué movimientos coinciden y cuáles necesitan revisión?

1. Extracto bancario
[Seleccionar archivo]

2. Tus registros
[Seleccionar archivo]

[Comparar archivos]
```

Mesa de revisión sólo aparece después de esa preparación simple.

---

# 10. Sistema de estados UX

Estados visibles canónicos:

```text
RESULTADO LISTO
HAY UNA DIFERENCIA
NECESITO UN DATO MÁS
NECESITA TU REVISIÓN
EN CURSO
```

Regla:

`RESULTADO PARCIAL` sólo se usa cuando la pregunta principal elegida realmente no pudo responderse por completo.

No se usa porque existan análisis secundarios no calculados.

No se usa `BLOQUEADO` salvo que exista un bloqueo operativo real que el usuario deba conocer.

---

# 11. Lenguaje y glosario de interfaz

## Términos empresariales visibles

```text
Ventas
Cobranzas
Margen
Costo
Descuento
Flujo de caja
Saldo inicial
Ingresos
Egresos
Saldo de caja proyectado
Cuentas por cobrar
Tiempo promedio de cobro
Activo corriente
Pasivo corriente
Cobertura de corto plazo
Conciliación bancaria
Extracto bancario
```

## Términos internos no visibles

```text
sold_vs_collected_gap
net_margin_real
working_capital
projected_closing_cash_balance
dso
current_ratio
semantic role
question_id
sheet_ref
column_ref
bounded outcome
```

Los identificadores internos sólo pueden aparecer en superficies de soporte/diagnóstico no destinadas al cliente.

---

# 12. Visual system revisado

Se conserva del `SERVICE_1_ENTERPRISE_VISUAL_SYSTEM_V1`:

- paleta papel / tinta / verde PymIA;
- alta legibilidad numérica;
- reglas y bordes como estructura;
- ausencia de gradients/glassmorphism/startup cards;
- tipografía sobria;
- tablas reales cuando el contenido es tabular;
- estados con texto, no sólo color;
- responsive y accesibilidad.

Se elimina de la experiencia primaria:

- estética de expediente como metáfora dominante;
- `CASE / REF / EVIDENCE` visible por sistema;
- numeración de instrumento como encabezado principal;
- metadata técnica persistente en todas las pantallas;
- “mesa de operaciones” como lenguaje que el usuario debe aprender;
- vocabulario de auditoría cuando no corresponde al producto vendido.

Nueva dirección:

```text
PYMIA — ANÁLISIS EMPRESARIAL CLARO
```

Visualmente serio.
Semánticamente empresarial.
Operativamente simple.

---

# 13. Componentes UI canónicos

La reimplementación no debe volver a construir cada pantalla con HTML aislado.

Componentes conceptuales:

```text
AppShell
AnalysisChooser
AnalysisGuide
FilePicker
FileSummary
UnderstandingSummary
DetectedDatum
ConfirmationQuestion
ResultHeader
PrimaryResult
ResultExplanation
OptionalExpansion
DataUsedDisclosure
LimitsDisclosure
ActionBar
AnalysisHistory
ReconciliationFilePair
ReconciliationReviewTable
```

Cada componente tiene una responsabilidad visual y semántica única.

---

# 14. State model de presentación

La UI trabaja con estados de presentación explícitos, derivados del estado real existente:

```text
CHOOSE_ANALYSIS
AWAITING_FILE
READING_FILE
UNDERSTANDING_READY
NEEDS_CONFIRMATION
READY_TO_CALCULATE
RESULT_READY
NEEDS_MORE_DATA
REQUIRES_REVIEW
SAVED
```

Estos estados no sustituyen P6/P7/P8/P10.

Son una traducción de presentación.

Regla:

```text
runtime state → presentation state → UI
```

Nunca:

```text
UI inventa autoridad → runtime
```

---

# 15. Arquitectura de implementación

El rediseño debe reemplazar el crecimiento por parches dentro de `service_1_assisted_web_v1.py`.

Objetivo de presentación:

```text
service_1_assisted_web_v1.py
    → controla HTTP / sesiones / llamadas existentes

presentation layer
    → compone páginas y componentes

CSS único de Servicio 1
    → sistema visual coherente
```

Propuesta de archivos de presentación:

```text
pymia/smartpyme/service_1_ui_v1.py
pymia/smartpyme/templates/service_1/
    shell.html
    login.html
    choose_analysis.html
    upload.html
    understanding.html
    confirmation.html
    result.html
    needs_more_data.html
    analyses.html
    reconciliation_upload.html
    reconciliation_review.html
pymia/smartpyme/static/service_1_v1.css
```

Si el runtime actual no permite templates externos sin aumentar riesgo, la primera migración puede mantener render server-side en Python, pero debe usar funciones/componentes coherentes en `service_1_ui_v1.py` y dejar `service_1_assisted_web_v1.py` como controlador.

No crear una segunda raíz productiva.
No crear parser.
No mover cálculos.
No cambiar endpoints funcionales salvo que una ruta puramente de presentación sea estrictamente necesaria y no cambie autoridad.

---

# 16. Estrategia de migración sin parches

## Corte UI-1 — Presentation foundation

```text
crear capa de presentación
crear shell y design tokens
crear componentes base
sin cambiar comportamiento
```

## Corte UI-2 — Single-source journeys

Migrar juntos:

```text
Ventas y cobranzas
Margen real
Flujo de caja
```

Incluye:

```text
choose
upload
understanding
confirmation
result
needs-more-data
```

No migrar pantalla por pantalla en commits independientes.

## Corte UI-3 — History / reentry

```text
Mis análisis
reapertura
estados consistentes
```

## Corte UI-4 — Reconciliation journey

```text
carga doble
comprensión
confirmación
review table
resultado/workpaper
```

Después de UI-4, retirar renderers legacy que queden físicamente sin callers.

---

# 17. Acceptance UX

El rediseño no se acepta por “se ve mejor”.

Se acepta si un usuario nuevo puede responder, sin explicación externa:

```text
1. ¿Qué análisis estoy eligiendo?
2. ¿Qué debería contener mi Excel?
3. ¿Qué encontró PymIA?
4. ¿Qué me está preguntando y por qué?
5. ¿Cuál es mi resultado principal?
6. ¿Qué no pudo calcular?
7. ¿Eso invalida mi resultado o sólo permite ampliarlo?
8. ¿Qué puedo hacer después?
```

Criterios concretos:

```text
NO internal jargon in primary UX
NO dead-end screen without next action
NO generic FALTA INFORMACIÓN when primary result exists
NO No disponible cards for optional analyses
NO hidden requirement discovered after several screens if it can be explained before upload
NO multi-question wall when questions can be sequential
NO duplicate headings describing the same state
NO technical metadata competing with the business result
```

---

# 18. Acceptance técnica

Debe permanecer intacto:

```text
ONE_CANONICAL_PRODUCT_ROOT
NO_LLM_RUNTIME_AUTHORITY
NO_SECOND_XLSX_PARSER
FAIL_CLOSED
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION
```

Verificación por corte:

```text
journey focal correspondiente
architecture baseline
real browser journey
```

No full suite como gate repetitivo de cada corte de presentación.

La aceptación final debe incluir navegador real desktop y mobile.

---

# 19. Definición de terminado

Servicio 1 tendrá una interfaz coherente cuando exista un solo lenguaje y una sola estructura de interacción desde login hasta resultado:

```text
EMPRESA
→ PREGUNTA DE NEGOCIO
→ ARCHIVO ADECUADO
→ COMPRENSIÓN VISIBLE
→ DUDA MATERIAL
→ RESULTADO PRINCIPAL
→ AMPLIACIÓN / LÍMITES / ENTREGA
```

No habrá pantallas heredadas con modelos mentales distintos dentro del mismo recorrido.

Este blueprint sustituye la estrategia de corrección visual incremental como criterio rector del próximo rediseño de Servicio 1.
