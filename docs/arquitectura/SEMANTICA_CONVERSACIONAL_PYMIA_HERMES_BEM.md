# Doctrina de Semántica Conversacional: PymIA ↔ Hermes ↔ BEM

## Estado
Documento doctrinario canónico  
**Fecha:** Mayo 2026  
**Ámbito:** Arquitectura máster, interfaces de comunicación e ingesta de evidencia

---

## Propósito

Establecer la doctrina formal y la división epistemológica de responsabilidades en el ecosistema PymIA. Este documento unifica la visión del **Método Científico Clínico-Operacional** aplicado a la interacción con dueños de PyMEs, delimitando de forma estricta los roles de **PymIA**, **Hermes** y **BEM**.

---

## 1. Frases Canónicas de la Doctrina

La verdad en PymIA se rige por un conjunto inquebrantable de máximas que guían el flujo de datos y conversación:

* **PymIA no cree: contrasta.**
* **Hermes no supone: pregunta.**
* **BEM no diagnostica: extrae.**
* **El dueño no es invalidado: es escuchado, estructurado y contrastado.**
* **La hipótesis no es diagnóstico.**
* **La narrativa no es diagnóstico.**
* **El PDF parseado no es evidencia validada.**
* **El OCR no es verdad matemática.**

---

## 2. La Cuadríada de Responsabilidades

El flujo de información en el sistema clínico-operativo es un engranaje donde cada actor cumple una función especializada y subordinada al método de contraste.

```text
  [Dueño PyME] --------(Dolor/Narrativa)--------> [Hermes]
       ^                                             | (Symptom/Claim)
       | (Sugerencias/Pregunta Mayéutica)            v
  [PymIA (Kernel)] <---(Evidencia Normalizada)---- [BEM (Frontera)]
```

### Dueño PyME (La Expresión del Dolor)
El dueño de la empresa es el origen del caso operativo. Expresa el dolor de la organización, describe su contexto, expone su intuición y, de forma inevitable, sus propias contradicciones. Su voz no es un conjunto de datos ordenados; es una narrativa subjetiva que requiere ser asimilada sin ser juzgada.

### Hermes (El Sirviente Conversacional)
Hermes es el sirviente entre la computadora sorda/muda (**PymIA**) y la organización humana (**PyME**). Su función es escuchar de forma empática, menguar en favor de la expresión del dueño para no opacar su voz, traducir el relato sin deformar y realizar preguntas de rigor y de inteligencia mayéutica para precisar los síntomas declarados.

### BEM (Business Evidence Model - El Asistente de Extracción)
BEM es la frontera documental de apoyo y traducción física. Asiste al sistema extrayendo datos estructurados desde la evidencia cruda y compleja aportada por el usuario (ej. archivos Excel caóticos, imágenes o documentos PDF).

### PymIA (El Kernel Computacional)
PymIA es el único soberano del cómputo y de la decisión lógica. Recibe la evidencia normalizada, evalúa las fórmulas matemáticas contra el catálogo de patologías, valida las dimensiones de la taxonomía contable y decide el estado operativo del diagnóstico.

---

## 3. BEM como Frontera Documental de Apoyo

El Business Evidence Model (BEM) es una frontera **auxiliar y secundaria** de la arquitectura. Su rol es puramente operativo y carece de facultades clínicas o de diagnóstico.

* **BEM no es el kernel:** No contiene lógica de negocio ni reglas de evaluación de patologías. Su único propósito es normalizar formatos.
* **BEM no es el conversador:** No dialoga con el dueño PyME ni genera respuestas en lenguaje natural; es una capa de infraestructura física documental.
* **BEM no es verdad diagnóstica:** Que BEM logre parsear un archivo y extraer una matriz limpia no significa que esa información sea coherente o validada. PymIA es quien decide si la evidencia extraída aprueba los filtros de validación interna.
* **Dependencia decreciente:** A medida que el kernel de PymIA madura en sus capacidades directas de ingesta y heurísticas, la dependencia de BEM debe menguar. PymIA opera idealmente sobre datos contables y operacionales limpios; BEM solo asiste la extracción cuando la evidencia de origen es cruda o desordenada.

---

## 4. Hermes como Sirviente Conversacional

Hermes no es un agente de IA autónomo con voluntad propia ni un chatbot corporativo publicitario. **Hermes es un sirviente de la verdad computacional de PymIA.**

* **Puente de traducción:** Traduce la rigidez matemática de las métricas y hallazgos calculados por PymIA en un diálogo comprensible, sobrio y de autoridad tranquila para el dueño PyME, sin deformar la realidad de los números.
* **Pregunta sin suponer:** Ante la ambigüedad, Hermes no presupone ni completa "al aire" la información que falta; de forma mayéutica, pregunta al dueño para recolectar datos precisos.
* **Silencio en favor del dueño:** Hermes mengua y se adapta al lenguaje particular del dueño de la PyME, capturando sus contradicciones lógicas sin invalidar su perspectiva.
* **Prohibición de diagnóstico:** Hermes tiene estrictamente prohibido improvisar hipótesis, inventar findings, o recetar cursos de acción operacionales que no estén explícitamente fundamentados en el `OperationalAuditResult` provisto por PymIA.

---

## 5. El Ciclo Científico / Método Hipotético-Deductivo

La aproximación clínico-operativa de SmartPyme sigue rigurosamente las fases del método científico. El sistema nunca procesa documentación a ciegas; primero escucha, formula hipótesis, y prescribe la evidencia necesaria para su contrastación.

```text
 1. Observación (El dueño expresa síntomas operativos a Hermes)
       │
       ▼
 2. Formulación de Hipótesis (PymIA abre HypothesisNodes v0)
       │
       ▼
 3. Definición de Evidencia Requerida (El sistema prescribe qué datos faltan)
       │
       ▼
 4. Recolección de Evidencia (BEM o INTERNAL_FACT extraen los registros)
       │
       ▼
 5. Contrastación Científica (PymIA ejecuta fórmulas contra el Catálogo de Patologías)
       │
       ▼
 6. Consolidación del Estado Lógico (Se confirma o bloquea la patología en el Kernel)
       │
       ▼
 7. Nueva Pregunta / Acción (Hermes formula el siguiente paso de rigor)
```

1. **Observación:** El dueño PyME describe un problema operativo con su propio lenguaje.
2. **Hipótesis:** El sistema asimila el claim literal, lo tipifica en un síntoma objetivo (`SymptomNode`) y asocia hipótesis preliminares candidatas (`HypothesisNode` v0).
3. **Evidencia Requerida:** PymIA prescribe de forma exacta qué datos concretos se necesitan para contrastar la hipótesis, evitando listas de requerimientos excesivas.
4. **Recolección:** El usuario aporta la documentación física, que es procesada según su nivel de entropía a través de `INTERNAL_FACT` (directo local síncrono) o `BEM_AI` (extracción pesada).
5. **Contrastación:** El kernel de PymIA evalúa la veracidad, cuadre matemático y consistencia interna de los datos.
6. **Estado Lógico:** PymIA consolida el estado final en el `OperationalAuditResult` (marcando hallazgos como calculados, bloqueados por falta de datos o no aplicables).
7. **Nueva Pregunta:** Hermes retoma el control del diálogo utilizando el `pathology_routing_summary` ligero para sugerir las siguientes acciones u opciones interactivas de rigor.

---

## 6. Implicación de Seguridad para Archivos PDF e Imágenes

Los documentos visuales (PDFs escaneados, capturas de pantalla, remitos de pago, fotos de listados) siguen protocolos de seguridad y aislamiento muy estrictos:

* **Ruta de extracción auxiliar:** Los PDFs e imágenes ingresan obligatoriamente a través de la clasificación `BEM_AI`. Están categorizados como evidencia de alta entropía y pasan por capas de curaduría de bajo acoplamiento.
* **Nunca son diagnóstico directo:** Ninguna lectura semántica preliminar de un PDF por parte de una IA conversacional se considera diagnóstico consolidado.
* **Fuerza de candidatos:** Los outputs documentales extraídos por BEM_AI actúan únicamente como "evidencia candidata" en espera. Solo se asimilan en la verdad del laboratorio cuando PymIA los convalida, contrasta sus referencias cruzadas contra otras fuentes de datos del negocio y aprueba su incorporación al balance general del caso contable.
