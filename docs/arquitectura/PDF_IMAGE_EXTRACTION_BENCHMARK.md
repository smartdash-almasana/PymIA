# Especificación de Benchmark de Extracción PDF/Imagen

## Estado
Documento canónico de diseño de pruebas y evaluación  
**Fecha:** Mayo 2026  
**Ámbito:** Admisión documental, evaluación de tecnologías de extracción de bajo acoplamiento

---

## Propósito

Definir el marco de evaluación comparativa (benchmark) para clasificar, parsear y extraer de forma estructurada la información contenida en documentos visuales de alta entropía (PDFs escaneados, imágenes de facturas, capturas de pantalla de transacciones) antes de habilitar su integración segura en la ruta **`BEM_AI`**.

---

## 1. Objetivo del Benchmark

El objetivo de este benchmark es evaluar de forma empírica y rigurosa la velocidad, el costo computacional/financiero, la precisión impositiva-contable y el nivel de ruido de diferentes tecnologías de extracción de texto y tablas. Se busca elegir un motor de extracción secundario de bajo acoplamiento que asista al sistema convirtiendo documentos visuales caóticos en datos planos tabulares estructurados (JSON/Markdown) legibles por el kernel de PymIA.

---

## 2. Motores a Evaluar

Se seleccionan tres frentes tecnológicos con distintos compromisos de coste, privacidad y rendimiento:

1. **IBM Docling (Local - Open Source):** Motor local de última generación diseñado para el parsing avanzado de documentos estructurados. Utiliza modelos locales livianos para la detección de layouts de páginas, orden de lectura y reconstrucción vectorial de tablas complejas sin llamadas de red a internet.
2. **Google Document AI (Nube - Comercial):** API de aprendizaje profundo en la nube de Google Cloud optimizada para la extracción estructurada de documentos fiscales (facturas, recibos, remitos). Excelente tasa de precisión pero con costo financiero y dependencias en la nube.
3. **Local OCR (Tesseract / PyMuPDF - Referencia básica):** Motores de extracción de texto básicos en local. Sirven de línea base (baseline) comparativa para medir el ROI y la ganancia de precisión de los motores avanzados frente al procesamiento tradicional.

---

## 3. Reglas Doctrinales Inquebrantables

La ejecución de pruebas y el procesamiento de documentos visuales se rigen por los principios de la doctrina semántica de PymIA:

* **PymIA no cree: contrasta; BEM no diagnostica: extrae.**
* **PDF e Imagen nunca entran directo a `INTERNAL_FACT`:** Cualquier archivo con extensión visual se deriva de forma obligatoria y excluyente por la ruta `BEM_AI`. Jamás se autoriza su procesamiento local síncrono directo por el parser de planillas.
* **El extractor no diagnostica:** El motor de parsing tiene estrictamente prohibido formular opiniones, emitir juicios operacionales, calificar la liquidez o la rentabilidad de la PyME, o resumir la salud del negocio.
* **El extractor no completa valores:** Si una celda contable es ilegible o está vacía en el PDF original, el extractor debe reportar `None` o `NaN`, jamás debe "calcular", deducir o aproximar el importe de forma autónoma.
* **El output es evidencia candidata:** Todo resultado estructurado devuelto por el extractor opera con rango de *Evidencia Candidata*. No es prueba contable validada hasta que el kernel de PymIA verifique su congruencia y cuadre matemático contra otras fuentes del negocio.

---

## 4. Verificación Previa de la Interfaz de Línea de Comandos (CLI)

Antes de ejecutar pruebas automáticas con la librería Python, se validará de forma manual y síncrona el estado de las herramientas CLI del sistema mediante los siguientes comandos en la terminal Linux:

```bash
# Validar si el ejecutable de Docling está en el PATH
which docling

# Validar las herramientas auxiliares de conversión
which docling-tools

# Comprobar la respuesta de ayuda y versión de la CLI
docling --help

# Comprobar la respuesta de ayuda de conversión
docling-tools --help
```

---

## 5. Comandos Tentativos de Extracción (A verificar según CLI instalada)

Los siguientes comandos representan los scripts de prueba tentativos para realizar las conversiones de PDF a Markdown estructurado o JSON nativo de layout (estos comandos están sujetos a revisión y ajuste fino una vez que se complete la instalación de dependencias en el sprint de ejecución):

### Conversión Tentativa PDF → Markdown
```bash
docling-tools convert --to md --output /tmp/pymia_pdf_smoke/prueba.md /opt/PymIA/prueba_excels/factura_ejemplo.pdf
```

### Conversión Tentativa PDF → JSON (Estructura de Layout Completa)
```bash
docling-tools convert --to json --output /tmp/pymia_pdf_smoke/prueba.json /opt/PymIA/prueba_excels/factura_ejemplo.pdf
```

---

## 6. Outputs Esperados en `/tmp/pymia_pdf_smoke`

Para realizar la auditoría comparativa cruzada de los motores evaluados en el benchmark, cada motor procesará un lote de facturas de prueba y guardará de forma aislada los siguientes artefactos físicos bajo `/tmp/pymia_pdf_smoke/{engine_name}/`:

* **`raw_text.txt`**: El volcado de texto plano lineal crudo extraído del PDF.
* **`document_structure.md`**: El documento exportado en Markdown estructurado, validando la jerarquía de títulos e integridad de tablas.
* **`structured.json`**: El JSON jerárquico nativo de la extracción que preserva metadatos y coordenadas de bounding boxes.
* **`extracted_tables/`**: Directorio conteniendo archivos individuales `.csv` por cada tabla contable detectada y extraída.
* **`metadata_metrics.json`**: Métricas operativas de la corrida (duración, consumo de memoria de la VM, tasa de confianza informada por el motor).

---

## 7. Métricas de Evaluación Comparativa

El benchmark medirá con precisión matemática cada motor a través de las siguientes 7 variables de control:

1. **Texto (Precisión de caracteres):** Tasa de caracteres correctos (Word Error Rate - WER) contrastada con un texto base (Ground Truth) de referencia verificado manualmente.
2. **Tablas (Integridad estructural):** Precisión en la detección de bordes, celdas fusionadas, cantidad de filas/columnas correctas extraídas y consistencia de las cabeceras.
3. **Orden de Lectura (Coherencia lineal):** Capacidad del motor de leer la factura de forma secuencial lógica, evitando mezclar columnas de tablas paralelas.
4. **Trazabilidad por Página (Paginación):** Conservación y herencia estricta del número de página original en cada párrafo o bloque de datos extraído.
5. **Tiempo (Latencia):** Tiempo transcurrido (en milisegundos) desde la invocación de la API de conversión hasta la escritura del JSON final en disco.
6. **Costo (Computacional y Financiero):**
   * *Docling/Local OCR:* Carga de CPU, RAM de la VM y consumo de disco.
   * *Google Document AI:* Costo financiero exacto en dólares por página procesada según precios vigentes de GCP.
7. **Ruido (Basura tipográfica):** Tasa de caracteres basura, letras rotas o símbolos extraños generados por fallas del motor OCR sobre imágenes de baja resolución.

---

## 8. Riesgos Identificados

* **Privacidad de Datos del Cliente:** Google Document AI requiere enviar la documentación contable sensible de las PyMEs fuera de la infraestructura local del cliente. Exige firmar acuerdos de confidencialidad de datos y limitar el entrenamiento público de modelos.
* **Costo Financiero Inesperado:** La facturación basada en páginas de las APIs en la nube puede dispararse exponencialmente ante la carga de extractos bancarios de cientos de páginas. Se sugiere limitar de forma estricta el tamaño del archivo subido en el primer contacto.
* **Peso de Dependencias en Local (Docling):** Docling requiere descargar modelos PyTorch y layout analyzers locales de peso considerable (varios gigabytes) en disco, lo que aumenta las necesidades de almacenamiento e infraestructura de la máquina virtual o contenedor del backend.
* **OCR Imperfecto en Datos Críticos:** Que una lectura defectuosa confunda un `8` con un `3` o un `0` con un `6` en una columna de "precio_unitario", falseando las métricas de margen. *Mitigación:* Se implementará un filtro de consistencia matemática en el kernel de PymIA que alerte sobre importes parciales que no cuadren con el total impositivo de la factura.
* **Falso Sentido de Evidencia Validada:** Que el usuario o el motor asuman que porque el PDF se parseó con éxito y se generó una tabla limpia, el negocio ha sido auditado. *Mitigación:* Reforzar en la interfaz de Hermes que todo dato extraído de PDF se mantiene en estado "preliminar" hasta su conciliación.

---

## 9. Criterios de Selección del Motor de Producción

Se seleccionará el motor óptimo ponderando las métricas bajo la siguiente regla de decisión:
* **Si el volumen de facturas es masivo y el presupuesto es acotado:** Se preferirá **Docling local** por su costo marginal nulo en producción y protección estricta de la privacidad local del cliente, siempre que la VM cumpla con los requisitos mínimos de hardware.
* **Si la tasa de legibilidad de imágenes/fotos de baja resolución es crítica:** Se preferirá **Google Document AI** debido a la robustez superior de su red multimodal en la nube para discernir caracteres distorsionados, asumiendo su costo por llamada.

---

## 10. Qué queda Prohibido

* **Prohibido integrar código:** No se autoriza escribir o subir scripts funcionales de extracción a la carpeta `tools/` o `conversa-engine/` durante esta fase de benchmarking.
* **Prohibido instalar paquetes:** No se permite correr `pip install` para instalar dependencias de visión u OCR pesadas de forma productiva.
* **Prohibido alterar BEM_AI:** El diseño e implementación física de workflows asíncronos o jobs en el BEM real permanece inalterado para salvaguardar el estado de la entrega.

---

## 11. Próximo Smoke Manual sugerido (Sin cambios en el Repo)

El siguiente paso recomendado consistirá en un smoke test manual aislado:
1. Crear una carpeta `/tmp/pymia_pdf_smoke/` en la terminal Linux de la VM de desarrollo.
2. Descargar de forma temporal una factura o PDF de prueba real a esa carpeta.
3. Ejecutar los comandos de CLI del motor que se encuentre instalado o probar de forma aislada el script de conversión Docling local en un entorno alternativo para evaluar la latencia y la legibilidad del Markdown resultante antes de proponer código al repositorio productivo.
