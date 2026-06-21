# PYMIA Product Universe and Service Depth Model — FINAL

## Estado

```text
Documento: PYMIA_PRODUCT_UNIVERSE_AND_SERVICE_DEPTH_MODEL_FINAL.md
Tipo: arquitectura de producto
Estado: FINAL_DRAFT
Propósito: definir la coherencia estructural del universo PymIA
Runtime impact: NONE
Code impact: NONE
```

---

# 1. Veredicto

```text
TESIS_SOLIDA_CON_RIESGOS
```

La tesis de producto es sólida porque evita una falsa dicotomía:

```text
ficha vs microservicio
```

PymIA no es solamente una ficha clínica organizacional.  
PymIA no es solamente una colección de microservicios.

PymIA debe entenderse como un **ecosistema operativo para PyMEs basado en profundidad variable de servicio**.

Su espectro va desde:

```text
1. Microservicios independientes de primeros auxilios.
2. Caja de herramientas administrativa + diagnósticos determinísticos.
3. Laboratorio organizacional completo / sistema operativo PyME impulsado por IA + dueño.
```

La `OrganizationalCaseFile` no compite con los microservicios.  
La `OrganizationalCaseFile` es el **sustrato acumulativo** del sistema.

Puede activarse en tres intensidades:

```text
Nivel 1 → ficha mínima
Nivel 2 → ficha parcial
Nivel 3 → ficha completa
```

No toda interacción requiere completar la ficha completa.  
Pero toda interacción valiosa debe poder dejar evidencia, variables, hipótesis, hallazgos, cálculos, incógnitas o preguntas siguientes dentro de la ficha.

---

# 2. Definición estructural de PymIA

PymIA es un **motor de inferencia organizacional para PyMEs**.

Convierte:

```text
datos imperfectos
lenguaje cotidiano del dueño
archivos desordenados
evidencia operacional
conectores autorizados
preguntas emergentes
```

en:

```text
variables organizacionales
fórmulas aplicables
hipótesis trazables
cuellos de botella
diagnósticos determinísticos
preguntas siguientes
interpretaciones progresivas
```

PymIA no exige que la PyME ya esté ordenada para poder ayudarla.  
Su función es precisamente transformar fricción administrativa en claridad matemática y operativa.

## PymIA no es

```text
ERP
CRM
BI genérico
Excel reader
chatbot administrativo
consultoría tradicional embotellada
SaaS administrativo genérico
```

## PymIA sí es

```text
un ecosistema de profundidad variable para entender, ordenar y diagnosticar organizaciones PyME
```

---

# 3. Modelo estructural

La arquitectura de producto debe pensarse como un continuo:

```text
Microservicio puntual
→ Toolkit diagnóstico
→ Laboratorio organizacional completo
```

Todos los niveles comparten la misma lógica interna:

```text
dato
→ variable
→ relación
→ fórmula
→ resultado
→ hipótesis
→ cuello de botella
→ pregunta siguiente
→ acción / reporte / decisión
```

La diferencia entre niveles no es la lógica.  
La diferencia es la **profundidad de evidencia, integración y continuidad**.

---

# 4. Capas del producto

## 4.1 Capa de interacción y captura

Canales posibles:

```text
WhatsApp
Telegram
chat web
app conversacional
voz/audio
botones
texto libre
carga de Excel
carga de PDF
carga de documentos
autorización de conectores/plugins
```

Regla:

```text
El dueño no completa formularios: conversa, sube evidencia y autoriza conectores.
```

## 4.2 Capa de microservicios

Motores acotados de una sola responsabilidad:

```text
Excel Treatment Lab
Mercado Libre Audit
Stock Quick Check
Margin Quick Check
Cash Gap Quick Check
Sales Channel Audit
Mini Dashboard Generator
```

Cada microservicio debe poder:

```text
resolver un problema puntual
generar evidencia estructurada
alimentar la OrganizationalCaseFile
emitir una pregunta provocadora
```

## 4.3 Capa de inferencia y diagnóstico

Incluye:

```text
motor de fórmulas
detección de anomalías
suficiencia de evidencia
activación de hipótesis
clasificación de cuellos de botella
interpretación determinística acotada
```

No debe confundir hipótesis con hallazgos.

## 4.4 Capa de estado y persistencia

Aquí vive la `OrganizationalCaseFile`.

No como formulario.  
No como expediente muerto.  
Sino como grafo de estado epistémico.

## 4.5 Capa de reconciliación de evidencia

Capa necesaria para evitar contradicciones no gobernadas.

Función:

```text
comparar fuentes
detectar contradicciones
distinguir bruto vs neto
distinguir declarado vs observado
distinguir histórico vs vigente
marcar conflictos
pedir aclaración
actualizar confianza
aplicar decaimiento temporal
```

Ejemplo:

```text
Excel Lab dice: margen bruto 30%
Mercado Libre Audit dice: margen neto post-comisiones 4%
Banco dice: caja insuficiente
```

PymIA no debe mostrar tres verdades desconectadas.  
Debe reconciliarlas:

```text
"Tu Excel mide margen bruto.
Mercado Libre muestra margen neto después de comisiones, envío y publicidad.
No son datos necesariamente contradictorios: miden niveles distintos.
Para saber rentabilidad real necesitamos cruzar ambos."
```

## 4.6 Capa de conocimiento enchufable

El conocimiento de dominio no debe ensuciar el kernel.

Debe entrar como:

```text
FormulaPack
PathologyPack
SectorPack
KnowledgePack
CatalogPack
ChannelPack
MarketplacePack
```

Doctrina:

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

---

# 5. Tres niveles de servicio

## Nivel 1 — Primeros Auxilios PyME

### Entrada típica

```text
"Tengo este Excel hecho un desastre."
"Revisame Mercado Libre."
"Ordename este stock."
"Decime qué productos dejan plata."
"Armame un tablero rápido."
"Sacame algo en limpio."
```

### Promesa de valor

```text
Te resuelvo este micro-problema ahora y te dejo una señal clara de lo que está pasando.
```

### Profundidad de ficha

```text
mínima: 10%–20%
```

Casilleros activados:

```text
identidad mínima
dolor puntual
archivo/fuente
tipo de evidencia
variables detectadas
hallazgo puntual
pregunta siguiente
```

### Evidencia requerida

Una sola fuente:

```text
Excel
PDF
captura
plugin autorizado
texto/audio del dueño
```

### Microservicios activados

```text
Excel Treatment Lab
ML Quick Audit
Stock Quick Check
Margin Quick Check
Mini Dashboard Generator
```

### Tipo de salida

```text
Excel curado
mini-dashboard
alerta puntual
tabla limpia
hallazgo provocador
archivo enriquecido
```

### Riesgo

Convertirse en:

```text
macro de Excel
herramienta gratuita aislada
scraper de marketplace
dashboard efímero sin continuidad
```

### Regla de escalamiento

Nivel 1 no escala con un botón comercial.  
Escala con una **pregunta provocadora**.

Ejemplo:

```text
"Te limpié el Excel. Pero encontré que tus productos más vendidos no parecen ser los más rentables. ¿Querés ver cuáles te están comiendo la caja?"
```

---

## Nivel 2 — Diagnóstico Determinístico / Caja de Herramientas

### Entrada típica

```text
"Vendo pero no me queda plata."
"No sé si gano."
"Mercado Libre me vende mucho pero no sé si me conviene."
"La caja no me cierra."
"Tengo mucho stock parado."
```

### Promesa de valor

```text
Te explico el cuello de botella de este subsistema con datos, fórmulas y evidencia suficiente.
```

### Profundidad de ficha

```text
parcial: 40%–60%
```

Casilleros activados:

```text
familia empresarial
canales de venta
modelo operativo
variables organizacionales
fórmulas candidatas
evidencias cruzadas
hipótesis activas
resultados calculados
faltantes de evidencia
```

### Evidencia requerida

Cruce de dos o más fuentes:

```text
ventas + costos
ventas + stock
Mercado Libre + costos
banco + ventas
stock + compras
```

### Microservicios activados

Orquestación de 2 o 3 microservicios:

```text
Excel Lab + Margin Check
Mercado Libre Audit + Sales Channel Audit
Stock Check + Cash Gap Check
Sales Channel Audit + Margin Check
```

### Tipo de salida

```text
diagnóstico determinístico acotado
mapa de cuello de botella
reporte de margen/caja/stock/canal
fórmulas aplicadas
evidencia insuficiente declarada
próximas preguntas
```

### Riesgo

Convertirse en:

```text
consultoría genérica
opinador IA
diagnóstico sin evidencia
reporte bonito sin matemática
```

### Qué no debe prometer

```text
reestructuración completa
rentabilidad global sin evidencia
solución estratégica total
predicciones sin datos
```

---

## Nivel 3 — Laboratorio Organizacional Completo

### Entrada típica

```text
"Quiero ordenar mi empresa."
"Quiero profesionalizar el negocio."
"Quiero entender por qué la empresa depende de mí."
"Quiero preparar la empresa para crecer."
"Quiero trabajar con PymIA como laboratorio completo."
```

### Promesa de valor

```text
Hacemos tu empresa progresivamente computable, interpretable y gobernable.
```

### Profundidad de ficha

```text
completa: 80%–100%
```

Casilleros activados:

```text
historia del caso
taxonomía completa
canales
modelo operativo
múltiples evidencias
variables
fórmulas
patologías
hipótesis longitudinales
resultados
interpretaciones
incógnitas
decisiones
evolución temporal
```

### Evidencia requerida

```text
múltiples fuentes
históricos
plugins
owner answers
documentos
validaciones cruzadas
replay de casos
actualizaciones periódicas
```

### Tipo de salida

```text
laboratorio organizacional
sistema operativo PyME asistido
seguimiento longitudinal
alertas
simulaciones
evolución de hipótesis
decisiones asistidas
```

### Riesgo

Convertirse en:

```text
ERP
CRM
sistema de facturación
gestor administrativo pesado
consultoría infinita
```

### Qué no debe prometer

```text
reemplazar contador
reemplazar ERP
automatizar toda la empresa
gobernar sin dueño
diagnóstico total sin evidencia viva
```

---

# 6. Tres entradas de cliente

## Entrada A — “Necesito resolver algo ahora”

### Lenguaje del dueño

```text
"Mirame este Excel."
"Está todo desordenado."
"Decime qué vendo más."
"Ordename esto."
"Revisame Mercado Libre."
```

### Canal probable

```text
WhatsApp
Telegram
web drag-and-drop
chat rápido
```

### Fricción tolerable

```text
casi cero
```

### Datos mínimos

```text
archivo
captura
autorización plugin
mensaje corto
```

### Entrega

```text
archivo curado
mini-dashboard
alerta puntual
hallazgo provocador
```

### Escalamiento

Mediante pregunta provocadora:

```text
"Encontré algo que puede explicar tu problema. ¿Querés que lo investiguemos?"
```

---

## Entrada B — “Necesito entender un problema”

### Lenguaje del dueño

```text
"No sé si gano."
"No entiendo la caja."
"El stock me está matando."
"Mercado Libre vende pero no sé si deja plata."
```

### Canal probable

```text
chat conversacional
audio
sesión guiada
```

### Fricción tolerable

```text
media
```

Puede responder 4–7 preguntas si percibe que el sistema entiende su dolor.

### Datos mínimos

```text
dolor declarado
taxonomía básica
canal dominante
1–2 evidencias
```

### Entrega

```text
diagnóstico determinístico acotado
mapa del subsistema afectado
fórmulas aplicadas
faltantes explícitos
```

### Escalamiento

Cuando el subsistema muestra conexión con otro:

```text
"El problema de caja parece venir de stock y plazos de cobro. Para confirmarlo necesitamos mirar el flujo completo."
```

---

## Entrada C — “Necesito ordenar mi empresa”

### Lenguaje del dueño

```text
"Quiero profesionalizar."
"Quiero que la empresa no dependa de mí."
"Quiero ordenar la operación."
"Quiero tomar mejores decisiones."
```

### Canal probable

```text
web app
sesión asistida
copilotaje
laboratorio recurrente
```

### Fricción tolerable

```text
alta
```

### Datos mínimos

```text
onboarding completo
múltiples evidencias
plugins
históricos
validaciones sucesivas
```

### Entrega

```text
Organizational Operating Lab
ficha completa
seguimiento
diagnósticos longitudinales
decisiones asistidas
```

---

## 6.4 Pregunta madre de entrada / No-oráculo

PymIA no debe comportarse como un oráculo.

No debe asumir mágicamente qué profundidad de servicio necesita el dueño.

Su función es reducir tinieblas e incertidumbre mediante:

```text
preguntas explícitas
opciones proporcionales
evidencia mínima
límites de suficiencia
```

La entrada correcta no es:

```text
PymIA interpreta por intuición qué necesita el dueño.
```

La entrada correcta es:

```text
PymIA pregunta qué tipo de ayuda necesita hoy.
```

## Pregunta madre

```text
¿Qué necesitás resolver hoy?
```

Opciones iniciales:

```text
1. Primeros Auxilios
   Tengo algo puntual para ordenar o revisar ahora.

2. Problema específico / diagnóstico sectorial
   Tengo un problema más complejo que quiero entender.

3. Estructura completa de la empresa
   Quiero analizar y ordenar la empresa como sistema.
```

## Traducción de opciones

### Opción 1 — Primeros Auxilios

Para casos como:

```text
Mirame este Excel.
Ordename esta planilla.
Revisame este stock.
Sacame algo en limpio.
```

Promesa:

```text
Revisión puntual, rápida y de baja fricción.
```

No promete diagnóstico completo.

### Opción 2 — Problema específico / diagnóstico sectorial

Para casos como:

```text
No sé si gano.
La caja no me cierra.
Mercado Libre vende pero no sé si deja plata.
El stock me está matando.
```

Promesa:

```text
Entender un cuello de botella con evidencia suficiente.
```

Puede activar fórmulas, cruces y diagnóstico acotado si la evidencia alcanza.

### Opción 3 — Estructura completa

Para casos como:

```text
Quiero ordenar mi empresa.
Quiero profesionalizar.
Quiero que la empresa no dependa de mí.
```

Promesa:

```text
Laboratorio organizacional completo.
```

Activa una ficha más profunda y una mirada longitudinal.

## Secuencia correcta

```text
pregunta inicial
→ opción elegida por el dueño
→ evidencia mínima
→ profundidad de servicio
→ respuesta proporcional
```

## Regla de diseño

```text
Service depth no debe ser adivinación.
Debe combinar:
1. elección explícita del dueño;
2. evidencia disponible;
3. señales del lenguaje;
4. límites de suficiencia.
```

La elección explícita del dueño manda primero.

Las señales de lenguaje ayudan, pero no reemplazan la pregunta inicial.

## Frase rectora

```text
PymIA no es un oráculo.
PymIA es un sistema operativo para reducir tinieblas e incertidumbre mediante preguntas, evidencia y opciones proporcionales.
```

---

# 7. Rol de la OrganizationalCaseFile

## Qué es

La `OrganizationalCaseFile` es el **grafo de estado epistémico** de una PyME.

Guarda no sólo datos, sino el estado de conocimiento del sistema sobre la empresa.

Debe distinguir:

```text
dato declarado
dato observado
dato inferido
dato calculado
dato confirmado
dato contradictorio
dato vencido
hipótesis
hallazgo
incógnita
pregunta pendiente
```

## Qué no es

```text
formulario
CRM
ERP
expediente administrativo muerto
reporte final
base de datos de campos planos
```

## Estados posibles de casilleros

```text
EMPTY
UNKNOWN
DECLARED
INFERRED
OBSERVED
CALCULATED
CONFIRMED
CONFLICTED
REJECTED
STALE
NEEDS_EVIDENCE
NEEDS_REFRESH
INTERPRETED
```

## Regla central

```text
Null es un estado válido.
```

PymIA debe preferir decir:

```text
"No sé tu margen real porque faltan comisiones, envíos y costos de reposición."
```

antes que inventar o rellenar con promedios sectoriales engañosos.

## Profundidad según nivel

| Nivel | Estado de ficha | Uso |
|---|---|---|
| Nivel 1 | mínima | registrar evidencia puntual y hallazgo |
| Nivel 2 | parcial | mapear subsistema y diagnosticar |
| Nivel 3 | completa | sostener laboratorio organizacional |

---

# 8. Reconciliación de evidencia

## Problema

Las PyMEs no tienen una sola verdad ordenada.

Pueden existir datos contradictorios:

```text
Excel del dueño
reporte del contador
Mercado Libre
banco
sistema de gestión
stock físico
WhatsApp
```

## Riesgo

Sin reconciliación, PymIA puede caer en “estado esquizofrénico”:

```text
una fuente dice una cosa
otra fuente dice otra
el reporte muestra ambas sin gobernarlas
```

## Solución

Incorporar una capa de reconciliación:

```text
source_type
source_confidence
measurement_scope
time_validity
metric_definition
conflict_status
reconciliation_question
```

## Jerarquía orientativa de confianza

```text
DECLARED_BY_OWNER < EXCEL_UPLOADED < SYSTEM_EXPORT < PLUGIN_OBSERVED < BANK_OBSERVED < CALCULATED_AND_CONFIRMED
```

Esta jerarquía no es absoluta.  
Debe considerar contexto y definición de métrica.

Ejemplo:

```text
El Excel puede medir margen bruto.
Mercado Libre puede medir margen neto post-comisión.
No son contradicción si miden cosas distintas.
```

## Pregunta de confrontación socrática

Cuando aparece conflicto, PymIA no acusa. Pregunta:

```text
"Tu Excel muestra margen bruto del 30%, pero Mercado Libre muestra margen neto del 4% después de comisiones, envío y publicidad. ¿Puede ser que tu Excel no incluya esos costos?"
```

---

# 9. Decaimiento temporal / Data Decay

La verdad organizacional caduca.

Una auditoría de stock o Mercado Libre de hace 90 días puede no representar la realidad actual.

## Necesidad

La OCF debe incluir vigencia temporal:

```text
observed_at
calculated_at
valid_until
confidence_decay
refresh_required
```

## Ejemplos

```text
stock auditado hace 60 días → baja confianza
margen ML hace 90 días → NEEDS_REFRESH
diagnóstico de caja hace 45 días → revisar vigencia
precios de lista hace 120 días → STALE
```

## Regla

PymIA no debe presentar como vigente una verdad vencida.

Debe decir:

```text
"Este diagnóstico se calculó con datos de hace 70 días. Puede haber cambiado. ¿Actualizamos la evidencia?"
```

---

# 10. Microservicios iniciales

## 10.1 Excel Treatment Lab

Función:

```text
recibir Excel caótico
detectar forma
limpiar
normalizar
enriquecer con fórmulas PyME
generar mini-dashboard
devolver Excel curado
alimentar OCF
```

Límites:

```text
no ejecutar macros
no sobrescribir original
no procesar archivos enormes sin advertencia
no asumir columnas ambiguas sin preguntar
no diagnosticar sin suficiencia
```

Salida típica:

```text
archivo_curado_pymIA.xlsx
hoja Hallazgos_PymIA
mini-dashboard
pregunta provocadora
```

## 10.2 Mercado Libre Audit

Función:

```text
auditar canal Mercado Libre con autorización explícita
leer ventas, stock, publicaciones, comisiones, envíos, publicidad, reputación, devoluciones y cancelaciones
calcular rentabilidad real del canal
detectar dependencia y erosión de margen
```

Reglas:

```text
read-only por defecto
autorización explícita
revocación inmediata
no modificar precios
no modificar stock
no usar datos para otros fines
```

## 10.3 Stock Quick Check

Función:

```text
detectar stock inmovilizado
rotación baja
SKU dormidos
capital atrapado
riesgo de quiebre
```

## 10.4 Margin Quick Check

Función:

```text
calcular margen por producto, canal o proyecto
detectar productos trampa
distinguir margen bruto de margen neto
```

## 10.5 Cash Gap Quick Check

Función:

```text
detectar descalce entre cobro, pago y stock
mapear presión de capital de trabajo
```

## 10.6 Sales Channel Audit

Función:

```text
comparar rentabilidad por canal
detectar dependencia
comparar local físico vs WhatsApp vs Mercado Libre vs ecommerce
```

## 10.7 Mini Dashboard Generator

Función:

```text
visualización efímera
top anomalías
pareto
alertas
tablas simples
resumen ejecutivo de chat
```

---

# 11. Mapa microservicio → ficha

## Excel Treatment Lab

| Elemento | Actualización |
|---|---|
| Evidencia | tabla normalizada |
| Variables | ventas, unidades, ticket, SKU, fechas |
| Fórmulas | Pareto, concentración SKU, margen estimado si hay costo |
| Hipótesis | dependencia de productos, desorden administrativo |
| OCF | evidencia_disponible, madurez_admin, variables_detectadas |
| Pregunta siguiente | “¿Tenés costos para calcular margen real?” |

## Mercado Libre Audit

| Elemento | Actualización |
|---|---|
| Evidencia | órdenes, comisiones, ads, reputación, stock |
| Variables | take rate, margen neto, cancelaciones, devoluciones |
| Fórmulas | rentabilidad post-comisión, ROAS, concentración canal |
| Hipótesis | ML se come el margen, dependencia marketplace |
| OCF | canal_dominante, dependencia_marketplace, margen_real_ml |
| Pregunta siguiente | “¿Tus precios en local son iguales a ML?” |

## Stock Quick Check

| Elemento | Actualización |
|---|---|
| Evidencia | stock, ventas, antigüedad |
| Variables | rotación, días de inventario, capital inmovilizado |
| Fórmulas | rotación, días de stock |
| Hipótesis | stock dormido, caja atrapada |
| OCF | inventario, cuello_stock, capital_inmovilizado |
| Pregunta siguiente | “¿Querés ver qué stock conviene liquidar?” |

## Margin Quick Check

| Elemento | Actualización |
|---|---|
| Evidencia | precio, costo, comisiones |
| Variables | margen bruto, margen neto, contribución |
| Fórmulas | margen, contribución marginal |
| Hipótesis | producto trampa, precio insuficiente |
| OCF | rentabilidad, productos_riesgo |
| Pregunta siguiente | “¿Faltan envíos o comisiones en este cálculo?” |

## Cash Gap Quick Check

| Elemento | Actualización |
|---|---|
| Evidencia | cobros, pagos, stock |
| Variables | plazo cobro, plazo pago, días stock |
| Fórmulas | ciclo de conversión de caja |
| Hipótesis | descalce financiero, caja rota |
| OCF | ciclo_caja, faltantes_financieros |
| Pregunta siguiente | “¿Cobrás después de pagar proveedores?” |

## Sales Channel Audit

| Elemento | Actualización |
|---|---|
| Evidencia | ventas por canal, costos por canal |
| Variables | margen por canal, dependencia, comisión |
| Fórmulas | margen neto por canal, concentración |
| Hipótesis | canal dominante no rentable |
| OCF | canales, dependencia, rentabilidad_canal |
| Pregunta siguiente | “¿Qué canal te deja más plata real?” |

---

# 12. Mercado Libre y ecommerce

## Regla doctrinal

```text
Canal de venta = dimensión taxonómica primaria.
```

Mercado Libre no es sólo un canal.  
En muchas PyMEs es un ecosistema económico paralelo.

Afecta:

```text
margen
stock
caja
rotación
comisiones
envíos
publicidad
reputación
cancelaciones
devoluciones
dependencia
```

## Pregunta que resuelve

```text
¿Mi negocio es rentable o sólo estoy trabajando para el marketplace?
```

## Datos del plugin

```text
órdenes
publicaciones
precios
stock publicado
comisiones
costo de envío asumido
publicidad / ads
devoluciones
cancelaciones
reputación
tiempos de entrega
```

## Evidencia generada

```text
PLUGIN_OBSERVED
```

con alta confianza, siempre respetando alcance y autorización.

## Fórmulas habilitadas

```text
margen neto Mercado Libre
take rate marketplace
ROAS
rentabilidad post-comisión
rotación por canal
concentración de ventas por canal
costo comercial total
tasa de devolución
tasa de cancelación
```

## Hipótesis posibles

```text
Mercado Libre erosiona margen
publicidad no rentable
stock mal sincronizado
producto estrella destruye valor
dependencia excesiva del marketplace
envíos se comen la rentabilidad
cancelaciones afectan salud del canal
```

## Límites

```text
read-only por defecto
autorización explícita
revocación inmediata
no modificar precios sin orden explícita
no modificar stock sin orden explícita
no vender datos
no usar información fuera del caso
```

---

# 13. Excel Treatment Lab

## Rol

El Excel Treatment Lab es la puerta de entrada de primeros auxilios más natural de PymIA.

No debe ser un Excel Reader genérico.

Debe ser la cámara de descompresión entre:

```text
caos administrativo del dueño
→ estructura computable de PymIA
```

## Fases

### 1. Triage

Detecta la forma del archivo:

```text
ventas
stock
compras
gastos
caja
extracto bancario
dump de sistema
lista de precios
control interno
desconocido
```

### 2. Desinfección

```text
desagrupar celdas combinadas
normalizar fechas
convertir texto a número
eliminar totales intermedios
detectar encabezados reales
identificar hojas útiles
```

### 3. Normalización

Mapea columnas:

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
```

### 4. Pregunta socrática ante ambigüedad

Ejemplo:

```text
"Veo una columna llamada Precio, pero no sé si es precio de venta, costo o lista sin IVA. ¿Qué representa?"
```

### 5. Enriquecimiento

Agrega columnas útiles:

```text
margen estimado
alerta de margen
días sin venta
rotación
concentración SKU
canal probable
```

### 6. Mini-dashboard

```text
top ventas
top rentabilidad
productos trampa
stock inmovilizado
anomalías
```

### 7. Inyección a OCF

Todo hallazgo queda registrado como:

```text
evidencia
variable
hipótesis
pregunta siguiente
```

---

# 14. Diferenciación producto

## PymIA no es Excel Lab

Excel Lab es una puerta de entrada.  
No es el producto completo.

## PymIA no es Mercado Libre Audit

ML Audit es una ruta investigativa.  
No es el sistema completo.

## PymIA no es ficha clínica solamente

La ficha es cerebro acumulativo.  
No es una experiencia de onboarding obligatoria.

## PymIA no es dashboard

El dashboard muestra.  
PymIA interpreta, pregunta y calcula.

## PymIA no es consultor mágico

No opina sin evidencia.  
No convierte hipótesis en hallazgos.

## PymIA es profundidad variable

```text
primeros auxilios
→ diagnóstico determinístico
→ laboratorio organizacional
```

---

# 15. Doctrina de coherencia

## 15.1 Toda interacción útil debe poder dejar evidencia

Si una interacción no deja evidencia, variable, hipótesis, hallazgo o pregunta, probablemente es ruido.

## 15.2 Toda herramienta es sensor

Ningún microservicio es fin en sí mismo.

```text
Excel Lab = sensor de datos administrativos
ML Audit = sensor de canal marketplace
Stock Check = sensor de inventario
Cash Gap = sensor financiero operativo
```

## 15.3 No toda interacción requiere ficha completa

La ficha se activa proporcionalmente al nivel de servicio.

## 15.4 La evidencia es soberana

Una hipótesis cae ante evidencia observada contradictoria.

## 15.5 Null es sagrado

No saber es mejor que inventar.

## 15.6 Toda hipótesis debe distinguirse de hallazgo

```text
hipótesis = posible explicación
hallazgo = explicación respaldada por evidencia suficiente
```

## 15.7 Todo cálculo debe declarar suficiencia

No hay fórmula válida sin declarar datos usados y faltantes.

## 15.8 Provocar, no vender

El paso de Nivel 1 a Nivel 2 debe nacer de un hallazgo, no de un upsell.

## 15.9 El conocimiento es enchufable

Sector, fórmula y patología entran por packs.

## 15.10 El dueño conversa, sube evidencia y autoriza conectores

No completa formularios eternos.

---

# 16. Riesgos y antipatrones

## Excel Reader genérico

Riesgo:

```text
el usuario usa PymIA sólo para limpiar planillas
```

Mitigación:

```text
todo Excel curado incluye hallazgo y pregunta provocadora
```

## Estado esquizofrénico

Riesgo:

```text
fuentes contradictorias sin reconciliación
```

Mitigación:

```text
Evidence Reconciliation Layer
```

## Onboarding infinito

Riesgo:

```text
pedir demasiados datos antes de dar valor
```

Mitigación:

```text
valor en Nivel 1
ficha proporcional
```

## Consultor mágico

Riesgo:

```text
opinar sin evidencia
```

Mitigación:

```text
suficiencia explícita
hipótesis separadas de hallazgos
```

## Hardcodear sectores

Riesgo:

```text
meter gastronomía, ferretería, textil o servicios en el kernel
```

Mitigación:

```text
Domain Packs / Sector Packs
```

## Convertirse en ERP

Riesgo:

```text
registrar todo el pasado en vez de diagnosticar el presente
```

Mitigación:

```text
PymIA no es sistema de carga operativa; usa evidencia para inferencia
```

## Convertirse en CRM

Riesgo:

```text
centrarse en contactos/clientes y gestión comercial genérica
```

Mitigación:

```text
PymIA se centra en física económica y organizacional
```

---

# 17. Lo que falta resolver

## 17.1 Motor de reconciliación de evidencia

Definir:

```text
conflict types
source ranking
metric scope
confidence update
reconciliation prompts
```

## 17.2 Data decay / TTL

Definir:

```text
cuánto dura una verdad
cuándo pedir actualización
cómo marcar STALE
cómo recalcular confianza
```

## 17.3 Pregunta provocadora

Diseñar el protocolo:

```text
cuándo provocar
cuándo callar
cómo no sonar vendedor
cómo escalar de Nivel 1 a 2
```

## 17.4 Packs sectoriales

Definir si los packs son:

```text
contratos de reglas
catálogos
motores determinísticos
plantillas de preguntas
packs de fórmulas
packs de patologías
```

## 17.5 Economía y permisos de plugins

Especialmente Mercado Libre:

```text
autorización
revocación
costos API
almacenamiento
privacidad
alcance read-only
```

---

# 18. Roadmap documental recomendado

## Prioridad 1 — OrganizationalCaseFile V1 TaskSpec

```text
ORGANIZATIONAL_CASE_FILE_V1_TASKSPEC.md
```

Debe definir:

```text
estructura de grafo epistémico
tipos de nodos
estados de casilleros
fuentes
confianza
conflictos
TTL
relación con replay JSONL
```

## Prioridad 2 — Excel Treatment Lab Product Concept

```text
EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md
```

Debe definir:

```text
triage
limpieza
normalización
enriquecimiento
límites
archivo curado
hallazgo provocador
inyección a OCF
```

## Prioridad 3 — Mercado Libre Audit Plugin Concept

```text
MERCADO_LIBRE_AUDIT_PLUGIN_CONCEPT.md
```

Debe definir:

```text
datos que lee
permisos
evidencia generada
variables
fórmulas
hipótesis
privacidad
revocación
```

## Prioridad 4 — Service Depth Model TaskSpec

```text
SERVICE_DEPTH_MODEL_TASKSPEC.md
```

Debe definir:

```text
niveles
triggers de escalamiento
fricción permitida
salidas por nivel
criterios de profundidad de ficha
```

## Prioridad 5 — Evidence Reconciliation Model

```text
EVIDENCE_RECONCILIATION_MODEL.md
```

Debe definir:

```text
conflictos entre fuentes
jerarquía de confianza
preguntas socráticas de reconciliación
diferencia bruto/neto
vigencia temporal
```

---

# 19. Decisiones doctrinales finales

```text
PymIA opera en un espectro de profundidad, no en un único modo de uso.
```

```text
La ficha no es un formulario: es el grafo epistémico vivo de la organización.
```

```text
Los microservicios son puertas de entrada y sensores, no productos desconectados.
```

```text
El producto entrega valor inmediato sin renunciar a acumulación de inteligencia.
```

```text
El canal de venta es taxonomía primaria.
```

```text
Mercado Libre es una ruta investigativa propia.
```

```text
Excel Treatment Lab no es un Excel Reader: es la cámara de descompresión del caos administrativo.
```

```text
Toda hipótesis debe declarar evidencia, confianza, vigencia y faltantes.
```

```text
Null es sagrado.
```

```text
El conocimiento de dominio es enchufable.
```

---

# 20. Cierre

PymIA debe poder empezar con una tarea pequeña y terminar construyendo un laboratorio organizacional completo.

Ese es el núcleo del producto:

```text
primeros auxilios
→ diagnóstico determinístico
→ sistema operativo organizacional
```

El dueño puede entrar por cualquier punto:

```text
resolver algo ahora
entender un problema
ordenar la empresa
```

Pero PymIA mantiene coherencia porque todo se traduce al mismo lenguaje interno:

```text
evidencia
→ variable
→ fórmula
→ hipótesis
→ cuello de botella
→ pregunta siguiente
→ decisión
```

La `OrganizationalCaseFile` es el tejido conectivo de ese universo.

No obliga a completar todo.  
No frena el valor inmediato.  
No reemplaza los microservicios.  
Los absorbe, los ordena y los convierte en comprensión acumulativa.

Ese es el producto.
