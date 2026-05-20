# Especificación de Diseño Conceptual: DocumentContextClassifier v1

## Estado
Documento canónico de diseño de arquitectura  
**Fecha:** Mayo 2026  
**Ámbito:** Admisión documental, clasificación semántica de evidencia y triaje

---

## Propósito

Definir el diseño conceptual, interfaces lógicas, límites operativos e integraciones de la compuerta inteligente de admisión documental: el **`DocumentContextClassifier`** v1. Este componente tiene como fin clasificar semánticamente cualquier archivo aportado por el dueño de la PyME antes de entregarlo a los parsers u orquestadores del sistema.

---

## 1. Problema que Resuelve

Durante la interacción con una PyME en el primer contacto, la entrega de documentación física es altamente caótica e indeterminista. El sistema se enfrenta a tres problemas críticos:

1. **Incertidumbre Documental:** Recibir archivos cuyos nombres o extensiones no indican con claridad qué información registran (ej. un archivo llamado `Datos_Finales.xlsx` que podría ser de stock, ventas o saldos bancarios).
2. **Clasificación de Dominio Dinámica:** Identificar el dominio operativo temático exacto del archivo analizando metadatos, nombres de hojas de cálculo y cabeceras de columnas, dirigiendo el archivo hacia la subestructura de procesamiento correspondiente.
3. **Prevención de Bypass Semántico:** Evitar que una planilla de un dominio incorrecto (ej. conciliaciones impositivas o liquidaciones laborales) ingrese al motor de cálculo de patologías de PymIA, lo que podría desencadenar falsos positivos de diagnóstico o fallos en las fórmulas matemáticas del kernel.

---

## 2. Qué NO Resuelve (Límites Estrictos)

Para preservar la soberanía lógica y mantener una arquitectura libre de acoplamientos, el `DocumentContextClassifier` tiene prohibido:

* **No calcula métricas:** No computa márgenes, inventarios, mermas de producción ni flujos de caja.
* **No diagnostica patologías:** No opina sobre la salud operacional de la PyME.
* **No extrae texto mediante OCR:** No procesa visualmente imágenes ni lee caracteres de PDFs; se limita a consumir metadatos o previews de texto provistos externamente.
* **No reemplaza a BEM_AI:** No realiza la extracción masiva de tablas pesadas de alta entropía.
* **No convalida evidencia:** Clasificar un archivo dentro de una categoría contable no lo convierte en *Evidencia Validada*; se mantiene estrictamente en el rango de **Evidencia Candidata** hasta que PymIA verifique su congruencia matemática.

---

## 3. Contrato de Entrada (Inputs)

Para realizar una clasificación deterministicamente controlada, el clasificador consume las siguientes variables en su interfaz de entrada:

* **`file_name`** (str): Nombre físico original del archivo (ej. `tabla_stock_deposito.xlsx`).
* **`mime_type`** (str): Tipo MIME detectado durante la carga (ej. `application/vnd.ms-excel`).
* **`extension`** (str): Extensión física del archivo en minúsculas (ej. `.csv`, `.xlsx`, `.pdf`, `.png`).
* **`entropy_level`** (float): Nivel estimado de entropía o ruido estructural calculado por la capa de ingesta inicial.
* **`sheet_names`** (list[str]): Nombres de las pestañas o sábanas de datos identificadas en el libro (vacío para archivos planos, PDFs o imágenes).
* **`column_headers`** (list[str]): Cabeceras de columnas identificadas en las filas superiores de datos.
* **`extracted_text_preview`** (str): Un búfer limitado (máximo primeros 1000 caracteres) del texto extraído de las primeras páginas para PDFs o imágenes (obtenido mediante un parsing rápido externo).
* **`source_type`** (str): Canal de origen por el cual se cargó el archivo (ej. `telegram_upload`, `web_dashboard`).

---

## 4. Contrato de Salida (Outputs)

El clasificador devuelve un objeto estructurado que determina el destino operativo del archivo:

* **`document_context`** (Literal): Una de las diez clases semánticas de negocio mínimas soportadas.
* **`ingestion_route`** (Literal): La ruta lógica asignada: `BEM_AI` (extracción pesada de alta entropía), `INTERNAL_FACT` (procesamiento directo y síncrono local) o `NARRATIVE` (procesamiento de chat plano).
* **`confidence`** (Literal["high", "medium", "low"]): El nivel de certidumbre en la asignación del contexto y ruta.
* **`reasons`** (list[str]): Argumentos lógicos o heurísticos de peso que justifican la decisión (ej. *"Cabeceras contienen 'factura' y 'cliente', asociando al dominio ventas"*).
* **`required_followup`** (str | None): Pregunta de rigor o aclaración sugerida para el usuario en caso de confianza baja o clasificación como `desconocido`.
* **`evidence_candidate_type`** (str): Categoría formal de evidencia candidata asignada (ej. `xlsx_sales_evidence`).

---

## 5. Clases Semánticas Mínimas Soportadas

El clasificador mapea la evidencia a uno de estos diez dominios operativos de negocio:

1. **`ventas`**: Registros de transacciones de salida, listas de pedidos, facturación diaria.
2. **`stock`**: Inventarios físicos, recuentos de depósitos, listas de códigos SKU.
3. **`caja`**: Libros de movimientos de caja chica, saldos de cuentas corrientes bancarias o Mercado Pago.
4. **`compras`**: Órdenes de compra de insumos, facturas recibidas de proveedores.
5. **`cobranzas`**: Registros de cuentas de clientes pendientes de cobro, cheques en cartera.
6. **`facturación`**: Emisiones fiscales, reportes consolidados del módulo impositivo.
7. **`fiscal/impositivo`**: Retenciones, liquidaciones de IVA y tasas impositivas de AFIP/entes reguladores.
8. **`laboral`**: Planillas de asistencia, liquidaciones de haberes del personal, aportes patronales.
9. **`producción`**: Fórmulas, mermas de materia prima, órdenes de fabricación interna.
10. **`desconocido`**: Archivos que no coinciden con ningún dominio o presentan cabeceras mixtas indescifrables.

---

## 6. Reglas de Enrutamiento y Epistemología

El clasificador rige sus decisiones lógicas mediante estrictas normas de seguridad de datos:

* **PDF e Imagen siempre van a `BEM_AI`:** Cualquier archivo cuya extensión sea `.pdf`, `.png`, `.jpg`, `.jpeg` o similar se deriva de forma obligatoria hacia la ruta externa de apoyo `BEM_AI`. Jamás se autoriza su procesamiento directo por la vía local.
* **`INTERNAL_FACT` es de uso restrictivo:** Solo se habilita para archivos `.xlsx` o `.csv` de baja entropía ($\le 0.3$), con cabeceras de columnas legibles y un nivel de confianza de clasificación `high`.
* **Rango de Evidencia Candidata:** Los outputs de este componente operan exclusivamente en el rango de **Evidencia Candidata**. Bajo ninguna circunstancia se asume que un archivo clasificado exitosamente constituye prueba contable verificada sin pasar por las validaciones de consistencia de PymIA.

---

## 7. Relación con Hermes (El Conducto)

* **Resolución de Ambigüedades:** Si el clasificador arroja un nivel de confianza `low` o clasifica el archivo como `desconocido`, el campo `required_followup` se poblará con una pregunta de rigor orientada al usuario.
* **Hermes pregunta sin suponer:** Hermes consumirá este followup de forma disciplinada, consultándole de forma amigable al dueño de la PyME qué información registra su planilla en lugar de especular o forzar una asignación de dominio errónea.
* **Hermes no diagnostica:** Hermes utiliza el contexto asignado únicamente para guiar la conversación y pedir la documentación complementaria prescrita por las hipótesis de PymIA.

---

## 8. Relación con PymIA (El Computador Soberano)

* **PymIA contrasta:** El kernel de PymIA recibe las variables normalizadas y las asocia a los hilos de auditoría activos. Contrasta las relaciones cruzadas de los datos (ej. cruzar los cobros declarados en el Excel de caja contra la facturación del Excel de ventas) para corroborar su veracidad matemática.
* **Soberanía del `OperationalAuditResult`:** Toda confirmación o descarte de patologías operativas permanece confinada a los cálculos matemáticos grounded de PymIA, reflejados exclusivamente en el `OperationalAuditResult`.

---

## 9. Pruebas de Integración Futuras (Suite de Verificación)

Para validar el clasificador cuando se implemente su código, se diseñará una suite de pruebas que aserte:

1. **`test_classifier_tabular_sales_xlsx`**: Una planilla de ventas típica con cabeceras en español (Fecha, Detalle, Importe, Cliente) debe clasificarse con confianza `high`, dominio `ventas` y ruta `INTERNAL_FACT`.
2. **`test_classifier_pdf_scanned_invoice`**: Un PDF impositivo de AFIP debe clasificarse con dominio `fiscal/impositivo` e `ingestion_route` de `BEM_AI` de forma síncrona.
3. **`test_classifier_unreadable_xlsx_fallback`**: Una planilla XLSX con columnas numéricas sin encabezados legibles (ej. `"col_1"`, `"col_2"`) debe forzar un dominio `desconocido` con confianza `low` y generar un mensaje estructurado de followup para Hermes.

---

## 10. Riesgos

* **Bypass por Nombres de Columnas Homónimos (Conflicto Multidominio):** Una planilla que registre tanto cobros impositivos como ventas diarias en la misma pestaña puede confundir al clasificador. *Mitigación:* Se implementará un conteo ponderado de palabras clave que priorice las clases más específicas antes de asignar `mixed` o `desconocido`.
* **Evasión de Ruta por Extensión Falsa:** Un usuario renombrando un archivo PDF a `.xlsx` para intentar forzar la ruta local. *Mitigación:* El pipeline de ingesta síncrono debe validar los magic bytes o estructura del libro físico de cálculo, arrojando un error fail-closed antes de activar el clasificador.
