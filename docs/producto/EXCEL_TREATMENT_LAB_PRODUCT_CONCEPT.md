# Excel Treatment Lab Product Concept

## Estado

```text
Documento: EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md
Tipo: PRODUCT_CONCEPT
Estado: CONCEPT_READY
Runtime impact: NONE
Code impact: NONE
Autoriza FIRST_AID_ENTRYPOINT_V1: NO
```

## Propósito

Definir `Excel Treatment Lab` como concepto de producto dentro del universo PymIA y como puerta `FIRST_AID` para capturar, curar y estructurar evidencia basada en Excel sin convertir esa fuente en el ingreso conceptual único del caso.

Este documento no autoriza runtime, contratos, tests ni implementación por sí solo.

Toda capacidad derivada requiere:

```text
archivo rector → contrato mínimo → test de aceptación → implementación focal → evidencia → checkpoint o ledger.
```

Este documento queda subordinado a `LIVE_DOCUMENT_PRIORITY_MAP.md`, especialmente a la regla producto vs runtime.

Este documento no implementa `FIRST_AID_ENTRYPOINT_V1`.

---

## 1. Tesis central

```text
Excel Treatment Lab no es un Excel Reader.
Excel Treatment Lab no es una macro.
Excel Treatment Lab no es BI genérico.
Excel Treatment Lab no es diagnóstico completo.
```

Excel Treatment Lab es una cámara de descompresión entre el caos administrativo del dueño y la estructura computable de PymIA.

Opera en `Nivel 1 / FIRST_AID`, con ficha mínima, entrega de valor inmediato y señal proporcional al nivel de servicio.

---

## 2. Rol

Excel Treatment Lab debe entenderse simultáneamente como:

```text
puerta FIRST_AID
sensor administrativo
tratamiento de evidencia Excel
generador de evidencia estructurada
disparador de pregunta provocadora
alimentador de OCF
```

Su misión no es agotar el análisis de la empresa, sino capturar una fuente concreta, volverla inteligible y producir una salida útil que pueda alimentar el caso.

---

## 3. Entrada típica

Excel Treatment Lab debe poder nacer desde pedidos como:

```text
"Mirame este Excel."
"Tengo esta planilla hecha un desastre."
"Ordename este stock."
"Decime qué productos dejan plata."
"Sacame algo en limpio."
"No sé qué estoy mirando."
```

Estas frases no habilitan diagnóstico pleno. Habilitan una intervención acotada sobre evidencia concreta.

---

## 4. Relación con Anamnesis Taxonómica Mínima

La regla canónica de PymIA sigue siendo:

```text
organismo/taxonomía → dolor → evidencia
```

Por lo tanto:

- Excel Treatment Lab no reemplaza la Anamnesis Taxonómica Mínima.
- Excel Treatment Lab no trata el Excel como ingreso conceptual único.
- En `Nivel 1` se permite ficha mínima del `10–20%` para entregar valor inmediato sobre una fuente concreta.
- Esa ficha mínima no anula la necesidad posterior de contexto taxonómico, dolor declarado y continuidad del caso.

Lectura correcta:

```text
Excel Treatment Lab puede empezar sobre una fuente.
PymIA no debe terminar reducido a esa fuente.
```

---

## 5. Relación con OrganizationalCaseFile

Excel Treatment Lab no reemplaza la `OrganizationalCaseFile`.

La OCF es el sustrato acumulativo; Excel Treatment Lab es un sensor que inyecta evidencia.

Regla doctrinal:

```text
La OCF es el sustrato acumulativo.
Excel Treatment Lab es un sensor que inyecta evidencia.
```

Eso implica:

- la OCF conserva continuidad, contexto, hipótesis, incógnitas y trazabilidad progresiva;
- Excel Treatment Lab agrega señales, evidencia curada y preguntas siguientes;
- el laboratorio Excel no completa por sí solo la ficha completa del caso.

---

## 6. Fases funcionales

Excel Treatment Lab debe pensarse en las siguientes fases:

```text
1. Intake mínimo
2. Triage del archivo
3. Desinfección
4. Normalización semántica
5. Pregunta socrática ante ambigüedad
6. Enriquecimiento
7. Mini-dashboard / resumen operativo
8. Inyección a OCF
9. Pregunta provocadora
```

Estas fases describen producto. No autorizan aún contratos técnicos ni runtime.

---

## 7. Intake mínimo

El intake mínimo de `FIRST_AID` debe registrar lo suficiente para no tratar el archivo como objeto aislado:

- fuente recibida;
- motivo o pedido declarado por el dueño;
- contexto mínimo disponible;
- nivel de ambigüedad;
- estado tentativo del archivo;
- siguiente decisión permitida.

La ficha mínima puede ser incompleta, pero debe evitar la ilusión de que el Excel explica por sí solo a la empresa.

---

## 8. Triage del archivo

Excel Treatment Lab debe intentar clasificar la forma probable del archivo como:

```text
ventas
stock
compras
gastos
caja
extracto bancario
lista de precios
dump de sistema
control interno
mixto
desconocido
```

El triage no confirma verdad de negocio. Sólo orienta el tratamiento posterior.

---

## 9. Desinfección

Operaciones permitidas:

```text
detectar encabezados reales
normalizar fechas
convertir texto numérico
identificar hojas útiles
separar totales intermedios
detectar celdas combinadas
detectar columnas ambiguas
```

Límites obligatorios:

```text
no sobrescribir original
no ejecutar macros
no asumir columnas ambiguas sin preguntar
no procesar archivos enormes sin advertencia
```

La desinfección busca volver legible la fuente, no reemplazar criterio ni evidencia faltante.

---

## 10. Normalización semántica

Excel Treatment Lab debe mapear columnas hacia variables candidatas como:

```text
fecha
producto
sku
cantidad
precio
costo
cliente
canal
stock
gasto
proveedor
medio de pago
```

Además debe distinguir con claridad:

```text
dato observado
dato declarado
dato inferido
dato ambiguo
dato faltante
```

La normalización semántica no debe esconder incertidumbre. Debe volverla visible.

---

## 11. Pregunta socrática ante ambigüedad

Cuando el archivo no permita resolver significado de columnas, hojas o valores, el siguiente paso correcto no es inventar estructura sino abrir pregunta socrática breve y accionable.

Ejemplos de ambigüedad que justifican pregunta:

- columna que podría ser precio o costo;
- hoja que mezcla ventas y stock;
- extracto que no indica cuentas;
- totales intermedios que contaminan el detalle;
- nomenclatura interna incomprensible.

Regla:

```text
Si la evidencia no alcanza, se pregunta.
Si la evidencia sigue sin alcanzar, se bloquea.
No se diagnostica.
```

---

## 12. Enriquecimiento

Sólo si existe suficiencia mínima de evidencia, pueden emerger señales como:

```text
margen estimado
alerta de margen
rotación
días sin venta
concentración SKU
ticket promedio
ventas por canal
stock inmovilizado
productos trampa
```

Regla operativa:

```text
Todo cálculo debe declarar datos usados y faltantes.
Si falta evidencia, se genera pregunta, no diagnóstico.
Null es sagrado.
```

El enriquecimiento debe ser proporcional al nivel `FIRST_AID`, no una promesa de comprensión total.

---

## 13. Salida owner-facing

Excel Treatment Lab puede producir entregables como:

```text
Excel curado
tabla limpia
hoja Hallazgos_PymIA
mini-dashboard
resumen ejecutivo breve
alertas puntuales
pregunta provocadora
```

Toda salida debe distinguir explícitamente:

```text
hallazgo puntual respaldado
hipótesis no confirmada
dato faltante
siguiente pregunta
```

La salida útil no es un dashboard bonito sin continuidad. Debe dejar rastro y próxima acción.

---

## 14. Inyección a OrganizationalCaseFile

Excel Treatment Lab debe poder aportar a la OCF señales como:

```text
evidence_refs
variables_detectadas
available_variables
missing_variables
open_unknowns
candidate_formulas
candidate_hypotheses
next_questions
service_depth_signal
```

Regla:

```text
Excel Treatment Lab no completa la OCF.
Sólo agrega evidencia y señales proporcionales al nivel FIRST_AID.
```

---

## 15. Relación con niveles de servicio

Excel Treatment Lab debe quedar alineado con el modelo vigente de profundidad:

```text
FIRST_AID:
una fuente, valor inmediato, ficha mínima 10–20%.

DETERMINISTIC_DIAGNOSIS:
requiere cruce de fuentes o suficiencia de variables.

ORGANIZATIONAL_LAB:
requiere continuidad, múltiples evidencias y ficha amplia.
```

Esto evita dos errores:

- inflar `FIRST_AID` hasta convertirlo en diagnóstico total;
- subestimar el valor de una intervención puntual sobre evidencia concreta.

---

## 16. Pregunta provocadora

Excel Treatment Lab debe cerrar con una pregunta provocadora sólo cuando exista señal real en los datos.

Protocolo:

```text
No vender.
No diagnosticar de más.
No prometer solución total.
Provocar sólo si hay señal real en datos.
```

Ejemplos:

```text
"Te ordené la planilla, pero aparece una señal: tus productos más vendidos no parecen ser los más rentables. ¿Querés que miremos margen real?"

"Hay stock sin movimiento visible. ¿Querés que calculemos cuánto capital está inmovilizado?"

"Veo ventas, pero no costos suficientes. ¿Tenés lista de costos o facturas de compra para estimar margen?"
```

La pregunta provocadora no cierra el caso. Abre el siguiente paso permitido.

---

## 17. Límites doctrinales obligatorios

```text
1. No es Excel Reader genérico, BI ni macro.
2. No ejecuta macros del usuario.
3. No sobrescribe el archivo original.
4. No procesa archivos enormes sin advertencia explícita.
5. No asume columnas ambiguas sin pregunta socrática.
6. No diagnostica sin suficiencia de evidencia.
7. No convierte hipótesis en hallazgos.
8. No inventa datos faltantes.
9. Todo Excel curado incluye hallazgo provocador y pregunta siguiente.
10. El conocimiento de dominio es enchufable: SectorPack, FormulaPack, PathologyPack, CatalogPack.
```

---

## 18. Riesgos y antipatrones

Riesgos a evitar:

```text
Excel Reader genérico
dashboard efímero sin continuidad
macro disfrazada
diagnóstico sin evidencia
onboarding infinito
BI genérico
hardcode sectorial
```

Lectura de antipatrones:

- si sólo limpia celdas, no es PymIA;
- si promete diagnóstico total con una sola fuente, rompe el modelo de suficiencia;
- si no alimenta OCF, produce valor efímero sin memoria;
- si mete conocimiento sectorial hardcodeado en vez de packs, contamina la frontera futura.

---

## 19. Criterio de cierre

Este documento queda listo si permite abrir después:

```text
FIRST_AID_ENTRYPOINT_V1
```

Pero declara explícitamente:

```text
Este documento no implementa FIRST_AID_ENTRYPOINT_V1.
```

Su función es dejar fijado el concepto de producto, sus límites, su relación con anamnesis, OCF y service depth, y el tipo de frente técnico que podría abrirse después.
