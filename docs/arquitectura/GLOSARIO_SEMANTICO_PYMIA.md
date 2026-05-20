# Glosario Canónico de Arquitectura Semántica PymIA

## Estado
Documento canónico máster de referencia  
**Fecha:** Mayo 2026  
**Ámbito:** Arquitectura máster, glosario técnico, interfaces y enrutamiento

---

## Propósito

Este glosario define con precisión absoluta e inquebrantable cada término, rol y flujo conceptual del ecosistema **PymIA**. Actúa como la única fuente de verdad semántica para desarrolladores, analistas e ingenieros con el objetivo de evitar desalineaciones, acoplamientos prohibidos o desviaciones de la doctrina clínico-operacional.

---

### Dueño
* **Definición corta:** El origen subjetivo del caso de negocio; el ser humano que dirige la organización y experimenta los dolores de su gestión.
* **Qué puede hacer:** Expresar dolores, relatar contextos, aportar intuiciones de gestión, manifestar contradicciones operacionales y cargar documentación cruda.
* **Qué NO puede hacer:** Formular diagnósticos contables científicamente validados ni reescribir las reglas matemáticas del kernel.
* **Relación con otros componentes:** Es escuchado por **Hermes**, analizado taxonómicamente por **PymIA**, y contrastado mediante la evidencia normalizada por **BEM** o **INTERNAL_FACT**.

---

### PyME
* **Definición corta:** El organismo operativo real bajo análisis; la estructura de procesos, flujos de caja, stocks y compras que se busca sanar.
* **Qué puede hacer:** Generar evidencia física (planillas, facturas, transacciones) que reflejen su salud real de forma independiente de la percepción de su dueño.
* **Qué NO puede hacer:** Hablar o interactuar de forma directa; requiere de su dueño como intérprete inicial de sus síntomas.
* **Relación con otros componentes:** Sus datos duros alimentan los repositorios de ingesta y son el sustrato del **OperationalAuditResult**.

---

### Hermes
* **Definición corta:** El sirviente conversacional de PymIA; el conducto y adaptador traductor de lenguaje entre la computadora sorda/muda y las organizaciones humanas.
* **Qué puede hacer:** Escuchar empáticamente al dueño PyME, preguntar con rigor mayéutico sin suponer, menguar ante la voz del dueño para registrar contradicciones, y traducir la verdad matemática de PymIA a un diálogo natural comprensible.
* **Qué NO puede hacer:** Diagnosticar de forma autónoma, formular afirmaciones sin sustento grounded, recalcular variables matemáticas, o poseer dependencias con infraestructura pesada dentro del kernel.
* **Relación con otros componentes:** Traduce los inputs de texto de los usuarios para **PymIA** y asimila la superficie de **pathology_routing_summary** para guiar los siguientes pasos de la conversación.

---

### PymIA
* **Definición corta:** El kernel de cálculo y decisión lógica clínico-operativo de SmartPyme; la computadora lógica del negocio.
* **Qué puede hacer:** Evaluar el catálogo de patologías, calcular fórmulas contra métricas contables, validar la consistencia cruzada de la evidencia, emitir diagnósticos consolidados y gobernar la verdad del caso operativo.
* **Qué NO puede hacer:** Conversar de forma directa con el usuario, conocer de canales de mensajería (Telegram), o depender de SDKs de terceros o providers conversacionales.
* **Relación con otros componentes:** El único soberano lógico; consume evidencias normalizadas y expone el **OperationalAuditResult** como resultado indiscutible de su cálculo.

---

### BEM (Business Evidence Model)
* **Definición corta:** El coprocesador documental y frontera auxiliar externa para la normalización de evidencias de alta entropía.
* **Qué puede hacer:** Extraer filas, columnas y variables de documentos complejos desordenados; preservar referencias cruzadas de origen; y emitir señales de calidad del dato.
* **Qué NO puede hacer:** Diagnosticar, confirmar patologías contables, decidir cursos de acción operacionales, o ser una dependencia interna obligatoria de PymIA.
* **Relación con otros componentes:** Asiste en la extracción compleja para dirigir datos depurados hacia el laboratorio de **PymIA**, perdiendo relevancia operativa a medida que el kernel madura.

---

### BEM_AI
* **Definición corta:** La ruta de enrutamiento documental de alta entropía destinada a PDFs, imágenes o planillas con estructura desordenada.
* **Qué puede hacer:** Canalizar de forma aislada y controlada la extracción pesada mediante OCR o modelos multimodales conversacionales por fuera del core síncrono.
* **Qué NO puede hacer:** Validar la veracidad matemática de los datos extraídos ni omitir las fases de validación interna del kernel.
* **Relación con otros componentes:** Es una rama de salida exclusiva del enrutador condicional de **intake_node** en el **AuditBoundaryGraph**.

---

### INTERNAL_FACT
* **Definición corta:** La ruta de enrutamiento documental local, determinista, síncrona y controlada para procesar planillas limpias de baja entropía.
* **Qué puede hacer:** Procesar localmente planillas `.xlsx` o `.csv` con estructura conocida y entropía controlada, lanzando de forma automática síncronamente el cálculo de auditorías.
* **Qué NO puede hacer:** Procesar PDFs, imágenes o planillas corruptas sin arrojar una excepción fail-closed controlada.
* **Relación con otros componentes:** Es la vía directa por la que transiciona **intake_node** hacia **locate_audit_node** cuando la entrada de datos es estructurada y limpia.

---

### NARRATIVE
* **Definición corta:** La ruta conversacional y de admisión destinada exclusivamente a procesar relatos humanos y textos de chat libres.
* **Qué puede hacer:** Registrar quejas del dueño PyME, asimilar respuestas a preguntas mayéuticas y alimentar el pipeline de anamnesis.
* **Qué NO puede hacer:** Procesar transacciones contables complejas, reconciliar sumas numéricas o emitir reportes de balance general.
* **Relación con otros componentes:** Dirige el texto de chat directamente hacia el enrutador conversacional de **routing_node** en el **AuditBoundaryGraph**, eludiendo la fase de localización física de archivos.

---

### OperationalAuditResult
* **Definición corta:** El documento JSON estructurado y validado que contiene la verdad grounded absoluta calculada para un caso operativo en una sesión.
* **Qué puede hacer:** Agrupar métricas (`ComputedMetric`), hallazgos de patología (`PathologyFindingResult`), señales operativas, hilos activos de auditoría, taxonomía e historial del caso contable.
* **Qué NO puede hacer:** Modificarse o mutar de forma directa por fuera de las reglas rigurosas de consistencia y referencias internas de PymIA.
* **Relación con otros componentes:** Es cargado dinámicamente de forma transitoria en memoria por el **routing_node** de **AuditBoundaryGraph** para fundamentar todas las respuestas que emita **Hermes**.

---

### pathology_routing_summary
* **Definición corta:** La superficie de enrutamiento ligera y expuesta de PymIA que mapea códigos de patologías, estados y siguientes preguntas sugeridas para Hermes.
* **Qué puede hacer:** Facilitar que el enrutador de mensajes asocie de forma inmediata palabras clave con patologías del caso activo sin transferir payloads pesados en memoria.
* **Qué NO puede hacer:** Ejecutar cálculos matemáticos, modificar el estado clínico, o almacenar tablas físicas del negocio.
* **Relación con otros componentes:** Consumido por el enrutador operacional de Hermes (`route_operational_audit_message`) para determinar las respuestas conversacionales adecuadas.

---

### AuditBoundaryGraph
* **Definición corta:** El grafo determinista de orquestación (LangGraph) que gobierna el pipeline de primer contacto e ingesta en `conversa-engine`.
* **Qué puede hacer:** Orquestar de forma síncrona y sessional las transiciones entre la ingesta del documento, la localización del JSON precalculado y el ruteo conversacional.
* **Qué NO puede hacer:** Contaminar el core de `pymia/` con importaciones de LangGraph ni actuar de forma autónoma con bucles de decisión LLM indeterministas.
* **Relación con otros componentes:** Se ejecuta en la frontera externa; encapsula e invoca de forma secuencial y controlada los módulos funcionales del sistema.

---

### Evidence candidate (Evidencia Candidata)
* **Definición corta:** Cualquier dato o matriz estructurada extraída de un archivo por BEM_AI que se encuentra en espera de verificación y cruce de datos.
* **Qué puede hacer:** Aportar valores contables iniciales propicios para formular hipótesis preliminares de trabajo.
* **Qué NO puede hacer:** Considerarse verdad probada del negocio ni sustentar diagnósticos consolidados confirmables.
* **Relación con otros componentes:** Es contrastada con el balance general del caso contable en el kernel de **PymIA** antes de transformarse en evidencia validada.

---

### Evidencia validada
* **Definición corta:** Datos contables y registros del negocio que han aprobado de forma exitosa los controles cruzados de consistencia y veracidad matemática del kernel.
* **Qué puede hacer:** Sustentar cálculos de métricas y justificar la confirmación definitiva de patologías del catálogo formal.
* **Qué NO puede hacer:** Mutarse, devaluarse de rango contable, o desvincularse de sus identificadores de referencia cruzada.
* **Relación con otros componentes:** Da origen a los **hallazgos** confirmables reportados en el **OperationalAuditResult**.

---

### Síntoma
* **Definición corta:** El reflejo o tipificación formal de un dolor del negocio declarado subjetivamente por el dueño en la fase inicial de diálogo.
* **Qué puede hacer:** Estructurar el reclamo difuso en una entidad técnica categorizada (ej. "incertidumbre de rentabilidad") provista de severidad e impacto percibido.
* **Qué NO puede hacer:** Confirmar la presencia de un desvío o patología matemática de forma directa; actúa solo como indicador inicial.
* **Relación con otros componentes:** Es capturado por el pipeline de admisión conversacional y da paso al enrutamiento de **hipótesis** candidatas.

---

### Hipótesis
* **Definición corta:** Una posibilidad de investigación clínica; un plan estructurado de búsqueda de desvíos en la PyME basado en un síntoma tipificado.
* **Qué puede hacer:** Asociar un síntoma a potenciales patologías de catálogo (ej. "margen erosionado") y prescribir con exactitud qué evidencias requerirá el sistema para contrastarla.
* **Qué NO puede hacer:** Asumirse como verdad del negocio ni formular prescripciones operativas o recetas de acción antes de la contrastación cuantitativa.
* **Relación con otros componentes:** Dirige de forma inteligente y selectiva el requerimiento de documentación hacia el laboratorio físico contable.

---

### Diagnóstico
* **Definición corta:** El estado de consolidación lógico de un caso de auditoría PyME; el dictamen contable formal contrastado con los datos.
* **Qué puede hacer:** Declararse únicamente cuando existe suficiencia de evidencias, informando el estado consolidado de desvíos reales e indicando los cursos de acción correctivos prioritarios.
* **Qué NO puede hacer:** Improvisarse "al aire" por el motor conversacional a partir de la narrativa del chat sin sustento del kernel.
* **Relación con otros componentes:** Es el fin último del ciclo científico; se expone de forma directa y justificada en el **OperationalAuditResult**.

---

### Hallazgo (Finding)
* **Definición corta:** La confirmación científica y matemática de la existencia de un desvío en una patología específica del catálogo formal de PymIA.
* **Qué puede hacer:** Vincularse directamente a métricas calculadas con trazabilidad física rigurosa y desencadenar señales operativas y oportunidades de mejora para la PyME.
* **Qué NO puede hacer:** Existir sin un sustento explícito de evidencia validada ni desvincularse de su correspondiente código de patología.
* **Relación con otros componentes:** Es una pieza clave del **OperationalAuditResult** que fundamenta las respuestas que Hermes emite.

---

### Anamnesis
* **Definición corta:** La fase clínica inicial del caso operativo en la que se interroga disciplinadamente al dueño para estructurar sus dolores y abrir hipótesis.
* **Qué puede hacer:** Capturar el vocabulario prioritario del dueño PyME, registrar contradicciones, calibrar la intensidad de su dolor y delimitar las áreas de fricción de la empresa.
* **Qué NO puede hacer:** Procesar balances contables, conciliar extractos de bancos o emitir diagnósticos matemáticos definitivos.
* **Relación con otros componentes:** Es liderada por **Hermes** y culmina con la generación del artefacto de admisión inicial del caso contable.

---

### Primer contacto
* **Definición corta:** La microfase secuencial inicial del diálogo con el usuario antes de contar con la suficiencia del laboratorio documental.
* **Qué puede hacer:** Recibir amigablemente al dueño PyME con preguntas de rigor mayéutico, asimilar su claim y diagnosticar de forma fail-closed la ruta de procesamiento.
* **Qué NO puede hacer:** Cerrar el caso de auditoría, formular recetas generales de optimización del negocio o requerir de forma abrumadora documentación no relacionada.
* **Relación con otros componentes:** Rige la apertura conversacional y orienta la primera fase transaccional del **AuditBoundaryGraph**.

---

### Método hipotético-deductivo
* **Definición corta:** El principio científico que rige las operaciones de SmartPyme: observación, formulación de hipótesis, requerimiento de evidencia, contrastación y consolidación de diagnóstico.
* **Qué puede hacer:** Imponer disciplina epistemológica de diseño, garantizando que el sistema no procese archivos a ciegas sin una hipótesis clínico-operativa directiva.
* **Qué NO puede hacer:** Alterarse o violarse para emitir respuestas especulativas o no fundamentadas en el chat con el usuario.
* **Relación con otros componentes:** Es la doctrina lógica máster que gobierna la interacción secuencial entre todos los componentes y actores de la arquitectura.

---

### Pregunta de rigor
* **Definición corta:** Pregunta estructurada y sistemática formulada por Hermes para recolectar variables indispensables de control (ej. el rubro, período o impacto operativo).
* **Qué puede hacer:** Reducir la vaguedad del relato difuso inicial y estandarizar la taxonomía básica requerida por el kernel de admisión de PymIA.
* **Qué NO puede hacer:** Invadir la experiencia de usuario con cuestionarios abrumadores; se dosifica con elegancia a razón de una pregunta de rigor por turno.
* **Relación con otros componentes:** Alimenta el pipeline de anamnesis inicial liderado por **Hermes**.

---

### Pregunta mayéutica
* **Definición corta:** Pregunta orientada a invitar a la reflexión de gestión del dueño, buscando que identifique el área exacta de su negocio donde reside la ineficiencia.
* **Qué puede hacer:** Direccionar la atención del dueño de la PyME hacia los desvíos sospechados (ej. cuestionar si se calcula margen por producto) y preparar el terreno intelectual para la entrega de evidencia.
* **Qué NO puede hacer:** Imponer aserciones técnicas culpabilizadoras ni sugerir desvíos antes de la contrastación matemática del kernel.
* **Relación con otros componentes:** Es formulada por **Hermes** a sugerencia del catálogo de patologías y el resumen de enrutamiento.

---

### Fail-closed (Fallo en cerrado)
* **Definición corta:** La regla de seguridad operativa absoluta que exige que ante cualquier anomalía, ambigüedad severa, error del sistema o falta de evidencia, el sistema prevea un desvío hacia un estado seguro y controlado, rehusándose a improvisar.
* **Qué puede hacer:** Detener la ejecución del flujo, reportar amigablemente que no es seguro diagnosticar en ese estado, y requerir el tipo de evidencia correcto sin propagar fallas catastróficas.
* **Qué NO puede hacer:** Dejar que una excepción inesperada de disco o red tire abajo el bot de Telegram o exponga trazas de depuración internas al usuario final.
* **Relación con otros componentes:** Rige transversalmente las transiciones del **AuditBoundaryGraph** y los middlewares de integración del backend.

---

### DocumentContextClassifier
* **Definición corta:** El componente de ingesta encargado de clasificar heurísticamente el dominio contable temático general de un documento analizando la semántica de sus hojas y cabeceras.
* **Qué puede hacer:** Identificar si un archivo contiene matrices asociadas a la categoría de "ventas", "compras", "stock" o "caja_banco" para guiar su asimilación en el laboratorio contable.
* **Qué NO puede hacer:** Calcular métricas contables finales de margen o liquidez de forma autónoma.
* **Relación con otros componentes:** Asiste en el pipeline controlado de curaduría de evidencias para determinar la idoneidad y el destino del parseo síncrono.

---

### OCR (Optical Character Recognition)
* **Definición corta:** El motor de reconocimiento de texto sobre imágenes y PDFs no estructurados utilizado como primer paso en la ruta externa de bajo nivel.
* **Qué puede hacer:** Traducir pixeles visuales en matrices de texto estructurado para que puedan ser leídas de forma programática.
* **Qué NO puede hacer:** Garantizar la precisión matemática de los números extraídos de la planilla contable ni suplir la validación cruzada de PymIA.
* **Relación con otros componentes:** Es un componente utilitario secundario y de bajo nivel encapsulado exclusivamente bajo el dominio de **BEM_AI**.

---

### PDF/imagen
* **Definición corta:** Archivos de evidencia física no tabulares que carecen de una representación secuencial directa y estructurada de datos.
* **Qué puede hacer:** Aportar registros de soporte contable en formatos de alta entropía (como fotos de facturas impresas, tickets de transacciones bancarias o balances en PDF).
* **Qué NO puede hacer:** Procesarse directamente de forma local y síncrona por el parser rápido del entorno controlado sin pasar por OCR o visión multimodal.
* **Relación con otros componentes:** Se canalizan obligatoria y exclusivamente por la ruta **BEM_AI** de extracción y curación externa de bajo acoplamiento.

---

### Bypass
* **Definición corta:** La desviación o cortocircuito de la arquitectura oficial en el que un componente externo (conversacional) intenta diagnosticar o formular aserciones operacionales directamente al dueño eludiendo el cálculo riguroso del kernel de PymIA.
* **Qué puede hacer:** Provocar alucinaciones graves en el chat conversacional, reportar desvíos inexistentes en el negocio y destruir la confianza técnica en la herramienta.
* **Qué NO puede hacer:** Generar un flujo de negocio robusto, trazable ni alineado a los estándares científicos de SmartPyme.
* **Relación con otros componentes:** Se previene de forma estricta confinando el motor conversacional exclusivamente al consumo pasivo de la superficie de **pathology_routing_summary** y del **OperationalAuditResult**.
