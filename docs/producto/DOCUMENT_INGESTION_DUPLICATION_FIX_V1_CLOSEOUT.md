# DOCUMENT_INGESTION_DUPLICATION_FIX_V1_CLOSEOUT

## Estado

```text
Tipo: CODE_FIX_CLOSEOUT
Estado: CLOSED
Runtime impact: NONE
Pipeline impact: NONE
XLSX delivery impact: NONE
LLM impact: NONE
```

## Problema

Existían dos versiones de `document_ingestion.py`:

```text
tools/document_ingestion.py
PymIA-Live/tools/document_ingestion.py
```

La versión raíz estaba desfasada respecto de la versión viva de `PymIA-Live`.

Riesgo:

```text
Dependiendo del PYTHONPATH, `from tools.document_ingestion import ...` podía resolver a una versión vieja sin ColumnConfirmationBuilder, ColumnConfirmationMatrix ni bloqueo de cálculo por columnas no confirmadas.
```

---

# 1. Decisión

Fuente canónica:

```text
PymIA-Live/tools/document_ingestion.py
```

La versión raíz queda como shim de compatibilidad:

```text
tools/document_ingestion.py
```

Su función es cargar y re-exportar la implementación viva de `PymIA-Live`.

---

# 2. Archivos modificados

```text
tools/document_ingestion.py
tests/test_document_ingestion.py
```

Archivo agregado por sincronización de contrato:

```text
pymia/contracts/column_confirmation_v1.py
```

Motivo:

```text
La capa raíz necesitaba resolver imports de column_confirmation_v1 usados por la implementación viva.
```

---

# 3. Ajuste de tests

`tests/test_document_ingestion.py` fue actualizado para reflejar el comportamiento vivo actual:

```text
computed_variables == {}
calculation_blocked == True
owner_questions presentes
```

Motivo:

```text
La versión viva no calcula variables si las columnas computacionales no están confirmadas por el dueño.
```

---

# 4. Validación ejecutada

Comando:

```text
python -m pytest tests/test_document_ingestion.py PymIA-Live/tests/tools/test_column_confirmation_builder.py PymIA-Live/tests/tools/test_structured_evidence_exporter_compute_variables.py PymIA-Live/tests/tools/test_structured_evidence_compute_blocks_unconfirmed_columns.py -q
```

Resultado:

```text
44 passed in 30.12s
```

---

# 5. Límites

```text
No se abrió runtime productivo.
No se tocó vertical_pipeline.py.
No se creó service_1_pipeline.py.
No se generó XLSX delivery.
No se abrió LLM adapter.
No se resolvió File Intake V1 completo.
```

---

# 6. Veredicto

```text
DOCUMENT_INGESTION_DUPLICATION_FIX_V1 = CLOSED
```

Condición:

```text
La fuente canónica queda en PymIA-Live/tools/document_ingestion.py. La raíz sólo conserva shim de compatibilidad.
```
