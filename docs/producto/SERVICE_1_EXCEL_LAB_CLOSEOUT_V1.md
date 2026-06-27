# SERVICE_1_EXCEL_LAB_CLOSEOUT_V1

## Estado

```text
Tipo: IMPLEMENTATION_CLOSEOUT
Estado: CLOSED
Runtime impact: BASELINE_INGESTION_READY
Pipeline impact: INTEGRATED
XLSX impact: READ_AND_CURATED
LLM impact: NONE
```

## Propósito

Cerrar documentalmente la **Etapa 3 — Productización de Laboratorio Excel** (`SERVICE_1_EXCEL_LAB_PRODUCTIZATION_V1`).

Este frente extrajo la lógica de ingesta, profiling y estructuración de Excel (que residía aislada en un script de desarrollo) y la convirtió en un módulo productivo importable, testeado y cableado dentro de `pymia.smartpyme`.

---

# 1. Cadena previa

```text
SERVICE_1_FIRST_AID_FAMILY_CLOSEOUT_V1
→ tools/document_ingestion.py (desarrollo aislado)
→ SERVICE_1_EXCEL_LAB_PRODUCTIZATION_V1 (productizado)
```

---

# 2. Archivos modificados y creados

### Creados
*   `PymIA-Live/pymia/smartpyme/excel_lab_ingestion_v1.py` (Núcleo productizado por fronteras)
*   `PymIA-Live/tests/smartpyme/test_excel_lab_ingestion_boundary_v1.py` (Tests focales de frontera)

### Modificados (Wrapper de compatibilidad e import rewiring)
*   `PymIA-Live/tools/document_ingestion.py` (Wrapper que re-exporta la lógica del núcleo)
*   `PymIA-Live/pymia/smartpyme/service_1_document_curation_report_to_owner_prompt_batch_bridge_v1.py` (Importación del módulo productivo)
*   `PymIA-Live/pymia/smartpyme/structured_evidence_builder.py` (Importación del módulo productivo)

---

# 3. Fronteras de la Capacidad

El nuevo módulo `excel_lab_ingestion_v1` delimita con precisión tres fronteras funcionales:

1.  **Ingestión / Lectura Estructural:**
    *   `XlsxDocumentIngestor` lee workbooks reales usando el profiler declarativo.
    *   `ContextClassifier` asigna contextos semánticos primarios a las hojas (ventas, stock, caja_banco, senales_operativas, generic).
    *   `RawTable` contiene la estructura cruda limpia del archivo.
2.  **Profiling / Extracción:**
    *   `SemanticFieldMapper` asocia las columnas del workbook a campos canónicos aplicando clasificadores semánticos y reglas de fallback de texto.
    *   `DocumentCurator` ejecuta validaciones sobre los datos normalizados (validación de tipos numéricos y tipado contra modelos Pydantic `VentaRow`, `ProductoRow`, etc.).
    *   `ColumnConfirmationBuilder` construye la matriz de confirmación de columnas, identificando patrones negativos y asignando estados pendientes.
3.  **Output Estructurado:**
    *   `StructuredEvidenceExporter` exporta la curación a un objeto de verdad de evidencia `StructuredEvidence` consumible por el core.
    *   Bloquea variables calculadas si las columnas requeridas carecen de confirmación humana explícita.
    *   `persist_curation_artifacts` escribe a disco las representaciones JSON de los análisis intermedios y de la evidencia final.

---

# 4. Lo que NO hace

*   No resuelve fórmulas interactivas dinámicas en XLSX (sujeto a Factoría / Exceland).
*   No inicia chatbot ni procesa inputs mediante LLM.
*   No ejecuta conciliaciones ni diagnóstico operativo.

---

# 5. Tests Focales

Archivo: `PymIA-Live/tests/smartpyme/test_excel_lab_ingestion_boundary_v1.py`

Verificaciones cubiertas:
*   Clasificación correcta de contextos por heurística de palabras clave.
*   Ingestión estructural y lectura de filas ignorando filas vacías o de encabezado incorrecto.
*   Mapeo de sinónimos y fallbacks en mapper semántico.
*   Validaciones duras de conversión numérica y tipado de registros detectando errores.
*   Deducción y bloqueo por patrones negativos (ej. "Medio de Pago" demotado a informational/unknown).
*   Generación correcta de `StructuredEvidence` emitiendo advertencias bloqueantes ante falta de confirmación.
*   Cálculo correcto de métricas de ventas, costos y márgenes sobre matrices confirmadas.
*   Persistencia exitosa de archivos JSON intermedios y finales.

Resultado:
*   `8 passed` en el archivo focal.
*   `1512 passed` en la suite de validación completa del repositorio.

---

# 6. Madurez de la Familia

```text
INGESTION_READER: IMPLEMENTED_VALIDATED
SEMANTIC_MAPPER: IMPLEMENTED_VALIDATED
EVIDENCE_EXPORTER: IMPLEMENTED_VALIDATED
WIRING: COMPLETED (consumers updated, backward wrapper verified)
```

---

# 7. Próxima Etapa

```text
ETAPA 4 — RESOLUCIÓN DE FACTORÍA EXCEL
```

Objetivo:
```text
Formalizar la dependencia con exeland2 en el repo y resolver el bridge de generación XLSX física.
```

---

# 8. Veredicto

```text
SERVICE_1_EXCEL_LAB_PRODUCTIZATION_V1 = CLOSED_IN_SCOPE_RUNTIME
```
