# SERVICE_1_OPERATOR_HARNESS_REAL_OUTPUT_AUDIT_V1

## Estado

```text
Tipo: OUTPUT_AUDIT
Servicio: SERVICE_1
Lane: Operator Harness First Aid
Estado: DRAFT_APPLIED
Runtime impact: NONE
Pipeline impact: VALIDATION_ONLY
FSM impact: NONE
LLM impact: NONE
Chatbot impact: NONE
```

## Objetivo

Auditar qué produce realmente `SERVICE_1_OPERATOR_HARNESS_V1` para un caso demo de First Aid.

La pregunta de producto es:

```text
¿Qué carpeta y qué artefactos puede revisar o entregar un operador?
```

---

# 1. Caso auditado

Caso sample:

```text
service_1_first_aid_comercio_minorista_demo
```

Entrada:

```text
precio_margen_basico
caja_diaria_triage
stock_alertas_basicas
```

Ejecución:

```text
operator harness
→ pipeline V1
→ delivery flow
→ carpeta de entrega
```

---

# 2. Inventario esperado de artefactos

La carpeta de entrega debe contener exactamente:

```text
first_aid_001_precio_margen_basico.xlsx
first_aid_002_caja_diaria_triage.xlsx
first_aid_003_stock_alertas_basicas.xlsx
operator_report.txt
summary.txt
```

---

# 3. Contrato esperado de cada XLSX

Cada XLSX debe abrir y contener estas hojas:

```text
Resumen
Datos usados
Resultados
Faltantes
Limitaciones
Claims prohibidos
Notas técnicas
```

Cada XLSX debe mantener:

```text
service_name = SERVICE_1
status = OK para el caso demo
claims prohibidos visibles
limitaciones visibles
```

---

# 4. Contrato esperado de summary.txt

`summary.txt` debe incluir:

```text
Resultados procesados: 3
precio_margen_basico: OK
caja_diaria_triage: OK
stock_alertas_basicas: OK
Limitaciones principales
Aclaraciones conservadoras
No es un diagnostico integral
No confirma saldo bancario real
No confirma stock fisico real
Entrega preliminar basada en datos declarados.
```

---

# 5. Contrato esperado de operator_report.txt

`operator_report.txt` debe incluir:

```text
Caso
Case ID
Tools ejecutadas: 3
resultados por tool
notas operador
Entrega preliminar basada en datos declarados.
```

---

# 6. Metadata esperada

La metadata devuelta por el harness debe coincidir con los archivos generados:

```text
generated_files == delivery_flow.deliveries[*].output_path
delivery_count == 3
tool_refs preservados
runtime_authorized == False en harness, pipeline y delivery_flow
```

---

# 7. Test de auditoría

Archivo:

```text
PymIA-Live/tests/smartpyme/test_service_1_operator_harness_real_output_audit_v1.py
```

Comando:

```text
python -m pytest tests/smartpyme/test_service_1_operator_harness_real_output_audit_v1.py tests/smartpyme/test_service_1_operator_harness_v1.py tests/smartpyme/test_service_1_pipeline_v1.py -q
```

---

# 8. Veredicto esperado

```text
SERVICE_1_OPERATOR_HARNESS_REAL_OUTPUT_AUDIT_V1_READY
```
