# SMARTPYME_SEMANTIC_DIALECTIC_PHASE

Estado: CANÓNICO  
Fecha: 2026-05-26  
HEAD base: 0299274

---

## Estado y propósito

Este documento define la **fase semántico-dialéctica** previa al análisis SmartPyme.

Cubre el método conversacional que transforma el relato crudo del dueño en estructura clínica-operacional contrastable.

No es un formulario. No es un chatbot libre. Es una dialéctica controlada entre:

- lenguaje crudo del dueño
- reformulación del sistema
- validación del usuario
- extracción de síntomas
- hipótesis abiertas
- preguntas de desambiguación
- evidencia requerida

---

## Qué problema resuelve

Resuelve la tensión entre:

1. **"Primero escuchar lenguaje crudo"** (anamnesis abierta)
2. **"Primero encuadrar organismo"** (taxonomía antes de síntoma)

La síntesis operativa es: **entrelazado, no secuencial puro**.

El dueño habla primero. El sistema captura sin interpretar. Reformula para validar. Confirma con el usuario. Extrae síntomas. Abre hipótesis. Desambigua. Recién entonces encuadra organismo. Recién entonces pide evidencia. Recién entonces sugiere clasificación.

---

## Secuencia de la fase

```text
Captura mínima estructural por selectores (si el canal lo permite)
→ Relato libre del usuario por texto/audio
→ Conservación literal del relato
→ Reformulación del sistema
→ Confirmación/corrección del usuario
→ Extracción de síntomas candidatos
→ Hipótesis abiertas
→ Preguntas de desambiguación
→ Encuadre de organismo (si falta)
→ Pedido de evidencia
→ Clasificación ejecutable sugerida
```

Cada paso es una micro-fase. No se saltean. No se fusionan prematuramente.

---

## Entrada híbrida: selectores estructurales + relato libre

La fase semántico-dialéctica se complementa con un microcuestionario estructural inicial que usa botones/selectores para capturar contexto rápido del organismo.

**Principio:** los selectores sirven para ubicar el organismo. El texto/audio sirve para entender el síntoma.

### Reglas

- Los selectores **no reemplazan** la conversación.
- Los selectores **reducen fricción** y mejoran contexto.
- El usuario **no debe sentir** que está llenando un ERP.
- Máximo recomendado: **3 a 5 selectores** antes del relato libre.
- Si el usuario llega con audio/texto espontáneo, **no interrumpirlo** con formulario; capturar primero y luego pedir contexto faltante.

### Ejemplo A — Bot con botones

El sistema inicia con selectores y luego abre la narrativa:

```text
Sistema:
"Para ubicar rápido tu negocio, marcame estas opciones y después
contame con tus palabras qué te preocupa."

Botones:
- Canal de venta: Local / Mayorista / Mercado Libre / Ecommerce / Mixto
- Stock: Sí / No / Informal
- Herramienta: Excel / Sistema / Cuaderno / Varios

Luego:
"Ahora contame qué querés entender o qué te preocupa.
Podés escribirlo o mandarlo por audio."
```

### Ejemplo B — Usuario manda audio primero

El sistema no debe cortar con formulario. Debe responder:

```text
Sistema:
"Recibí tu explicación. Antes de pedirte documentos, necesito ubicar
dos datos rápidos: ¿vendés por local, Mercado Libre, ecommerce,
mayorista o mixto? ¿Manejás stock?"
```

---

## Objetos conceptuales

### RawInboundEvent

Entrada cruda desde cualquier canal. Registra sin interpretar.

### OwnerUtterance

Frase textual del dueño. Se preserva sin reescribir.

Ejemplo:
```text
"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY"
"Paulita tiene un Excel con el stock"
"RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY por producto"
```

### OwnerClaim

Dolor declarado por el dueño, estructurado como objeto clínico.

Metadata mínima:
- claim literal
- intensidad percibida
- temporalidad
- causalidad percibida
- impacto operacional
- área afectada

### BusinessContext

Contexto del organismo PyME:
- rubro
- naturaleza económica
- dominio operacional
- tipo de organismo

### SemanticSignal

Indicador semántico detectado en narrativa cruda.

Taxonomía:
- `lenguaje_no_tecnico`
- `intuicion_sin_evidencia`
- `urgencia_emocional`
- `incertidumbre_financiera`
- `dependencia_del_dueno`
- `delegacion_fragil`
- `caos_normalizado`

### OperationalSymptom

Síntoma operacional contrastable derivado del claim.

Ejemplo:
```text
Claim: "Vendemos mucho pero no queda plata."
Síntoma operacional: incertidumbre de rentabilidad
```

### HypothesisCandidate

Hipótesis inicial sin cerrar.

Ejemplo:
```text
Síntoma: incertidumbre de rentabilidad
Hipótesis v0: margen erosionado, fuga operativa o tensión de caja
```

### ClarificationQuestion

Pregunta de desambiguación. No induce. No ofrece menú cerrado.

### EvidenceNeed

Documento o dato necesario para contrastar hipótesis.

### EvidenceRequest

Pedido formal de evidencia al dueño.

### ReadyToAnalyze

Estado final de la fase. Evidencia suficiente. Clasificación sugerida. Listo para laboratorio.

---

## Estados

### RAW_CAPTURED

Entrada cruda registrada. Todavía no se interpretó.

### ORGANISM_CONTEXT_MISSING

Falta encuadrar el tipo de organización antes de continuar.

### OWNER_CLAIM_REFORMULATED

El sistema reformuló el dolor. Pendiente confirmación del usuario.

### WAITING_OWNER_CONFIRMATION

El sistema espera que el dueño confirme o corrija la reformulación.

### NEEDS_DISAMBIGUATION

El síntoma es ambiguo. Se requieren preguntas de clarificación.

### HYPOTHESIS_OPEN

Hipótesis iniciales formuladas. No cerradas.

### NEEDS_EVIDENCE

Hipótesis abierta, pero falta documentación concreta para contrastar.

### EVIDENCE_REQUESTED

Pedido de evidencia emitido al dueño. Pendiente recepción.

### READY_FOR_TAXONOMIC_ROUTING

Evidencia suficiente para sugerir clasificación ejecutable.

### BLOCKED_INSUFFICIENT_CONTEXT

Falta evidencia mínima crítica. El sistema bloquea con claridad.

---

## Reglas de conversación

### Regla 1: Una pregunta por turno

Por defecto, una sola pregunta por turno. La más informativa posible. Nunca diagnostica: investiga.

### Regla 2: No diagnóstico prematuro

El sistema no afirma datos operacionales sin evidencia real. Diferencia explícitamente entre:
- señal
- hipótesis
- estimación orientativa
- diagnóstico confirmado

### Regla 3: Lenguaje de dueño PyME

Claro, operacional, entendible. Sin tecnicismos innecesarios. Sin arquitectura interna. Sin "IA mágica".

Preferir:
```text
"Con estos datos, la señal principal es…"
"Todavía lo tomo como lectura preliminar."
"Lo primero que revisaría es…"
"Para mirarlo con números necesito…"
```

Evitar:
```text
"Estado epistemológico"
"Hipótesis inicial prioritaria"
"nodo de hipótesis"
"pipeline de admisión"
"veredicto definitivo"
```

### Regla 4: No mezclar contexto de empresa con síntoma

El tipo de organismo es contexto. El dolor es síntoma. No se fusionan prematuramente.

### Regla 5: No mezclar hipótesis con clasificación ejecutable

La hipótesis es abierta. La clasificación ejecutable se sugiere solo al final, tras evidencia.

---

## Preguntas mayéuticas iniciales

Preguntas de apertura que no inducen:

```text
Contame, qué es lo que más te preocupa del negocio ahora mismo?
Dónde sentís que el negocio te está fallando hoy?
Si tuvieras que señalar un problema urgente, cuál sería?
Qué pasó?
Cómo te diste cuenta?
Desde cuándo?
```

Estas preguntas:
- permiten narrativa abierta;
- no ofrecen menú cerrado;
- buscan lenguaje crudo;
- no diagnostican.

---

## Reformulación del dolor

El sistema reformula el relato para validar comprensión.

Ejemplo:

```text
Entrada: "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY, Paulita tiene un Excel con el stock."

Reformulación:
"Esto entendí que querés revisar:
1. No sabés con claridad si ganás por producto.
2. Te preocupa tener stock inmovilizado.

Para contrastar esto voy a necesitar documentación inicial."
```

Esta reformulación cumple tres funciones:
- valida que el sistema entendió al dueño;
- transforma relato en objetos operacionales;
- habilita el pedido de evidencia.

---

## Confirmación/corrección del usuario

El dueño confirma o corrige la reformulación.

Si confirma:
```text
"Exacto, eso es lo que me preocupa."
→ El sistema avanza a extracción de síntomas y apertura de hipótesis.
```

Si corrige:
```text
"No, el stock no me preocupa tanto. Lo que me preocupa es que no sé si los precios están bien."
→ El sistema ajusta el claim y reformula nuevamente.
```

El sistema no avanza sin confirmación explícita o implícita del usuario.

---

## Extracción de síntomas

Cada dolor confirmado se transforma en síntoma operacional.

Ejemplo:

```text
Claim confirmado: "RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY por producto."
Síntoma operacional: incertidumbre de rentabilidad
Área afectada: margen, precios
Temporalidad: no declarada (pendiente desambiguación)
Intensidad percibida: alta (por lenguaje de urgencia)
```

Metadata mínima por síntoma:
- claim literal
- intensidad percibida
- temporalidad
- causalidad percibida
- impacto operacional
- área afectada
- evidencia requerida
- nivel de confianza inicial

---

## Hipótesis abiertas

El sistema genera hipótesis iniciales sin cerrarlas.

Ejemplo:

```text
Síntoma: incertidumbre de rentabilidad
Hipótesis v0:
- margen erosionado
- fuga operativa
- tensión de caja
- costos desactualizados
- precios de venta no alineados a costo
```

Las hipótesis son candidatas. No son diagnóstico. No son hallazgo.

---

## Preguntas de desambiguación

Preguntas concretas para reducir ambigüedad:

```text
Desde cuándo notaste este problema?
Qué impacto te está generando hoy en plata o en tiempo?
Qué proceso puntual está más afectado hoy: ventas, caja, stock, compras u otro?
Tenés ventas del último trimestre aunque sea en Excel o PDF?
```

Estas preguntas deben precisar:
- intensidad
- frecuencia
- temporalidad
- impacto operacional
- causalidad percibida

---

## Pedido de evidencia

La evidencia se pide según hipótesis, no como lista genérica.

Ejemplos:

```text
Si el dolor es margen:
→ lista de precios
→ costos unitarios
→ ventas recientes

Si el dolor es stock:
→ hoja de stock
→ movimientos
→ ventas por producto

Si el dolor es caja:
→ cierre de caja
→ extractos
→ cuentas por cobrar/pagar

Si el dolor es proveedores duplicados:
→ maestro de proveedores (Excel con columnas: proveedor, cuit, razon_social)
```

El archivo puede llegar como Excel, PDF, imagen, captura, CSV, export de plataforma o texto estructurado.

---

## Límites: qué NO hace esta fase

Esta fase NO:
- diagnostica;
- calcula margen, caja ni rentabilidad;
- interpreta documentos estructurados;
- gestiona canal, sesión ni historial de mensajes;
- invoca APIs externas;
- ejecuta laboratorio;
- genera reporte final;
- sugiere clasificación ejecutable sin evidencia.

Esta fase SOLO:
- captura relato crudo;
- reformula para validar;
- extrae síntomas;
- abre hipótesis;
- desambigua;
- pide evidencia;
- prepara para routing/análisis.

---

## Relación con SMARTPYME_INTERROGATION_TAXONOMY.md

`SMARTPYME_INTERROGATION_TAXONOMY.md` define la capa taxonómica (el "qué"):
- taxonomía de señales
- taxonomía de síntomas
- taxonomía de dominios
- taxonomía de evidencias
- estados del interrogatorio
- clasificación ejecutable sugerida

`SMARTPYME_SEMANTIC_DIALECTIC_PHASE.md` define la capa semántico-dialéctica (el "cómo"):
- método conversacional
- reformulación del dolor
- confirmación del usuario
- extracción de síntomas
- hipótesis abiertas
- preguntas de desambiguación

Ambos documentos son complementarios. No se solapan. No se contradicen.

---

## Relación con runtime real

### Clasificaciones vigentes

El runtime SmartPyme MVP local soporta actualmente:
- `excel_diagnostic`: diagnóstico financiero tabular genérico
- `supplier_duplicate_check`: detección de proveedores duplicados y normalización de maestro

### Sin routing automático asumido

Este documento no asume que existe routing automático por columnas. La clasificación puede ser explícita vía CLI (`--classification`).

### Sin HTML asumido

Este documento no asume que existe `--html-out`. El reporte HTML es capacidad opcional, no obligatoria.

### Mapeo evidencia → clasificación

Ejemplo de mapeo sano:

```text
Columnas: proveedor, cuit, razon_social
→ supplier_duplicate_check

Columnas: monto, fecha_factura, concepto
→ excel_diagnostic
```

Si el usuario pasa clasificación explícita distinta, el sistema respeta pero puede advertir inconsistencia.

---

## Criterio de salida hacia análisis

La fase semántico-dialéctica queda cerrada cuando:

1. El relato crudo fue capturado.
2. La reformulación fue confirmada por el usuario.
3. Los síntomas fueron extraídos y estructurados.
4. Las hipótesis iniciales fueron formuladas.
5. Las preguntas de desambiguación fueron respondidas (o el sistema acepta incertidumbre).
6. La evidencia requerida fue identificada.
7. La evidencia fue aportada (o el sistema bloquea con claridad).
8. La clasificación ejecutable fue sugerida y confirmada.

Cierre no significa diagnóstico. Significa que el sistema sabe qué analizar y con qué evidencia.

---

## Ejemplos

### Ejemplo 1: "No me cierra la plata"

**Frase cruda:**
```text
"No me cierra la plata."
```

**Reformulación:**
```text
"Entiendo que sentís que los números no te dan.
Esto puede significar varias cosas:
- que los ingresos no alcanzan para cubrir gastos;
- que hay fugas que no estás viendo;
- que los precios no están alineados con los costos.

Antes de analizar números, necesito entender mejor qué tipo de negocio estamos mirando.
¿Es un comercio, una fábrica, una empresa de servicios u otro tipo de organización?"
```

**Pregunta de confirmación:**
```text
"¿Es eso lo que te preocupa, o hay algo más específico que notaste?"
```

**Síntoma candidato:**
```text
incertidumbre de rentabilidad o tensión de caja
```

**Hipótesis abierta:**
```text
- margen erosionado
- fuga operativa
- caja insuficiente
- costos desactualizados
```

**Próxima pregunta:**
```text
"¿Desde cuándo notaste esto? ¿Fue gradual o de golpe?"
```

**Evidencia probable:**
```text
- ventas del período
- costos o facturas de compra
- lista de precios vigente
- extracto/caja
```

**Qué NO debe concluir todavía:**
```text
- "Tu problema es de margen."
- "Tenés una fuga de caja."
- "Necesitás bajar costos."
```

---

### Ejemplo 2: "Vendo pero no me queda nada"

**Frase cruda:**
```text
"Vendo pero no me queda nada."
```

**Reformulación:**
```text
"Entiendo que vendés, pero sentís que el resultado final no es el que esperabas.
Esto puede ser porque:
- los márgenes por producto son muy chicos;
- los costos fijos son muy altos;
- los precios de venta están desactualizados;
- hay una mezcla de productos que no te conviene.

Antes de analizar números, necesito entender mejor qué tipo de negocio estamos mirando.
¿Es un comercio, una fábrica, una empresa de servicios u otro tipo de organización?"
```

**Pregunta de confirmación:**
```text
"¿Es eso lo que te preocupa, o hay algo más específico que notaste?"
```

**Síntoma candidato:**
```text
incertidumbre de rentabilidad
```

**Hipótesis abierta:**
```text
- margen erosionado
- costos fijos desproporcionados
- precios de venta no alineados a costo
- mezcla de productos no rentable
```

**Próxima pregunta:**
```text
"¿Qué proceso puntual está más afectado hoy: ventas, caja, stock, compras u otro?"
```

**Evidencia probable:**
```text
- ventas del período
- costos o facturas de compra
- lista de precios vigente
- estructura de costos fijos
```

**Qué NO debe concluir todavía:**
```text
- "Tu problema es que vendés productos de bajo margen."
- "Tenés que subir precios."
- "Necesitás reducir costos fijos."
```

---

### Ejemplo 3: "Tengo proveedores repetidos"

**Frase cruda:**
```text
"Tengo proveedores repetidos."
```

**Reformulación:**
```text
"Entiendo que sospechás que tenés proveedores cargados más de una vez en tu sistema o planilla.
Esto puede causar:
- pagos duplicados;
- dificultad para negociar volumen;
- desorden administrativo.

Antes de analizar el archivo, necesito entender mejor qué tipo de negocio estamos mirando.
¿Es un comercio, una fábrica, una empresa de servicios u otro tipo de organización?"
```

**Pregunta de confirmación:**
```text
"¿Es eso lo que te preocupa, o hay algo más específico que notaste?"
```

**Síntoma candidato:**
```text
desorden de maestro de proveedores
```

**Hipótesis abierta:**
```text
- proveedores duplicados por CUIT
- proveedores duplicados por nombre similar
- variaciones de razón social no normalizadas
- falta de proceso de alta de proveedores
```

**Próxima pregunta:**
```text
"¿Tenés un Excel o planilla con el maestro de proveedores? Necesito columnas como: proveedor, CUIT, razón social."
```

**Evidencia probable:**
```text
- maestro de proveedores (Excel con columnas: proveedor, cuit, razon_social)
```

**Qué NO debe concluir todavía:**
```text
- "Tenés 15 proveedores duplicados."
- "Estás pagando doble."
- "Necesitás un ERP."
```

---

### Ejemplo 4: "El Excel está imposible"

**Frase cruda:**
```text
"El Excel está imposible."
```

**Reformulación:**
```text
"Entiendo que tenés una planilla que se volvió difícil de manejar.
Esto puede ser porque:
- tiene demasiadas columnas o filas;
- hay datos inconsistentes o duplicados;
- falta estructura para analizar;
- hay fórmulas rotas o referencias cruzadas.

Antes de analizar el archivo, necesito entender mejor qué tipo de negocio estamos mirando.
¿Es un comercio, una fábrica, una empresa de servicios u otro tipo de organización?"
```

**Pregunta de confirmación:**
```text
"¿Es eso lo que te preocupa, o hay algo más específico que notaste?"
```

**Síntoma candidato:**
```text
caos documental operacional
```

**Hipótesis abierta:**
```text
- fragmentación operacional
- evidencia normalización necesaria
- falta de estructura para análisis
- dependencia manual excesiva
```

**Próxima pregunta:**
```text
"¿Qué información tiene ese Excel? ¿Ventas, costos, stock, proveedores, otra cosa?"
```

**Evidencia probable:**
```text
- el Excel en cuestión (cualquier formato)
```

**Qué NO debe concluir todavía:**
```text
- "Tu Excel está mal armado."
- "Necesitás un sistema."
- "Tenés que contratar a alguien para que lo ordene."
```

---

### Ejemplo 5: "Copio todo a mano"

**Frase cruda:**
```text
"Copio todo a mano."
```

**Reformulación:**
```text
"Entiendo que estás haciendo tareas manuales que te consumen tiempo.
Esto puede ser porque:
- no hay integración entre sistemas;
- falta automatización de procesos;
- la información está dispersa en múltiples fuentes;
- no hay un flujo de trabajo definido.

Antes de analizar el proceso, necesito entender mejor qué tipo de negocio estamos mirando.
¿Es un comercio, una fábrica, una empresa de servicios u otro tipo de organización?"
```

**Pregunta de confirmación:**
```text
"¿Es eso lo que te preocupa, o hay algo más específico que notaste?"
```

**Síntoma candidato:**
```text
improductividad operativa por dependencia manual
```

**Hipótesis abierta:**
```text
- dependencia manual excesiva
- falta de automatización
- fragmentación de fuentes de datos
- proceso no estandarizado
```

**Próxima pregunta:**
```text
"¿Qué proceso puntual estás haciendo a mano? ¿Cuánto tiempo te consume por día o por semana?"
```

**Evidencia probable:**
```text
- descripción del proceso
- planillas usadas
- capturas del flujo de trabajo
```

**Qué NO debe concluir todavía:**
```text
- "Necesitás un ERP."
- "Tenés que automatizar con Zapier."
- "Tu proceso es ineficiente."
```

---

## Documentos base consultados

- `docs/ingenieria_conversacional.PROTOCOLO_PRIMER_CONTACTO_v1.md`
- `docs/arquitectura/CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO.md`
- `docs/producto/protocolo-anamnesis-mvp.md`
- `docs/producto/capa-00-canal-entrada.md`
- `docs/producto/capa-01-admision-epistemologica.md`
- `docs/catalogo/anamnesis-y-catalogos.md`
- `docs/catalogo/primary_context_taxonomy.v1.json`
- `docs/contratos/contratos-clinicos-operacionales.md`
- `docs/contracts/pymia_first_clinical_interview_mcp_contract.md`
- `docs/ingenieria_conversacional.NORMATIVA_v1.md`
- `docs/ingenieria_conversacional.MAPA_INTEGRACION_v1.md`
- `docs/smartpyme/SMARTPYME_INTERROGATION_TAXONOMY.md`

---

## Restricciones preservadas

Este documento:
- no autoriza runtime nuevo;
- no autoriza MCP;
- no autoriza jobs ni workflows;
- no autoriza orquestación;
- no modifica código;
- no toca Hermes real;
- no toca producción;
- no toca secretos ni `.env`.

Solo establece método semántico-dialéctico canónico para futuros frentes de implementación controlada.
